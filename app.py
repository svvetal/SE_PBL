from flask import Flask, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt

import flask
from flask import Flask, render_template, jsonify, request
import RPi.GPIO as GPIO
from time import sleep

from flask import Flask, render_template, Response
import os

if os.environ.get('CAMERA'):
    Camera = import_module('camera_' + os.environ['CAMERA']).Camera
else:
    from camera import Camera

mA1=18
mA2=23
mB1=24
mB2=25

ir_left = 2
ir_center = 3
ir_right = 4
buzz = 17
obs_led = 16
pow_led = 21

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(mA1, GPIO.OUT)
GPIO.setup(mA2, GPIO.OUT)
GPIO.setup(mB1, GPIO.OUT)
GPIO.setup(mB2, GPIO.OUT)
GPIO.output(mA1 , 0)
GPIO.output(mA2 , 0)
GPIO.output(mB1, 0)
GPIO.output(mB2, 0)

GPIO.setup(ir_left, GPIO.IN)
GPIO.setup(ir_center, GPIO.IN)
GPIO.setup(ir_right, GPIO.IN)
GPIO.setup(buzz, GPIO.OUT)
GPIO.output(buzz,0)
GPIO.setup(obs_led, GPIO.OUT)
GPIO.output(obs_led,0)
GPIO.setup(pow_led, GPIO.OUT)
GPIO.output(pow_led,1)

servo = 26

GPIO.setup(servo, GPIO.OUT)

p = GPIO.PWM(servo, 50)

p.start(0)

app = Flask(__name__)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

class RegisterForm(FlaskForm):
    username = StringField(validators = [InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder" : "Username"})

    password = PasswordField(validators = [InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder" : "Password"})

    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username = username.data).first()

        if existing_user_username:
            raise ValidationError(
                "That Username already exists. Please choose a Different one")

class LoginForm(FlaskForm):
    username = StringField(validators = [InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder" : "Username"})

    password = PasswordField(validators = [InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder" : "Password"})

    submit = SubmitField("Login")

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('control'))

    return render_template('login.html', form=form)

@app.route('/control', methods=['GET', 'POST'])
@login_required
def control():
    return render_template('Motor_test.html')

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password = hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/forward')
def forward():
    GPIO.output(mA1 , 1)
    GPIO.output(mA2 , 0)
    GPIO.output(mB1, 0)
    GPIO.output(mB2, 1)
    return ("nothing")

@app.route('/backward')
def backward():
    GPIO.output(mA1 , 0)
    GPIO.output(mA2 , 1)
    GPIO.output(mB1, 1)
    GPIO.output(mB2, 0)
    return ("nothing")

@app.route('/right')
def right():
    GPIO.output(mA1 , 0)
    GPIO.output(mA2 , 1)
    GPIO.output(mB1, 0)
    GPIO.output(mB2, 0)
    return ("nothing")

@app.route('/left')
def left():
    GPIO.output(mA1 , 0)
    GPIO.output(mA2 , 0)
    GPIO.output(mB1, 1)
    GPIO.output(mB2, 0)
    return ("nothing")

@app.route('/stop')
def stop():
    GPIO.output(mA1 , 0)
    GPIO.output(mA2 , 0)
    GPIO.output(mB1, 0)
    GPIO.output(mB2, 0)
    return ("nothing")

@app.route('/set_speed')
def set_speed():
    speed = request.args.get("speed")
    p.ChangeDutyCycle(int(speed))
    return render_template('Motor_test.html')

@app.route('/update')
def update():
    data_1 = GPIO.input(ir_left)
    data_2 = GPIO.input(ir_center)
    data_3 = GPIO.input(ir_right)
    global irl,irc,irr
    irl = "No Obstacle Detected"
    irc = "No Obstacle Detected"
    irr = "No Obstacle Detected"
    if data_1 == 0:
        irl = "Obstacle Detected"
        GPIO.output(buzz, 1)
        GPIO.output(obs_led, 1)
    elif data_2 == 0:
        irc = "Obstacle Detected"
        GPIO.output(buzz, 1)
        GPIO.output(obs_led, 1)
    elif data_3 == 0:
        irr = "Obstacle Detected"
        GPIO.output(buzz, 1)
        GPIO.output(obs_led, 1)
    elif data_1 == 1:
        irl = "No Obstacle Detected"
        GPIO.output(buzz, 0)
        GPIO.output(obs_led, 0)
    elif data_2 == 1:
        irc = "No Obstacle Detected"
        GPIO.output(buzz, 0)
        GPIO.output(obs_led, 0)
    elif data_3 == 1:
        irr = "No Obstacle Detected"
        GPIO.output(buzz, 0)
        GPIO.output(obs_led, 0)
    templateData = {'data1' : irl, 'data2' : irc, 'data3' : irr}
    return jsonify(templateData), 200

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0')