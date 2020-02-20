#!/usr/bin/env python
from importlib import import_module
import os
from flask import Flask, render_template, Response
from camera_opencv import Camera
from camera import CameraOff
from carControl1 import CarControls

#Global Actions
showCamera = True
carControls = CarControls()
app = Flask(__name__)

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
@app.route('/left-turnn')
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
@app.route('/breaks')
def breaks():
    global carControls
    carControls.breaks()
    return ("breaks applied")

@app.route('/exit')
def exit():
    global carControls
    carControls.clean()
    return ("cleaned")

if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
