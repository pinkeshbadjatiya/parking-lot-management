from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


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

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'authentication.login'

from authentication.models import Users

@login_manager.user_loader
def load_user(user_id):
    print user_id
    return Users.query.filter(Users.id == int(user_id)).first()


####################
# Blueprints
####################

from ParkingLotClient.authentication.controllers import mod_auth
from ParkingLotClient.client.controllers import mod_client

app.register_blueprint(mod_auth, url_prefix='/auth')
app.register_blueprint(mod_client, url_prefix='/client')

if __name__=="__main__":
    app.run(host='0.0.0.0', port=8080)