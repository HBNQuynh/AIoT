from flask import Flask, render_template
import threading
import serial
import queue
import time

app = Flask(__name__, template_folder='.')

cmd_queue = queue.Queue()


@app.route('/')
def hello_world():
    return render_template('dashboard.html', data=data)


@app.route('/auto')
def auto():
    return 'Current data=' + str(data)


@app.route('/turn_on_off')
def turn_on_off():
    global led_status

    if led_status == 'OFF':
        cmd_queue.put('1')
        led_status = 'ON'
    else:
        cmd_queue.put('0')
        led_status = 'OFF'


@app.route('/led_status')
def update_led_status():
    return 'Led is ' + led_status


def readingThread(ser):
    global is_stopping
    global data
    global led_status

    while not is_stopping:
        line = ser.readline().strip()
        if line == b'ON':
            led_status = 'ON'
        elif line == b'OFF':
            led_status = 'OFF'
        elif line == b'BLINK':
            led_status = 'BLINKING'
        else:
            update_data(line)

def controlThread(ser):
    global is_stopping

    while not is_stopping:
        if cmd_queue.empty():
            time.sleep(1)
        else:
            cmd = cmd_queue.get()
            print(cmd)
            ser.write(cmd.encode())



def update_data(s):
    global data
    try:
        data = float(s)
        return True
    except ValueError:
        return False


if __name__ == "__main__":
    global is_stopping
    is_stopping = False
    global data
    data = 0
    h_serial  = serial.Serial('COM8', 9600, timeout=1)

    h_reading_thread = threading.Thread(target=readingThread, args=(h_serial,))
    h_reading_thread.start()

    h_control_thread = threading.Thread(target=controlThread, args=(h_serial,))
    h_control_thread.start()

    app.run()

    
    is_stopping = True
    h_reading_thread.join()
    h_control_thread.join()

    h_serial.close()
    print("APP IS CLOSED\n")