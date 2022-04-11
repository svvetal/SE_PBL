import flask
from flask import Flask, render_template
import RPi.GPIO as GPIO
from time import sleep

mA1=18
mA2=23
mB1=24
mB2=25

IR_right = 2
IR_center = 3
IR_left = 4
buzzer = 17


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

GPIO.setup(IR_right, GPIO.IN)
GPIO.setup(IR_center, GPIO.IN)
GPIO.setup(IR_left, GPIO.IN)
GPIO.setup(buzzer, GPIO.OUT)
GPIO.output(buzzer, False)


app = Flask(__name__, template_folder='template')
    
@app.route('/')
def home():
    ir_center = GPIO.input(IR_center)
    ir_right = GPIO.input(IR_right)
    ir_left = GPIO.input(IR_left)
    return render_template('Motor_Final.html',ir_center=ir_center, ir_left=ir_left, ir_right=ir_right)

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
        

if __name__ == '__main__':
    app.run()