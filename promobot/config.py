import base64
import os
import random
import re


class Config():
    data = {
        'proxies': {
            'http': '',
            'https': ''
        }
    }

    def __init__(self):
        self.set_proxy()

        self.data['monitor'] = {
            'delay': int(os.environ.get('DELAY', 40)),
            'muted': eval(os.environ.get('MUTED', 'false').title()),
            'reset': int(os.environ.get('RESET_TIME', 24)),
            'timeout': int(os.environ.get('TIMEOUT', 30)),
        }

        self.data['urls'] = [
            {
                'url': 'https://www.hardmob.com.br/forums/407-Promocoes'
                       '?s=&pp=50&daysprune=1&sort=dateline&order=desc',
                'topic': {
                    'tag': 'div',
                    'class': 'threadinfo'
                },
                'thread': {
                    'tag': 'a',
                    'class': 'title'
                }
            },
            {
                'url': 'https://www.pelando.com.br/recentes',
                'tool': 'selenium',
                'topic': {
                    'tag': 'div',
                    'class': 'sc-1t2mqdt-9 jmQjPk'
                },
                'thread': {
                    'tag': 'a',
                },
                'desc': {
                    'tag': 'a',
                    'class': 'sc-1t2mqdt-10 oueGS'
                }
            },
            {
                'url': 'https://www.pelando.com.br',
                'tool': 'selenium',
                'topic': {
                    'tag': 'div',
                    'class': 'sc-1t2mqdt-9 jmQjPk'
                },
                'thread': {
                    'tag': 'a',
                },
                'desc': {
                    'tag': 'a',
                    'class': 'sc-1t2mqdt-10 oueGS'
                }
            },
            {
                'url': 'https://www.pelando.com.br/mais-quentes',
                'tool': 'selenium',
                'topic': {
                    'tag': 'div',
                    'class': 'sc-1t2mqdt-9 jmQjPk'
                },
                'thread': {
                    'tag': 'a',
                },
                'desc': {
                    'tag': 'a',
                    'class': 'sc-1t2mqdt-10 oueGS'
                }
            },
            {
                'url': 'https://www.gatry.com',
                'topic': {
                    'tag': 'div',
                    'class': 'informacoes'
                },
                'thread': {
                    'tag': 'a',
                    'class': 'mais hidden-xs'
                },
                'desc': {
                    'tag': 'p',
                    'class': 'preco comentario clear'
                }
            },
            # {
            #     'url': 'https://forum.adrenaline.com.br/'
            #            'forums/for-sale.221',
            #     'topic': {
            #         'tag': 'div',
            #         'class': 'structItem-title'
            #     },
            #     'thread': {
            #         'tag': 'a',
            #         'preview-tooltip': 'data-xf-init'
            #     }
            # },
            {
                'url': 'https://www.ofertaesperta.com',
                'tool': 'selenium',
                'topic': {
                    'tag': 'div',
                    'class': 'common-card'
                },
                'thread': {
                    'tag': 'a',
                },
                'desc': {
                    'tag': 'div',
                    'class': 'store-icon'
                }
            },
            {
                'url': 'https://www.promobit.com.br',
                'topic': {
                    'tag': 'div',
                    'class': 'pr-tl-card'
                },
                'thread': {
                    'tag': 'a',
                    'class': 'access_url'
                },
                'desc': {
                    'tag': 'div',
                    'class': 'where'
                }
            },
            {
                'url': 'https://www.promobit.com.br/promocoes/'
                       'melhores-ofertas',
                'topic': {
                    'tag': 'div',
                    'class': 'pr-tl-card'
                },
                'thread': {
                    'tag': 'a',
                    'class': 'access_url'
                },
                'desc': {
                    'tag': 'div',
                    'class': 'where'
                }
            },
        ]

        self.data['telegram'] = {
            'token': os.environ.get(
                'TELEGRAM_TOKEN',
                ''
            ),
            'chat_passwd': os.environ.get('TELEGRAM_CHAT_PASSWD', '')
        }

        telegram_token = self.data['telegram']['token']

        self.data['telegram'].update({
            'url': f'https://api.telegram.org/bot{telegram_token}/sendMessage'
        })

        self.data['db'] = {
            'host': os.environ.get('DB_HOST', 'localhost:27017'),
            'user': os.environ.get('MONGO_INITDB_ROOT_USERNAME'),
            'passwd': os.environ.get('MONGO_INITDB_ROOT_PASSWORD'),
            'client': os.environ.get(
                'MONGO_INITDB_DATABASE',
                'promobot'
            ),
        }

    def set_proxy(self):
        ip_address = ''
        ips = []
        proxy_file = '/etc/environment'
        url = base64.b64decode(
            os.environ.get('AUTH_PROXY', '')
        ).decode('utf-8').strip()

        proxy_enabled = eval(
            os.environ.get('PROXY_ENABLED', 'False').title()
        )

        if not proxy_enabled:
            if "HTTP_PROXY" in os.environ:
                del os.environ['HTTP_PROXY']

            if "HTTPS_PROXY" in os.environ:
                del os.environ['HTTPS_PROXY']

            return

        if ips:
            ip_address = random.choice(ips)

        elif os.path.exists(proxy_file):
            with open(proxy_file, 'r', encoding='UTF-8') as file:
                get_proxy = re.search(r'http://\S+', file.read())
                file.close()

                ip_address = get_proxy.group()

        ip_auth = ip_address.replace(
            'http://',
            f'http://{url}'
        )

        os.environ['HTTP_PROXY'] = ip_auth
        os.environ['HTTPS_PROXY'] = ip_auth

        self.data['proxies'].update({
            'http': os.environ.get('HTTP_PROXY'),
            'https': os.environ.get('HTTPS_PROXY')
        })
