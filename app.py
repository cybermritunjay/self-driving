#!/usr/bin/env python
from importlib import import_module
import os
from flask import Flask, render_template, Response
from flask_socketio import SocketIO
import time
from camera_opencv import Camera
from camera import CameraOff
#from carControl1 import CarControls

#Global Actions
showCamera = True
#carControls = CarControls()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'Mritunjay'
socketio = SocketIO(app)
sensorValue=90

#Action Functoins
@app.route('/toggleCamera')
def toggleCamera():
    global showCamera
    if showCamera:
        showCamera = False
    else:
        showCamera = True
    return ("Camera is", showCamera)


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


def gen(cameraOff, camera):
    """Video streaming generator function."""
    while True:
        frame = cameraOff.get_frame()
        dummy = camera.get_frame()
        if showCamera:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + dummy + b'\r\n')
        else:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(CameraOff(), Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

#left Functoins
@app.route('/left-turn')
def leftTurn():
    global carControls
    carControls.left()
    return ("Left Turn Taken")
#right Functoins
@app.route('/right-turn')
def rightTurn():
    global carControls
    carControls.right()
    return ("right Turn Taken")

#forward Functoins
@app.route('/forward')
def forward():
    global carControls
    carControls.forward()
    return ("go forward")
#backward Functoins
@app.route('/backward')
def backward():
    global carControls
    carControls.reverse()
    return ("go backwards")
#break Functoins
@app.route('/stop')
def stop():
    global carControls
    carControls.stop()
    return ("breaks applied")

@app.route('/exit')
def exit():
    global carControls
    carControls.clean()
    return ("cleaned")


@socketio.on('connect')
def connect_handler():
    print("connected")
    time.sleep(1)
    socketio.emit('ultrasonic', {"val": "connection Started"})
@socketio.on('ultrasonic')
def ultrasonic_handler():
    global sensorValue
    time.sleep(1)
    sensorValue +=1
    socketio.emit('ultrasonic', {"val": sensorValue})


if __name__ == '__main__':
    socketio.run(app,host='0.0.0.0', debug=True)
