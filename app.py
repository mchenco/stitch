import os
from flask import Flask
from flask import request
from apscheduler.scheduler.background import BackgroundScheduler
from flask.ext.sqlalchemy import SQLAlchemy

from send import send

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)

scheduler = BackgroundScheduler()

class User(db.Model):
  userid = db.Column(db.String(100), primary_key=True)
  happiness = db.Column(db.Integer)
  hunger = db.Column(db.Integer)
  health = db.Column(db.Integer)

  def __init__(self, userid):
      self.userid = userid
      self.happiness = 50
      self.hunger = 50
      self.health = 50

def handle(userid, message):
  if db.session.query(User).filter(User.userid == userid).count() == 0:
    new_user = User(userid)
    db.session.add(new_user)
    db.session.commit()
    send(userid, "new user created")

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
          user = event['sender']['id']
          message = event['message']['text']
          handle(user, message)

  return "hello world"

def hello():
  print("hello from scheduler")

scheduler.add_job(hello, 'interval', seconds=5)
scheduler.start()
