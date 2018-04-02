from __future__ import print_function
from flask import g, Blueprint, request, jsonify
from flask_mail import Message
from ParkingLotClient import db
import sys
import arrow
import jwt
from passlib.hash import argon2
import datetime
from datetime import datetime as dt

from ParkingLotClient import app
from flask_login import login_required
from flask import Flask, render_template, redirect, url_for, session


from .models import Token, Charge
#from .models import User

from flask import url_for

mod_client = Blueprint('client', __name__)

#app = Flask(__name__)
#app.debug = True

@mod_client.route('/home', methods=['GET', 'POST'])
def show_home():

    return render_template('home.html', headerTitle='Parking Lot - Home')


#@mod_client.route('/display', methods=['GET', 'POST'])
def display_info(ls):

    #ls[0] == 1(for entry), 2(for exit), 3(for synch)
    if ls[0] == 1 or ls[0] == 2:
        empty_slots = ls[1]

    if ls[0] == 3:

        snap = ls[1]
        now = dt.now()

        now_day = now.weekday()
        now_day = (now_day + 1)%7
        now_hour = now.hour

        summ = 0
        four_hour_avg = 0
        one_day_avg = 0
        two_day_avg = 0

        for i in range(now_hour, now_hour + 4):
            four_hour_avg += snap[now_day][i]
        four_hour_avg = float(four_hour_avg)/4

        #calculate average for one day
        for i in range(0, 24):
            summ += snap[now_day][i]
        one_day_avg = float(summ)/24

        #calculate average for more than one day
        j = 1
        
        while j != 2:
            now_day = (now_day + 1)%7
            for i in range(0, 24):
                summ += snap[now_day][i]

            j = j + 1

        two_day_avg = float(summ)/24*2
                
            

@mod_client.route('/payment', methods=['GET', 'POST'])
def payment_process():

    if(session['allow']):

        pay_method = session['pay_method']
        session['pay_method'] = ""

        final_price = session['final_price']
        session['final_price'] = ""

        session['allow'] = False

        return render_template('payment.html', headerTitle='Parking Lot - Receipt for Customer', pay_method = pay_method, final_price = final_price)


def calc_for_date(start_dtime, end_dtime, snap):
    temp_sum = 0
    weekday = start_dtime.weekday()
    weekday = (weekday + 1)%7
    entry_hour = start_dtime.hour
    exit_hour = end_dtime.hour

    for i in range(entry_hour, exit_hour + 1):
        temp_sum += float(snap[weekday][i])

    return temp_sum


def calc_price(entry_dtime, exit_dtime, price_snapshot):

    #Converting the string snapshot into suitable list of lists structure

    ls = price_snapshot.split('#')
    price_snapshot = []
    for i in ls:
        price_snapshot.append(i.split(','))

    ls = []
    summ = 0

    days = (exit_dtime.date() - entry_dtime.date()).days
    fin_time = dt.strptime("23:59:00", '%H:%M:%S')
    start_time = dt.strptime("00:01:00", '%H:%M:%S')
    fin_time = fin_time.time()
    start_time = start_time.time()

    #If car entered and exited on the same Date
    if(days == 0):
        summ = calc_for_date(entry_dtime, exit_dtime, price_snapshot)

    #If car entered and exited on different dates
    else:

        for i in range(days+1):

            if i == 0:
                summ += calc_for_date(entry_dtime, dt.combine(entry_dtime.date(),fin_time), price_snapshot)
            if i > 0 and i < days:
                temp_date = entry_dtime.date()+datetime.timedelta(days = i)
                summ += calc_for_date(dt.combine(temp_date, start_time), dt.combine(temp_date, fin_time), price_snapshot)

            if i == days:
                summ += calc_for_date(dt.combine(exit_dtime.date(),start_time), exit_dtime, price_snapshot)

    return summ

@mod_client.route('/exit', methods=['GET', 'POST'])

def exit_processing():

    if request.method == 'POST':

        token_input = request.form["token_id"]
        pay_method = request.form["pay_method"]

        #Extract Token corresponding to queried token_id
        token_object = Token.query.filter_by(token_id = token_input).first()

        exit_dtime = dt.now()
        entry_dtime = token_object.entry_date
        #exit_dtime = dt.strptime('2017-03-5 19:10:00', '%Y-%m-%d %H:%M:%S')

        #Extract Charge corresponding to the Particular token
        charge_object = Charge.query.filter_by(charge_id = token_object.charge_id).first()
        price_snapshot = charge_object.price_snapshot

        #Find the amount Customer needs to pay
        final_price = calc_price(entry_dtime, exit_dtime, price_snapshot)

        token_object.computed_charge = final_price
        token_object.pay_method = pay_method
        token_object.exit_date = exit_dtime
        db.session.commit()

        session['pay_method'] = pay_method
        session['final_price'] = final_price
        session['allow'] = True

        return redirect(url_for('client.payment_process'))

    else:
        return render_template('exit.html', headerTitle='Parking Lot - Exit')

@mod_client.route('/tokenDisplay', methods=['GET', 'POST'])
def token_display():
    if(session['token_session']):
        new_token_id = session['new_token_id']
        session['new_token_id'] = ""

        customer_entry_time = session['customer_entry_time']
        session['customer_entry_time'] = ""
        # print(customer_entry_time, file=sys.stderr)
        session['token_session'] = False
        return render_template('tokenDisplay.html', headerTitle='Parking Lot - Token for Customer' , new_token_id = new_token_id, customer_entry_time = customer_entry_time)
    else:
        return 'Token Generated'


@mod_client.route('/entry', methods=['GET', 'POST'])
def entry_processing():
    if request.method == 'POST':
        #get the current time to push along with customer car no
        entry_dtime = dt.now()
        #operator entered car Number
        carNo = request.form["CarNumber"]

        #Find active charge Id
        #Currently no active charge Id
        activeCharge = Charge.query.filter(Charge.ch_active.is_(True)).first()
        if (activeCharge is not None):
            chid = activeCharge.charge_id
        else:
            notActiveCharge = Charge.query.filter(Charge.ch_active.is_(False)).first()
            if (notActiveCharge is not None):
                chid = notActiveCharge.charge_id

        #create and push new token and generate token id
        getToken = Token(charge_id = chid, vehicle_no = carNo, entry_date = entry_dtime )
        db.session.add(getToken)
        db.session.commit()
        #print(new_token.token_id, file=sys.stderr)

        session['new_token_id'] = getToken.token_id
        session['customer_entry_time'] = entry_dtime
        session['token_session'] = True
        return redirect(url_for('client.token_display'))
    else:
        return render_template('entry.html', headerTitle='Parking Lot - Entry for Customer')
