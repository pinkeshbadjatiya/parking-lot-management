from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from ParkingLotServer.networksync.controllers import push_price_updates


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
    print user_id
    return Users.query.filter(Users.id == int(user_id)).first()


####################
# Blueprints
####################
from ParkingLotServer.authentication.controllers import mod_auth
from ParkingLotServer.admin.controllers import mod_admin
from ParkingLotServer.networksync.controllers import mod_networksync

app.register_blueprint(mod_auth, url_prefix='/auth')
app.register_blueprint(mod_admin, url_prefix='/admin')
app.register_blueprint(mod_networksync, url_prefix='/networksync')


scheduler = BackgroundScheduler()				# Starting a scheduler for scheduled jobs
scheduler.start()
scheduler.add_job(
    func=push_price_updates,
    trigger=IntervalTrigger(hours=app.config['NETWORK_SCHEDULER_HOURLY_PRICE_UPDATE_PUSHES']),
    id='Price_Pushes',
    name='Price_Pushes',
    replace_existing=True)

atexit.register(lambda: scheduler.shutdown())			# Shutting down the scheduler when exiting the app

if __name__=="__main__":
    app.run(host='0.0.0.0', port=8080)
