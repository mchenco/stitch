from flask import Flask
from flask import request

app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def index():
  if request.args.get('hub.verify_token') == 'eyeshield' and request.args.get('hub.mode') == 'subscribe':
    print("verifying")
    return request.args.get('hub.challenge')

  data = request.json
  if data['object'] == 'page':
    for entry in data['entry']:
      for event in entry['messaging']:
        if 'message' in event:
          print(event)
  return "hellow orld"
