import os
from dotenv import load_dotenv



environment = os.getenv('USE_LOCAL_ENV')

if environment == 'true':
    # dotenv_file = '.env.local'
    print('***')
    print(environment)
    print('===Your environment is LOCAL!===')
    dotenv_file = '.env.local'
else:
    # dotenv_file = '.env'
    print('***')
    print(environment)
    print('===Your environment is DOCKER!===')
    dotenv_file = '.env'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, dotenv_file))
# print('===FASTAPI===ENVIRON====')
# print(os.environ)
# print('===')
