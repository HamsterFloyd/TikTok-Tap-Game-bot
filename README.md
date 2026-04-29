# Tik Tok Tap Game Bot
A lightweight computer-vision bot that automatically clicks target icons.

The bot watches a selected area of the screen, detects target icons using image template matching, and clicks them automatically.

## Features

- Real-time screen capture
- Automatic target icon detection
- Automatic mouse clicks on detected icons
- Custom screen region support
- PNG-based template matching
- Built-in click cooldown to prevent repeated clicks
- Emergency stop via PyAutoGUI failsafe

## How it works

The bot uses OpenCV to find target icons on the screen, mss to capture the screen quickly, PyAutoGUI to perform mouse clicks, and NumPy for image processing.

It compares the current screen image with prepared icon templates and clicks matching positions.

## Repository files

```
game_bot/
├── bot.py
├── rgion.py
├── icon.png
├── icon2.png
└── README.md
```

## Files

### bot.py

The main bot file.

It scans the configured screen area and automatically clicks the target icon when it appears.

### region.py

A helper script for selecting the game area.

Run this file, move your mouse to the top-left and bottom-right corners of the desired game region, and it will output coordinates that you can paste into `bot.py`.

### icon.png

This is the main icon template.

You should replace this file with your own target icon.

Use a clean PNG screenshot of the icon you want the bot to click.

Recommended:

- crop the image close to the icon
- avoid unnecessary background
- keep the same size as the icon appears in the game
- use PNG format

### icon2.png

Do not replace this file unless you know what you are doing.

This template is already included as an additional useful icon for the bot.

## Installation

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install opencv-python mss pyautogui numpy
```

## Usage

First, replace `icon.png` with your own target icon.

Then run the bot:

```bash
python bot.py
```

The bot will start scanning the configured screen region and clicking matching icons automatically.

To stop the bot:

```text
Ctrl + C
```

Emergency stop:

```text
Move the mouse to the top-left corner of the screen.
```

## Selecting a screen region

To improve speed and accuracy, use `region.py` to select only the game area.

Run:

```bash
python region.py
```

Follow the instructions in the terminal:

1. Move your mouse to the top-left corner of the game area.
2. Press Enter.
3. Move your mouse to the bottom-right corner of the game area.
4. Press Enter.

The script will output a ready-to-use region block:

```python
GAME_REGION = {
    "left": 300,
    "top": 200,
    "width": 800,
    "height": 600
}
```

Copy this block into `bot.py`.

If you want the bot to scan the whole screen, use:

```python
GAME_REGION = None
```

## Configuration

Main settings are located at the top of `bot.py`:

```python
ICON_TEMPLATE_PATHS = [
    "icon.png",
    "icon2.png",
]

GAME_REGION = None

ICON_THRESHOLD = 0.75
CLICK_COOLDOWN = 0.15
LOOP_DELAY = 0.02
```

### ICON_THRESHOLD

Controls how strict the image matching is.

Lower value means more matches but a higher chance of false clicks.

Higher value means fewer matches but better precision.

Recommended starting value:

```python
ICON_THRESHOLD = 0.75
```

If the bot does not detect the icon, try:

```python
ICON_THRESHOLD = 0.65
```

If the bot clicks the wrong places, try:

```python
ICON_THRESHOLD = 0.85
```

### CLICK_COOLDOWN

Prevents repeated clicks on the same position.

```python
CLICK_COOLDOWN = 0.15
```

### LOOP_DELAY

Controls the delay between screen scans.

```python
LOOP_DELAY = 0.02
```

Lower values make the bot react faster but use more CPU.

## macOS permissions

On macOS, you may need to allow your terminal app to capture the screen and control the mouse.

Open:

```text
System Settings → Privacy & Security
```

Enable permissions for Terminal, iTerm, or your Python launcher:

```text
Screen Recording
Accessibility
```

After changing permissions, restart the terminal.
