#!/usr/bin/env python
from importlib import import_module
import os
from flask import Flask, render_template, Response
from flask_socketio import SocketIO
import time
from camera_opencv import Camera
from camera import CameraOff
from carControl1 import CarControls

#Global Actions
showCamera = True
laneDetection = True
objectDetection = True
carControls = CarControls()
app = Flask(__name__)
stearingAngle = 0
app.config['SECRET_KEY'] = 'Mritunjay'
socketio = SocketIO(app)


#Main Route
@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')

#Streaming Route
def gen(cameraOff, camera):
    """Video streaming generator function."""
    global stearingAngle

    while True:
        frame = cameraOff.get_frame()
        dummy, stearingAngle = camera.get_frame(False,False)
        if showCamera:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + dummy + b'\r\n')
        else:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

#Video Route
@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(CameraOff(), Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


#Action Functoins
#toggle Camera
@app.route('/toggleCamera')
def toggleCamera():
    global showCamera
    if showCamera:
        showCamera = False
    else:
        showCamera = True
    return ("Camera is", showCamera)

#toggle Auto Piolet
@app.route('/toggleAutoPiolet')
def toggleAutoPiolet():
    global laneDetection
    if laneDetection:
        laneDetection = False
    else:
        laneDetection = True
    return ("Camera is", laneDetection)


#Toggle Sign Detection
@app.route('/toggleSignDetection')
def toggleSignDetection():
    global objectDetection
    if objectDetection:
        objectDetection = False
    else:
        objectDetection = True
    return ("Camera is", objectDetection)

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
    carControls.goForward()
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

#horn function
@app.route('/horn')
def horn():
    global carControls
    carControls.blowHorn()
    return ("horn")

#lights function
@app.route('/lights')
def lights():
    global carControls
    carControls.lights()
    return ("lights")

#Exit Function
@app.route('/exit')
def exit():
    global carControls
    carControls.clean()
    return ("cleaned")

#connect Socket Route
@socketio.on('connect')
def connect_handler():
    print("connected")
    time.sleep(1)
    socketio.emit('ultrasonic', {"val": "connection Started"})

#repeated ultrasonic Check Route
@socketio.on('ultrasonic')
def ultrasonic_handler():
    global carControls
    time.sleep(1)
    #socketio.emit('ultrasonic', {"front": "112",'back':"112"})
    #if autoPiolet:
    #    carControls.stablizeTurn(stearingAngle)
    socketio.emit('ultrasonic', {
                  "front": carControls.distanceFront(), 'back': carControls.distanceBack()})


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True)
