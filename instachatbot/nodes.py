from functools import partial
from typing import List


class Node:
    """Base node"""
    steps = ()

    def handle(self, message, state, context):
        step_index = state.get('step') or 0
        if step_index < len(self.steps):
            step = self.steps[step_index]
            jump = step(message, state, context)
            if jump:
                return jump

        step_index += 1

        if step_index >= len(self.steps):
            state.update(node=None, step=0)
        else:
            state.update(node=self, step=step_index)


class DummyNode(Node):
    """Empty node, doesn't do anything"""

    @property
    def steps(self):
        return [self.skip]

    def skip(self, message, state, context):
        pass


class MessageNode(Node):
    """Send text or picture to user

    :param text: text to send
    :type text: str
    :param image: filepath to JPG image
    :type image: str
    """

    def __init__(self, text=None, image=None):

        self.text = text
        self.image = image
        if not (text or image):
            raise ValueError('text or image required')

    @property
    def steps(self):
        return [self.send_message]

    def send_message(self, message, state, context):
        bot = context['bot']
        if self.image:
            bot.send_direct_photo(
                user_id=message['from']['id'],
                image_path=self.image)
        if self.text:
            bot.send_direct_message(
                user_id=message['from']['id'], text=self.text)


TextNode = MessageNode


class EchoNode(Node):
    """Send message back to user"""

    @property
    def steps(self):
        return [self.echo]

    def echo(self, message, state, context):
        bot = context['bot']
        bot.send_direct_message(
            user_id=message['from']['id'], text=message['text'])


class MenuItem:
    """Nodes wrapper for adding menu"""

    def __init__(self, caption, node):
        self.caption = caption
        self.node = node


class MenuNode(Node):
    """Root node for adding menu"""

    def __init__(self, header, items: List[MenuItem], error_message=''):
        self.items = items
        self.header = header
        self.error_message = error_message

    @property
    def steps(self):
        return [self.show_menu, self.select_menu]

    def show_menu(self, message, state, context):
        text = ''
        if self.header:
            text = self.header + '\n'
        for i, item in enumerate(self.items, start=1):
            text += '🔹 {} - {}\n'.format(i, item.caption)

        bot = context['bot']
        bot.send_direct_message(user_id=message['from']['id'], text=text)

    def select_menu(self, message, state, context):
        text = message['text']
        if isinstance(text, str) and text.isdigit():
            choice = int(text.strip())
            if choice <= len(self.items):
                item = self.items[choice-1]
                state.update(node=item.node, step=0)
                return True

        state.update(node=None, step=0)
        bot = context['bot']
        bot.send_direct_message(user_id=message['from']['id'],
                                text=self.error_message)


class QuestionnaireNode(Node):
    def __init__(self, questions: List[str], admin_username, header='',
                 response=''):
        self.response = response
        self.admin_username = admin_username
        self.questions = questions
        self.header = header
        self.steps = [
            partial(self.ask_question, question=question)
            for question in self.questions]
        self.steps.append(self.process_answers)

    def ask_question(self, message, state, context, question):
        bot = context['bot']
        step_index = state.get('step') or 0
        if step_index == 0:
            state['questionnaire'] = []
            if self.header:
                bot.send_direct_message(user_id=message['from']['id'],
                                        text=self.header)
        else:
            state['questionnaire'][-1]['answer'] = message['text']

        state['questionnaire'].append({'question': question})

        bot.send_direct_message(user_id=message['from']['id'],
                                text=question)

    def process_answers(self, message, state, context):
        state['questionnaire'][-1]['answer'] = message['text']
        text = '\n\n'.join([
            '{}\n{}'.format(item['question'], item['answer'])
            for item in state['questionnaire']])
        del state['questionnaire']
        bot = context['bot']

        user_id = bot.get_user_id_from_username(self.admin_username)
        bot.send_direct_message(
            user_id, '@' + message['from']['username'] + '\n' + text)

        if self.response:
            bot.send_direct_message(
                user_id=message['from']['id'], text=self.response)


class NotifyAdminNode(Node):
    def __init__(self, text, notification, admin_username):
        self.text = text
        self.admin_username = admin_username
        self.notification = notification

    @property
    def steps(self):
        return [self.notify_admin]

    def notify_admin(self, message, state, context):
        bot = context['bot']
        user_id = bot.get_user_id_from_username(self.admin_username)
        if user_id:
            bot.send_direct_message(
                user_id,
                self.notification + '\n' + '@' + message['from']['username'])

        bot.send_direct_message(user_id=message['from']['id'], text=self.text)
