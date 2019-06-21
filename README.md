# instachatbot

[![CircleCI](https://circleci.com/gh/art-vasilyev/instachatbot.svg?style=svg)](https://circleci.com/gh/art-vasilyev/instachatbot)
[![codecov](https://codecov.io/gh/art-vasilyev/instachatbot/branch/master/graph/badge.svg)](https://codecov.io/gh/art-vasilyev/instachatbot)
[![PyPI version](https://badge.fury.io/py/instachatbot.svg)](https://badge.fury.io/py/instachatbot)
[![PyPI - Downloads](https://img.shields.io/pypi/dw/instachatbot.svg?label=PyPI%20downloads)](https://pypistats.org/packages/instachatbot)

Simple framework for building Instagram chat bots with menu driven interface

## Installation

```
pip3 install instachatbot
```
To install development version:
```
pip3 install git+https://github.com/art-vasilyev/instachatbot.git
```
## How to use

Create sample script `main.py`:
```python
from instachatbot.bot import InstagramChatBot
from instachatbot.nodes import (
    MenuNode, MenuItem, MessageNode, QuestionnaireNode, NotifyAdminNode)

menu = MenuNode(
    '💡Choose menu:\n',
    [
        MenuItem(
            'text message',
            MessageNode('This is a message😀')),
        MenuItem(
            'questionnaire',
            QuestionnaireNode(
                [
                    'What is your favourite book? 📚',
                    'What is your favourite fruit? 🍐 🍊 🍋'
                ],
                header='Please answer the following questions',
                admin_username='<user to send results to>',
                response='Thank your for your answers')),
        MenuItem(
            'send notification to admin',
            NotifyAdminNode(
                'Thank you',
                notification='Sample notification from bot user',
                admin_username='<username to send notification to>'
            )
        ),
    ],
    error_message='Failed to select menu.'
)

chatbot = InstagramChatBot(menu=menu)
chatbot.login(
    username='<instagram-username>',
    password='<instagram-password>')
chatbot.start()
```

Run the script:
```
python3 main.py
```

## Persistent conversation state

By default conversation state is discarded on bot restart, to make it persistent you should provide persistent storage on bot initialization:
```python
chatbot = InstagramChatBot(menu=menu, storage=FileStorage())
```
