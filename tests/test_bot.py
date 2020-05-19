from instachatbot.bot import InstagramChatBot
from instachatbot.nodes import (
    MenuNode, MenuItem, MessageNode, QuestionnaireNode, DummyNode,
    NotifyAdminNode)


class FakeBot(InstagramChatBot):
    def __init__(self, menu, storage=None, trigger=None):
        super(FakeBot, self).__init__(menu, storage=storage, trigger=trigger)
        self.messages = {}

    def send_direct_message(self, user_id, text):
        if user_id not in self.messages:
            self.messages[user_id] = []
        self.messages[user_id].append(text)

    def get_user_id_from_username(self, username):
        return username


class TestBot:
    user_id = 9912873321
    bot_id = 19501769420
    chat_id = '340282366841710300949128307236372348100'
    username = 'user'

    def build_message(self, text):
        return {
            'text': text,
            'chat': {'id': self.chat_id},
            'from': {'id': self.user_id, 'username': self.username}
        }

    def send_message(self, bot, text):
        message = self.build_message(text)
        bot.handle_message(message, {'bot': bot})

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

        self.send_message(bot, 'test')
        state = bot.conversation.get_state(self.chat_id)
        assert state['node'] is menu

        self.send_message(bot, '1')
        state = bot.conversation.get_state(self.chat_id)
        assert state['node'] is menu
        assert 'test message' in bot.messages[self.user_id][-2]
        assert 'Menu' in bot.messages[self.user_id][-1]

    def test_questionnaire(self):
        question_node = QuestionnaireNode(
            ['question1', 'question2'],
            admin_username='admin')
        menu = MenuNode('💡Menu', [MenuItem('questionnaire', question_node)])
        bot = FakeBot(menu=menu)
        bot.user_id = self.bot_id

        state = bot.conversation.get_state(self.chat_id)
        assert state is None

        self.send_message(bot, 'test')
        state = bot.conversation.get_state(self.chat_id)
        assert state['node'] is menu

        self.send_message(bot, '1')
        state = bot.conversation.get_state(self.chat_id)
        assert state['node'] is question_node
        assert bot.messages[self.user_id][-1] == 'question1'

        self.send_message(bot, 'answer1')
        state = bot.conversation.get_state(self.chat_id)
        assert state['node'] is question_node
        assert bot.messages[self.user_id][-1] == 'question2'

        self.send_message(bot, 'answer2')
        state = bot.conversation.get_state(self.chat_id)
        assert state['node'] is menu
        assert 'question1' in bot.messages['admin'][-1]
        assert 'answer1' in bot.messages['admin'][-1]
        assert 'question2' in bot.messages['admin'][-1]
        assert 'answer2' in bot.messages['admin'][-1]

    def test_dummy_node(self):
        node = DummyNode()
        menu = MenuNode('💡Menu', [MenuItem('dummy', node)])
        bot = FakeBot(menu=menu)
        bot.user_id = self.bot_id

        self.send_message(bot, 'test')
        assert len(bot.messages[self.user_id]) == 1
        assert 'Menu' in bot.messages[self.user_id][-1]

        self.send_message(bot, '1')
        assert len(bot.messages[self.user_id]) == 2
        assert 'Menu' in bot.messages[self.user_id][-1]

    def test_message_node(self):
        node = MessageNode(text='test message')
        menu = MenuNode('💡Menu', [MenuItem('message', node)])
        bot = FakeBot(menu=menu)
        bot.user_id = self.bot_id

        self.send_message(bot, 'test')
        assert len(bot.messages[self.user_id]) == 1

        self.send_message(bot, '1')
        assert len(bot.messages[self.user_id]) == 3
        assert 'test message' in bot.messages[self.user_id][-2]
        assert 'Menu' in bot.messages[self.user_id][-1]

    def test_notify_node(self):
        admin_username = 'test_admin'
        node = NotifyAdminNode(text='notification is sent',
                               notification='notification',
                               admin_username=admin_username)
        menu = MenuNode('💡Menu', [MenuItem('notify', node)])
        bot = FakeBot(menu=menu)
        bot.user_id = self.bot_id

        self.send_message(bot, 'test')
        assert len(bot.messages[self.user_id]) == 1

        self.send_message(bot, '1')
        assert 'notification is sent' in bot.messages[self.user_id][-2]
        assert 'Menu' in bot.messages[self.user_id][-1]
        assert bot.messages[admin_username][-1] == (
            'notification\n@{}'.format(self.username))

    def test_menu_trigger(self):
        node = MessageNode(text='test message')
        menu = MenuNode('💡Menu', [MenuItem('message', node)])
        bot = FakeBot(menu=menu, trigger='/menu')
        bot.user_id = self.bot_id

        self.send_message(bot, 'test')
        assert not bot.messages

        self.send_message(bot, '/menu')
        assert 'Menu' in bot.messages[self.user_id][-1]

        self.send_message(bot, '1')
        assert 'message' in bot.messages[self.user_id][-1]
        message_count = len(bot.messages[self.user_id])

        self.send_message(bot, 'test')
        assert len(bot.messages[self.user_id]) == message_count

        self.send_message(bot, 'test')
        assert len(bot.messages[self.user_id]) == message_count

        self.send_message(bot, '/menu')
        assert len(bot.messages[self.user_id]) == message_count + 1

    def test_dummy_node_with_trigger(self):
        node = DummyNode()
        menu = MenuNode('💡Menu', [MenuItem('dummy', node)])
        bot = FakeBot(menu=menu, trigger='/menu')
        bot.user_id = self.bot_id

        self.send_message(bot, '/menu')
        assert len(bot.messages[self.user_id]) == 1
        assert 'Menu' in bot.messages[self.user_id][-1]

        self.send_message(bot, '1')
        assert len(bot.messages[self.user_id]) == 1
