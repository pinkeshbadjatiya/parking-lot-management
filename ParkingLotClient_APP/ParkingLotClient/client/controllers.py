from sqlalchemy import and_, func, between
from flask_login import login_required, current_user
from flask import Flask, render_template, redirect, url_for, session, g, Blueprint, request, jsonify, url_for

import datetime
from datetime import datetime as dt
from datetime import timedelta

from ParkingLotClient import db, app, socketio
from .models import Token, Charge, ParkingLot, HourlyUtil

mod_client = Blueprint('client', __name__)


def populateHourlyUtil():
    try:
        # Getting current date and current hour
        currDT = str(dt.now())
        currDate = currDT[0:currDT.find(' ')]
        currHour = currDT[currDT.find(' '):currDT.find(':')].strip()
        currHourInt = int(currHour)

        # Getting capacity of the current parking lot
        activePL = ParkingLot.query.filter_by(pl_active='t').first()
        parkingLotCapacity = int(activePL.pl_capacity)

        # Getting number of current occupied slots and utilization percentage
        currActiveTokens = Token.query.filter_by(exit_date=None).all()
        currUtil = parkingLotCapacity - len(currActiveTokens)
        currUtilPercent = (currUtil * 100) / parkingLotCapacity

        if(currHourInt == 0):
            prevDT = str(dt.now() - timedelta(days=1))
            prevDate = prevDT[0:prevDT.find(' ')]

            # Getting exit transactions of the last hour of the previous day
            lastHourTransactions = Token.query.filter(between(Token.exit_date, func.to_date(prevDate + " 23:00", "YYYY-MM-DD HH24:MI"), func.to_date(prevDate + " 23:59", "YYYY-MM-DD HH24:MI"))).all()

            # Getting revenue collected till start of the last hour
            prevRev = 0.0

            lastlastHourUtil = HourlyUtil.query.filter(and_(HourlyUtil.util_date == func.to_date(prevDate, "YYYY-MM-DD"), HourlyUtil.util_hour == 22)).first()
            if(lastlastHourUtil is None):
                prevRev = 0.0
            else:
                prevRev = float(lastlastHourUtil.rev)

            # Getting revenue collected in the last hour
            currRev = 0.0
            for lastHourTransaction in lastHourTransactions:
                currRev = currRev + float(lastHourTransaction.computed_charge)

            # Computing cumulative revenue and storing as a new row in the Hourly Util table
            currCumuRev = currRev + prevRev
            hourlyUtilEntry = HourlyUtil(prevDate, 23, currUtilPercent, currCumuRev)
            db.session.add(hourlyUtilEntry)
            db.session.commit()
        else:

            # Getting exit transactions of the last hour
            lastHourTransactions = Token.query.filter(between(Token.exit_date, func.to_date(currDate + " " + str(currHourInt - 1) + ":00", "YYYY-MM-DD HH24:MI"), func.to_date(currDate + " " + str(currHourInt - 1) + ":59", "YYYY-MM-DD HH24:MI"))).all()

            # Getting revenue collected till start of the last hour
            prevRev = 0.0
            if(currHourInt >= 2):
                lastlastHourUtil = HourlyUtil.query.filter(and_(HourlyUtil.util_date == func.to_date(currDate, "YYYY-MM-DD"), HourlyUtil.util_hour == (currHourInt - 2))).first()
                if(lastlastHourUtil is None):
                    prevRev = 0.0
                else:
                    prevRev = float(lastlastHourUtil.rev)

            # Getting revenue collected in the last hour
            currRev = 0.0
            for lastHourTransaction in lastHourTransactions:
                currRev = currRev + float(lastHourTransaction.computed_charge)

            # Computing cumulative revenue and storing as a new row in the Hourly Util table
            currCumuRev = currRev + prevRev
            hourlyUtilEntry = HourlyUtil(currDate, currHour, currUtilPercent, currCumuRev)
            db.session.add(hourlyUtilEntry)
            db.session.commit()

    except Exception, e:
        print e


def getCurUtilization():
    activePL = ParkingLot.query.filter_by(pl_active='t').first()
    parkingLotCapacity = int(activePL.pl_capacity)

    # Getting number of current occupied slots and utilization percentage
    currActiveTokens = Token.query.filter_by(exit_date=None).all()
    emptySlots = parkingLotCapacity - len(currActiveTokens)
    return parkingLotCapacity, emptySlots


