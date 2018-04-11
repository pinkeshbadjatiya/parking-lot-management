from flask import g, Blueprint, request, jsonify, current_app
from flask_mail import Message

import arrow
import jwt
from passlib.hash import argon2

from flask import request
from sqlalchemy import and_

from flask_login import login_required
from flask import Flask, render_template, redirect, flash
from .models import StagingPriceUpdates
from ParkingLotServer.admin.models import Charge, ParkingLot, Utilization
from ParkingLotServer import app, db
import requests, json

from flask import url_for

mod_networksync = Blueprint('networksync', __name__)



def push_price_updates(parklot_id=None):
    # First fetch the currently active prices of all the parking lots or one parking lot
    if not parklot_id:
        active_charges = Charge.query.filter_by(ch_active='t').all()
    else:
        active_charges = Charge.query.filter(and_(Charge.ch_active == 't', Charge.pl_id == parklot_id)).all()

    for active_charge in active_charges:
        current_staging_charge = StagingPriceUpdates.query.filter_by(ch_id=active_charge.charge_id).first()

        if not current_staging_charge:
            # Charge is not yet staged for pushing
            # First dummy send the old staging charges if not sent already
            old_staging_charges = StagingPriceUpdates.query.filter(and_(StagingPriceUpdates.pl_id == active_charge.pl_id, StagingPriceUpdates.ch_sent == False)).update({StagingPriceUpdates.ch_sent: True})
            db.session.commit()

            # Now, insert the new charge to be sent and update the current_staging_charge
            staged_snapshot = StagingPriceUpdates(active_charge.pl_id, active_charge.charge_id, active_charge.price_snapshot)
            current_staging_charge = staged_snapshot
            db.session.add(staged_snapshot)
            db.session.commit()


        if current_staging_charge.ch_sent:
            # Charge was staged and already sent. Just skip
            continue
        else:
            # Charge is already staged but not sent. Send it now.
            client_hostname = current_app.config['PARKING_LOT_CLIENT_HOSTNAMES'][active_charge.pl_id]
            print client_hostname

            # make a POST request
            res = requests.post(client_hostname + '/networksync/updatePrices', json={
                'price_snapshot': current_staging_charge.price_snapshot
            })
            print 'response from server:', res.text
            response = json.loads(res.text)
            if 'error' in response:
                print 'ERROR (on updating prices at client)', response['error']

            # if push is successful then make ch_sent=='t'
            if res.status_code == 200:
                current_staging_charge.ch_sent = 't'
                db.session.add(current_staging_charge)
                db.session.commit()


@mod_networksync.route('/updatePrices', methods=['POST'])
def return_price_updates():
    data = request.get_json()
    if 'parkinglot_id' not in data:
        return jsonify({
            'error': 'No ParkingLotID specified.'
        })

    parklot_id = data['parkinglot_id']
    push_price_updates(parklot_id=parklot_id)

    return jsonify({
        'message': 'ok'
    })


@mod_networksync.route('/registerdailyutil', methods=['GET', 'POST'])
def register_daily_util():
    if request.method == 'POST':
        reqParams = request.json
        utilDate = reqParams['utilDate']
        anyUtilData = Utilization.query.filter_by(util_date=utilDate).first()
        if anyUtilData:
            return jsonify({'message': 'ok'})
        else:
            try:
                newUtilization = Utilization(reqParams['plID'], reqParams['utilDate'], reqParams['utilPerHourStr'], reqParams['revPerHourStr'], reqParams['avgUtil'], reqParams['totalRev'])
                db.session.add(newUtilization)
                db.session.commit()
                return jsonify({'message': 'ok'})

            except Exception, e:
                return jsonify({'error': e})
