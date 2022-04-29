#for motor
import flask
from flask import Flask, render_template
import RPi.GPIO as GPIO
from time import sleep

#for camera
import io
import picamera
import logging
import socketserver
from threading import Condition
from http import server

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


PAGE="""\
<html>
<head>
<title>Raspberry Pi - Surveillance Camera</title>
</head>
<body>
<center><h1>Raspberry Pi - Surveillance Camera</h1></center>
<center><img src="stream.mjpg" width="640" height="480"></center>
</body>
</html>
"""

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
    output = StreamingOutput()
    #Uncomment the next line to change your Pi's Camera rotation (in degrees)
    camera.rotation = 180
    camera.start_recording(output, format='mjpeg')
    try:
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    finally:
        camera.stop_recording()

if __name__ == '__main__':
    app.run()