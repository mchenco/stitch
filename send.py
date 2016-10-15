import requests

PAGE_TOKEN = 'EAAJn85XdH4wBAGrixqaZCPSwoyk2t6q8dQ1Hi9ygmiBZBTBeOjOqEY0YOzVbtZAfRiajOKoV9j5Q0DL95qjTok4W2nSjlezlZBRnUVFwDXizXFe3KI174h57OZAdoYaZCpEvQIXsSRvtR5M2THdeuzgZC2mpk3P7ZABoCMr9QrtgmgZDZD'
FACEBOOK_MESSAGE_URL = 'https://graph.facebook.com/v2.6/me/messages?access_token={}'.format(
    PAGE_TOKEN)

def create_postback_button(title, payload):
    return {
        'type': 'postback',
        'title': title,
        'payload': payload,
    }


def send(user, message=None, buttons=None):
    """Send a message to a given user."""
    json = {
        'recipient': {'id': str(user)},
        'message': {'text': message or ''},
    }

    # Create buttons
    if buttons:
        fb_buttons = [
            create_postback_button(button['title'], button['payload'])
            for button in buttons
        ]
        attachment = {
            'type': 'template',
            'payload': {
                'template_type': 'button',
                'text': message,
                'buttons': fb_buttons,
            }
        }
        json['message'].pop('text', None)
        json['message']['attachment'] = attachment

    r = requests.post(
        FACEBOOK_MESSAGE_URL,
        json=json,
    )
    # if "error" in r.json:
    print "SEND REQUEST TO FACEBOOK:"
    print json
    print r.text
    print r.json()
