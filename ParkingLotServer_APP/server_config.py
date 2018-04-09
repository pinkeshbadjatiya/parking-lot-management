DEBUG = True
# TESTING = True
JWT_SECRET = 'some-secret-string'
SECRET_KEY = 'fskfjskgflaj'
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://plserveruser:server@pl@10.2.5.98/' \
                          'plserverdb'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Network Sync module params
NETWORK_SCHEDULER_HOURLY_PRICE_UPDATE_PUSHES = 24
PARKING_LOT_CLIENT_HOSTNAMES = {
    1: 'http://127.0.0.1:5000'
}
