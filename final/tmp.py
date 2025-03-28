import threading
import serial
import queue
import time
import panel as pn
import atexit
import signal
import json
import os
from datetime import datetime

pn.extension()

# ==========================
# 1. Biến toàn cục
# ==========================
data_lock = threading.Lock()  # Khóa đồng bộ
data = 0.0  # Giá trị cảm biến ánh sáng
led_status = 'OFF'  # Trạng thái đèn LED
is_stopping = False  # Cờ dừng luồng
h_serial = None  # Đối tượng serial
h_reading_thread = None
h_control_thread = None

cmd_queue = queue.Queue()

# ==========================
# 2. Giao diện Panel
# ==========================
sensor_view = pn.indicators.Number(
    name="Cảm biến ánh sáng", 
    value=data, 
    colors=[(50, "green"), (2000, "red")]
)

led_status_view = pn.widgets.StaticText(
    name="Trạng thái LED", 
    value=led_status, 
    styles={"font-size": "20px", "color": "white"}
)

toggle_led_button = pn.widgets.Button(
    name="Bật/Tắt LED", 
    button_type="success",
    styles={"width": "200px", "height": "50px"}
)

def update_ui():
    global data, led_status
    with data_lock:
        sensor_view.value = data
        led_status_view.value = led_status
    print(f"Cập nhật giao diện: data={data}, led_status={led_status}")

def toggle_led(event):
    global led_status
    with data_lock:
        if led_status == 'OFF':
            cmd_queue.put('1')
            led_status = 'ON'
        else:
            cmd_queue.put('0')
            led_status = 'OFF'
    update_ui()

toggle_led_button.on_click(toggle_led)

# ==========================
# 3. Serial Communication
# ==========================
def reading_thread(ser):
    global data, led_status, is_stopping
    while not is_stopping:
        try:
            if ser and ser.is_open:
                line = ser.readline().strip()
                with data_lock:
                    if line == b'ON':
                        led_status = 'ON'
                    elif line == b'OFF':
                        led_status = 'OFF'
                    elif line == b'BLINK':
                        led_status = 'BLINKING'
                    else:
                        try:
                            data = float(line)
                        except ValueError:
                            pass
        except Exception as e:
            print(f"Lỗi trong readingThread: {e}")

def control_thread(ser):
    global is_stopping
    while not is_stopping:
        try:
            if ser and ser.is_open:
                if not cmd_queue.empty():
                    cmd = cmd_queue.get()
                    ser.write(cmd.encode())
            else:
                time.sleep(0.5)
        except Exception as e:
            print(f"Lỗi trong controlThread: {e}")

def initialize_serial():
    global h_serial
    try:
        if h_serial and h_serial.is_open:
            h_serial.close()
        h_serial = serial.Serial('COM7', 115200, timeout=1)
    except Exception as e:
        print(f"Lỗi khi khởi tạo cổng COM: {e}")
        h_serial = None

# ==========================
# 4. Dọn dẹp và khởi tạo
# ==========================
def reset_state():
    global h_serial, h_reading_thread, h_control_thread, is_stopping
    is_stopping = False
    initialize_serial()
    if h_serial:
        h_reading_thread = threading.Thread(target=reading_thread, args=(h_serial,))
        h_control_thread = threading.Thread(target=control_thread, args=(h_serial,))
        h_reading_thread.start()
        h_control_thread.start()

def cleanup():
    global is_stopping, h_serial
    print("Đang tắt hệ thống...")
    is_stopping = True
    if h_serial and h_serial.is_open:
        h_serial.close()
    print("Hệ thống đã tắt.")

atexit.register(cleanup)

signal.signal(signal.SIGINT, lambda sig, frame: cleanup() or exit(0))

# ==========================
# 5. Giao diện chính
# ==========================
dashboard = pn.template.FastListTemplate(
    title="Light Sensor Dashboard",
    main=[
        pn.Row(sensor_view, 
               pn.Column(led_status_view, toggle_led_button))
    ],
    theme="dark",
    theme_toggle=False
)

pn.state.add_periodic_callback(update_ui, period=1000)
dashboard.servable()
reset_state()
