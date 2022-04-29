import flask
from flask import Flask, render_template, jsonify
import RPi.GPIO as GPIO
from time import sleep

ir_left = 2
ir_center = 3
ir_right = 4
buzz = 17

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(ir_left, GPIO.IN)
GPIO.setup(ir_center, GPIO.IN)
GPIO.setup(ir_right, GPIO.IN)
GPIO.setup(buzz, GPIO.OUT)
GPIO.output(buzz,0)

app = Flask(__name__, template_folder='template')

@app.route('/')
def home():
    return render_template('ir_sensor.html')

@app.route('/update')
def update():
    data_1 = GPIO.input(ir_left)
    data_2 = GPIO.input(ir_center)
    data_3 = GPIO.input(ir_right)
    if data_1 == 0:
        GPIO.output(buzz, 1)
    elif data_2 == 0:
        GPIO.output(buzz, 1)
    elif data_3 == 0:
        GPIO.output(buzz, 1)
    elif data_1 == 1:
        GPIO.output(buzz, 0)
    elif data_2 == 1:
        GPIO.output(buzz, 0)
    elif data_3 == 1:
        GPIO.output(buzz, 0)
    templateData = {'data1' : data_1, 'data2' : data_2, 'data3' : data_3}
    return jsonify(templateData), 200

if __name__ == '__main__':
    app.run()