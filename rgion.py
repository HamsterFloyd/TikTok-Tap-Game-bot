import time
import pyautogui

print("Наведи мышь на ЛЕВЫЙ ВЕРХНИЙ угол области игры.")
input("Когда наведёшь — нажми Enter в терминале...")

left, top = pyautogui.position()
print(f"Левый верхний угол: x={left}, y={top}")

print("\nТеперь наведи мышь на ПРАВЫЙ НИЖНИЙ угол области игры.")
input("Когда наведёшь — нажми Enter в терминале...")

right, bottom = pyautogui.position()
print(f"Правый нижний угол: x={right}, y={bottom}")

width = right - left
height = bottom - top

print("\nВставь это в bot.py:\n")
print("GAME_REGION = {")
print(f'    "left": {left},')
print(f'    "top": {top},')
print(f'    "width": {width},')
print(f'    "height": {height}')
print("}")