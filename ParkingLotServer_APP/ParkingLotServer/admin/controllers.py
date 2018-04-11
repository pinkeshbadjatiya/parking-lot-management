from flask import g, Blueprint, request, jsonify
from flask_mail import Message

import arrow
import jwt
from passlib.hash import argon2

import datetime
from datetime import timedelta
from sqlalchemy import and_
from ParkingLotServer import app, db
from flask_login import login_required
from flask import Flask, render_template, redirect, flash
from .models import ParkingLot, Utilization, Charge

from flask import url_for

mod_admin = Blueprint('admin', __name__)


@mod_admin.route('/viewUpdatePrices', methods=['GET', 'POST'])
@login_required
def view_update_prices():
    # Getting Parking Lot List from the DB through model and sending it to utilization page
    days = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]
    hoursList = ["D \ H", "00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23"]
    plList = []
    plListMap = {}
    plListRaw = ParkingLot.query.filter_by(pl_active='t').all()
    for plListRawItem in plListRaw:
        plList.append(plListRawItem.pl_name)
        plListMap[plListRawItem.pl_name] = plListRawItem.id

    headerTitle = 'Parking Lot - Price Snapshot'
    if request.method == 'POST':
        # Update the new received price
        price_snapshot = request.form.get("price_snapshot")
        print price_snapshot

        return jsonify({
            'message': 'ok'
            })

    if request.method == 'GET':
        #if request.form['button'] == 'view_pricesnapshot':
        selected_pl = request.args.get('pl')
        #selected_pl = request.form['inputPLSelect']

        # Check if parking lot is present
        if selected_pl not in plListMap:
            return render_template('viewprices.html',
                                    headerTitle=headerTitle,
                                    parkinglotList=plList,
                                    daysList=days,
                                    hoursList=hoursList,
                                    priceDataPresent=False)

        parklot_id = plListMap[selected_pl]
        charge_obj = Charge.query.filter_by(pl_id=parklot_id, ch_active='t').first()
        if not charge_obj:
            return render_template('viewprices.html',
                                    headerTitle=headerTitle,
                                    parkinglotList=plList,
                                    daysList=days,
                                    hoursList=hoursList,
                                    priceDataPresent=False,
                                    message="No charge data available")

        # Convert to lists
        price_snapshot = charge_obj.price_snapshot.split("#")
        for i, day in enumerate(price_snapshot):
            price_snapshot[i] = price_snapshot[i].split(",")

        return render_template('viewprices.html',
                                headerTitle=headerTitle,
                                parkinglotList=plList,
                                priceDataPresent='true',
                                parkinglotname=selected_pl,
                                daysList=days,
                                hoursList=hoursList,
                                pricesnapshot=price_snapshot)

    return render_template('viewprices.html', headerTitle=headerTitle, parkinglotList=plList, daysList=days, hoursList=hoursList, priceDataPresent=True)


def get_parking_lots():
    plList = []
    plListMap = {}
    plListRaw = ParkingLot.query.filter_by(pl_active='t').all()
    for plListRawItem in plListRaw:
        plList.append([plListRawItem.pl_name, plListRawItem.pl_address, plListRawItem.pl_capacity, plListRawItem.pl_default_price, plListRawItem.id])
        plListMap[str(plListRawItem.id)] = plListRawItem
    return plList, plListMap


@mod_admin.route('/configureParkingLots', methods=['GET', 'POST'])
@login_required
def configure_parking_lots():
    # print 'Configure Parking Lots'
    plList, plListMap = get_parking_lots()
    if request.method == 'POST':
        if request.form['button'] == 'delete_pl':
            db.session.delete(plListMap[request.form['id']])
            db.session.commit()
            print "delete request " + request.form['id']
            # delete operation to be performed
        if request.form['button'] == 'add_pl':
            parking_lot = ParkingLot(request.form['pl_name'], request.form['pl_address'], request.form['pl_capacity'], request.form['pl_price'], True)
            db.session.add(parking_lot)
            db.session.commit()

            # Insert default price snapshot
            default_price = request.form['pl_price'].strip()
            default_price_snapshot = "#".join([",".join([default_price] * 24)] * 7)
            default_charge = Charge(parking_lot.id, default_price_snapshot, True)
            db.session.add(default_charge)
            db.session.commit()

            # if parking_lot.id != 1 :
            #     flash('Error in adding parking lot')
            print "add request"
    plList, plListMap = get_parking_lots()
    return render_template('parkinglots.html', headerTitle='Parking Lot - Configuration', parkinglotList=plList)


