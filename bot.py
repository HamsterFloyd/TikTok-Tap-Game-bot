import time
from dataclasses import dataclass

import cv2
import mss
import numpy as np
import pyautogui


# === НАСТРОЙКИ ===

ICON_TEMPLATE_PATHS = [
    "icon.png",
    "icon2.png",
]

# None = весь экран.
# Лучше потом заменить на область игры:
# GAME_REGION = {"left": 300, "top": 200, "width": 800, "height": 600}
GAME_REGION = None

ICON_THRESHOLD = 0.75

CLICK_COOLDOWN = 0.15
LOOP_DELAY = 0.02

pyautogui.FAILSAFE = True


@dataclass
class Detection:
    x: int
    y: int
    w: int
    h: int
    score: float
    template_name: str

    @property
    def center(self):
        return self.x + self.w // 2, self.y + self.h // 2


def load_template(path: str):
    image = cv2.imread(path, cv2.IMREAD_COLOR)

    if image is None:
        raise FileNotFoundError(f"Не удалось загрузить шаблон: {path}")

    h, w = image.shape[:2]
    return {
        "name": path,
        "image": image,
        "w": w,
        "h": h,
    }


def screenshot_bgr(sct, region):
    if region is None:
        monitor = sct.monitors[1]
    else:
        monitor = region

    shot = sct.grab(monitor)
    frame = np.array(shot)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

    offset_x = monitor["left"]
    offset_y = monitor["top"]

    return frame, offset_x, offset_y


def find_template(frame, template_data, threshold):
    template = template_data["image"]
    template_w = template_data["w"]
    template_h = template_data["h"]
    template_name = template_data["name"]

    result = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
    locations = np.where(result >= threshold)

    detections = []

    for y, x in zip(*locations):
        score = float(result[y, x])
        detections.append(
            Detection(
                x=x,
                y=y,
                w=template_w,
                h=template_h,
                score=score,
                template_name=template_name,
            )
        )

    return non_max_suppression(detections)


def non_max_suppression(detections, overlap_threshold=0.3):
    if not detections:
        return []

    boxes = np.array([
        [d.x, d.y, d.x + d.w, d.y + d.h, d.score]
        for d in detections
    ])

    boxes = boxes[boxes[:, 4].argsort()[::-1]]

    selected = []

    while len(boxes) > 0:
        current = boxes[0]
        selected.append(current)

        if len(boxes) == 1:
            break

        rest = boxes[1:]

        xx1 = np.maximum(current[0], rest[:, 0])
        yy1 = np.maximum(current[1], rest[:, 1])
        xx2 = np.minimum(current[2], rest[:, 2])
        yy2 = np.minimum(current[3], rest[:, 3])

        w = np.maximum(0, xx2 - xx1)
        h = np.maximum(0, yy2 - yy1)

        intersection = w * h
        current_area = (current[2] - current[0]) * (current[3] - current[1])
        rest_area = (rest[:, 2] - rest[:, 0]) * (rest[:, 3] - rest[:, 1])

        union = current_area + rest_area - intersection
        iou = intersection / union

        boxes = rest[iou < overlap_threshold]

    # Важно: после NMS template_name теряется, но для кликов он не нужен.
    return [
        Detection(
            x=int(b[0]),
            y=int(b[1]),
            w=int(b[2] - b[0]),
            h=int(b[3] - b[1]),
            score=float(b[4]),
            template_name="unknown",
        )
        for b in selected
    ]


def merge_detections(detections, overlap_threshold=0.3):
    """
    Убирает дубли, если icon.png и icon2.png нашли почти одно и то же место.
    """
    return non_max_suppression(detections, overlap_threshold=overlap_threshold)


def is_near_recent_click(x, y, recent_clicks, distance=30):
    now = time.time()

    for cx, cy, click_time in recent_clicks:
        if now - click_time > CLICK_COOLDOWN:
            continue

        if abs(x - cx) <= distance and abs(y - cy) <= distance:
            return True

    return False


def cleanup_recent_clicks(recent_clicks):
    now = time.time()

    return [
        click
        for click in recent_clicks
        if now - click[2] <= CLICK_COOLDOWN
    ]


def main():
    templates = [load_template(path) for path in ICON_TEMPLATE_PATHS]

    recent_clicks = []

    print("Бот запущен.")
    print("Ищет шаблоны:", ", ".join(ICON_TEMPLATE_PATHS))
    print("Остановка: Ctrl+C.")
    print("Аварийная остановка: увести мышь в левый верхний угол экрана.")

    with mss.mss() as sct:
        while True:
            frame, offset_x, offset_y = screenshot_bgr(sct, GAME_REGION)

            all_icons = []

            for template_data in templates:
                found = find_template(
                    frame=frame,
                    template_data=template_data,
                    threshold=ICON_THRESHOLD
                )
                all_icons.extend(found)

            all_icons = merge_detections(all_icons)
            all_icons = sorted(all_icons, key=lambda d: (d.y, d.x))

            for icon in all_icons:
                local_x, local_y = icon.center

                screen_x = offset_x + local_x
                screen_y = offset_y + local_y

                if is_near_recent_click(screen_x, screen_y, recent_clicks):
                    continue

                pyautogui.click(screen_x, screen_y)
                recent_clicks.append((screen_x, screen_y, time.time()))

            recent_clicks = cleanup_recent_clicks(recent_clicks)

            time.sleep(LOOP_DELAY)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nБот остановлен.")
