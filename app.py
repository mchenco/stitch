import os
from flask import Flask
from flask import request
from apscheduler.scheduler import Scheduler
from flask.ext.sqlalchemy import SQLAlchemy

from send import send

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)

sched = Scheduler()

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
  else:
    if "status" in message.lower():
      print("reporting status")
      report_status(userid)
    else:
      print("didn't find status")

def report_status(userid):
  user = User.query.get(userid)
  status = "Happiness: "+ str(user.happiness) + "\n"
  status += "Hunger: " + str(user.hunger) + "\n"
  status += "Health: " + str(user.health)
  send(userid, status)

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

def decay_happiness():
  for user in User.query.all():
    user.happiness -= 1
    db.session.commit()
    #TODO: if happiness drops below threshold, send appropriate response

def decay_hunger():
  for user in User.query.all():
    user.hunger -= 1
    db.session.commit()

def decay_health():
  for user in User.query.all():
    user.health -= 1
    db.session.commit()

sched.add_interval_job(decay_hunger, minutes=5)
sched.add_interval_job(decay_happiness, minutes=30)
sched.add_interval_job(decay_health, minutes=60)
sched.start()

app.run(use_reloader=False, port=os.environ.get("PORT"), host='0.0.0.0')
