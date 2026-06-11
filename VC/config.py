# =========================================================================
# VisionControl - Configurações e Hub de Configuração
# =========================================================================
import tkinter as tk
from tkinter import ttk

# =========================================================================
# CONSTANTES GLOBAIS
# =========================================================================
EXIBIR_CAMERA = True
CAMERA_ID = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# Fator de suavização do mouse (0.0 a 1.0)
SMOOTH_FACTOR = 0.35

# Área ativa do mouse (porcentagem da tela)
MOUSE_AREA_X_MIN = 0.50
MOUSE_AREA_X_MAX = 0.95
MOUSE_AREA_Y_MIN = 0.15
MOUSE_AREA_Y_MAX = 0.85

# Distância para detectar pinça (normalizada 0-1)
PINCH_DISTANCE = 0.04

# Frames de confirmação para debounce de gestos
DEBOUNCE_FRAMES = 3

# Timeout de segurança para soltar teclas (ms)
KEY_RELEASE_TIMEOUT = 500

# =========================================================================
# CONFIGURAÇÃO PADRÃO DOS GESTOS
# =========================================================================
DEFAULT_LEFT_HAND = {
    "1_DEDO": "w",
    "2_DEDOS": "a",
    "3_DEDOS": "d",
    "4_DEDOS": "s",
    "PINCA_INDICADOR": "space",
    "PINCA_MEDIO": "shift",
    "PINCA_ANELAR": "ctrl",
    "PINCA_MINIMO": "e",
}

DEFAULT_RIGHT_HAND = {
    "1_DEDO": None,
    "2_DEDOS": "r",
    "3_DEDOS": "tab",
    "4_DEDOS": "1",
    "PINCA_INDICADOR": "mouse_left",
    "PINCA_MEDIO": "mouse_right",
    "PINCA_ANELAR": "2",
    "PINCA_MINIMO": "3",
}

# Label amigável para cada gesto
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

# Teclas que são modificadoras e precisam de cuidado especial
MODIFIER_KEYS = {"ctrl", "alt", "shift", "win"}


def get_display_name(key):
    """Converte nome técnico da tecla para texto amigável."""
    if not key:
        return "Nenhum"
    if key == "mouse_left":
        return "Clique Esq"
    if key == "mouse_right":
        return "Clique Dir"

    nomes = {
        "space": "Espaço",
        "ctrl": "Ctrl",
        "ctrlleft": "Ctrl Esq",
        "ctrlright": "Ctrl Dir",
        "shift": "Shift",
        "shiftleft": "Shift Esq",
        "shiftright": "Shift Dir",
        "alt": "Alt",
        "altleft": "Alt Esq",
        "altright": "Alt Dir",
        "win": "Win",
        "enter": "Enter",
        "return": "Enter",
        "up": "↑ Cima",
        "down": "↓ Baixo",
        "left": "← Esq",
        "right": "→ Dir",
        "tab": "Tab",
        "backspace": "Backspace",
        "delete": "Delete",
        "escape": "ESC",
        "pageup": "PgUp",
        "pagedown": "PgDown",
        "home": "Home",
        "end": "End",
        "insert": "Insert",
        "f1": "F1",
        "f2": "F2",
        "f3": "F3",
        "f4": "F4",
        "f5": "F5",
        "f6": "F6",
        "f7": "F7",
        "f8": "F8",
        "f9": "F9",
        "f10": "F10",
        "f11": "F11",
        "f12": "F12",
    }
    return nomes.get(key, key.upper())


def normalize_key(key):
    """Normaliza nomes de teclas para o padrão usado pelo pynput."""
    if not key:
        return None
    key = key.lower().strip()
    mapping = {
        "ctrlleft": "ctrl",
        "ctrlright": "ctrl",
        "shiftleft": "shift",
        "shiftright": "shift",
        "altleft": "alt",
        "altright": "alt",
        "return": "enter",
    }
    return mapping.get(key, key)


