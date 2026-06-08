import math
import cv2
import mediapipe as mp
import pydirectinput
import pyautogui
import tkinter as tk
from tkinter import ttk


# =========================================================================
# CONFIGURAÇÕES GERAIS
# =========================================================================

EXIBIR_CAMERA = True

CAMERA_ID = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# Suavização do mouse
# Quanto menor, mais suave/lento. Quanto maior, mais rápido/brusco.
SMOOTH_FACTOR = 0.35

# Área útil da mão direita para controlar o mouse.
# Ajuste caso o mouse esteja chegando muito rápido nas bordas.
MOUSE_AREA_X_MIN = 0.50
MOUSE_AREA_X_MAX = 0.95
MOUSE_AREA_Y_MIN = 0.15
MOUSE_AREA_Y_MAX = 0.85

# Distância para detectar pinça entre polegar e dedo
PINCH_DISTANCE = 0.055

pyautogui.FAILSAFE = False
pydirectinput.PAUSE = 0


# =========================================================================
# HUB DE CONFIGURAÇÃO
# =========================================================================

KEY_OPTIONS = {
    "Nenhum": None,
    "W": "w",
    "A": "a",
    "S": "s",
    "D": "d",
    "E": "e",
    "R": "r",
    "TAB": "tab",
    "1": "1",
    "2": "2",
    "3": "3",
    "4": "4",
    "Espaço": "space",
    "CTRL esquerdo": "ctrlleft",
    "SHIFT esquerdo": "shiftleft",
    "ALT esquerdo": "altleft",
}


DEFAULT_LEFT_HAND = {
    "1_DEDO": "W",
    "2_DEDOS": "A",
    "3_DEDOS": "D",
    "4_DEDOS": "S",
    "PINCA_INDICADOR": "Espaço",
    "PINCA_MEDIO": "SHIFT esquerdo",
    "PINCA_ANELAR": "CTRL esquerdo",
    "PINCA_MINIMO": "E",
}

DEFAULT_RIGHT_HAND = {
    "1_DEDO": "Nenhum",
    "2_DEDOS": "R",
    "3_DEDOS": "TAB",
    "4_DEDOS": "1",
    "PINCA_INDICADOR": "Clique esquerdo",
    "PINCA_MEDIO": "Clique direito",
    "PINCA_ANELAR": "2",
    "PINCA_MINIMO": "3",
}


GESTURE_LABELS = {
    "1_DEDO": "1 dedo aberto",
    "2_DEDOS": "2 dedos abertos",
    "3_DEDOS": "3 dedos abertos",
    "4_DEDOS": "4 dedos abertos",
    "PINCA_INDICADOR": "Pinça polegar + indicador",
    "PINCA_MEDIO": "Pinça polegar + médio",
    "PINCA_ANELAR": "Pinça polegar + anelar",
    "PINCA_MINIMO": "Pinça polegar + mínimo",
}


RIGHT_HAND_OPTIONS = {
    **KEY_OPTIONS,
    "Clique esquerdo": "mouse_left",
    "Clique direito": "mouse_right",
}


