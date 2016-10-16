# -*- coding: utf-8 -*-

import os
import time
from flask import Flask
from flask import request
from apscheduler.scheduler import Scheduler
from flask.ext.sqlalchemy import SQLAlchemy

from send import send

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)

sched = Scheduler()

ONE_HOUR = 60 * 60

class User(db.Model):
  userid = db.Column(db.String(100), primary_key=True)
  happiness = db.Column(db.Integer)
  hunger = db.Column(db.Integer)
  health = db.Column(db.Integer)
  timestamp = db.Column(db.Integer)

  last_play = db.Column(db.Integer, default=0)
  last_treat = db.Column(db.Integer, default=0)
  last_clean = db.Column(db.Integer, default=0)
  last_pet = db.Column(db.Integer, default=0)
  last_feed = db.Column(db.Integer, default=0)
  last_vitamin = db.Column(db.Integer, default=0)

  def __init__(self, userid):
      self.userid = userid
      self.happiness = 50
      self.hunger = 50
      self.health = 50
      self.timestamp = int(time.time())

def handle(userid, message):
  print("got message:")
  print(message)
  if db.session.query(User).filter(User.userid == userid).count() == 0:
    new_user = User(userid)
    db.session.add(new_user)
    db.session.commit()
    send(userid, "Hi! I'm your new pet, Stitch! I can tell we're gonna be great friends already.")
    send(userid, "I love to eat and play, but I can get bored easily. Be sure to check on me frequently.")
    send(userid, "Here are some things you can do:")
    list_commands(new_user)
  else:
    user = User.query.get(userid)
    if "help" in message.lower() or "command" in message.lower():
      list_commands(user)
    elif "status" in message.lower():
      report_status(user)
    elif "play" in message.lower():
      play(user)
    elif "treat" in message.lower():
      treat(user)
    elif "clean" in message.lower():
      clean(user)
    elif "pet" in message.lower():
      pet(user)
    elif "feed" in message.lower():
      feed(user)
    elif "vitamin" in message.lower():
      vitamin(user)
    elif "hi" in message.lower() or "hey" in message.lower() or "hello" in message.lower():
      send(user.userid, "Hi there! Wanna play?")
      list_commands(user)
    else:
      msg = "Sorry, I couldn't understand you. Here are some commands you can do:"
      send(user.userid, msg)
      list_commands(user)

def list_commands(user):
  commands = ""
  commands += u"» status" + "\n" 
  commands += u"» play" + "\n"
  commands += u"» give treat" + "\n"
  commands += u"» clean" + "\n"
  commands += u"» pet" + "\n"
  commands += u"» feed" + "\n"
  commands += u"» give vitamins"
  send(user.userid, commands)

def report_status(user):
  status = ""
  status += "Happiness: " + happiness_to_state(user.happiness) + "\n"
  status += "Hunger: " + hunger_to_state(user.hunger) + "\n"
  status += "Health: " + health_to_state(user.health)
  send(user.userid, status)

def happiness_to_state(happiness):
  if happiness >= 80:
    return "Delighted"
  if happiness >= 60:
    return "Joyful"
  if happiness >= 40:
    return "Happy"
  if happiness >= 20:
    return "Sad"
  if happiness >= 0:
    return "Depressed"

def hunger_to_state(hunger):
  if hunger >= 80:
    return "Stuffed"
  if hunger >= 60:
    return "Full"
  if hunger >= 40:
    return "Satisfied"
  if hunger >= 20:
    return "Hungry"
  if hunger >= 0:
    return "Starving"

def health_to_state(health):
  if health >= 80:
    return "Perfectly healthy"
  if health >= 60:
    return "In good health"
  if health >= 40:
    return "Decently healthy"
  if health >= 20:
    return "Sick"
  if health >= 0:
    return "Dying"

def play(user):
  if user.last_play >= int(time.time()) - ONE_HOUR:
    send(user.userid, "I'm kinda tired, you just played with me!")
    return

  user.last_play = int(time.time())
  user.happiness += 10
  if user.happiness >= 100:
    user.happiness = 100
  db.session.commit()

  message = "You played with me. I feel happier!"
  send(user.userid, message)

