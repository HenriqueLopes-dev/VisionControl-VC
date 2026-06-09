import pydirectinput
import pyautogui
from config import MOUSE_AREA_X_MIN, MOUSE_AREA_X_MAX, MOUSE_AREA_Y_MIN, MOUSE_AREA_Y_MAX, SMOOTH_FACTOR

pyautogui.FAILSAFE = False
pydirectinput.PAUSE = 0

# =========================================================================
# CONTROLE DE TECLADO E MOUSE
# =========================================================================

active_keyboard = {
    "left": None,
    "right": None,
}

mouse_buttons = {
    "left": False,
    "right": False,
}

def press_keyboard(source, key):
    current_key = active_keyboard[source]

    if key == current_key:
        return

    if current_key:
        pydirectinput.keyUp(current_key)

    active_keyboard[source] = None

    if key:
        pydirectinput.keyDown(key)
        active_keyboard[source] = key

def release_keyboard(source):
    current_key = active_keyboard[source]

    if current_key:
        pydirectinput.keyUp(current_key)
        active_keyboard[source] = None

def release_all_keyboard():
    release_keyboard("left")
    release_keyboard("right")

def set_mouse_button(button, pressed):
    if button == "left":
        if pressed and not mouse_buttons["left"]:
            pydirectinput.mouseDown(button="left")
            mouse_buttons["left"] = True

        elif not pressed and mouse_buttons["left"]:
            pydirectinput.mouseUp(button="left")
            mouse_buttons["left"] = False

    elif button == "right":
        if pressed and not mouse_buttons["right"]:
            pydirectinput.mouseDown(button="right")
            mouse_buttons["right"] = True

        elif not pressed and mouse_buttons["right"]:
            pydirectinput.mouseUp(button="right")
            mouse_buttons["right"] = False

def release_mouse_buttons():
    set_mouse_button("left", False)
    set_mouse_button("right", False)

def aplicar_acao_mao_esquerda(config, gesture_id):
    if gesture_id == "NEUTRO":
        release_keyboard("left")
        return "Neutro"

    key = config["left"].get(gesture_id)

    if key:
        press_keyboard("left", key)
        return key.upper()

    release_keyboard("left")
    return "Nenhum"

def aplicar_acao_mao_direita(config, gesture_id):
    if gesture_id == "NEUTRO":
        release_keyboard("right")
        release_mouse_buttons()
        return "Neutro"

    action = config["right"].get(gesture_id)

    if action != "mouse_left":
        set_mouse_button("left", False)

    if action != "mouse_right":
        set_mouse_button("right", False)

    if action == "mouse_left":
        release_keyboard("right")
        set_mouse_button("left", True)
        return "Clique esquerdo"

    if action == "mouse_right":
        release_keyboard("right")
        set_mouse_button("right", True)
        return "Clique direito"

    if action:
        press_keyboard("right", action)
        return action.upper()

    release_keyboard("right")
    return "Nenhum"

# =========================================================================
# MOVIMENTO DO MOUSE
# =========================================================================

screen_width, screen_height = pyautogui.size()
prev_mouse_x, prev_mouse_y = screen_width // 2, screen_height // 2

def clamp(value, min_value, max_value):
    return max(min_value, min(max_value, value))

def mover_mouse_pela_palma(landmarks):
    global prev_mouse_x, prev_mouse_y

    points = [
        landmarks[0],
        landmarks[5],
        landmarks[9],
        landmarks[13],
        landmarks[17],
    ]

    palm_x = sum(point.x for point in points) / len(points)
    palm_y = sum(point.y for point in points) / len(points)

    normalized_x = (palm_x - MOUSE_AREA_X_MIN) / (MOUSE_AREA_X_MAX - MOUSE_AREA_X_MIN)
    normalized_y = (palm_y - MOUSE_AREA_Y_MIN) / (MOUSE_AREA_Y_MAX - MOUSE_AREA_Y_MIN)

    normalized_x = clamp(normalized_x, 0.0, 1.0)
    normalized_y = clamp(normalized_y, 0.0, 1.0)

    target_mouse_x = int(normalized_x * screen_width)
    target_mouse_y = int(normalized_y * screen_height)

    mouse_x = int(prev_mouse_x + (target_mouse_x - prev_mouse_x) * SMOOTH_FACTOR)
    mouse_y = int(prev_mouse_y + (target_mouse_y - prev_mouse_y) * SMOOTH_FACTOR)

    if abs(mouse_x - prev_mouse_x) > 2 or abs(mouse_y - prev_mouse_y) > 2:
        pydirectinput.moveTo(mouse_x, mouse_y)
        prev_mouse_x = mouse_x
        prev_mouse_y = mouse_y