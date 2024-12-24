import threading
import serial
import queue
import time
import panel as pn
import atexit
import asyncio
from openai import OpenAI
import json


pn.extension()
client = OpenAI()
#python -m panel serve web.py

# Biến toàn cục
global data 
data = 0.0  # Lưu giá trị cảm biến ánh sáng
global led_status
led_status = 'OFF'
global is_stopping
is_stopping = False
global h_serial
h_serial = None
global h_reading_thread
h_reading_thread = None

cmd_queue = queue.Queue()

# Giao diện Panel
sensor_view = pn.indicators.Number(
    name="Cảm biến ánh sáng", 
    value=data, 
    format="{value} lux", 
    colors=[(50, "green"), (300, "red")]
)

led_status_view = pn.widgets.StaticText(
    name="Trạng thái LED", 
    value=led_status, 
    styles={"font-size": "20px", "colors": "white"}
)

# Nút điều khiển LED
toggle_led_button = pn.widgets.Button(
    name="Bật/Tắt LED", 
    button_type="success",
    styles={"width" : "200px", "height": "50px"}
)

# Hàm cập nhật giao diện
def update_ui():
    sensor_view.value = data
    led_status_view.value = led_status

# Hàm bật/tắt đèn trên web
def toggle_led(event):
    global led_status

    if led_status == 'OFF':
        cmd_queue.put('1')  # Gửi lệnh bật LED
        led_status = 'ON'
    else:
        cmd_queue.put('0')  # Gửi lệnh tắt LED
        led_status = 'OFF'
    update_ui()

toggle_led_button.on_click(toggle_led)


# Hàm tắt đèn
def turn_off_light():
    global led_status

    cmd_queue.put('0')  # Gửi lệnh tắt LED
    led_status = 'OFF'
    update_ui()

    return "Đèn đã được tắt."

# Hàm bật đèn
def turn_on_light():
    global led_status

    cmd_queue.put('1')  # Gửi lệnh bật LED
    led_status = 'ON'
    update_ui()

    return "Đèn đã được bật."

# Hàm trả về trạng thái của đèn
def get_led_status():
    global led_status

    if led_status == 'ON':
        return "Đèn đang bật"
    elif led_status == 'OFF':
        return "Đèn đang tắt"
    elif led_status == 'BLINKING':
        return "Đèn đang nhấp nháy"
    else:
        return "Không xác định được trạng thái đèn"

# Xử lý Function Calling với GPT
def chat_with_gpt(user_input):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Bạn là một trợ lý AI giúp điều khiển đèn LED IoT. Bạn có thể bật, tắt và kiểm tra trạng thái đèn LED."},
            {"role": "user", "content": user_input}
        ],
        functions=[
            {
                "name": "turn_on_light",
                "description": "Bật đèn LED."
            },
            {
                "name": "turn_off_light",
                "description": "Tắt đèn LED."
            },
            {
                "name": "get_led_status",
                "description": "Lấy trạng thái hiện tại của đèn LED."
            }
        ],
        function_call="auto"
    )
    
    response_message = response.choices[0].message
    
    if response_message.function_call:
        function_name = response_message.function_call.name
        
        if function_name == "turn_on_light":
            return turn_on_light()
        
        if function_name == "turn_off_light":
            return turn_off_light()
        
        if function_name == "get_led_status":
            return get_led_status()
    
    else:
        return response_message.content
    

# ==========================
# 1️⃣ Cấu hình Chatbot
# ==========================
async def get_response(contents, user, instance):
    response = chat_with_gpt(contents)

    for i in range(len(response)):
        yield response[:i+1]
        await asyncio.sleep(0.03)

    # Kích hoạt Text-to-Speech khi chatbot hoàn thành phản hồi
    text_to_speech.value = response
    text_to_speech.speak = True


# Khởi tạo Chat Interface
chat_bot = pn.chat.ChatInterface(
    callback=get_response, 
    max_height=800,
    show_clear = False
    )

chat_bot.send("Ask me what a wind turbine is", user="Assistant", respond=False)

# ==========================
# 2️⃣ Cấu hình Speech-to-Text
# ==========================
# Widget chọn ngôn ngữ
language_selector = pn.widgets.Select(
    name='Chọn ngôn ngữ', 
    options={'Tiếng Việt': 'vi-VN', 'English': 'en-US'}, 
    value='en-US'
)

# Widget Speech-to-Text
speech_to_text = pn.widgets.SpeechToText(button_type="light", height=50, lang=language_selector.value)

# Widget text to speech
text_to_speech = pn.widgets.TextToSpeech(name="Voicebot", auto_speak=False)

# Hàm cập nhật ngôn ngữ cho Speech-to-Text và Text-to-Speech
def update_language(event):
    speech_to_text.lang = event.new
    text_to_speech.lang = event.new
    print(text_to_speech.lang)

language_selector.param.watch(update_language, 'value')

# Xử lý kết quả từ Speech-to-Text và gửi đến ChatBot
def handle_speech_results(results):
    if speech_to_text.results:
        text = speech_to_text.results[0]['alternatives'][0]['transcript']
        user_input = str(text)
        chat_bot.send(user_input, user="User", respond=True)
    else:
        return pn.pane.Str("Không có kết quả từ giọng nói.", width=200, height=100)


# Thread
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


# Hàm khởi tạo cổng COM
def initialize_serial():
    global h_serial
    if h_serial and h_serial.is_open:
        h_serial.close()
    try:
        h_serial = serial.Serial('COM8', 9600, timeout=1)
    except serial.SerialException as e:
        print(f"Lỗi khi khởi tạo cổng COM: {e}")
        h_serial = None

# Hàm dọn dẹp tài nguyên khi thoát
def cleanup():
    global is_stopping
    print("\nĐang tắt hệ thống...")
    is_stopping = True
    if h_serial and h_serial.is_open:
        h_serial.close()
    if h_reading_thread.is_alive():
        h_reading_thread.join()
    if h_control_thread.is_alive():
        h_control_thread.join()
    print("Hệ thống đã tắt.")

# Đăng ký cleanup khi thoát
atexit.register(cleanup)

# Khởi tạo cổng COM
initialize_serial()

# Tạo và chạy các luồng
h_reading_thread = threading.Thread(target=readingThread, args=(h_serial,))
h_control_thread = threading.Thread(target=controlThread, args=(h_serial,))
h_reading_thread.start()
h_control_thread.start()

# Tạo layout với Panel
dashboard = pn.template.FastListTemplate(
    title='Light Sensor Dashboard', 
    # sidebar= pn.Column(
    #     "## 🗣️ **Speech-to-Text: Tiếng Anh và Tiếng Việt**",
    #     language_selector,
    #     speech_to_text,
    #     pn.bind(handle_speech_results, speech_to_text)
    # ),
    main=[pn.Row(sensor_view, 
                 pn.Column(led_status_view, toggle_led_button)),
          pn.Row(
            pn.Column(
                "## 🗣️ **Speech-to-Text: Tiếng Anh và Tiếng Việt**",
                language_selector,
                speech_to_text,
                pn.bind(handle_speech_results, speech_to_text)
            ),
            pn.Column(
                chat_bot,
                text_to_speech
            ))],

    theme="dark",
    theme_toggle=False,
    background_color="#2c2828",
    accent="#00A170"
)

# Thêm callback cập nhật mỗi 1 giây
pn.state.add_periodic_callback(update_ui, period=1000)  # 1000 ms = 1 giây

# Chạy ứng dụng Panel
dashboard.servable()