from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

import atexit
import requests
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging


def init_db(db):
    db.create_all()

    def save(model):
        db.session.add(model)
        db.session.commit()

    db.Model.save = save

app = Flask(__name__)
app.config.from_object('server_config')
db = SQLAlchemy(app)
init_db(db)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'authentication.login'

from authentication.models import Users
from admin.models import ParkingLot


@login_manager.user_loader
def load_user(user_id):
    return Users.query.filter(Users.id == int(user_id)).first()


scheduler = BackgroundScheduler()				# Starting a scheduler for scheduled jobs

log = logging.getLogger('apscheduler.executors.default')
log.setLevel(logging.INFO)  # DEBUG

fmt = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
h = logging.StreamHandler()
h.setFormatter(fmt)
log.addHandler(h)

def init_admin():
    global scheduler
    pl_clients = app.config['PARKING_LOT_CLIENT_HOSTNAMES']
    for cID, cHost in pl_clients.iteritems():
        print 'INIT_ADMIN: Requesting unsent utils from client: %s ' %(cID)
        client_response = requests.get(cHost + '/networksync/getunsentutils')
        print 'INIT_ADMIN: Received unsent utils from client: %s ' %(cID)
    #scheduler.remove_job('init_admin')

####################
# Blueprints
####################
from ParkingLotServer.authentication.controllers import mod_auth
from ParkingLotServer.admin.controllers import mod_admin
from ParkingLotServer.networksync.controllers import mod_networksync
from ParkingLotServer.networksync.controllers import push_price_updates

app.register_blueprint(mod_auth, url_prefix='/auth')
app.register_blueprint(mod_admin, url_prefix='/admin')
app.register_blueprint(mod_networksync, url_prefix='/networksync')

scheduler.add_job(
    func=push_price_updates,
    trigger=IntervalTrigger(hours=app.config['NETWORK_SCHEDULER_HOURLY_PRICE_UPDATE_PUSHES']),
    id='Price_Pushes',
    name='Price_Pushes',
    replace_existing=True)

scheduler.add_job(
    init_admin,
    "date",
    run_date=datetime.now() + timedelta(seconds=5),
    id='init_admin',
    name='init_admin',
    replace_existing=True)

scheduler.start()

atexit.register(lambda: scheduler.shutdown())			# Shutting down the scheduler when exiting the app

if __name__=="__main__":
    app.run(host='0.0.0.0', port=8080)
