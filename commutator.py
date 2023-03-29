from botfunctions import bot
import json


def button(text, color):
    return {
        "action": {
            "type": "text",
            "payload": "{\"button\": \"" + "1" + "\"}",
            "label": f"{text}"
        },
        "color": f"{color}"
    }


commutator = {
    "one_time": False,
    "buttons": [
        [button('Искать', 'primary')],
        [button('Далее', 'secondary')]
    ]
}


def transmitter(user_id, text):
    bot.vk.method('messages.send', {'user_id': user_id,
                                    'message': text,
                                    'random_id': 0,
                                    'commutator': commutator})


commutator = json.dumps(commutator, ensure_ascii=False).encode('utf-8')
commutator = str(commutator.decode('utf-8'))
