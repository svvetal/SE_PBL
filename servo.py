import flask
from flask import Flask, render_template, request
import RPi.GPIO as GPIO
from time import sleep

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

servo = 26

GPIO.setup(servo, GPIO.OUT)

p = GPIO.PWM(servo, 50)

p.start(0)

app = Flask(__name__, template_folder = 'template')

@app.route('/')
def home():
    return render_template('servo.html')

@app.route('/set_speed')
def set_speed():
    speed = request.args.get("speed")
    p.ChangeDutyCycle(int(speed))
    return render_template('servo.html')

if __name__ == '__main__':
    app.run()
