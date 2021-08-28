import argparse
from dotenv import load_dotenv
import os
import openai
from flask import Flask, request, Response, session
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
logger.setLevel(logging.WARN)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
app.config["SECRET_KEY"] = os.getenv("SESSION_SECRET_KEY")

import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

start_sequence = "\nA:"
restart_sequence = "\n\nQ: "

base_prompt = "I am a highly intelligent question answering penguin bot. If you ask me a question that is rooted in truth, I will give you the answer. If you ask me a question that is nonsense, trickery, or has no clear answer, I will respond with \"Unknown\".\n\nQ: What is human life expectancy in the United States?\nA: Human life expectancy in the United States is 78 years.\n\nQ: Who was president of the United States in 1955?\nA: Dwight D. Eisenhower was president of the United States in 1955.\n\nQ: Which party did he belong to?\nA: He belonged to the Republican Party.\n\nQ: What is the square root of banana?\nA: Unknown\n\nQ: How does a telescope work?\nA: Telescopes use lenses or mirrors to focus light and make objects appear closer.\n\nQ: Where were the 1992 Olympics held?\nA: The 1992 Olympics were held in Barcelona, Spain.\n\nQ: How many squigs are in a bonk?\nA: Unknown\n\nQ:"

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
        chat_log = session.get("chat_log")
        input_text = message.text
        reply = get_reply_gpt3(input_text, chat_log)
        session["chat_log"] = append_interaction_to_chat_log(input_text, reply, chat_log)
        viber.send_messages(viber_request.sender.id, [
            TextMessage(text=reply)
        ])
    elif isinstance(viber_request, ViberSubscribedRequest):
        viber.send_messages(viber_request.get_user.id, [
            TextMessage(text="thanks for subscribing!")
        ])
    elif isinstance(viber_request, ViberFailedRequest):
        logger.warn("client failed receiving message. failure: {0}".format(viber_request))

    return Response(status=200)

def get_reply(input_text):
    response = chatbot.get_response(input_text)
    return response.serialize()['text']

def get_reply_gpt3(question, chat_log=None):
    prompt_text = f"{base_prompt}{restart_sequence}: {question}{start_sequence}:"
    response = openai.Completion.create(
        engine="davinci",
        prompt=prompt_text,
        temperature=0.8,
        max_tokens=150,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.3,
        stop=["\n"],
    )
    story = response["choices"][0]["text"]
    return str(story)

def append_interaction_to_chat_log(question, answer, chat_log=None):
    if chat_log is None:
        chat_log = base_prompt
    return f"{chat_log}{restart_sequence} {question}{start_sequence}{answer}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Viber Chatbot')
    parser.add_argument('--name', '-n', required=True, help='Name of the Bot')
    parser.add_argument('--image-url', '-i', help='Profile Image for the Bot')
    parser.add_argument('--viber-auth-token', '-v', required=True, help='Viber Authentication Token')
    
    args = parser.parse_args()
    app.viber = init_viber_bot(args.name, args.image_url, args.viber_auth_token)
    app.run(host='0.0.0.0', port=5001)