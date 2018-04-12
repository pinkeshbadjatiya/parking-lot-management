from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
import logging, requests
from flask.ext.socketio import SocketIO, emit

def init_db(db):
    db.create_all()

    def save(model):
        db.session.add(model)
        db.session.commit()

    db.Model.save = save


app = Flask(__name__)
app.config.from_object('client_config')
db = SQLAlchemy(app)
init_db(db)
migrate = Migrate(app, db)

socketio = SocketIO(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'authentication.login'

from authentication.models import Users
from client.models import ParkingLot

@login_manager.user_loader
def load_user(user_id):
    #print user_id
    return Users.query.filter(Users.id == int(user_id)).first()


def init_client():
    pl_server_hostname = app.config['PARKING_LOT_ADMIN_HOSTNAME']
    current_pl = ParkingLot.query.filter_by(pl_active='t').first()
    print 'INIT_CLIENT: Requesting price updates from admin: %s ' %(pl_server_hostname)
    server_response = requests.post(pl_server_hostname + '/networksync/updatePrices', json={
        'parkinglot_id': current_pl.pl_id
    })
    print 'INIT_CLIENT: Received updated prices from admin: %s ' %(pl_server_hostname)

log = logging.getLogger('apscheduler.executors.default')
log.setLevel(logging.INFO)  # DEBUG

fmt = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
h = logging.StreamHandler()
h.setFormatter(fmt)
log.addHandler(h)

####################
# Blueprints
####################
from ParkingLotClient.authentication.controllers import mod_auth
from ParkingLotClient.client.controllers import mod_client, populateHourlyUtil
from ParkingLotClient.networksync.controllers import mod_networksync, sendDailyUtils

app.register_blueprint(mod_auth, url_prefix='/auth')
app.register_blueprint(mod_client, url_prefix='/client')
app.register_blueprint(mod_networksync, url_prefix='/networksync')

scheduler = BackgroundScheduler()
scheduler.add_job(
    func=populateHourlyUtil,
    trigger=IntervalTrigger(hours=app.config["UTIL_COLLECTOR_HOURLY"]),
    id='Hourly_Util_Job',
    name='Hourly_Util_Job',
    replace_existing=True)

scheduler.add_job(
    func=sendDailyUtils,
    trigger=IntervalTrigger(hours=app.config["NETWORK_SCHEDULER_DAILY_UTIL_SENDER"]),
    id='Daily_Util_Job',
    name='Daily_Util_Job',
    replace_existing=True)

scheduler.add_job(
    init_client,
    "date",
    run_date=datetime.now() + timedelta(seconds=10),
    id='init_client',
    name='init_client',
    replace_existing=True)

scheduler.start()

#Shutting down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

if __name__=="__main__":
    app.run(host='0.0.0.0', port=8080)
