from flask import g, Blueprint, request, jsonify
from flask_mail import Message

import arrow
import jwt
from passlib.hash import argon2

from server import app
from flask_login import login_required
from flask import Flask, render_template
#from .models import User

from flask import url_for

mod_client = Blueprint('client', __name__)

@mod_client.route('/utilization', methods=['GET'])
def view_utilization():
    return render_template('dashboard.html', headerTitle='Parking Lot - Dashboard')
