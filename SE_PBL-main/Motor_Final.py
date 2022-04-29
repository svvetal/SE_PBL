import flask
from flask import Flask, render_template, jsonify, request
import RPi.GPIO as GPIO
from time import sleep

mA1=18
mA2=23
mB1=24
mB2=25

ir_left = 2
ir_center = 3
ir_right = 4
buzz = 17

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

servo = 26

GPIO.setup(servo, GPIO.OUT)

p = GPIO.PWM(servo, 50)

p.start(0)


app = Flask(__name__, template_folder='template')
    
@app.route('/')
def home():
    return render_template('Motor_Final.html')

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
    return render_template('Motor_Final.html')

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
    elif data_2 == 0:
        irc = "Obstacle Detected"
        GPIO.output(buzz, 1)
    elif data_3 == 0:
        irr = "Obstacle Detected"
        GPIO.output(buzz, 1)
    elif data_1 == 1:
        irl = "No Obstacle Detected"
        GPIO.output(buzz, 0)
    elif data_2 == 1:
        irc = "No Obstacle Detected"
        GPIO.output(buzz, 0)
    elif data_3 == 1:
        irr = "No Obstacle Detected"
        GPIO.output(buzz, 0)
    templateData = {'data1' : irl, 'data2' : irc, 'data3' : irr}
    return jsonify(templateData), 200

if __name__ == '__main__':
    app.run()