DEBUG = True
# TESTING = True
JWT_SECRET = 'some-secret-string'
SECRET_KEY = 'fskfjskgflaj'
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://plclientuser:client@pl@10.2.5.98/' \
                          'plclientdb'
SQLALCHEMY_TRACK_MODIFICATIONS = False
UTIL_COLLECTOR_HOURLY = 1
NETWORK_SCHEDULER_DAILY_UTIL_SENDER = 24
PARKING_LOT_ADMIN_HOSTNAME = 'http://127.0.0.1:5000'
