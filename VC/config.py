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
# HUB DE CONFIGURAÇÃO DINÂMICA
# =========================================================================

# Agora os dicionários guardam o valor exato que o sistema entende
DEFAULT_LEFT_HAND = {
    "1_DEDO": "w",
    "2_DEDOS": "a",
    "3_DEDOS": "d",
    "4_DEDOS": "s",
    "PINCA_INDICADOR": "space",
    "PINCA_MEDIO": "shiftleft",
    "PINCA_ANELAR": "ctrlleft",
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

def get_display_name(key):
    """Transforma a tecla técnica em um texto bonito para exibir no botão"""
    if not key: return "Nenhum"
    if key == "mouse_left": return "🖱️ Clique Esq"
    if key == "mouse_right": return "🖱️ Clique Dir"
    
    nomes = {
        "space": "Espaço",
        "ctrlleft": "Ctrl Esq",
        "shiftleft": "Shift Esq",
        "altleft": "Alt Esq",
        "enter": "Enter",
        "up": "Seta Cima",
        "down": "Seta Baixo",
        "left": "Seta Esq",
        "right": "Seta Dir",
        "tab": "Tab",
        "backspace": "Backspace"
    }
    return nomes.get(key, key.upper())

def abrir_hub_configuracao():
    root = tk.Tk()
    root.title("VisionControl - Configuração")
    root.geometry("650x620") 
    root.resizable(False, False)

    config = {
        "left": {},
        "right": {},
        "start": False,
    }

    # Estados atuais das teclas
    left_state = DEFAULT_LEFT_HAND.copy()
    right_state = DEFAULT_RIGHT_HAND.copy()
    
    # Variável para saber qual botão está "escutando" o teclado no momento
    active_listener = None

    title = tk.Label(root, text="VisionControl - Gestos", font=("Arial", 16, "bold"))
    title.pack(pady=10)

    info = tk.Label(
        root,
        text="Clique no botão da tecla e pressione a nova tecla do teclado.\n(Pressione ESC para limpar a tecla de um gesto)",
        font=("Arial", 10)
    )
    info.pack(pady=5)

    notebook = ttk.Notebook(root)
    notebook.pack(pady=10, padx=20, expand=True, fill="both")

    aba_esquerda = ttk.Frame(notebook)
    aba_direita = ttk.Frame(notebook)

    notebook.add(aba_esquerda, text="Mão Esquerda")
    notebook.add(aba_direita, text="Mão Direita (Mouse)")

    left_frame = tk.Frame(aba_esquerda, padx=10, pady=10)
    left_frame.pack(pady=10)

    right_frame = tk.Frame(aba_direita, padx=10, pady=10)
    right_frame.pack(pady=10)

    # --- LÓGICA DINÂMICA (KEYBINDER) ---
    def set_listener(btn, side, gesture_id):
        nonlocal active_listener
        # Se havia outro botão escutando, restaura o texto dele
        if active_listener:
            old_btn, old_side, old_gest = active_listener
            val = left_state[old_gest] if old_side == 'left' else right_state[old_gest]
            old_btn.config(text=get_display_name(val))
            
        active_listener = (btn, side, gesture_id)
        btn.config(text="[ Pressione... ]")

    def set_mouse_action(btn, side, gesture_id, action):
        nonlocal active_listener
        if active_listener and active_listener[0] == btn:
            active_listener = None
            
        if side == 'left':
            left_state[gesture_id] = action
        else:
            right_state[gesture_id] = action
            
        btn.config(text=get_display_name(action))

    def on_key_press(event):
        nonlocal active_listener
        if not active_listener:
            return
            
        btn, side, gesture_id = active_listener
        keysym = event.keysym.lower()
        
        # Traduz a tecla capturada para o formato do pydirectinput
        tk_to_pydi = {
            "space": "space", "return": "enter", "escape": "none",
            "control_l": "ctrlleft", "control_r": "ctrlright",
            "shift_l": "shiftleft", "shift_r": "shiftright",
            "alt_l": "altleft", "alt_r": "altright",
            "prior": "pageup", "next": "pagedown",
            "minus": "-", "equal": "=", "comma": ",", "period": ".",
            "kp_0": "num0", "kp_1": "num1", "kp_2": "num2", "kp_3": "num3",
        }
        
        pydi_key = tk_to_pydi.get(keysym, keysym)
        if pydi_key == "none": # Usamos ESC para limpar o atalho
            pydi_key = None
            
        # Salva o estado atualizado
        if side == 'left':
            left_state[gesture_id] = pydi_key
        else:
            right_state[gesture_id] = pydi_key
            
        btn.config(text=get_display_name(pydi_key))
        active_listener = None

    # Ouve os botões do teclado na janela inteira
    root.bind('<Key>', on_key_press)

    # --- DESENHANDO A INTERFACE ---
    for row, gesture_id in enumerate(GESTURE_LABELS):
        # === ABA ESQUERDA ===
        tk.Label(left_frame, text=GESTURE_LABELS[gesture_id], anchor="w", width=22).grid(row=row, column=0, pady=5)
        
        btn_esq = tk.Button(left_frame, text=get_display_name(left_state.get(gesture_id)), width=14, font=("Arial", 9, "bold"))
        btn_esq.config(command=lambda b=btn_esq, g=gesture_id: set_listener(b, 'left', g))
        btn_esq.grid(row=row, column=1, padx=2)
        
        tk.Button(left_frame, text="🖱️ Esq", width=6, command=lambda b=btn_esq, g=gesture_id: set_mouse_action(b, 'left', g, 'mouse_left')).grid(row=row, column=2, padx=1)
        tk.Button(left_frame, text="🖱️ Dir", width=6, command=lambda b=btn_esq, g=gesture_id: set_mouse_action(b, 'left', g, 'mouse_right')).grid(row=row, column=3, padx=1)

        # === ABA DIREITA ===
        tk.Label(right_frame, text=GESTURE_LABELS[gesture_id], anchor="w", width=22).grid(row=row, column=0, pady=5)
        
        btn_dir = tk.Button(right_frame, text=get_display_name(right_state.get(gesture_id)), width=14, font=("Arial", 9, "bold"))
        btn_dir.config(command=lambda b=btn_dir, g=gesture_id: set_listener(b, 'right', g))
        btn_dir.grid(row=row, column=1, padx=2)
        
        tk.Button(right_frame, text="🖱️ Esq", width=6, command=lambda b=btn_dir, g=gesture_id: set_mouse_action(b, 'right', g, 'mouse_left')).grid(row=row, column=2, padx=1)
        tk.Button(right_frame, text="🖱️ Dir", width=6, command=lambda b=btn_dir, g=gesture_id: set_mouse_action(b, 'right', g, 'mouse_right')).grid(row=row, column=3, padx=1)

    # --- BOTÕES DE INICIAR/CANCELAR ---
    def iniciar():
        config["left"] = left_state
        config["right"] = right_state
        config["start"] = True
        root.destroy()

    def cancelar():
        config["start"] = False
        root.destroy()

    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="Iniciar VisionControl", command=iniciar, width=22, height=2, bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=10)
    tk.Button(button_frame, text="Cancelar", command=cancelar, width=14, height=2).grid(row=0, column=1, padx=10)

    root.mainloop()

    if not config["start"]:
        return None

    return config