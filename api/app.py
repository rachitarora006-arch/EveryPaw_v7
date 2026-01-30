import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from serverless_wsgi import handle_request

def handler(event, context):
    return handle_request(app, event, context)