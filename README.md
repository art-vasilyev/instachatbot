# instachatbot
Simple framework for building Instagram chat bots with menu driven interface

## How to use

Install requirements:
```
pip install -r requirements.txt
```

Create sample script `main.py`:
```
from instachatbot.bot import InstagramChatBot
from instachatbot.nodes import (
    MenuNode, MenuItem, TextNode, QuestionnaireNode, NotifyAdminNode)

menu = MenuNode(
    '💡Choose menu:\n',
    [
        MenuItem(
            'text message',
            TextNode('This is a message😀')),
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
