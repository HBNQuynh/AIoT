# import panel as pn
# import asyncio
# from time import sleep

# pn.extension()

# async def get_response(contents, user, instance):
#     if "turbine" in contents.lower():
#         response = "A wind turbine converts wind energy into electricity."
#     else:
#         response = "Sorry, I don't know."

#     for i in range(len(response)):
#         yield response[:i+1]
#         await asyncio.sleep(0.02)

# chat_bot = pn.chat.ChatInterface(callback=get_response, max_height=1000)
# chat_bot.send("Ask me what a wind turbine is", user="Assistant", respond=False)
# chat_bot.servable()


# # Widget chọn ngôn ngữ
# language_selector = pn.widgets.Select(
#     name='Chọn ngôn ngữ', options={'Tiếng Việt': 'vi-VN', 'English': 'en-US'}, value='vi-VN'
# )

# # Widget SpeechToText (ban đầu mặc định là Tiếng Việt)
# speech_to_text = pn.widgets.SpeechToText(button_type="light", height=50, lang=language_selector.value)

# def update_language(event):
#     speech_to_text.lang = event.new

# language_selector.param.watch(update_language, 'value')

# def results_callback(results):
#     print("Kết quả giọng nói:", speech_to_text.results)
#     return pn.pane.Str(f"Kết quả: {speech_to_text.results}", width=400, height=50)

# app = pn.Column(
#     "## 🗣️ **Speech-to-Text: Tiếng Anh và Tiếng Việt**",
#     language_selector,
#     speech_to_text,
#     pn.bind(results_callback, speech_to_text)
# )

# app.servable()

# import panel as pn
# import asyncio
# import json

# pn.extension()

# # ==========================
# # 1️ Cấu hình Chatbot
# # ==========================
# async def get_response(contents, user, instance):
#     if "xin chào" in contents.lower():
#         response = "Xin chào"
#     else:
#         response = "tôi không hiểu"

#     for i in range(len(response)):
#         yield response[:i+1]
#         await asyncio.sleep(0.02)

#     # Kích hoạt Text-to-Speech khi chatbot hoàn thành phản hồi
#     text_to_speech.value = response
#     text_to_speech.speak = True

# # Khởi tạo Chat Interface
# chat_bot = pn.chat.ChatInterface(
#     callback=get_response, 
#     max_height=800,
#     show_clear = False
#     )

# chat_bot.send("Ask me what a wind turbine is", user="Assistant", respond=False)

# # ==========================
# # 2️ Cấu hình Speech-to-Text
# # ==========================
# # Widget chọn ngôn ngữ
# language_selector = pn.widgets.Select(
#     name='Chọn ngôn ngữ', 
#     options={'Tiếng Việt': 'vi-VN', 'English': 'en-US'}, 
#     value='en-US',
#     width=200
# )

# # Widget Speech-to-Text
# speech_to_text = pn.widgets.SpeechToText(button_type="light", height=50, lang=language_selector.value)

# # Widget text to speech
# text_to_speech = pn.widgets.TextToSpeech(name="Voicebot", auto_speak=False)

# # Hàm cập nhật ngôn ngữ cho Speech-to-Text và Text-to-Speech
# def update_language(event):
#     speech_to_text.lang = event.new
#     text_to_speech.lang = event.new
#     print(text_to_speech.lang)

# language_selector.param.watch(update_language, 'value')

# # Xử lý kết quả từ Speech-to-Text và gửi đến ChatBot
# def handle_speech_results(results):
#     if speech_to_text.results:
#         text = speech_to_text.results[0]['alternatives'][0]['transcript']
#         user_input = str(text)
#         chat_bot.send(user_input, user="User", respond=True)
#     else:
#         return pn.pane.Str("Không có kết quả từ giọng nói.", width=200, height=100)


