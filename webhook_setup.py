import argparse
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration

def init_viber_bot(name, avatar_url, auth_token):
    return Api(BotConfiguration(
        name=name,
        avatar=avatar_url,
        auth_token=auth_token
    ))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Viber Chatbot')
    parser.add_argument('--name', '-n', required=True, help='Name of the Bot')
    parser.add_argument('--image-url', '-i', help='Profile Image for the Bot')
    parser.add_argument('--viber-auth-token', '-v', required=True, help='Viber Authentication Token')
    parser.add_argument('--https-url', '-u', required=True, help='HTTPS URL for messages to be sent to')

    args = parser.parse_args()
    viber = init_viber_bot(args.name, args.image_url, args.viber_auth_token)
    viber.set_webhook(args.https_url)
