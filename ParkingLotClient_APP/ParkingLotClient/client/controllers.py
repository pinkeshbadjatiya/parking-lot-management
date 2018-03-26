from flask import g, Blueprint, request, jsonify
from flask_mail import Message
from ParkingLotClient import db

import arrow
import jwt
from passlib.hash import argon2
import datetime
from datetime import datetime as dt

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


def calc_for_date(start_dtime, end_dtime, snap):
    
    return 0


def calc_price(entry_dtime, exit_dtime, price_snapshot):

    #Converting the string snapshot into suitable list of lists structure
    
    ls = price_snapshot.split('#')
    price_snapshot = []
    for i in ls:
        price_snapshot.append(i.split(','))

    ls = []
    sum = 0
    
    days = (exit_dtime.date() - entry_dtime.date()).days
    fin_time = dt.strptime("23:59:00", '%H:%M:%S')
    start_time = dt.strptime("00:01:00", '%H:%M:%S')
    fin_time = fin_time.time()
    start_time = start_time.time()

    #If car entered and exited on the same Date
    if(days == 0):
        sum = calc_for_date(entry_dtime, exit_dtime, price_snapshot)

    #If car entered and exited on different dates
    else:
        
        for i in range(days+1):
            
            if i == 0:
                sum += calc_for_date(entry_dtime, dt.combine(entry_dtime.date(),fin_time), price_snapshot)
            if i > 0 and i < days:
                temp_date = entry_dtime.date()+datetime.timedelta(days = i)
                sum += calc_for_date(dt.combine(temp_date, start_time), dt.combine(temp_date, fin_time), price_snapshot)

            if i == days:
                sum += calc_for_date(dt.combine(exit_dtime.date(),start_time), exit_dtime, price_snapshot)

    return sum

@mod_client.route('/exit', methods=['GET', 'POST'])

def exit_processing():
    
    token_input = 27
    #Extract Token corresponding to queried token_id
    token_object = Token.query.filter_by(token_id = token_input).first()

    s = token_object.entry_time
    exit_dtime = dt.now()
    entry_dtime = dt.strptime(s, '%Y-%m-%d %H:%M:%S')
    exit_dtime = dt.strptime('2017-03-5 19:10:00', '%Y-%m-%d %H:%M:%S')

    #Extract Charge corresponding to the Particular token
    charge_object = Charge.query.filter_by(charge_id = token_object.charge_id).first()
    price_snapshot = charge_object.price_snapshot
    
    print calc_price(entry_dtime, exit_dtime, price_snapshot)

    return render_template('exit.html', headerTitle='Parking Lot - Exit')
