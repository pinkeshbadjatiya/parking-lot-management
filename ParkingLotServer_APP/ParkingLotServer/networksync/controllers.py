from flask import g, Blueprint, request, jsonify, current_app
from flask_mail import Message

import arrow
import jwt
from passlib.hash import argon2

from flask import request
from sqlalchemy import and_
from ParkingLotServer import db

from flask_login import login_required
from flask import Flask, render_template, redirect, flash
from .models import StagingPriceUpdates
from ParkingLotServer.admin.models import Charge, ParkingLot, Utilization
import requests

from flask import url_for

mod_networksync = Blueprint('networksync', __name__)


@mod_networksync.route('/updatePrices', methods=['POST'])
def return_price_updates():
    data = request.get_json()
    if 'parkinglot_id' not in data:
        return jsonify({'error': 'No ParkingLotID specified.'})

    parklot_id = data['parkinglot_id']

    # Check if the current price snapshot is updated in StagingPriceUpdates table
    active_charge = Charge.query.filter(and_(Charge.pl_id == parklot_id, Charge.ch_active == 't')).first()
    current_staging_charge = StagingPriceUpdates.query.filter_by(ch_id=active_charge.ch_id).first()

    if not current_staging_charge:
        # Charge is not yet staged for pushing
        # First dummy send the old staging charges if not sent already
        old_staging_charges = StagingPriceUpdates.query.filter(and_(StagingPriceUpdates.pl_id == active_charge.pl_id, StagingPriceUpdates.ch_sent == 'f')).update({StagingPriceUpdates.ch_sent: 't'})
        db.session.add(old_staging_charges)
        db.session.commit()

        # Now, insert the new charge to be sent and also update the sent flag before sending
        staged_snapshot = StagingPriceUpdates(active_charge.pl_id, active_charge.charge_id, active_charge.price_snapshot)
        staged_snapshot.ch_sent = 't'
        db.session.add(staged_snapshot)
        db.session.commit()

        # Now return the new charge
        return jsonify({
            'price_snapshot': staged_snapshot.price_snapshot
        })

    elif current_staging_charge.ch_sent == 't':
        # Charge was staged and already sent. Just skip
        return jsonify({
            'price_snapshot': ''
        })
    elif current_staging_charge.ch_sent == 'f':
        # Charge is already staged but not sent. Send it now.
        current_staging_charge.ch_sent = 't'
        db.session.add(current_staging_charge)
        db.session.commit()
        return jsonify({
            'price_snapshot': current_staging_charge.price_snapshot
        })


def push_price_updates():
    # First fetch the currently active prices of all the parking lots
    active_charges = Charge.query.filter_by(ch_active='t').all()
    for active_charge in active_charges:
        current_staging_charge = StagingPriceUpdates.query.filter_by(ch_id=active_charge.ch_id).first()

        if not current_staging_charge:
            # Charge is not yet staged for pushing
            # First dummy send the old staging charges if not sent already
            old_staging_charges = StagingPriceUpdates.query.filter(and_(StagingPriceUpdates.pl_id == active_charge.pl_id, StagingPriceUpdates.ch_sent == 'f')).update({StagingPriceUpdates.ch_sent: 't'})
            db.session.add(old_staging_charges)
            db.session.commit()

            # Now, insert the new charge to be sent
            staged_snapshot = StagingPriceUpdates(active_charge.pl_id, active_charge.charge_id, active_charge.price_snapshot)
            db.session.add(staged_snapshot)
            db.session.commit()

        if current_staging_charge.ch_sent == 't':
            # Charge was staged and already sent. Just skip
            continue
        elif current_staging_charge.ch_sent == 'f':
            # Charge is already staged but not sent. Send it now.
            client_hostname = current_app.config['PARKING_LOT_CLIENT_HOSTNAMES'][active_charge.pl_id]

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
                active_charge.ch_sent = 't'
                db.session.add(active_charge)
                db.session.commit()
                
@mod_networksync.route('/registerdailyutil', methods=['GET', 'POST'])
def register_daily_util():
    if request.method == 'POST':
        reqParams = request.json
        utilDate = reqParams['utilDate']
        anyUtilData = Utilization.query.filter_by(util_date=utilDate).first()
        if(anyUtilData is not None):
            return jsonify({'message': 'ok'})
        else:
            try:
                newUtilization = Utilization(reqParams['plID'], reqParams['utilDate'], reqParams['utilPerHourStr'], reqParams['revPerHourStr'], reqParams['avgUtil'], reqParams['totalRev'])
                db.session.add(newUtilization)
                db.session.commit()
                return jsonify({'message': 'ok'})
                
            except Exception, e:
                return jsonify({'error': e})
