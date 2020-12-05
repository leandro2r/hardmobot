import docker
import logging
import re
import telebot
import time
from datetime import datetime

if __package__ is None or __package__ == '':
    from config import Config
    from data import Data
else:
    from promobot.config import Config
    from promobot.data import Data


logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

config = Config().data
bot = telebot.TeleBot(
    config['telegram'].get('token')
)

data = Data(
    config.get('db')
)


def handle_help(message, **kwargs):
    msg = ''
    support = kwargs.get('support')

    if message.chat.type == 'private':
        if data.find_chat(message.chat.id):
            msg = (
                'You can chat with me using one of the '
                'following commands below: /{}'.format(
                    '\n/'.join(support)
                )
            )

    return msg


def handle_intro(message, **kwargs):
    msg = ''
    cmd = kwargs.get('cmd')
    args = message.text.split()[1:]

    if message.chat.type == 'private':
        d = {
            'id': message.chat.id,
            'user': '{} {} ({})'.format(
                message.chat.first_name,
                message.chat.last_name,
                message.chat.username,
            )
        }

        if len(args) > 0:
            if config['telegram'].get('chat_passwd') == args[0]:
                if 'start' in cmd:
                    msg = 'Now you gonna receive all reports!'
                    data.add_chat(d)
                elif 'stop' in cmd:
                    msg = 'You will no longer receive the reports!'
                    data.del_chat(d)
                else:
                    forall = 'I\'m under maintenance...'
                    msg = 'Message has been sent for all chats!'

                    if len(args) > 1:
                        forall = ' '.join(args[1:])

                    for id in data.list_chats():
                        bot.send_message(
                            id,
                            text='Hey all, {}'.format(
                                forall
                            )
                        )
            else:
                d.update({
                    'date': datetime.utcfromtimestamp(
                        message.date
                    ).strftime('%Y-%m-%dT%H:%M:%S.000Z'),
                })
                data.add_intruder(d)

    return msg


def handle_mgmt(message, **kwargs):
    msg = ''
    cmd = kwargs.get('cmd')
    args = message.text.split()[1:]

    if message.chat.type == 'private':
        if data.find_chat(message.chat.id):
            if 'config' in cmd:
                if len(args) > 0:
                    data.add_config(args)

                msg = 'Configs:\n'
                for d in data.list_config():
                    for k, v in d.items():
                        msg += '{}={}\n'.format(
                            k, v
                        )
            elif 'docker' in cmd:
                info = 'status'
                if len(args) > 0:
                    info = args[0]

                msg = manage_docker(info)
            elif 'who' in cmd:
                who = '\n'.join(
                    str(i) for i in data.list_users(all=True)
                )
                msg = 'Users:\n{}'.format(
                    who,
                )
            else:
                msg = 'Empty keyword list.'

                if len(args) > 0:
                    if 'add' in cmd:
                        data.add_keywords(args)
                    elif 'del' in cmd:
                        data.del_keywords(args)

                items = data.list_keywords()

                if items:
                    msg = '\n'.join(
                        items
                    )

    return msg


def manage_docker(info):
    msg = ''
    client = docker.from_env()

    ps = client.containers.list(
        filters={'name': 'promobot'}
    )

    for p in ps:
        state = p.attrs.get('State')

        started_at = datetime.strptime(
            state.get('StartedAt')[0:26],
            '%Y-%m-%dT%H:%M:%S.%f'
        )

        runtime = datetime.utcnow() - started_at

        msg += '{} {} ({})\n'.format(
            p.status.title(),
            runtime,
            p.name.split('_')[1].title(),
        )

    return msg


@bot.message_handler(func=lambda message: True)
def bot_reply(message):
    cmd = message.text.split()[0]

    if cmd:
        cmd = re.sub('[^a-z]+', '', cmd.lower())

    d = {
        'mgmt': [
            'add', 'del', 'list', 'who', 'docker', 'config'
        ],
        'help': [
            'help'
        ],
        'intro': [
            'start', 'stop', 'forall'
        ],
    }

    for opt in d.keys():
        if cmd in d.get(opt):
            if opt == 'mgmt':
                res = handle_mgmt(
                    message,
                    cmd=cmd,
                )
            elif opt == 'help':
                res = handle_help(
                    message,
                    support=d.get('mgmt'),
                )
            elif opt == 'intro':
                res = handle_intro(
                    message,
                    cmd=cmd,
                )

            if not res:
                res = 'This message costed me R$0,31.'

            try:
                bot.reply_to(
                    message,
                    res
                )
            except Exception:
                pass


def main():
    try:
        bot.polling(none_stop=True)
    except Exception:
        time.sleep(20)
