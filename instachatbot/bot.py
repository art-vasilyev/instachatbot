import time
import logging

from instabot.api import api

from instachatbot.nodes import Node, MenuNode
from instachatbot.state import Conversation
from instachatbot.storage import Storage


class InstagramChatBot:
    def __init__(self, menu: MenuNode, storage: Storage = None, trigger=None):
        self.logger = logging.getLogger('InstagramChatBot')
        self._api = api.API()
        self.menu_node = menu
        self._last_message_timestamp = {}
        self.conversation = Conversation(menu, storage)
        self.user_id = None
        self.trigger = trigger

    def login(self, username, password, proxy=None):
        self._api.login(username, password, proxy=proxy)
        self.user_id = self._api.user_id

    def start(self, polling_interval=1):
        start_timestamp = time.time() * 1000000

        while True:
            time.sleep(polling_interval)

            # approve pending threads
            self._api.get_pending_inbox()
            for thread in self._api.last_json['inbox']['threads']:
                self._api.approve_pending_thread(thread['thread_id'])

            # process messages
            self._api.get_inbox_v2()

            for message in self.parse_messages(
                    self._api.last_json, start_timestamp):
                self.logger.debug('Got message from %s: %s',
                                  message['from'], message['text'])
                context = {
                    'bot': self
                }
                self.handle_message(message, context)

    def stop(self):
        self._api.logout()

    def parse_messages(self, body, start_timestamp):
        threads = body['inbox']['threads']
        for thread in threads:
            if thread.get('is_group'):
                continue

            thread_id = thread['thread_id']
            last_seen_timestamp = thread.get(
                'last_seen_at', {}).get(
                    str(self.user_id), {}).get('timestamp', 0)
            if last_seen_timestamp:
                last_seen_timestamp = int(last_seen_timestamp)

            last_seen_timestamp = max(
                last_seen_timestamp,
                self._last_message_timestamp.get(thread_id, 0))

            items = thread.get('items')
            users = {user['pk']: user['username'] for user in thread['users']}
            users[body['viewer']['pk']] = body['viewer']['username']
            for item in items:

                if start_timestamp > item['timestamp']:
                    continue
                if last_seen_timestamp >= item['timestamp']:
                    continue

                self._last_message_timestamp[thread_id] = item['timestamp']

                yield {
                    'id': str(item['item_id']),
                    'date': item['timestamp'],
                    'type': item['item_type'],
                    'text': item.get('text'),
                    'from': {
                        'id': str(item['user_id']),
                        'username': users.get(item['user_id'])
                    },
                    'chat': {
                        'id': str(thread_id),
                        'title': thread['thread_title'],
                        'type': thread['thread_type'],
                    }
                }

    def handle_message(self, message, context):
        chat_id = message['chat']['id']
        state = self.conversation.get_state(chat_id) or {}

        node: Node = state.get('node') or self.menu_node
        if not state:
            # start menu only if trigger message is sent
            if self.trigger and message.get('text') != self.trigger:
                return

        jump = node.handle(message, state, context)
        self.conversation.save_state(chat_id, state)
        if jump:
            self.handle_message(message, context)

        # show root menu again only if trigger is not required
        if not state and not self.trigger:
            self.handle_message(message, context)

    def get_user_id_from_username(self, username):
        self._api.search_username(username)
        if "user" in self._api.last_json:
            return str(self._api.last_json["user"]["pk"])
        else:
            return None

    def send_direct_message(self, user_id, text):
        logging.debug('Sending message to %s: %s', user_id, text)
        self._api.send_direct_item(item_type='text', users=[user_id],
                                   text=text)

    def send_direct_photo(self, user_id, image_path):
        logging.debug('Sending photo to %s: %s', user_id, image_path)
        self._api.send_direct_item(item_type='photo', users=[user_id],
                                   filepath=image_path)