def abrir_hub_configuracao():
    root = tk.Tk()
    root.title("VisionControl - Hub de Configuração")
    root.geometry("720x620")
    root.resizable(False, False)

    config = {
        "left": {},
        "right": {},
        "start": False,
    }

    title = tk.Label(
        root,
        text="VisionControl - Configuração de Gestos",
        font=("Arial", 16, "bold")
    )
    title.pack(pady=10)

    info = tk.Label(
        root,
        text=(
            "Punho fechado = neutro.\n"
            "A mão direita controla o mouse o tempo todo pelo centro da palma.\n"
            "Use pinça na mão direita para clicar enquanto continua mirando."
        ),
        font=("Arial", 10)
    )
    info.pack(pady=5)

    main_frame = tk.Frame(root)
    main_frame.pack(pady=10)

    left_frame = tk.LabelFrame(main_frame, text="Mão esquerda - comandos principais", padx=10, pady=10)
    left_frame.grid(row=0, column=0, padx=10, sticky="n")

    right_frame = tk.LabelFrame(main_frame, text="Mão direita - mouse + ações", padx=10, pady=10)
    right_frame.grid(row=0, column=1, padx=10, sticky="n")

    left_vars = {}
    right_vars = {}

    key_names = list(KEY_OPTIONS.keys())
    right_names = list(RIGHT_HAND_OPTIONS.keys())

    for row, gesture_id in enumerate(GESTURE_LABELS):
        label = tk.Label(left_frame, text=GESTURE_LABELS[gesture_id], anchor="w", width=25)
        label.grid(row=row, column=0, padx=5, pady=5)

        var = tk.StringVar(value=DEFAULT_LEFT_HAND.get(gesture_id, "Nenhum"))
        combo = ttk.Combobox(left_frame, textvariable=var, values=key_names, state="readonly", width=18)
        combo.grid(row=row, column=1, padx=5, pady=5)

        left_vars[gesture_id] = var

    for row, gesture_id in enumerate(GESTURE_LABELS):
        label = tk.Label(right_frame, text=GESTURE_LABELS[gesture_id], anchor="w", width=25)
        label.grid(row=row, column=0, padx=5, pady=5)

        var = tk.StringVar(value=DEFAULT_RIGHT_HAND.get(gesture_id, "Nenhum"))
        combo = ttk.Combobox(right_frame, textvariable=var, values=right_names, state="readonly", width=18)
        combo.grid(row=row, column=1, padx=5, pady=5)

        right_vars[gesture_id] = var

    neutral_label = tk.Label(
        root,
        text="Importante: mão fechada não executa comando nenhum.",
        font=("Arial", 10, "bold")
    )
    neutral_label.pack(pady=10)

    def iniciar():
        for gesture_id, var in left_vars.items():
            config["left"][gesture_id] = KEY_OPTIONS[var.get()]

        for gesture_id, var in right_vars.items():
            config["right"][gesture_id] = RIGHT_HAND_OPTIONS[var.get()]

        config["start"] = True
        root.destroy()

    def cancelar():
        config["start"] = False
        root.destroy()

    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    start_button = tk.Button(
        button_frame,
        text="Iniciar VisionControl",
        command=iniciar,
        width=22,
        height=2
    )
    start_button.grid(row=0, column=0, padx=10)

    cancel_button = tk.Button(
        button_frame,
        text="Cancelar",
        command=cancelar,
        width=14,
        height=2
    )
    cancel_button.grid(row=0, column=1, padx=10)

    root.mainloop()

    if not config["start"]:
        return None

    return config


# =========================================================================
# FUNÇÕES DE GESTOS
# =========================================================================

def distance(point_a, point_b):
    return math.sqrt(
        (point_a.x - point_b.x) ** 2 +
        (point_a.y - point_b.y) ** 2
    )


def get_open_fingers(landmarks):
    indicador_aberto = landmarks[8].y < landmarks[6].y
    medio_aberto = landmarks[12].y < landmarks[10].y
    anelar_aberto = landmarks[16].y < landmarks[14].y
    minimo_aberto = landmarks[20].y < landmarks[18].y

    return {
        "indicador": indicador_aberto,
        "medio": medio_aberto,
        "anelar": anelar_aberto,
        "minimo": minimo_aberto,
    }


def detectar_gesto(landmarks):
    fingers = get_open_fingers(landmarks)

    indicador = fingers["indicador"]
    medio = fingers["medio"]
    anelar = fingers["anelar"]
    minimo = fingers["minimo"]

    finger_count = sum([
        indicador,
        medio,
        anelar,
        minimo,
    ])

    # Punho fechado é sempre neutro
    if finger_count == 0:
        return "NEUTRO"

    thumb_tip = landmarks[4]

    # Pinças têm prioridade
    if distance(thumb_tip, landmarks[8]) < PINCH_DISTANCE:
        return "PINCA_INDICADOR"

    if distance(thumb_tip, landmarks[12]) < PINCH_DISTANCE:
        return "PINCA_MEDIO"

    if distance(thumb_tip, landmarks[16]) < PINCH_DISTANCE:
        return "PINCA_ANELAR"

    if distance(thumb_tip, landmarks[20]) < PINCH_DISTANCE:
        return "PINCA_MINIMO"

    if finger_count == 1:
        return "1_DEDO"

    if finger_count == 2:
        return "2_DEDOS"

    if finger_count == 3:
        return "3_DEDOS"

    if finger_count == 4:
        return "4_DEDOS"

    return "NEUTRO"


