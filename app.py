#!/usr/bin/env python
from importlib import import_module
import os
from flask import Flask, render_template, Response
from flask_socketio import SocketIO
import time
from lane_object_detection import Camera
from cameraOff import CameraOff
from carControl1 import CarControls

#Global Actions
showCamera = True
laneDetection = True
objectDetection = True

Stop = False
blowHornTime = time.time()
goStright = False
noHorn = False
keepLeftTime = False
uTurnActive = False

carControls = CarControls()
app = Flask(__name__)
stearingAngle = 0
app.config['SECRET_KEY'] = 'Mritunjay'
socketio = SocketIO(app)


#Sign handler
def handelSign(obj):
    global Stop
    global goStright
    global noHorn
    global keepLeftTime
    global blowHornTime
    global uTurnActive

    if 'blow-horn' in obj:
        if time.time() - blowHornTime > 10:
            carControls.blowHorn()
            blowHornTime = time.time()
    if 'keep-left' in obj:
        if time.time() - keepLeftTime > 10:
            carControls.left()
            time.sleep(0.3)
            carControls.right()
            keepLeftTime = time.time()
    if 'stop' in obj:
        Stop = True 
    else:
        Stop = False   
    if 'no-horn' in obj:
        noHorn = True
    else:
        noHorn=False
    if 'go-stright' in obj:
        carControls.goForward()
        goStright = True
    else:
        goStright = False
    if 'speed-50' in obj:
        carControls.speed50 = True
    else:
        carControls.speed50 = False
    
    if 'u-turn' in obj:
        if not uTurnActive:
            uTurnActive = True
            socketio.emit('u-turn')
            carControls.uTurn()
            uTurnActive = False

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
        if showCamera:
            dummy, stearingAngle,objects = camera.get_frame(laneDetection,objectDetection)
            if objectDetection:
                handelSign(objects)
            if laneDetection:
                carControls.stablizeTurn(stearingAngle)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + dummy + b'\r\n')
        else:
            frame = cameraOff.get_frame()
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
    if Stop:
        return
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
    if goStright:
        return
    global carControls
    carControls.stop()
    return ("breaks applied")

#horn function
@app.route('/horn')
def horn():
    if noHorn:
        return
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
    socketio.emit('ultrasonic', {"front": "112",'back':"112"})
    #socketio.emit('ultrasonic', {
    #              "front": carControls.distanceFront(), 'back': carControls.distanceBack()})


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True)
