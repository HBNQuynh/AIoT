import threading
import serial
import queue
import time
import panel as pn
import atexit
import asyncio
from openai import OpenAI
import json
import os
from datetime import datetime #lấy thời gian thực
import signal


# Khởi tạo các thành phần của Panel
pn.extension()
client = OpenAI()


# ==========================
# Cấu hình lưu trữ
# ==========================
CHAT_HISTORY_FILE = "chat_history.json"

# Hàm lưu lịch sử hội thoại vào tệp JSON
def save_chat_histories():
    with open(CHAT_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(chat_histories, f, ensure_ascii=False, indent=4)

# Hàm tải lịch sử hội thoại từ tệp JSON
def load_chat_histories():
    if os.path.exists(CHAT_HISTORY_FILE):
        with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# Khởi tạo lịch sử hội thoại
chat_histories = load_chat_histories()
current_chat_id = list(chat_histories.keys())[0] if chat_histories else "Chat 1"
if not chat_histories:
    chat_histories[current_chat_id] = []

# Hàm đổi tên chat_id trong lịch sử hội thoại
def rename_chat_id(old_id, new_id):
    if old_id in chat_histories and new_id not in chat_histories:
        chat_histories[new_id] = chat_histories.pop(old_id)
        save_chat_histories()


# ==========================
# Biến toàn cục
# ==========================
global data, led_status, is_stopping, h_serial, h_reading_thread, h_control_thread
data = 0.0  # Lưu giá trị cảm biến ánh sáng
led_status = 'OFF'
is_stopping = False
h_serial = None
h_reading_thread = None
h_control_thread = None

cmd_queue = queue.Queue()


# ==========================
# Giao diện và logic UI
# ==========================
sensor_view = pn.indicators.Number(
    name="Cảm biến ánh sáng", 
    value=data, 
    colors=[(1000, "green"), (2000, "red")],
    css_classes=["view"]
)

led_status_view = pn.widgets.StaticText(
    name="Trạng thái LED", 
    value=led_status, 
    css_classes=["view"]
)

# Nút điều khiển LED
toggle_led_button = pn.widgets.Button(
    name="Bật/Tắt LED", 
    button_type="success",
    styles={'width': '200px', 'height': '50px'}
)

# Hàm cập nhật giao diện
def update_ui():
    sensor_view.value = data
    led_status_view.value = led_status
    print(f"Cập nhật giao diện: data={data}, led_status={led_status}")

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

# ==================================
# Xử lý Function Calling với GPT
# ==================================
def chat_with_gpt(user_input):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Bạn là một trợ lý AI giúp điều khiển đèn LED IoT. Bạn có thể bật, tắt và kiểm tra trạng thái đèn LED. Nếu trời sáng quá, hãy tắt đèn, còn nếu trời tối, hãy bật đèn lên nhé!"},
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
    
    return response.choices[0].message
    
def handle_response(response_message):
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
# Cấu hình Chatbot
# ==========================
async def get_response(contents, user, instance):
    global current_chat_id

    # Đổi tên chat_id cho dễ phân biệt các đoạn chat
    if "Chat" in current_chat_id and current_chat_id != contents: 
        rename_chat_id(current_chat_id, contents)
        current_chat_id = contents

    response_msg = chat_with_gpt(contents)
    response = handle_response(response_msg)

    for i in range(len(response)):
        yield response[:i+1]
        await asyncio.sleep(0.02)

    # Kích hoạt Text-to-Speech khi chatbot hoàn thành phản hồi
    text_to_speech.value = response
    text_to_speech.speak = True

    # Lưu đoạn chat vào lịch sử
    if current_chat_id not in chat_histories:
        chat_histories[current_chat_id] = []

    chat_histories[current_chat_id].append({
        "user": contents,
        "bot": response,
        "timestamp": datetime.now().isoformat()
    })

    # Lưu vào tệp JSON
    save_chat_histories()
    update_chat_list()


# Khởi tạo Chat Interface
chat_bot = pn.chat.ChatInterface(
    callback=get_response, 
    max_height=500,
    show_clear=False
)

# Tải nội dung hội thoại hiện tại
for msg in chat_histories[current_chat_id]:
    timestamp = datetime.fromisoformat(msg['timestamp']) if 'timestamp' in msg else datetime.now()
    chat_bot.send(msg['user'], user="User", respond=False, timestamp=timestamp)
    chat_bot.send(msg['bot'], user="Assistant", respond=False, timestamp=timestamp)

# ==========================
# Quản lý danh sách chat
# ==========================
chat_list = pn.widgets.Select(name="Danh sách đoạn chat", options=list(chat_histories.keys()), width=250)

def update_chat_list():
    """Cập nhật danh sách các cuộc hội thoại."""
    chat_list.options = list(chat_histories.keys())

def load_chat(event):
    """Tải một cuộc hội thoại từ danh sách."""
    global current_chat_id
    selected_chat = chat_list.value
    if selected_chat and selected_chat in chat_histories:
        current_chat_id = selected_chat
        chat_bot.clear()
        for msg in chat_histories[current_chat_id]:
            timestamp = datetime.fromisoformat(msg['timestamp']) if 'timestamp' in msg else datetime.now()
            chat_bot.send(msg['user'], user="User", respond=False, timestamp=timestamp)
            chat_bot.send(msg['bot'], user="Assistant", respond=False, timestamp=timestamp)



chat_list.param.watch(load_chat, 'value')

# Bắt đầu một cuộc hội thoại mới
def start_new_chat(event):
    global current_chat_id

    if chat_histories[current_chat_id] == []:
        return
    new_chat_id = f"Chat {len(chat_histories) + 1}"
    chat_histories[new_chat_id] = []
    current_chat_id = new_chat_id
    chat_bot.clear()
    update_chat_list()
    save_chat_histories()

# Nút bắt đoạn chat mới
new_chat_button = pn.widgets.Button(name="🆕 New chat", button_type="primary")
new_chat_button.on_click(start_new_chat)

# Hàm xóa đoạn chat hiện tại
def delete_current_chat(event):
    global current_chat_id
    if current_chat_id in chat_histories:
        del chat_histories[current_chat_id]
        save_chat_histories()
        current_chat_id = list(chat_histories.keys())[0] if chat_histories else "Chat 1"
        if not chat_histories:
            chat_histories[current_chat_id] = []
        chat_bot.clear()
        update_chat_list()

# Nút xóa đoạn chat hiện tại
delete_chat_button = pn.widgets.Button(name="🗑️ Xóa đoạn chat hiện tại", button_type="danger")
delete_chat_button.on_click(delete_current_chat)


# ===========================================
# Cấu hình Speech-to-Text và Text-to-Speech
# ===========================================
# Widget chọn ngôn ngữ
language_selector = pn.widgets.Select(
    name='Chọn ngôn ngữ', 
    options={'Tiếng Việt': 'vi-VN', 'English': 'en-US'}, 
    value='en-US',
    width=200
)

# Widget Speech-to-Text
speech_to_text = pn.widgets.SpeechToText(button_type="light", height=50, lang=language_selector.value)

# Widget text to speech
text_to_speech = pn.widgets.TextToSpeech(name="Voicebot", auto_speak=False)

# Hàm cập nhật ngôn ngữ cho Speech-to-Text và Text-to-Speech
def update_language(event):
    speech_to_text.lang = event.new
    text_to_speech.lang = event.new

language_selector.param.watch(update_language, 'value')

# Xử lý kết quả từ Speech-to-Text và gửi đến ChatBot
def handle_speech_results(results):
    if speech_to_text.results:
        text = speech_to_text.results[0]['alternatives'][0]['transcript']
        user_input = str(text)
        chat_bot.send(user_input, user="User", respond=True)


# ==========================
# Cấu hình giao diện
# ==========================
sidebar = pn.Column(
    "## 💬 **ChatGPT-Like Interface**",
    language_selector, 
    speech_to_text,
    pn.bind(handle_speech_results, speech_to_text),
    chat_list,
    new_chat_button,
    delete_chat_button,
    width=300,
    height=500,
    css_classes=["sidebar"]
)


dashboard = pn.template.FastListTemplate(
    title='Smart Lighting System', 
    main=[pn.Row(sensor_view, 
                 pn.Column(led_status_view, toggle_led_button)),
          pn.Row(
            sidebar, 
            pn.Column(
                "## 🤖 **ChatBot**",
                chat_bot,
                text_to_speech
            )
          ),
         ],

    theme="dark",
    theme_toggle=False,
    background_color="#2c2828",
    accent="#00A170"
)

# Thêm CSS tùy chỉnh
theme_css = """
.sidebar {
    #background-color: #F9F9F9;
    padding: 10px;
    border-right: 1px solid #DDDDDD;
}

.view {
    font-size: 24px;
    text-align: center;
    padding: 20px;
    margin: 10px;
}
"""


# ==========================
# Serial và Threads
# ==========================
# Thread đọc dữ liệu từ cổng COM
def readingThread(ser):
    global is_stopping, data, led_status

    while not is_stopping:
        if ser and ser.is_open:
            try:
                line = ser.readline().strip()

                if line == b'ON':
                    led_status = 'ON'
                elif line == b'OFF':
                    led_status = 'OFF'
                elif line == b'BLINK':
                    led_status = 'BLINKING'
                else:
                    update_data(line)
            except Exception as e:
                print(f"Lỗi trong readingThread: {e}")

# Thread điều khiển cổng COM
def controlThread(ser):
    global is_stopping

    while not is_stopping:
        if ser and ser.is_open:
            try:
                if cmd_queue.empty():
                    time.sleep(1)
                else:
                    cmd = cmd_queue.get()
                    print(cmd)
                    ser.write(cmd.encode())
            except Exception as e:
                print(f"Lỗi trong controlThread: {e}")



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
        h_serial = serial.Serial('COM7', 115200, timeout=1)
    except serial.SerialException as e:
        print(f"Lỗi khi khởi tạo cổng COM: {e}")
        h_serial = None


# Hàm đặt lại trạng thái
def reset_state():
    global data, led_status, is_stopping, h_serial, h_reading_thread, h_control_thread

    # Đặt trạng thái mặc định
    data = 0.0
    led_status = 'OFF'
    is_stopping = False

    # Khởi tạo lại cổng COM
    initialize_serial()

    # Khởi động lại các luồng
    if not h_reading_thread or not h_reading_thread.is_alive():
        h_reading_thread = threading.Thread(target=readingThread, args=(h_serial,))
        h_reading_thread.start()

    if not h_control_thread or not h_control_thread.is_alive():
        h_control_thread = threading.Thread(target=controlThread, args=(h_serial,))
        h_control_thread.start()


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

# Hàm xử lý tín hiệu
def signal_handler(sig, frame):
    print("\nTín hiệu SIGINT nhận được, đang dọn dẹp...")
    cleanup()
    print("Thoát chương trình.")
    exit(0)  # Thoát chương trình

# Đăng ký hàm xử lý tín hiệu SIGINT (Ctrl+C)
signal.signal(signal.SIGINT, signal_handler)


# ==========================
# Khởi động hệ thống
# ==========================

# Khởi tạo trạng thái ban đầu
reset_state()

# Thêm CSS tùy chỉnh vào cấu hình
pn.config.raw_css.append(theme_css)

# Thêm callback cập nhật mỗi 1 giây
pn.state.add_periodic_callback(update_ui, period=1000)  # 1000 ms = 1 giây

# Chạy ứng dụng Panel
dashboard.servable()