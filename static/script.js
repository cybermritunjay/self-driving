function showCover(){
    document.getElementById('page-cover').style.display = 'block'
}
function hideCover(){
    document.getElementById('page-cover').style.display ='none'
}
function lower() {
    showCover()
    document.getElementById("joystick-svg").style.backgroundImage = `url('{{ url_for('static', filename="img/joystick/Analog_Joystick_down.jpg") }} ')`;
    fetch(window.location.href + 'backward').then((data) => {
        console.log(data)
        document.getElementById("joystick-svg").style.backgroundImage = `url('{{ url_for('static', filename="img/joystick/Analog_Joystick.jpg") }} ')` 
    hideCover()
    })
}
function upper() {
    showCover()
    document.getElementById("joystick-svg").style.backgroundImage = `url('{{ url_for('static', filename="img/joystick/Analog_Joystick_top.jpg") }} ')`;
    fetch(window.location.href + 'forward').then((data) => {
        console.log(data);
        document.getElementById("joystick-svg").style.backgroundImage = `url('{{ url_for('static', filename="img/joystick/Analog_Joystick.jpg") }} ')` 
    hideCover()
    })
}
function left() { 
    showCover()  
    document.getElementById("joystick-svg").style.backgroundImage = `url('{{ url_for('static', filename="img/joystick/Analog_Joystick_left.jpg") }} ')`;
    fetch(window.location.href + 'left-turn').then((data) => {
        document.getElementById("joystick-svg").style.backgroundImage = `url('{{ url_for('static', filename="img/joystick/Analog_Joystick.jpg") }} ')`     
    hideCover()
    })
}
function right() {
    showCover()
    document.getElementById("joystick-svg").style.backgroundImage = `url('{{ url_for('static', filename="img/joystick/Analog_Joystick_right.jpg") }} ')`;
    fetch(window.location.href + 'right-turn').then((data) => {
        console.log(data);
        document.getElementById("joystick-svg").style.backgroundImage = `url('{{ url_for('static', filename="img/joystick/Analog_Joystick.jpg") }} ')` 
    hideCover()
    })
}
function stop() {
    showCover()
    fetch(window.location.href + 'stop').then((data) => {
        console.log(data);
    hideCover()
    })
}
function cameraVisionHandler() {
    document.getElementById("camera-vision").classList.toggle("function-inactive")
    document.getElementById("camera-vision").classList.toggle("function-active")
    fetch(window.location.href + 'toggleCamera').then((data) => {
        console.log(data);
        
    })
}
function turnOffCar() {
    showCover()
    fetch(window.location.href + 'exit').then((data) => {
        console.log(data);
    })
}
function autoPioletHandler() {
    document.getElementById("auto-piolet").classList.toggle("function-inactive")
    document.getElementById("auto-piolet").classList.toggle("function-active")
}
function signHandler() {
    document.getElementById("sign-detection").classList.toggle("function-inactive")
    document.getElementById("sign-detection").classList.toggle("function-active")
}


var socket = io();
    socket.on('connect', function() {
       console.log("Connection Established")
    });
    socket.on( 'ultrasonic', function(distance) {
        document.getElementById('distance-box').innerHTML = '<p style="color:#fff" >Distance from front:'+distance.front+'</p><br/><p style="color:#fff" >Distance from back:'+distance.back+'</p>'
        socket.emit('ultrasonic')
    })