def abrir_hub_configuracao():
    """Abre a janela de configuração e retorna as configurações do usuário."""
    root = tk.Tk()
    root.title("VisionControl - Configuração")
    root.geometry("820x680")
    root.resizable(False, False)

    # Garante que a janela apareça no centro da tela
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (820 // 2)
    y = (root.winfo_screenheight() // 2) - (680 // 2)
    root.geometry(f"820x680+{x}+{y}")

    config = {"left": {}, "right": {}, "start": False}
    left_state = DEFAULT_LEFT_HAND.copy()
    right_state = DEFAULT_RIGHT_HAND.copy()
    left_continuous = {}
    right_continuous = {}
    active_listener = [None]  # Usando lista para mutabilidade em closures

    # --- HEADER ---
    tk.Label(root, text="VisionControl", font=("Segoe UI", 18, "bold"), fg="#2196F3").pack(pady=(15, 5))
    tk.Label(
        root,
        text="Configure os gestos de cada mão. Clique no botão e pressione a tecla desejada.\n"
             "ESC limpa a tecla. 'Contínuo' segurado a tecla enquanto o gesto estiver ativo.",
        font=("Segoe UI", 10),
        fg="#666666"
    ).pack(pady=5)

    # --- NOTEBOOK (ABAS) ---
    notebook = ttk.Notebook(root)
    notebook.pack(pady=10, padx=20, expand=True, fill="both")

    aba_esquerda = ttk.Frame(notebook)
    aba_direita = ttk.Frame(notebook)
    notebook.add(aba_esquerda, text=" Mão Esquerda ")
    notebook.add(aba_direita, text=" Mão Direita (Mouse) ")

    left_frame = tk.Frame(aba_esquerda, padx=10, pady=10)
    left_frame.pack(pady=10, expand=True)

    right_frame = tk.Frame(aba_direita, padx=10, pady=10)
    right_frame.pack(pady=10, expand=True)

    # --- LÓGICA DO KEY LISTENER ---
    def set_listener(btn, side, gesture_id):
        if active_listener[0]:
            old_btn, old_side, old_gest = active_listener[0]
            val = left_state[old_gest] if old_side == "left" else right_state[old_gest]
            old_btn.config(text=get_display_name(val))
        active_listener[0] = (btn, side, gesture_id)
        btn.config(text="[ Pressione... ]", bg="#FFF3E0")

    def set_mouse_action(btn, side, gesture_id, action):
        if active_listener[0] and active_listener[0][0] == btn:
            active_listener[0] = None
        if side == "left":
            left_state[gesture_id] = action
        else:
            right_state[gesture_id] = action
        btn.config(text=get_display_name(action), bg="SystemButtonFace")

    def on_key_press(event):
        if not active_listener[0]:
            return

        btn, side, gesture_id = active_listener[0]
        keysym = event.keysym.lower()

        tk_to_internal = {
            "space": "space",
            "return": "enter",
            "escape": None,
            "control_l": "ctrl",
            "control_r": "ctrl",
            "shift_l": "shift",
            "shift_r": "shift",
            "alt_l": "alt",
            "alt_r": "alt",
            "win_l": "win",
            "win_r": "win",
            "prior": "pageup",
            "next": "pagedown",
            "minus": "-",
            "equal": "=",
            "comma": ",",
            "period": ".",
            "slash": "/",
            "semicolon": ";",
            "quoteright": "'",
            "bracketleft": "[",
            "bracketright": "]",
            "backslash": "\\",
            "grave": "`",
        }

        internal_key = tk_to_internal.get(keysym, keysym)

        if side == "left":
            left_state[gesture_id] = internal_key
        else:
            right_state[gesture_id] = internal_key

        btn.config(text=get_display_name(internal_key), bg="SystemButtonFace")
        active_listener[0] = None

    root.bind("<Key>", on_key_press)

    # --- TABELA DE CONFIGURAÇÃO ---
    def criar_tabela(parent_frame, side, state_dict, continuous_dict):
        """Cria a tabela de gestos com label, botão de tecla, botões de mouse e checkbox."""
        # Header
        headers = ["Gesto", "Tecla", "Mouse", "Contínuo"]
        widths = [24, 14, 7, 8]
        for col, (h, w) in enumerate(zip(headers, widths)):
            lbl = tk.Label(parent_frame, text=h, font=("Segoe UI", 9, "bold"), fg="#333333")
            lbl.grid(row=0, column=col, padx=3, pady=(0, 8))

        for row, gesture_id in enumerate(GESTURE_LABELS, start=1):
            # Label do gesto
            tk.Label(
                parent_frame,
                text=GESTURE_LABELS[gesture_id],
                anchor="w",
                width=22,
                font=("Segoe UI", 9)
            ).grid(row=row, column=0, pady=4, sticky="w")

            # Botão da tecla
            btn = tk.Button(
                parent_frame,
                text=get_display_name(state_dict.get(gesture_id)),
                width=14,
                font=("Segoe UI", 9, "bold"),
                cursor="hand2"
            )
            btn.config(command=lambda b=btn, g=gesture_id: set_listener(b, side, g))
            btn.grid(row=row, column=1, padx=3)

            # Frame para botões de mouse
            mouse_frame = tk.Frame(parent_frame)
            mouse_frame.grid(row=row, column=2, padx=2)

            tk.Button(
                mouse_frame,
                text="Esq",
                width=4,
                font=("Segoe UI", 7),
                command=lambda b=btn, g=gesture_id: set_mouse_action(b, side, g, "mouse_left")
            ).pack(side=tk.LEFT, padx=1)

            tk.Button(
                mouse_frame,
                text="Dir",
                width=4,
                font=("Segoe UI", 7),
                command=lambda b=btn, g=gesture_id: set_mouse_action(b, side, g, "mouse_right")
            ).pack(side=tk.LEFT, padx=1)

            # Checkbox contínuo (padrão: True para movimento, False para ações)
            is_movement = gesture_id in ["1_DEDO", "2_DEDOS", "3_DEDOS", "4_DEDOS"]
            var = tk.BooleanVar(value=is_movement)
            chk = tk.Checkbutton(
                parent_frame,
                text="Segurar",
                variable=var,
                font=("Segoe UI", 8)
            )
            chk.grid(row=row, column=3, padx=5)
            continuous_dict[gesture_id] = var

    criar_tabela(left_frame, "left", left_state, left_continuous)
    criar_tabela(right_frame, "right", right_state, right_continuous)

    # --- BOTÕES INFERIORES ---
    button_frame = tk.Frame(root)
    button_frame.pack(pady=15)

    def iniciar():
        for gest in GESTURE_LABELS:
            config["left"][gest] = {
                "acao": normalize_key(left_state.get(gest)),
                "continuo": left_continuous[gest].get()
            }
            config["right"][gest] = {
                "acao": normalize_key(right_state.get(gest)),
                "continuo": right_continuous[gest].get()
            }
        config["start"] = True
        root.destroy()

    def cancelar():
        config["start"] = False
        root.destroy()

    tk.Button(
        button_frame,
        text="Iniciar VisionControl",
        command=iniciar,
        width=22,
        height=2,
        bg="#4CAF50",
        fg="white",
        font=("Segoe UI", 10, "bold"),
        cursor="hand2"
    ).grid(row=0, column=0, padx=10)

    tk.Button(
        button_frame,
        text="Cancelar",
        command=cancelar,
        width=14,
        height=2,
        font=("Segoe UI", 10),
        cursor="hand2"
    ).grid(row=0, column=1, padx=10)

    root.mainloop()

    if not config["start"]:
        return None

    return config