@mod_admin.route('/utilization', methods=['GET', 'POST'])
@login_required
def view_utilization():
    # Getting Parking Lot List from the DB through model and sending it to utilization page
    plList = []
    plListMap = {}
    plListRaw = ParkingLot.query.filter_by(pl_active='t').all()
    for plListRawItem in plListRaw:
        plList.append(plListRawItem.pl_name)
        plListMap[plListRawItem.pl_name] = plListRawItem.id

    if request.method == 'POST':
        if request.form['button'] == 'view_utilization':
            selected_date = request.form['inputDateSelect']
            selected_pl = request.form['inputPLSelect']
            parklot_id = plListMap[selected_pl]

            selected_date_day = selected_date[selected_date.rfind('-') + 1:]
            selected_date_month = selected_date[selected_date.find('-') + 1:selected_date.rfind('-')]
            selected_date_year = selected_date[0:selected_date.find('-')]
            selDate = datetime.date(int(selected_date_year), int(selected_date_month), int(selected_date_day))

            selDateM1 = selDate - timedelta(days=1)
            selDateM2 = selDate - timedelta(days=2)

            selDateStats = Utilization.query.filter(and_(Utilization.pl_id == parklot_id, Utilization.util_date == str(selDate))).first()
            if(selDateStats is None):
                return render_template('utilization.html',
                                       headerTitle='Parking Lot - Utilization',                                  parkinglotList = plList, 
                                       chartDataPresent = 'no',
                                       sdate = selected_date,
                                       spl = selected_pl)
            selDateM1Stats = Utilization.query.filter(and_(Utilization.pl_id == parklot_id, Utilization.util_date == str(selDateM1))).first()
            selDateM2Stats = Utilization.query.filter(and_(Utilization.pl_id == parklot_id, Utilization.util_date == str(selDateM2))).first()

            # daysUtil = str(selDateStats.avg_util) + ',' + str(selDateStats.avg_util) + ',' + str(selDateStats.avg_util)
            # daysRev = str(selDateStats.total_rev) + ',' + str(selDateStats.total_rev) + ',' + str(selDateStats.total_rev)
            # selDateM1Stats = ParkingLot.query.filter_by(pl_active='t')
            return render_template('utilization.html',
                                    headerTitle='Parking Lot - Utilization',
                                    parkinglotList=plList,
                                    chartDataPresent='yes',
                                    sdate=selected_date,
                                    sdate_year=selected_date_year,
                                    sdate_month=selected_date_month,
                                    sdate_day=selected_date_day,
                                    spl=selected_pl,
                                    perHourUtil=selDateStats.util_per_hour,
                                    perHourRev=selDateStats.rev_per_hour    ,
                                    selDateUtil=selDateStats.avg_util,
                                    selDateRev=selDateStats.total_rev,
                                    selDateM1Util=selDateM1Stats.avg_util,
                                    selDateM1Rev=selDateM1Stats.total_rev,
                                    selDateM2Util=selDateM2Stats.avg_util,
                                    selDateM2Rev=selDateM2Stats.total_rev)
                                    # prevDaysUtil=daysUtil,
                                    # prevDaysRev=daysRev)

    return render_template('utilization.html', headerTitle='Parking Lot - Utilization', parkinglotList=plList, chartDataPresent='')


@mod_admin.route('/dashboard', methods=['GET', 'POST'])
@login_required
def show_dashboard():
    return render_template('dashboard.html', headerTitle='Parking Lot - Dashboard')
