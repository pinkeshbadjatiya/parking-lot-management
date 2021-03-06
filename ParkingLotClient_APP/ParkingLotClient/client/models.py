from ParkingLotClient import db
from passlib.hash import argon2


class Users(db.Model):

    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    verified = db.Column(db.Boolean, default=False, nullable=False)

    def __init__(self, email, password, first_name, last_name):
        self.email = email
        self.password = argon2.hash(password)
        self.first_name = first_name
        self.last_name = last_name

    def authenticate(self, password):
        return argon2.verify(password, self.password)

    def change_password(self, old_password, new_password):
        if not argon2.verify(old_password, self.password):
            return False
        self.password = argon2.hash(new_password)
        self.save()
        return True


class HourlyUtil(db.Model):

    __tablename__ = "hourly_util"

    id = db.Column(db.Integer, primary_key=True)
    util_date = db.Column(db.Date, nullable=False)
    util_hour = db.Column(db.Integer, nullable=False)
    util = db.Column(db.Float, nullable=False)
    rev = db.Column(db.Float, nullable=False)

    def __init__(self, util_date, util_hour, util, rev):
        self.util_date = util_date
        self.util_hour = util_hour
        self.util = util
        self.rev = rev


class ParkingLot(db.Model):

    __tablename__ = "parkinglot"

    id = db.Column(db.Integer, primary_key=True)
    pl_id = db.Column(db.Integer, nullable=False)
    pl_name = db.Column(db.String(255), nullable=False)
    pl_address = db.Column(db.String(255), nullable=False)
    pl_capacity = db.Column(db.Integer, nullable=False)
    pl_default_price = db.Column(db.Float, nullable=False)
    pl_active = db.Column(db.Boolean, default=True, nullable=False)

    def __init__(self, pl_id, pl_name, pl_address, pl_capacity, pl_default_price, pl_active):
        self.pl_id = pl_id
        self.pl_name = pl_name
        self.pl_address = pl_address
        self.pl_capacity = pl_capacity
        self.pl_default_price = pl_default_price
        self.pl_active = pl_active


class Token(db.Model):
    __tablename__ = "token"

    token_id = db.Column(db.Integer, primary_key=True)
    charge_id = db.Column(db.Integer, db.ForeignKey('charge.charge_id'))
    vehicle_no = db.Column(db.String(200), nullable=False)
    computed_charge = db.Column(db.Float, nullable=True)
    pay_method = db.Column(db.String(200), nullable=True)

    entry_date = db.Column(db.DateTime, nullable=False)
    exit_date = db.Column(db.DateTime,nullable=True)
    entry_operator_id = db.Column(db.String(50), nullable=False)
    exit_operator_id = db.Column(db.String(50), nullable=True)

    #def __init__(self, charge_id, vehicle_no, computed_charge, pay_method, entry_date, exit_date):
        #self.token_id = token_id
        #self.charge_id = charge_id
        #self.vehicle_no = vehicle_no
        #self.computed_charge = computed_charge
        #self.pay_method = pay_method
        #self.entry_date = entry_date
        #self.exit_date = exit_date


class Charge(db.Model):
    __tablename__ = "charge"

    charge_id = db.Column(db.Integer, primary_key=True)
    ch_active = db.Column(db.Boolean, default=True, nullable=False)
    update_date = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)

    pl_id = db.Column(db.Integer, db.ForeignKey('parkinglot.id'))
    price_snapshot = db.Column(db.String(2500), nullable=False)

    def __init__(self, pl_id, price_snapshot):
        self.pl_id = pl_id
        self.price_snapshot = price_snapshot
