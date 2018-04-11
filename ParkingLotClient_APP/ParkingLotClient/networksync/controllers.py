from flask import g, Blueprint, request, jsonify
from flask_mail import Message
from ParkingLotClient import db
import sys
import arrow
import jwt
import requests
from passlib.hash import argon2
import json

import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import and_, func, between

import datetime
from datetime import datetime as dt
from datetime import date, timedelta

from ParkingLotClient import app, socketio
from flask_login import login_required
from flask import Flask, render_template, redirect, url_for, session

from .models import UtilizationStage
from ParkingLotClient.client.models import HourlyUtil, ParkingLot, Charge
from ParkingLotClient.client.controllers import computerAvgParkingLotRate

from flask import url_for
from flask.ext.socketio import SocketIO, emit

mod_networksync = Blueprint('networksync', __name__)
#socketio = SocketIO(app)

def computeDailyUtil():
    #Getting current parling lot id
    plDetail = ParkingLot.query.filter_by(pl_active='t').first()
    plID = plDetail.pl_id

    #Getting Util Date
    yesterday = str(date.today() - timedelta(1))

    #Getting Util Stats
    yUtils = HourlyUtil.query.filter(HourlyUtil.util_date == yesterday).all()
    avgUtil = 0.0;
    totalRev = 0.0;

    utilPerHour = {}
    revPerHour = {}
    for elemHour in range(24):
        utilPerHour[elemHour] = 0.0;
        revPerHour[elemHour] = 0.0;

    for yUtil in yUtils:
        revPerHour[yUtil.util_hour] = yUtil.rev
        utilPerHour[yUtil.util_hour] = yUtil.util
        avgUtil = avgUtil + yUtil.util
        if(yUtil.util_hour == 23):
            totalRev = rev;

    avgUtil = float(avgUtil) / 24.0

    utilPerHourStr = '['
    revPerHourStr = '['
    for elemHour in range(24):
        utilPerHourStr = utilPerHourStr + utilPerHour[elemHour] + ','
        revPerHourStr = revPerHourStr + revPerHour[elemHour] + ','
    utilPerHourStr = utilPerHourStr[0:-1] + ']'
    revPerHourStr = revPerHourStr[0:-1] + ']'

    dailyUtilEntry = UtilizationStage(plID, yesterday, utilPerHourStr, revPerHourStr, avgUtil, totalRev, False)
    db.session.add(dailyUtilEntry)
    db.session.commit()


def sendDailyUtils(compute_util=True):

    if compute_util:
        computeDailyUtil()

    remainingUtils = UtilizationStage.query.filter_by(is_sent = False).all()
    for remainingUtil in remainingUtils:
        server_hostname = app.config['PARKING_LOT_ADMIN_HOSTNAME']

        # make a POST request
        server_response = requests.post(server_hostname + '/networksync/registerdailyutil', json={'plID': remainingUtil.pl_id, 'utilDate': str(remainingUtil.util_date), 'utilPerHourStr': remainingUtil.util_per_hour, 'revPerHourStr': remainingUtil.rev_per_hour, 'avgUtil': remainingUtil.avg_util, 'totalRev': remainingUtil.total_rev})

        #On obtaining confirm code in HTTPResponse
        response = json.loads(server_response.text)

        #Error at the admin end
        if 'error' in response:
            print 'ERROR (on inserting utilization at admin): ', response['error']

        else:
            #Update current object's is_sent to True if the response came properly
            if server_response.status_code == 200:
                remainingUtil.is_sent = True
                db.session.add(remainingUtil)
                db.session.commit()


@mod_networksync.route('/getunsentutils', methods=['GET'])
def sendUnsentUtils():
    sendDailyUtils(compute_util=False)
    return jsonify({'message': 'ok'})


@mod_networksync.route('/updatePrices', methods=['POST'])
def update_local_prices():
    data = request.get_json()
    if 'price_snapshot' not in data:
        return jsonify({'error': 'No PriceSnapshot given'})

    price_snapshot = data['price_snapshot']
    current_parkinglot = ParkingLot.query.filter_by().first()

    # Make the old active charges inactive and insert the new active charge
    old_active_charges = Charge.query.filter_by(ch_active='t').update({Charge.ch_active: False})
    #db.session.add(old_active_charges)
    #db.session.commit()

    new_charge = Charge(current_parkinglot.id, price_snapshot)
    db.session.add(new_charge)
    db.session.commit()
    four_hour_avg, one_day_avg, two_day_avg = computerAvgParkingLotRate()

    socketio.emit('Charge_Message', { 'fourHourAvg': four_hour_avg, 'oneDayAvg': one_day_avg, 'twoDayAvg': two_day_avg})

    return jsonify({'message': 'ok'})
