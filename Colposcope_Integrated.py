from flask import Flask, render_template, request, url_for, Response
from pyA20.gpio import gpio
from pyA20.gpio import port
from time import sleep
from orangepwm import *
import numpy
import cv2
import time
import threading

app = Flask(__name__)

camera = cv2.VideoCapture(0)
gpio.init()

# Set GPIO pin PA6 as PWM output with a frequency of 100 Hz
gpio.setcfg(port.PG6, gpio.OUTPUT)
gpio.setcfg(port.PG7, gpio.OUTPUT)
pwm = OrangePwm(1000, port.PA6)
gpio.output(port.PG6, gpio.LOW)
gpio.output(port.PG7, gpio.LOW)
pwm.start(0)
#camera.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
#camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)

pwm_cahaya = {'LED1' : '0', 'LED2' : '0', 'LED3' : '0', 'LED4' : '0'}
Tombol = {'Capture': 'False', 'Adapt' : 'False'}
font = cv2.FONT_HERSHEY_SIMPLEX

def take_frame():
    prev_frame_time = 0
    new_frame_time = 0
    count = 0
    fps_integral = 0
    while True:
        success, frame = camera.read()
        new_frame_time = time.time()
        fps = 1 / (new_frame_time - prev_frame_time)
        prev_frame_time = new_frame_time
        fps = int(fps)
        fps_integral = fps_integral + fps
        count = count + 1
        fps_mean = int(fps_integral / count)
        cv2.putText(frame, str(fps_mean), (7, 70), font, 3, (100, 255, 0), 3, cv2.LINE_AA)
        #frame = cv2.resize(frame, (224,224), interpolation = cv2.INTER_AREA)
        if success:
            if Tombol['Capture']=='True':
                Tombol['Capture']='False'
                cv2.imwrite('static/tersimpan.jpg', frame)
            try:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            except Exception as e:
                pass
        else:
            pass

def board_pencahayaan():
    while True:
       led_1.duty_cycle = 20000
       led_2.duty_cycle = 20000
       led_3.duty_cycle = 20000
       led_4.duty_cycle = 20000


@app.route('/tes')
def tes():
    return "Halo"

@app.route('/video_feed')
def video_feed():
    return Response(take_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_pantulan')
def get_pantulan():
    gambar_raw = cv2.imread(img)
    tinggi, lebar, d = gambar_raw
    count_pantulan_Q1 = 0
    count_pantulan_Q2 = 0
    count_pantulan_Q3 = 0
    count_pantulan_Q4 = 0
    for i in range(tinggi/2):
        for j in range(lebar/2):
            a, b, c = image[i, j]
            if a >= 229 and b >= 229 and c >= 229:
                # Menghitung Jumlah pixel yang merupakan pantulan cahaya
                count_pantulan_Q1 = count_pantulan_Q1 + 1
        for j in range(lebar/2, lebar):
            a, b, c = image[i, j]
            if a >= 229 and b >= 229 and c >= 229:
                count_pantulan_Q2 = count_pantulan_Q2 + 1
    for i in range(tinggi/2, tinggi):
        for j in range(lebar/2):
            a, b, c = image[i, j]
            if a >= 229 and b >= 229 and c >= 229:
                # Menghitung Jumlah pixel yang merupakan pantulan cahaya
                count_pantulan_Q3 = count_pantulan_Q3 + 1
        for j in range(lebar/2, lebar):
            a, b, c = image[i, j]
            if a >= 229 and b >= 229 and c >= 229:
                count_pantulan_Q4 = count_pantulan_Q4 + 1

@app.route('/adapt_cahaya')
def adapt_cahaya():
    if pantulan_Q1>0.01:
        pwm_cahaya['LED1'] = cari_intensitas(pantulan_Q1)
    elif pantulan_Q2>0.01:
        pwm_cahaya['LED2'] = cari_intensitas(pantulan_Q2)
    elif pantulan_Q3>0.01:
        pwm_cahaya['LED3'] = cari_intensitas(pantulan_Q3)
    elif pantulan_Q3>0.01:
        pwm_cahaya['LED4'] = cari_intensitas(pantulan_Q4)


@app.route('/simpan', methods=('POST', 'GET'))
def simpan():
    if request.method == 'POST':
        Tombol['Capture'] = request.form['tombol_state']
    return Tombol['Capture']

@app.route('/atur_cahaya')
def atur_cahaya():
    return pwm_cahaya

@app.route('/atur_cahaya/LED1', methods=('POST', 'GET'))
def atur_cahaya_LED1():
    if request.method =='POST':
        PWM_LED1 = request.form['LED1']
        pwm_cahaya['LED1'] = PWM_LED1
    return pwm_cahaya['LED1']

@app.route('/atur_cahaya/LED2', methods=('POST', 'GET'))
def atur_cahaya_LED2():
    if request.method =='POST':
        PWM_LED2 = request.form['LED2']
        pwm_cahaya['LED2'] = PWM_LED2
    return pwm_cahaya['LED2']

@app.route('/atur_cahaya/LED3', methods=('POST', 'GET'))
def atur_cahaya_LED3():
    if request.method =='POST':
        PWM_LED3 = request.form['LED3']
        pwm_cahaya['LED3'] = PWM_LED3
    return pwm_cahaya['LED3']

@app.route('/atur_cahaya/LED4', methods=('POST', 'GET'))
def atur_cahaya_LED4():
    if request.method =='POST':
        PWM_LED4 = request.form['LED4']
        pwm_cahaya['LED4'] = PWM_LED4
    return pwm_cahaya['LED4']

if __name__ == '__main__':
    app.run(host='0.0.0.0')
    threading.Thread(target=board_pencahayaan).start()