import tkinter as tk
from tkinter import ttk

# =========================================================================
# CONFIGURAÇÕES GERAIS
# =========================================================================

EXIBIR_CAMERA = True

CAMERA_ID = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

SMOOTH_FACTOR = 0.35

MOUSE_AREA_X_MIN = 0.50
MOUSE_AREA_X_MAX = 0.95
MOUSE_AREA_Y_MIN = 0.15
MOUSE_AREA_Y_MAX = 0.85

PINCH_DISTANCE = 0.055

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