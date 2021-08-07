# Viber Chatbot

## Setup Instructions
Install dependencies
```
python3 -m venv env
source env/bin/activate
pip3 install -r requirements.txt
```
You may also need to install the spacy `en` model via
```
python3 -m spacy download en
```
Then, run the server with
```
python app.py -n <NAME_OF_BOT> -i <URL_TO_BOT_PROFILE_IMAGE> -v <VIBER_AUTHENTICATION_TOKEN>
```
Once it's running, create the webhook with
```
python webhook_setup.py -n <NAME_OF_BOT> -i <URL_TO_BOT_PROFILE_IMAGE> -v <VIBER_AUTHENTICATION_TOKEN> -u <SERVER_HTTPS_URL>
```

You can obtain an HTTPS URL using a tool like [ngrok](https://ngrok.com/) and have it forward requests to `localhost:5001`.
```

