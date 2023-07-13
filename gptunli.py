from json import dumps
from random import choice, randint
from string import ascii_letters, digits
from textwrap import dedent
from time import time

from httpx import Client
from rich.console import Console
from rich.markdown import Markdown


class Colors:
    GREEN = '\033[38;5;121m'
    END = '\033[0m'


class ChatGPTUnli:
    OPTIONS = """
        GPTUnli - A command-line tool for interacting with GPTUnli chatbot. (https://chatgptunli.com)
            DOUBLE "enter" to send a message.
            - Type "!exit" to exit the program.
            - Type "!clear" to clear the console.
            - Type "!new" to start a new conversation.
    """

    def __init__(self):
        self.console = Console()
        self.client_id = None
        self.context_id = None
        self.conversation = []
        self.base_url = 'https://www.chatgptunli.com/wp-json/mwai-ui/v1/chats'
        self.client = Client(timeout=120)
        self.client.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0',
            'Content-Type': 'application/json'
        })

    def __del__(self):
        self.client.close()

    def time_stamp(self):
        return int(time() * 1000)

    def random_string(
        self, length: int
        ):

        letters = ascii_letters + digits
        return ''.join(choice(letters) for _ in range(length))

    def get_query(
        self, prompt: str
        ):

        print(prompt, end='')
        return '\n'.join(iter(input, ''))

    def post_data(
        self, query: str, assistant_message: dict
        ):

        return {
            'id': 'default',
            'botId': 'default',
            'session': 'N/A',
            'clientId': self.random_string(11) if self.client_id is None else self.client_id,
            'contextId': randint(100, 999) if self.context_id is None else self.context_id,
            'messages': [assistant_message] + self.conversation,
            'newMessage': query
        }

    def assistant_message(self):
        return {
            'id': self.random_string(11),
            'role': 'assistant',
            'content': 'Hi! How can I help you?',
            'who': 'AI: ',
            'html': 'Hi! How can I help you?',
            'timestamp': self.time_stamp()
        }

    def user_message(
        self, query: str
        ):

        return {
            'id': self.random_string(11),
            'role': 'user',
            'content': query,
            'who': 'User: ',
            'html': query,
            'timestamp': self.time_stamp(),
        }

    def send_message(
        self, query: str
        ):

        assistant_message = self.assistant_message()
        user_message = self.user_message(query)
        self.conversation.append(user_message)
        data = self.post_data(query, assistant_message)
        response = self.client.post(
            f'{self.base_url}/submit',
            data=dumps(data)
        )
        content = response.json()
        assistant_reply = content.get('reply')
        assistant_html = content.get('html')

        if not assistant_reply and not assistant_html :
            return 'An error occurred while processing the response.'

        assistant_message = {
            'id': self.random_string(11),
            'role': 'assistant',
            'content': assistant_reply,
            'who': 'AI: ',
            'html': assistant_html,
            'timestamp': self.time_stamp()
        }

        self.conversation.append(assistant_message)
        self.client_id = data['clientId']
        self.context_id = data['contextId']

        return assistant_reply

    def run(self):
        self.console.clear()
        print(dedent(self.OPTIONS))
        while True:
            query = self.get_query(f'{Colors.GREEN}You{Colors.END} : ').lower()
            if query == '!exit':
                break
            elif query == '!clear':
                self.console.clear()
                print(dedent(self.OPTIONS))
            elif query == '!new':
                self.console.clear()
                print(dedent(self.OPTIONS))
                self.client_id = None
                self.context_id = None
                self.conversation = []
            else:
                result = self.send_message(query)
                self.console.print(Markdown(result, code_theme='fruity'))
                print()


if __name__ == '__main__':
    ChatGPTUnli().run()
