# AIoT - Smart Lighting System

The **AIoT (Artificial Intelligence of Things)** project is designed to build an intelligent monitoring and control system that combines IoT sensor data with AI models for analysis and visualization. The **final version** is a fully integrated system: from data preprocessing and model training to a web-based dashboard that visualizes sensor readings and manages devices. Through the dashboard, users can monitor environmental metrics, check device status in real time, and switch between manual and automatic control modes.

You can watch a detailed demo video [here](https://youtu.be/kpJ3Pxjll1U), which includes:

* Required hardware
* Circuit setup (both simulator and real device)
* State diagram of all possible system states (see more in [proposal.pdf](https://github.com/HBNQuynh/AIoT/blob/main/final/Project%20proposal.pdf))
* Full system demonstration

## Features

* **IoT Data Collection**

  * Connects to sensors and devices.
  * Reads environmental data (light itensity).

* **Data Processing & AI Analysis**

  * Cleans and preprocesses raw sensor data.
  * Uses AI to make decisions (e.g., turn lights on/off based on thresholds, anomaly detection).

* **Device Control**

  * **Manual mode:** toggle devices directly from the dashboard.
  * **Automatic mode:** system controls devices based on sensor readings and predefined thresholds.

* **Web Dashboard**

  * **Flask**: backend server and control API.
  * **Panel**: interactive UI with charts, tables, and control buttons.
  * Supports real-time monitoring and remote control, with mode switching between Auto and Manual.

## Run the Dashboard

### 1. Clone the repository

```bash
git clone https://github.com/HBNQuynh/AIoT.git
cd AIoT/final
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure OpenAI API key

The project uses the `openai` library. Set your API key as an environment variable:

```bash
export OPENAI_API_KEY="your_api_key_here"   # Linux/Mac
setx OPENAI_API_KEY "your_api_key_here"     # Windows PowerShell
```

### 4. Connect Arduino

* Make sure your Arduino is connected and streaming sensor data via **COM7** (update this in `web.py`: `h_serial = serial.Serial('COM7', 115200, timeout=1)`).
* On Linux/Mac, replace `COM7` with `/dev/ttyUSB0` or `/dev/ttyACM0`.

### 5. Launch the app

```bash
python web.py
```

### 6. Access the dashboard

Open your browser and go to: `http://localhost:5006`

Here you can:

* Monitor live light sensor data.
* Toggle the LED manually or let the system run in auto mode.
* Interact with the AI-powered chatbot to control lights or check system status (supports **Speech-to-Text** & **Text-to-Speech**).
* Manage multiple chat sessions

✨ The **final version** is the complete project. Please run everything inside the `final/` folder instead of `midterm/`.
