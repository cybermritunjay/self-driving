function lower() {
    document.getElementById("joystick-svg").style.backgroundImage = `url('{{ url_for('static', filename="img/joystick/Analog_Joystick_down.jpg") }} ')`;
    fetch(window.location.href + 'backward').then((data) => {
        console.log(data)
        document.getElementById("joystick-svg").style.backgroundImage = `url('{{ url_for('static', filename="img/joystick/Analog_Joystick.jpg") }} ')` 
    })
}
function upper() {
    document.getElementById("joystick-svg").style.backgroundImage = `url('{{ url_for('static', filename="img/joystick/Analog_Joystick_top.jpg") }} ')`;
    fetch(window.location.href + 'forward').then((data) => {
        console.log(data);
        document.getElementById("joystick-svg").style.backgroundImage = `url('{{ url_for('static', filename="img/joystick/Analog_Joystick.jpg") }} ')` 
    })
}
function left() {   
    document.getElementById("joystick-svg").style.backgroundImage = `url('{{ url_for('static', filename="img/joystick/Analog_Joystick_left.jpg") }} ')`;
    fetch(window.location.href + 'left-turn').then((data) => {
        document.getElementById("joystick-svg").style.backgroundImage = `url('{{ url_for('static', filename="img/joystick/Analog_Joystick.jpg") }} ')`     })
}
function right() {
    document.getElementById("joystick-svg").style.backgroundImage = `url('{{ url_for('static', filename="img/joystick/Analog_Joystick_right.jpg") }} ')`;
    fetch(window.location.href + 'right-turn').then((data) => {
        console.log(data);
        document.getElementById("joystick-svg").style.backgroundImage = `url('{{ url_for('static', filename="img/joystick/Analog_Joystick.jpg") }} ')` 
    })
}
function breaks() {
    fetch(window.location.href + 'break').then((data) => {
        console.log(data);
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