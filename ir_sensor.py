import flask
from flask import Flask, render_template, jsonify
import RPi.GPIO as GPIO
from time import sleep

ir = 18
led = 4

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(ir, GPIO.IN)
GPIO.setup(led, GPIO.OUT)
GPIO.output(led,0)

app = Flask(__name__, template_folder='template')

@app.route('/')
def home():
    return render_template('ir_sensor.html')

@app.route('/update')
def update():
    data = GPIO.input(ir)
    if data == 0:
        GPIO.output(led, 1)
    else:
        GPIO.output(led, 0)
    templateData = {'data' : data}
    return jsonify(templateData), 200

if __name__ == '__main__':
    app.run()