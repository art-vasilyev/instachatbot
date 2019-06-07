from instachatbot.bot import InstagramChatBot
from instachatbot.nodes import MenuNode, MenuItem, MessageNode


class FakeBot(InstagramChatBot):
    def __init__(self, menu, storage=None):
        super(FakeBot, self).__init__(menu, storage=storage)
        self.messages = []

    def send_direct_message(self, user_id, text):
        self.messages.append(text)


class TestBot:
    user_id = 9912873321
    bot_id = 19501769420
    chat_id = '340282366841710300949128307236372348100'

    def test_parse_messages(self):
        timestamp = 1559826742121822

        text = 'Test'

        message_body = {
            'inbox': {
                'threads': [
                    {
                        'is_group': False,
                        'items': [
                            {
                                'item_id': (
                                    '28773724711249397008013560068964352'),
                                'item_type': 'text',
                                'text': text,
                                'timestamp': timestamp,
                                'user_id': self.user_id
                            }
                        ],
                        'thread_id': self.chat_id,
                        'thread_title': 'user',
                        'thread_type': 'private',
                        'thread_v2_id': '18037398148086980',
                        'users': [
                            {
                                'full_name': 'User',
                                'pk': self.user_id,
                                'username': 'user'
                            }
                        ],
                    }
                ],
            },
            'viewer': {
                'full_name': 'Bot Name',
                'pk': self.bot_id,
                'username': 'botname'
            }
        }
        bot = FakeBot(menu=MenuNode('test', []))
        bot.user_id = self.bot_id
        messages = list(bot.parse_messages(message_body, timestamp-1))
        assert len(messages) == 1
        assert messages[0]['text'] == text

    def test_handle_message(self):
        msg_node = MessageNode('test message')
        menu = MenuNode('💡Menu', [MenuItem('message', msg_node)])
        bot = FakeBot(menu=menu)
        bot.user_id = self.bot_id

        state = bot.conversation.get_state(self.chat_id)
        assert state is None

        message = self.build_message('test')
        bot.handle_message(message, {'bot': bot})
        state = bot.conversation.get_state(self.chat_id)
        assert state['node'] is menu

        message = self.build_message('1')
        bot.handle_message(message, {'bot': bot})
        state = bot.conversation.get_state(self.chat_id)
        assert state['node'] is menu
        assert 'test message' in bot.messages[-2]
        assert 'Menu' in bot.messages[-1]

    def build_message(self, text):
        return {
            'text': text,
            'chat': {'id': self.chat_id},
            'from': {'id': self.user_id}
        }