def computerAvgParkingLotRate():
        activeCharge = Charge.query.filter(Charge.ch_active.is_(True)).first()
        if (activeCharge is not None):
            price_snapshot = activeCharge.price_snapshot
        else:
            inactiveCharge = Charge.query.filter(Charge.ch_active.is_(False)).first()
            if (inactiveCharge is not None):
                price_snapshot = inactiveCharge.price_snapshot
        ls = price_snapshot.split('#')
        snap = []
        for i in ls:
            snap.append(i.split(','))

        now = dt.now()
        now_day = now.weekday()
        now_day = (now_day + 1) % 7
        now_hour = now.hour

        summ = 0
        four_hour_avg = 0
        one_day_avg = 0
        two_day_avg = 0

        for i in range(now_hour, now_hour + 4):
            four_hour_avg += float(snap[now_day][i % 24])
        four_hour_avg = float(four_hour_avg) / 4

        # calculate average for one day
        for i in range(0, 24):
            summ += float(snap[now_day][i])
        one_day_avg = float(summ) / 24

        # calculate average for more than one day
        j = 1
        while j != 2:
            now_day = (now_day + 1) % 7
            for i in range(0, 24):
                summ += float(snap[now_day][i])
            j = j + 1

        two_day_avg = float(summ) / (24 * 2)
        return int(four_hour_avg), int(one_day_avg), int(two_day_avg)


@mod_client.route('/home', methods=['GET', 'POST'])
@login_required
def show_home():
    return render_template('home.html', headerTitle='Parking Lot - Home', username=current_user.first_name + " " + current_user.last_name)


@mod_client.route('/ParkingLotDisplay', methods=['GET', 'POST'])
def display_info():
    four_hour_avg, one_day_avg, two_day_avg = computerAvgParkingLotRate()
    totalSlots, emptySlots = getCurUtilization()

    return render_template('ParkingLotDisplay.html', headerTitle='Parking Lot - Info', pl_total_slots=totalSlots, pl_empty_slots=emptySlots, fourHourAvg=int(four_hour_avg), oneDayAvg=int(one_day_avg), twoDayAvg=int(two_day_avg))


@mod_client.route('/print_summary', methods=['GET', 'POST'])
@login_required
def print_summary():

    if(session['allow']):

        pay_method = session['pay_method']
        session['pay_method'] = ""

        final_price = session['final_price']
        session['final_price'] = ""

        token_id = session['token_id']
        session['token_id'] = ""

        exit_time = session['exit_time']
        session['exit_time'] = ""

        session['allow'] = False

        return render_template('summary.html', headerTitle='Parking Lot - Receipt for Customer', pay_method=pay_method, final_price=final_price, token_id=token_id, exit_time=exit_time)


def calc_for_date(start_dtime, end_dtime, snap):
    temp_sum = 0
    weekday = start_dtime.weekday()
    weekday = (weekday + 1) % 7
    entry_hour = start_dtime.hour
    exit_hour = end_dtime.hour

    for i in range(entry_hour, exit_hour + 1):
        temp_sum += float(snap[weekday][i])

    return temp_sum


def calc_price(entry_dtime, exit_dtime, price_snapshot):

    # Converting the string snapshot into suitable list of lists structure
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

    # If car entered and exited on the same Date
    if(days == 0):
        summ = calc_for_date(entry_dtime, exit_dtime, price_snapshot)

    # If car entered and exited on different dates
    else:

        for i in range(days + 1):

            if i == 0:
                summ += calc_for_date(entry_dtime, dt.combine(entry_dtime.date(), fin_time), price_snapshot)
            if i > 0 and i < days:
                temp_date = entry_dtime.date() + datetime.timedelta(days=i)
                summ += calc_for_date(dt.combine(temp_date, start_time), dt.combine(temp_date, fin_time), price_snapshot)

            if i == days:
                summ += calc_for_date(dt.combine(exit_dtime.date(), start_time), exit_dtime, price_snapshot)

    return summ


def pay():
    return True


