from flask import g, Blueprint, request, jsonify
from flask_mail import Message
from ParkingLotClient import db

import arrow
import jwt
from passlib.hash import argon2

from ParkingLotClient import app
from flask_login import login_required
from flask import Flask, render_template

from .models import Token, Charge
#from .models import User

from flask import url_for

mod_client = Blueprint('client', __name__)


@mod_client.route('/home', methods=['GET', 'POST'])

def show_home():
    return render_template('home.html', headerTitle='Parking Lot - Home')

@mod_client.route('/exit', methods=['GET', 'POST'])

def exit_processing():
    
    first = Token.query.filter_by(token_id = 27).first()
    second = Token.query.filter_by(token_id = 35).first()
    third = Charge.query.filter_by(charge_id = 72).first()
    print "Yay ",first.vehicle_no, second.vehicle_no, third.update_date

    return render_template('exit.html', headerTitle='Parking Lot - Exit')