def gesture_to_text(gesture_id):
    if gesture_id == "NEUTRO":
        return "Neutro"

    return GESTURE_LABELS.get(gesture_id, "Desconhecido")


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

    # Primeiro libera ações anteriores que não combinam
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

    # Centro aproximado da palma:
    # punho + bases dos dedos
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


# =========================================================================
# INÍCIO DO PROGRAMA
# =========================================================================

config = abrir_hub_configuracao()

if config is None:
    print("VisionControl cancelado.")
    raise SystemExit


mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)

cap = cv2.VideoCapture(CAMERA_ID)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)

print("--------------------------------------------------")
print("VisionControl iniciado!")
print(f"Exibir câmera: {EXIBIR_CAMERA}")
print("Punho fechado = neutro")
print("Mão direita = mouse sempre ativo")
print("ESC na janela da câmera para fechar")
print("CTRL + C no terminal para encerrar")
print("--------------------------------------------------")

try:
    while cap.isOpened():
        success, frame = cap.read()

        if not success:
            break

        frame = cv2.flip(frame, 1)
        frame_h, frame_w, _ = frame.shape

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        has_left_hand = False
        has_right_hand = False

        left_gesture_text = "Nenhum"
        left_action_text = "Nenhum"

        right_gesture_text = "Nenhum"
        right_action_text = "Nenhum"

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                landmarks = hand_landmarks.landmark
                wrist_x = landmarks[0].x

                gesture_id = detectar_gesto(landmarks)

                if EXIBIR_CAMERA:
                    mp_draw.draw_landmarks(
                        frame,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS
                    )

                # MÃO DIREITA - mouse + ações
                if wrist_x > 0.5:
                    has_right_hand = True

                    # O mouse se move sempre, independente do gesto
                    mover_mouse_pela_palma(landmarks)

                    right_gesture_text = gesture_to_text(gesture_id)
                    right_action_text = aplicar_acao_mao_direita(config, gesture_id)

                # MÃO ESQUERDA - comandos principais
                else:
                    has_left_hand = True

                    left_gesture_text = gesture_to_text(gesture_id)
                    left_action_text = aplicar_acao_mao_esquerda(config, gesture_id)

        if not has_left_hand:
            release_keyboard("left")

        if not has_right_hand:
            release_keyboard("right")
            release_mouse_buttons()

        if EXIBIR_CAMERA:
            cv2.line(
                frame,
                (frame_w // 2, 0),
                (frame_w // 2, frame_h),
                (255, 255, 255),
                1
            )

            cv2.putText(
                frame,
                f"Esq gesto: {left_gesture_text}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                f"Esq acao: {left_action_text}",
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                f"Dir gesto: {right_gesture_text}",
                (10, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 0, 0),
                2
            )

            cv2.putText(
                frame,
                f"Dir acao: {right_action_text}",
                (10, 130),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 0, 0),
                2
            )

            cv2.putText(
                frame,
                "Punho fechado = neutro",
                (10, frame_h - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                2
            )

            cv2.imshow("VisionControl - Modo Teste", frame)

            if cv2.waitKey(1) & 0xFF == 27:
                break
        else:
            cv2.waitKey(1)

except KeyboardInterrupt:
    print("\nEncerrando de forma segura pelo terminal...")

finally:
    release_all_keyboard()
    release_mouse_buttons()

    cap.release()
    cv2.destroyAllWindows()

    print("VisionControl encerrado.")