@mod_client.route('/exit', methods=['GET', 'POST'])
@login_required
def exit_processing():

    if request.method == 'POST':

        token_input = request.form["token_id"]
        pay_method = request.form["pay_method"]
        token_object_exists = 0

        # Extract Token corresponding to queried token_id
        if token_input.isdigit():
            token_object_exists = Token.query.filter_by(token_id=token_input).count()
            token_object = Token.query.filter_by(token_id=token_input).first()

        if token_object_exists > 0:
            if token_object.exit_date is None:

                exit_dtime = dt.now()
                entry_dtime = token_object.entry_date
                exit_dtime = dt.strptime(exit_dtime.strftime('%Y-%m-%d %H:%M'), '%Y-%m-%d %H:%M')

                # Extract Charge corresponding to the Particular token
                charge_object = Charge.query.filter_by(charge_id=token_object.charge_id).first()
                price_snapshot = charge_object.price_snapshot

                # Find the amount Customer needs to pay
                final_price = calc_price(entry_dtime, exit_dtime, price_snapshot)
                final_price = float("{0:.2f}".format(final_price))

                # Customer pays the amount
                if not pay():
                    return render_template('exit.html', headerTitle='Parking Lot - Exit', errorMsg="Payment Failed")

                token_object.computed_charge = final_price
                token_object.pay_method = pay_method
                token_object.exit_date = exit_dtime
                token_object.exit_operator_id = current_user.id
                db.session.commit()

                totalSlots, emptySlots = getCurUtilization()
                socketio.emit('PL_Message', {'pl_empty_slots': emptySlots})

                session['pay_method'] = pay_method
                session['final_price'] = final_price
                session['token_id'] = token_input
                session['exit_time'] = exit_dtime.strftime('%Y-%m-%d %H:%M')
                session['allow'] = True

                return redirect(url_for('client.print_summary'))

            else:
                return render_template('exit.html', headerTitle='Parking Lot - Exit', errorMsg="Token already used")
        else:
            return render_template('exit.html', headerTitle='Parking Lot - Exit', errorMsg="Invalid Token")
    else:
        return render_template('exit.html', headerTitle='Parking Lot - Exit', errorMsg="")


@mod_client.route('/tokendisplay', methods=['GET', 'POST'])
@login_required
def token_display():
    if(session['token_session']):
        token_id = session['new_token_id']
        session['new_token_id'] = ""
        entry_time = session['customer_entry_time']
        session['customer_entry_time'] = ""
        # print(customer_entry_time, file=sys.stderr)
        opId = session['operatoId']
        session['operatoId'] = ""

        session['token_session'] = False
        activePL = ParkingLot.query.filter_by(pl_active='t').first()

        # if (activePL is not None):
        pl_Name = activePL.pl_name
        pl_Address = activePL.pl_address

        return render_template('tokendisplay.html', headerTitle='Customer Token', tokenId=token_id, entryTime=entry_time, plName=pl_Name, plAddress=pl_Address, operatorId=opId)
    else:
        return render_template('home.html', headerTitle='Parking Lot - Home', username=current_user.first_name + " " + current_user.last_name)


@mod_client.route('/entry', methods=['GET', 'POST'])
@login_required
def entry_processing():
    if request.method == 'POST':
        # get the current time to push along with customer car no
        entry_dtime = dt.now()
        entry_dtime = dt.strptime(entry_dtime.strftime('%Y-%m-%d %H:%M'), '%Y-%m-%d %H:%M')
        # operator entered car Number
        carNo = request.form.get('CarNumber', None)
        if carNo:
            # dont do anything if carNO is empty
            # Find active charge Id
            # Currently no active charge Id
            activeCharge = Charge.query.filter(Charge.ch_active.is_(True)).first()
            if (activeCharge is not None):
                chid = activeCharge.charge_id
            else:
                notActiveCharge = Charge.query.filter(Charge.ch_active.is_(False)).first()
                if (notActiveCharge is not None):
                    chid = notActiveCharge.charge_id

            totalSlots, curEmprtySlots = getCurUtilization()
            if curEmprtySlots > 0:
                # create and push new token and generate token id
                getToken = Token(charge_id=chid, vehicle_no=carNo, entry_date=entry_dtime, entry_operator_id=current_user.id)
                db.session.add(getToken)
                db.session.commit()

                totalSlots, emptySlots = getCurUtilization()
                # socketio.emit('PL_Message', { 'pl_empty_slots' : emptySlots, 'fourHourAvg': four_hour_avg, 'oneDayAvg': one_day_avg, 'twoDayAvg': two_day_avg})
                socketio.emit('PL_Message', {'pl_empty_slots': emptySlots})

                session['new_token_id'] = getToken.token_id
                session['customer_entry_time'] = entry_dtime
                session['operatoId'] = current_user.id
                session['token_session'] = True
                return redirect(url_for('client.token_display'))
            else:
                errorMsg = 'Parking Lot full !!'
                return render_template('entry.html', headerTitle='Parking Lot - Entry for Customer', errorMessage=errorMsg)
        else:
            errorMsg = 'Please enter valid car No !!'
            return render_template('entry.html', headerTitle='Parking Lot - Entry for Customer', errorMessage=errorMsg)
    else:
        return render_template('entry.html', headerTitle='Parking Lot - Entry for Customer')
