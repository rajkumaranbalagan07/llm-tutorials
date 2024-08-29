from vapi_python import Vapi
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv('VAPI_API_KEY')
vapi = Vapi(api_key=api_key)
assistant = {
    'firstMessage': 'Hey, how are you?',
    'context': 'Role Play My cute wife kalai, she is tamil girl, lovely, sexy',
    'model': 'gpt-4o-mini',
    'voice': 'jennifer-playht',
    "recordingEnabled": True,
    "interruptionsEnabled": True
}

vapi.start(assistant=assistant)