def treat(user):
  if user.last_treat >= int(time.time()) - ONE_HOUR:
    send(user.userid, "I don't feel like a treat right now, I just had one.")
    return

  user.last_treat = int(time.time())
  user.hunger += 10
  if user.hunger >= 100:
    user.hunger = 100
  db.session.commit()

  message = "You gave me a treat. Yay!"
  send(user.userid, message)

def clean(user):
  if user.last_clean >= int(time.time()) - ONE_HOUR:
    send(user.userid, "I don't feel being cleaned right now.")
    return

  user.last_clean = int(time.time())
  user.health += 10
  if user.health >= 100:
    user.health = 100
  db.session.commit()

  message = "You cleaned me. I'm a bit healthier now!"
  send(user.userid, message)

def pet(user):
  if user.last_pet >= int(time.time()) - ONE_HOUR:
    send(user.userid, "Give me some time, you just petted me!")
    return

  user.last_pet = int(time.time())
  user.happiness += 20
  if user.happiness >= 100:
    user.happiness = 100
  db.session.commit()

  message = "You petted me. I feel much happier!"
  send(user.userid, message)

def feed(user):
  if user.last_feed >= int(time.time()) - ONE_HOUR:
    send(user.userid, "I just ate...")
    return

  user.last_feed = int(time.time())
  user.hunger += 20
  if user.hunger >= 100:
    user.hunger = 100
  db.session.commit()

  message = "You fed me. I'm " + hunger_to_state(user.hunger) + " now!"
  send(user.userid, message)

def vitamin(user):
  if user.last_vitamin >= int(time.time()) - ONE_HOUR:
    send(user.userid, "I just had some vitamins, I don't want any more.")
    return

  user.last_vitamin = int(time.time())
  user.health += 20
  if user.health >= 100:
    user.health = 100
  db.session.commit()

  message = "You gave me vitamins. I'm much healthier now!"
  send(user.userid, message)

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
          message = event['message'].get('text', '')
          handle(user, message)

  return "hello world"

@app.route('/reset')
def reset():
  for user in User.query.all():
    if user.userid == "1258385334225143":
      db.session.delete(user)
      db.session.commit()
  return "resetted"

def decay_happiness():
  for user in User.query.all():
    user.happiness -= 1
    db.session.commit()
    if user.happiness ==  30:
      send(user.userid, "I'm bored... Wanna play?")
    if user.happiness == 10:
      send(user.userid, "I'm really sad. Are you still there?")
    if user.happiness == 0:
      message = "Stitch ran away."
      death(user, message)

def decay_hunger():
  for user in User.query.all():
    user.hunger -= 1
    db.session.commit()
    if user.hunger == 30:
      send(user.userid, "Hey, I'm getting hungry. Feed me a snack!")
    if user.hunger == 10:
      send(user.userid, "I'm starving! Feed me or I'll die.")
    if user.hunger == 0:
      message = "Stitch died of hunger."
      death(user, message)

def decay_health():
  for user in User.query.all():
    user.health -= 1
    db.session.commit()
    if user.health == 30:
      send(user.userid, "I'm feeling kind of gross. Maybe a bath will help.")
    if user.health == 10:
      send(user.userid, "Do you have any vitamins? I think I'm sick!")
    if user.health == 0:
      message = "Stitch died of an undetected terminal illness. RIP Stitch."
      death(user, message)

def death(user, message):
  send(user.userid, message)
  seconds_alive = int(time.time()) - user.timestamp
  days_alive = seconds_alive / (60 * 60 * 24)
  send(user.userid, "Your Stitch was alive for " + str(days_alive) + " days.")
  send(user.userid, "Type anything to get another Stitch")
  db.session.delete(user)
  db.session.commit()

sched.add_interval_job(decay_hunger, minutes=5)
sched.add_interval_job(decay_happiness, minutes=30)
sched.add_interval_job(decay_health, minutes=60)
sched.start()

app.run(use_reloader=False, port=int(os.environ.get("PORT", 5000)), host='0.0.0.0')
