from flask import g, Blueprint, request, jsonify
from flask_mail import Message

import arrow
import jwt
from passlib.hash import argon2

from ParkingLotServer import app, db
from flask_login import login_required
from .models import Users

from flask import url_for, render_template, redirect, flash

from flask_login import logout_user, login_user, current_user
mod_auth = Blueprint('authentication', __name__)

#@mod_auth.route('/', methods=['GET'])
#@login_required
#def home():
#    print current_user
#    return "WOW! Welcome %s." %(current_user.email)

@mod_auth.route('/login', methods=['GET','POST'])
def login():
    errorMsg = ''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = Users.query.filter_by(email=email).first()
        if user is not None and user.authenticate(password):
            user.authenticated = True
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash('Thanks for logging in, {}'.format(current_user.email))
            #return redirect(url_for('authentication.home'))
            return redirect(url_for('admin.show_dashboard', headerTitle='Parking Lot Administration - Dashboard'))
        else:
            #flash('ERROR! Incorrect login credentials.', 'error')
            errorMsg = 'Invalid Login! Try Again.'
    return render_template('login.html', headerTitle='Parking Lot Administration - Login', errorMessage = errorMsg)

@mod_auth.route('/register' , methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html', headerTitle='Parking Lot Administration - Register')
    user = Users(request.form['firstname'], request.form['lastname'], request.form['email'], request.form['password'])
    db.session.add(user)
    db.session.commit()
    flash('User successfully registered')
    return redirect(url_for('authentication.login', headerTitle='Parking Lot Administration - Login'))


@mod_auth.route('/logout', methods=['GET','POST'])
@login_required
def logout():
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    flash('Goodbye!', 'info')
    return redirect(url_for('authentication.login'))


@mod_auth.route('/change_password', methods=['POST'])
@login_required
def change_password():
    old_password = request.form['old_password']
    new_password = request.form['new_password']
    if current_user.change_password(old_password, new_password):
        flash('Password changed successfully', 'info')
        return redirect(url_for('authentication.login', headerTitle='Parking Lot Administration - Login'))
    else:
        flash('Some error occured', 'error')
        return redirect(url_for('authentication.change_password', headerTitle='Parking Lot Administration - Change Password'))
