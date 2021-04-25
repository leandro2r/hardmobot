import os
import pymongo


class Data():
    def __init__(self, config):
        client = config.get('client')

        conn = pymongo.MongoClient(
            host=config.get('host'),
            username=config.get('user'),
            password=config.get('passwd'),
        )

        self.database = conn[client]

    def add_config(self, envs):
        data = []
        col = self.database.get('config')

        if any('delay' or 'reset' or 'timeout' in s for s in envs):
            data = dict(s.split('=') for s in envs)

            col.update_many(
                {},
                {"$set": data},
                upsert=True,
            )

    def list_config(self):
        col = self.database.get('config')

        configs = list(
            col.find(
                {},
                {'_id': False}
            )
        )

        return configs

    def add_intruder(self, data):
        col = self.database.get('intruder')

        if data:
            col.update_one(
                data,
                {'$setOnInsert': data},
                upsert=True,
            )

    def list_users(self, **kwargs):
        users = []
        col = [
            self.database.get('chat')
        ]

        if kwargs.get('all', False):
            col.append(self.database.get('intruder'))

        for i in enumerate(col):
            users.extend(
                list(
                    col[i].distinct(
                        'user'
                    )
                )
            )

            if i < len(col) - 1:
                users.append('---')

        return users

    def add_chat(self, data):
        col = self.database.get('chat')

        if data:
            col.update_one(
                data,
                {'$setOnInsert': data},
                upsert=True,
            )

    def del_chat(self, data):
        col = self.database.get('chat')

        if data:
            col.delete_many({
                'id': data.get('id')
            })
            return True

        return False

    def find_chat(self, chat_id):
        col = self.database.get('chat')

        chat = col.count_documents({
            'id': chat_id
        })

        return chat

    def list_chats(self):
        col = self.database.get('chat')

        chat_ids = list(
            col.distinct(
                'id'
            )
        )

        return chat_ids

    def add_keywords(self, keywords, **kwargs):
        data = []
        col = self.database.get('keyword')

        if kwargs.get('initial'):
            initial = os.environ.get(
                'INITIAL_KEYWORDS'
            )
            keywords = list(
                filter(None, initial.split(';'))
            )

        if keywords:
            for val in keywords:
                data.append({
                    'keyword': val,
                })

            col.insert_many(
                data,
                ordered=False,
            )

    def del_keywords(self, keywords):
        col = self.database.get('keyword')

        if keywords:
            col.delete_many({
                'keyword': {
                    '$in': keywords
                }
            })

            return True

        return False

    def list_keywords(self):
        col = self.database.get('keyword')

        keywords = list(
            col.distinct(
                'keyword'
            )
        )

        return keywords