# # ==========================
# # 4. Tạo giao diện Sidebar
# # ==========================
# sidebar = pn.Column(
#     "## 💬 **ChatGPT-Like Interface**",
#     language_selector, 
#     speech_to_text,
#     pn.bind(handle_speech_results, speech_to_text),
#     pn.pane.Markdown("## **Quản lý đoạn chat**"),
    
#     width=300,
#     css_classes=["sidebar"]
# )


# # ==========================
# # 5. Giao diện chính
# # ==========================
# app = pn.Row(
#     sidebar, 
#     pn.Column(
#         "## 🤖 **ChatBot**",
#         chat_bot,
#         text_to_speech)
#     )


# # Thêm CSS tùy chỉnh
# theme_css = """
# .sidebar {
#     background-color: #F9F9F9;
#     padding: 10px;
#     border-right: 1px solid #DDDDDD;
# }
# """

# pn.config.raw_css.append(theme_css)

# # Khai báo ứng dụng
# app.servable()


import panel as pn
import asyncio
import json
import os

pn.extension()

# ==========================
# 1. Cấu hình lưu trữ
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

# ==========================
# 2. Cấu hình Chatbot
# ==========================
async def get_response(contents, user, instance):
    if "xin chào" in contents.lower():
        response = "Xin chào"
    else:
        response = "Tôi không hiểu"

    for i in range(len(response)):
        yield response[:i+1]
        await asyncio.sleep(0.02)

    # Kích hoạt Text-to-Speech khi chatbot hoàn thành phản hồi
    text_to_speech.value = response
    text_to_speech.speak = True

    # Lưu đoạn chat vào lịch sử
    if current_chat_id not in chat_histories:
        chat_histories[current_chat_id] = []
    chat_histories[current_chat_id].append({"user": contents, "bot": response})

    # Lưu vào tệp JSON
    save_chat_histories()
    update_chat_list()

# Khởi tạo Chat Interface
chat_bot = pn.chat.ChatInterface(
    callback=get_response, 
    max_height=800,
    show_clear=False
)

# Tải nội dung hội thoại hiện tại
for msg in chat_histories.get(current_chat_id, []):
    chat_bot.send(f"**User**: {msg['user']}\n**Bot**: {msg['bot']}", user="History", respond=False)

# ==========================
# 3. Quản lý danh sách chat
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
            chat_bot.send(f"**User**: {msg['user']}\n**Bot**: {msg['bot']}", user="History", respond=False)

chat_list.param.watch(load_chat, 'value')

# Bắt đầu một cuộc hội thoại mới
def start_new_chat(event):
    global current_chat_id
    new_chat_id = f"Chat {len(chat_histories) + 1}"
    chat_histories[new_chat_id] = []
    current_chat_id = new_chat_id
    chat_bot.clear()
    update_chat_list()
    save_chat_histories()

new_chat_button = pn.widgets.Button(name="🆕 Bắt đầu cuộc chat mới", button_type="primary")
new_chat_button.on_click(start_new_chat)

# ==========================
# 4. Cấu hình Speech-to-Text và Text-to-Speech
# ==========================
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
# 5. Tạo giao diện Sidebar
# ==========================
sidebar = pn.Column(
    "## 💬 **ChatGPT-Like Interface**",
    language_selector, 
    speech_to_text,
    pn.bind(handle_speech_results, speech_to_text),
    pn.pane.Markdown("## **Danh sách các cuộc hội thoại**"),
    chat_list,
    new_chat_button,
    width=300,
    css_classes=["sidebar"]
)

# ==========================
# 6. Giao diện chính
# ==========================
app = pn.Row(
    sidebar, 
    pn.Column(
        "## 🤖 **ChatBot**",
        chat_bot,
        text_to_speech
    )
)

# Thêm CSS tùy chỉnh
theme_css = """
.sidebar {
    background-color: #F9F9F9;
    padding: 10px;
    border-right: 1px solid #DDDDDD;
}
"""

pn.config.raw_css.append(theme_css)

# Khai báo ứng dụng
app.servable()

#python -m panel serve chatbot.py (chay tren terminal)
