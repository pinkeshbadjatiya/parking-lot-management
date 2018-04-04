from flask import g, Blueprint, request, jsonify
from flask_mail import Message

import arrow
import jwt
from passlib.hash import argon2
from apscheduler.scheduler import Scheduler
import datetime as dt
from sqlalchemy import and_, func

from ParkingLotClient import app
from flask_login import login_required
from flask import Flask, render_template
#from .models import User

from flask import url_for

mod_client = Blueprint('client', __name__)

cron = Scheduler(daemon=True)
cron.start()

@cron.interval_schedule(hours=1)
def populateHourlyUtil():
    currDT = str(dt.datetime.now())
    currDate = currDT[0:currDT.find(' ')]
    currHour = currDT[currDT.find(' '):currDT.find(':')].strip()
    currHourInt = int(currHour)
    
    #Code from Table or client config for getting parking lot capacity
    #parkingLotCapacity
    
    currActiveTokens = Token.query.filter_by(exit_time == None).all()
    currUtil = parkingLotCapacity - len(currActiveTokens) 
    currUtilPercent = (currUtil * 100) / parkingLotCapacity
    
    lastHourTransactions = Token.query.filter_by(exit_time.between(func.to_date(currDate + " " + str(currHourInt-1) + ":00", "YYYY-MM-DD HH24:MI"), func.to_date(currDate + " " + str(currHourInt) + ":59", "YYYY-MM-DD HH24:MI")).all()
    
    prevRev = 0.0
    if(currHourInt >= 2):
        lastlastHourUtil = HourlyUtil.query.filter(and_(util_date == currDate, util_hour == str(currHourInt-2)).first()
        prevRev = int(lastlastHourUtil.rev)
    
    currRev = 0.0
    for lastHourTransaction in lastHourTransactions:
        currRev = currRev + float(lastHourTransaction.computed_charge)

    currCumuRev = currRev + prevRev
    hourlyUtilEntry = HourlyUtil(currDate, currHour, currUtilPercent, currCumuRev)
    session.add(hourlyUtilEntry)
