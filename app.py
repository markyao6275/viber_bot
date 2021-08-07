import argparse
from flask import Flask, request, Response
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages import VideoMessage
from viberbot.api.messages.text_message import TextMessage
import logging

from viberbot.api.viber_requests import ViberConversationStartedRequest
from viberbot.api.viber_requests import ViberFailedRequest
from viberbot.api.viber_requests import ViberMessageRequest
from viberbot.api.viber_requests import ViberSubscribedRequest
from viberbot.api.viber_requests import ViberUnsubscribedRequest

from webhook_setup import init_viber_bot

app = Flask(__name__)
chatbot = ChatBot("Flying Penguin")
trainer = ChatterBotCorpusTrainer(chatbot)

trainer.train(
    "chatterbot.corpus.english"
)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

@app.route('/', methods=['POST'])
def incoming():
    viber = app.viber
    logger.debug("received request. post data: {0}".format(request.get_data()))
    # every viber message is signed, you can verify the signature using this method
    if not viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
        return Response(status=403)

    # this library supplies a simple way to receive a request object
    viber_request = viber.parse_request(request.get_data())

    if isinstance(viber_request, ViberMessageRequest):
        message = viber_request.message
        reply = chatbot.get_response(message.text)
        viber.send_messages(viber_request.sender.id, [
            TextMessage(text=reply.serialize()['text'])
        ])
    elif isinstance(viber_request, ViberSubscribedRequest):
        viber.send_messages(viber_request.get_user.id, [
            TextMessage(text="thanks for subscribing!")
        ])
    elif isinstance(viber_request, ViberFailedRequest):
        logger.warn("client failed receiving message. failure: {0}".format(viber_request))

    return Response(status=200)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Viber Chatbot')
    parser.add_argument('--name', '-n', required=True, help='Name of the Bot')
    parser.add_argument('--image-url', '-i', help='Profile Image for the Bot')
    parser.add_argument('--viber-auth-token', '-v', required=True, help='Viber Authentication Token')
    
    args = parser.parse_args()
    app.viber = init_viber_bot(args.name, args.image_url, args.viber_auth_token)
    app.run(host='0.0.0.0', port=5001)