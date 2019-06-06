from instachatbot.bot import InstagramChatBot
from instachatbot.nodes import MenuNode


def test_parse_messages():
    timestamp = 1559826742121822
    user_id = 9912873321
    bot_id = 19501769420
    text = 'Test'

    message_body = {
        'inbox': {
            'threads': [
                {
                    'is_group': False,
                    'items': [
                        {
                            'item_id': '28773724711249397008013560068964352',
                            'item_type': 'text',
                            'text': text,
                            'timestamp': timestamp,
                            'user_id': user_id
                        }
                    ],
                    'thread_id': '340282366841710300949128307236372348100',
                    'thread_title': 'user',
                    'thread_type': 'private',
                    'thread_v2_id': '18037398148086980',
                    'users': [
                        {
                            'full_name': 'User',
                            'pk': user_id,
                            'username': 'user'
                        }
                    ],
                }
            ],
        },
        'viewer': {
            'full_name': 'Bot Name',
            'pk': bot_id,
            'username': 'botname'
        }
    }
    bot = InstagramChatBot(menu=MenuNode('test', []))
    bot.user_id = bot_id
    messages = list(bot.parse_messages(message_body, timestamp-1))
    assert len(messages) == 1
    assert messages[0]['text'] == text
