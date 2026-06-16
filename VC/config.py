# =========================================================================
# VisionControl - Configuracoes e Hub de Configuracao
# =========================================================================
import json
import os
import tkinter as tk
from tkinter import ttk

# Caminho do arquivo de configuracao
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


def criar_config_padrao():
    """Cria e retorna um dicionario de configuracao padrao."""
    config = {
        "left": {},
        "right": {},
        "simples": {},
        "modo_simples_ativado": False,
        "settings": {
            "exibir_camera": EXIBIR_CAMERA,
            "camera_topmost": CAMERA_TOPMOST,
            "camera_id": CAMERA_ID,
            "smooth_factor": SMOOTH_FACTOR,
            "debounce_frames": DEBOUNCE_FRAMES,
            "pinch_distance": PINCH_DISTANCE,
            "key_release_timeout": KEY_RELEASE_TIMEOUT,
            "exit_key": EXIT_KEY,
            "exit_key_name": EXIT_KEY_NAME,
            "config_key": CONFIG_KEY,
            "config_key_name": CONFIG_KEY_NAME,
        }
    }
    for gest in GESTURE_LABELS:
        config["left"][gest] = {
            "acao": DEFAULT_LEFT_HAND.get(gest),
            "continuo": gest in ["1_DEDO", "2_DEDOS", "3_DEDOS", "4_DEDOS"],
        }
        config["right"][gest] = {
            "acao": DEFAULT_RIGHT_HAND.get(gest),
            "continuo": gest in ["1_DEDO", "2_DEDOS", "3_DEDOS", "4_DEDOS"],
        }
    for zone_id, vals in DEFAULT_SIMPLE_MODE.items():
        config["simples"][zone_id] = {
            "acao": vals["acao"],
            "continuo": vals["continuo"],
        }
    return config


def salvar_config(config_dict):
    """Salva o dicionario de configuracao em config.json."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config_dict, f, indent=2, ensure_ascii=False)


def carregar_config():
    """Carrega config.json ou retorna None se nao existir."""
    if not os.path.exists(CONFIG_FILE):
        return None
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

# =========================================================================
# CONSTANTES GLOBAIS (Valores padrao - podem ser sobrescritos pelo hub)
# =========================================================================
EXIBIR_CAMERA = True
CAMERA_ID = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# Fator de suavizacao do mouse (0.0 a 1.0)
SMOOTH_FACTOR = 0.35

# Area ativa do mouse (porcentagem da tela)
MOUSE_AREA_X_MIN = 0.50
MOUSE_AREA_X_MAX = 0.95
MOUSE_AREA_Y_MIN = 0.15
MOUSE_AREA_Y_MAX = 0.85

# Distancia para detectar pinca (normalizada 0-1)
PINCH_DISTANCE = 0.04

# Frames de confirmacao para debounce de gestos
DEBOUNCE_FRAMES = 3

# Timeout de seguranca para soltar teclas (ms)
KEY_RELEASE_TIMEOUT = 500

# Janela da camera sempre por cima
CAMERA_TOPMOST = True

# Teclas de controle do VisionControl (codigos cv2.waitKey)
EXIT_KEY = 27       # ESC
EXIT_KEY_NAME = "ESC"
CONFIG_KEY = 118    # 'v'
CONFIG_KEY_NAME = "V"

# =========================================================================
# CONFIGURACAO PADRAO DOS GESTOS
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

# Label amigavel para cada gesto
GESTURE_LABELS = {
    "1_DEDO": "1 dedo aberto",
    "2_DEDOS": "2 dedos abertos",
    "3_DEDOS": "3 dedos abertos",
    "4_DEDOS": "4 dedos abertos",
    "PINCA_INDICADOR": "Pinca polegar + indicador",
    "PINCA_MEDIO": "Pinca polegar + medio",
    "PINCA_ANELAR": "Pinca polegar + anelar",
    "PINCA_MINIMO": "Pinca polegar + minimo",
}

# =========================================================================
# MODO SIMPLES - Zonas na tela
# =========================================================================
SIMPLE_ZONE_LABELS = {
    "S_CIMA": "Cima",
    "S_BAIXO": "Baixo",
    "S_ESQUERDA": "Esquerda",
    "S_DIREITA": "Direita",
}

DEFAULT_SIMPLE_MODE = {
    "S_CIMA": {"acao": "up", "continuo": False},
    "S_BAIXO": {"acao": "down", "continuo": False},
    "S_ESQUERDA": {"acao": "left", "continuo": False},
    "S_DIREITA": {"acao": "right", "continuo": False},
}

# Teclas que sao modificadoras e precisam de cuidado especial
MODIFIER_KEYS = {"ctrl", "alt", "shift", "win"}


def get_display_name(key):
    """Converte nome tecnico da tecla para texto amigavel."""
    if not key:
        return "Nenhum"
    if key == "mouse_left":
        return "Clique Esq"
    if key == "mouse_right":
        return "Clique Dir"

    nomes = {
        "space": "Espaco",
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
        "up": "Seta Cima",
        "down": "Seta Baixo",
        "left": "Seta Esq",
        "right": "Seta Dir",
        "tab": "Tab",
        "backspace": "Backspace",
        "delete": "Delete",
        "escape": "ESC",
        "pageup": "PgUp",
        "pagedown": "PgDown",
        "home": "Home",
        "end": "End",
        "insert": "Insert",
        "f1": "F1", "f2": "F2", "f3": "F3", "f4": "F4",
        "f5": "F5", "f6": "F6", "f7": "F7", "f8": "F8",
        "f9": "F9", "f10": "F10", "f11": "F11", "f12": "F12",
    }
    return nomes.get(key, key.upper())


def normalize_key(key):
    """Normaliza nomes de teclas para o padrao usado pelo pynput."""
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
    """Abre a janela de configuracao e retorna as configuracoes do usuario."""
    # Se nao existir config.json, cria com valores padrao
    if not os.path.exists(CONFIG_FILE):
        salvar_config(criar_config_padrao())
        print(f"Configuracao padrao salva em {CONFIG_FILE}")

    root = tk.Tk()
    root.title("VisionControl - Configuracao")
    root.geometry("840x760")
    root.resizable(True, True)
    root.minsize(840, 600)

    # Garante que a janela aparece no centro da tela
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (840 // 2)
    y = (root.winfo_screenheight() // 2) - (760 // 2)
    root.geometry(f"840x760+{x}+{y}")

    config = {
        "left": {},
        "right": {},
        "simples": {},
        "modo_simples_ativado": False,
        "start": False,
        "settings": {}
    }
    left_state = DEFAULT_LEFT_HAND.copy()
    right_state = DEFAULT_RIGHT_HAND.copy()
    simple_state = {k: v["acao"] for k, v in DEFAULT_SIMPLE_MODE.items()}
    left_continuous = {}
    right_continuous = {}
    simple_continuous = {}
    active_listener = [None]
    _ctrl_key_capture = [None]  # (btn, var_code, var_name) p/ capturar teclas de controle

    # Variaveis das configuracoes
    var_exibir_camera = tk.BooleanVar(value=EXIBIR_CAMERA)
    var_camera_topmost = tk.BooleanVar(value=CAMERA_TOPMOST)
    var_camera_id = tk.IntVar(value=CAMERA_ID)
    var_smooth = tk.DoubleVar(value=SMOOTH_FACTOR)
    var_debounce = tk.IntVar(value=DEBOUNCE_FRAMES)
    var_pinch = tk.DoubleVar(value=PINCH_DISTANCE)
    var_timeout = tk.IntVar(value=KEY_RELEASE_TIMEOUT)
    var_exit_key = tk.IntVar(value=EXIT_KEY)
    var_exit_key_name = tk.StringVar(value=EXIT_KEY_NAME)
    var_config_key = tk.IntVar(value=CONFIG_KEY)
    var_config_key_name = tk.StringVar(value=CONFIG_KEY_NAME)

    # --- HEADER ---
    tk.Label(root, text="VisionControl", font=("Segoe UI", 18, "bold"), fg="#2196F3").pack(pady=(15, 5))
    tk.Label(
        root,
        text="Configure os gestos ou o modo simples. Clique no botao e pressione a tecla desejada.\n"
             "ESC limpa a tecla. 'Segurar' mantem a tecla pressionada enquanto o gesto/zona estiver ativo.",
        font=("Segoe UI", 10),
        fg="#666666"
    ).pack(pady=5)

    # --- NOTEBOOK (ABAS) ---
    notebook = ttk.Notebook(root)
    notebook.pack(pady=10, padx=20, expand=True, fill="both")

    aba_esquerda = ttk.Frame(notebook)
    aba_direita = ttk.Frame(notebook)
    aba_config = ttk.Frame(notebook)
    notebook.add(aba_esquerda, text=" Mao Esquerda ")
    notebook.add(aba_direita, text=" Mao Direita (Mouse) ")
    notebook.add(aba_config, text=" Configuracoes ")

    left_frame = tk.Frame(aba_esquerda, padx=10, pady=10)
    left_frame.pack(pady=10, expand=True)

    right_frame = tk.Frame(aba_direita, padx=10, pady=10)
    right_frame.pack(pady=10, expand=True)

    def _resolve_side_state(side):
        if side == "left":
            return left_state
        if side == "right":
            return right_state
        return simple_state

    def _resolve_side_continuous(side):
        if side == "left":
            return left_continuous
        if side == "right":
            return right_continuous
        return simple_continuous

    # --- LÓGICA DO KEY LISTENER ---
    def set_listener(btn, side, zone_id):
        state = _resolve_side_state(side)
        if active_listener[0]:
            old_btn, old_side, old_zone = active_listener[0]
            old_state = _resolve_side_state(old_side)
            val = old_state.get(old_zone)
            old_btn.config(text=get_display_name(val), bg="SystemButtonFace")
        active_listener[0] = (btn, side, zone_id)
        btn.config(text="[ Pressione... ]", bg="#FFF3E0")

    def set_mouse_action(btn, side, zone_id, action):
        if active_listener[0] and active_listener[0][0] == btn:
            active_listener[0] = None
        state = _resolve_side_state(side)
        state[zone_id] = action
        btn.config(text=get_display_name(action), bg="SystemButtonFace")

    def capturar_ctrl_tecla(btn, var_code, var_name):
        """Captura a proxima tecla como tecla de controle (sair/config)."""
        if _ctrl_key_capture[0]:
            old_btn, _, _ = _ctrl_key_capture[0]
            old_btn.config(text=old_btn.old_text, bg="SystemButtonFace")
        _ctrl_key_capture[0] = (btn, var_code, var_name)
        btn.old_text = btn.cget("text")
        btn.config(text="...", bg="#FFF9C4")

    def on_key_press(event):
        # Verifica captura de tecla de controle primeiro
        if _ctrl_key_capture[0]:
            btn, var_code, var_name = _ctrl_key_capture[0]
            keysym = event.keysym
            code, name = None, None

            if keysym == "Escape":
                code, name = 27, "ESC"
            elif keysym == "Space":
                code, name = 32, "SPACE"
            elif keysym == "Return":
                code, name = 13, "ENTER"
            elif keysym == "Tab":
                code, name = 9, "TAB"
            elif keysym.startswith("F") and len(keysym) <= 3:
                try:
                    n = int(keysym[1:])
                    if 1 <= n <= 12:
                        code, name = 111 + n, keysym.upper()
                except ValueError:
                    pass
            elif len(event.char) == 1 and event.char.isprintable():
                code = ord(event.char.lower())
                name = event.char.upper()

            if code is not None:
                var_code.set(code)
                var_name.set(name)
                btn.config(text=name, bg="SystemButtonFace")
            else:
                btn.config(text=var_name.get(), bg="SystemButtonFace")
            _ctrl_key_capture[0] = None
            return

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

        state = _resolve_side_state(side)
        state[gesture_id] = internal_key

        btn.config(text=get_display_name(internal_key), bg="SystemButtonFace")
        active_listener[0] = None

    root.bind("<Key>", on_key_press)

    # --- TABELA DE CONFIGURACAO (Gestos / Modo Simples) ---
    def criar_tabela(parent_frame, side, state_dict, continuous_dict, labels_dict):
        """Cria a tabela de zonas/gestos com label, botao de tecla, botoes de mouse e checkbox."""
        headers = ["Gesto", "Tecla", "Mouse", "Segurar"]
        for col, h in enumerate(headers):
            lbl = tk.Label(parent_frame, text=h, font=("Segoe UI", 9, "bold"), fg="#333333")
            lbl.grid(row=0, column=col, padx=3, pady=(0, 8))

        buttons = {}
        for row, zone_id in enumerate(labels_dict, start=1):
            # Label
            tk.Label(
                parent_frame,
                text=labels_dict[zone_id],
                anchor="w",
                width=24,
                font=("Segoe UI", 9)
            ).grid(row=row, column=0, pady=4, sticky="w")

            # Botao da tecla
            btn = tk.Button(
                parent_frame,
                text=get_display_name(state_dict.get(zone_id)),
                width=14,
                font=("Segoe UI", 9, "bold"),
                cursor="hand2"
            )
            btn.config(command=lambda b=btn, z=zone_id: set_listener(b, side, z))
            btn.grid(row=row, column=1, padx=3)
            buttons[zone_id] = btn

            # Frame para botoes de mouse
            mouse_frame = tk.Frame(parent_frame)
            mouse_frame.grid(row=row, column=2, padx=2)

            tk.Button(
                mouse_frame,
                text="Esq",
                width=4,
                font=("Segoe UI", 7),
                command=lambda b=btn, z=zone_id: set_mouse_action(b, side, z, "mouse_left")
            ).pack(side=tk.LEFT, padx=1)

            tk.Button(
                mouse_frame,
                text="Dir",
                width=4,
                font=("Segoe UI", 7),
                command=lambda b=btn, z=zone_id: set_mouse_action(b, side, z, "mouse_right")
            ).pack(side=tk.LEFT, padx=1)

            # Checkbox continuo
            is_movement = zone_id in ["1_DEDO", "2_DEDOS", "3_DEDOS", "4_DEDOS"]
            var = tk.BooleanVar(value=is_movement)
            chk = tk.Checkbutton(
                parent_frame,
                text="Segurar",
                variable=var,
                font=("Segoe UI", 8)
            )
            chk.grid(row=row, column=3, padx=5)
            continuous_dict[zone_id] = var

        return buttons

    left_buttons = criar_tabela(left_frame, "left", left_state, left_continuous, GESTURE_LABELS)
    right_buttons = criar_tabela(right_frame, "right", right_state, right_continuous, GESTURE_LABELS)

    # --- ABA MODO SIMPLES ---
    aba_simples = ttk.Frame(notebook)
    notebook.add(aba_simples, text=" Modo Simples ")
    simple_frame = tk.Frame(aba_simples, padx=10, pady=10)
    simple_frame.pack(pady=10, expand=True)
    simple_buttons = criar_tabela(simple_frame, "simples", simple_state, simple_continuous, SIMPLE_ZONE_LABELS)

    # Carrega config salva e preenche a UI
    saved_config = carregar_config()
    if saved_config:
        for gest in GESTURE_LABELS:
            if gest in saved_config.get("left", {}):
                acao = saved_config["left"][gest].get("acao")
                left_state[gest] = acao
                left_continuous[gest].set(saved_config["left"][gest].get("continuo", False))
                left_buttons[gest].config(text=get_display_name(acao))
            if gest in saved_config.get("right", {}):
                acao = saved_config["right"][gest].get("acao")
                right_state[gest] = acao
                right_continuous[gest].set(saved_config["right"][gest].get("continuo", False))
                right_buttons[gest].config(text=get_display_name(acao))

        for zone_id in SIMPLE_ZONE_LABELS:
            if zone_id in saved_config.get("simples", {}):
                acao = saved_config["simples"][zone_id].get("acao")
                simple_state[zone_id] = acao
                simple_continuous[zone_id].set(saved_config["simples"][zone_id].get("continuo", False))
                simple_buttons[zone_id].config(text=get_display_name(acao))

        cfg = saved_config.get("settings", {})
        var_exibir_camera.set(cfg.get("exibir_camera", EXIBIR_CAMERA))
        var_camera_topmost.set(cfg.get("camera_topmost", CAMERA_TOPMOST))
        var_camera_id.set(cfg.get("camera_id", CAMERA_ID))
        var_smooth.set(cfg.get("smooth_factor", SMOOTH_FACTOR))
        var_debounce.set(cfg.get("debounce_frames", DEBOUNCE_FRAMES))
        var_pinch.set(cfg.get("pinch_distance", PINCH_DISTANCE))
        var_timeout.set(cfg.get("key_release_timeout", KEY_RELEASE_TIMEOUT))
        var_exit_key.set(cfg.get("exit_key", EXIT_KEY))
        var_exit_key_name.set(cfg.get("exit_key_name", EXIT_KEY_NAME))
        var_config_key.set(cfg.get("config_key", CONFIG_KEY))
        var_config_key_name.set(cfg.get("config_key_name", CONFIG_KEY_NAME))
        if "modo_simples_ativado" in saved_config:
            config["modo_simples_ativado"] = saved_config["modo_simples_ativado"]

    # --- ABA CONFIGURACOES ---
    config_frame = tk.Frame(aba_config, padx=20, pady=20)
    config_frame.pack(expand=True, fill="both")

    def criar_slider(parent, texto, var, minval, maxval, resolucao, row, unit=""):
        tk.Label(parent, text=texto, font=("Segoe UI", 10, "bold"), anchor="w").grid(
            row=row, column=0, pady=8, sticky="w"
        )
        slider = tk.Scale(
            parent, from_=minval, to=maxval, resolution=resolucao,
            orient=tk.HORIZONTAL, variable=var, length=250,
            font=("Segoe UI", 9)
        )
        slider.grid(row=row, column=1, pady=8, padx=10, sticky="w")
        tk.Label(parent, text=unit, font=("Segoe UI", 9), fg="#666666").grid(
            row=row, column=2, pady=8, sticky="w"
        )

    # Camera ON/OFF
    tk.Label(config_frame, text="Camera:", font=("Segoe UI", 10, "bold"), anchor="w").grid(
        row=0, column=0, pady=8, sticky="w"
    )
    tk.Checkbutton(config_frame, text="Exibir janela da camera", variable=var_exibir_camera,
                   font=("Segoe UI", 9)).grid(row=0, column=1, pady=8, sticky="w", padx=10)

    # Camera Topmost
    tk.Label(config_frame, text="Por cima:", font=("Segoe UI", 10, "bold"), anchor="w").grid(
        row=1, column=0, pady=8, sticky="w"
    )
    tk.Checkbutton(config_frame, text="Camera sempre por cima da tela (topmost)",
                   variable=var_camera_topmost,
                   font=("Segoe UI", 9)).grid(row=1, column=1, pady=8, sticky="w", padx=10)

    # Camera ID
    tk.Label(config_frame, text="Camera ID:", font=("Segoe UI", 10, "bold"), anchor="w").grid(
        row=2, column=0, pady=8, sticky="w"
    )
    spin_id = tk.Spinbox(config_frame, from_=0, to=5, width=5, textvariable=var_camera_id,
                         font=("Segoe UI", 9))
    spin_id.grid(row=2, column=1, pady=8, sticky="w", padx=10)

    # Sensibilidade do mouse
    criar_slider(config_frame, "Sensib. Mouse:", var_smooth, 0.05, 1.0, 0.05, 3)
    tk.Label(config_frame, text="(mais alto = mais rapido)", font=("Segoe UI", 8),
             fg="#999999").grid(row=3, column=2, pady=8, sticky="w")

    # Debounce frames
    criar_slider(config_frame, "Debounce:", var_debounce, 1, 10, 1, 4, "frames")
    tk.Label(config_frame, text="(frames p/ confirmar gesto)", font=("Segoe UI", 8),
             fg="#999999").grid(row=4, column=2, pady=8, sticky="w")

    # Pinch distance
    criar_slider(config_frame, "Dist. Pinca:", var_pinch, 0.01, 0.1, 0.01, 5)
    tk.Label(config_frame, text="(menor = mais preciso)", font=("Segoe UI", 8),
             fg="#999999").grid(row=5, column=2, pady=8, sticky="w")

    # Key release timeout
    criar_slider(config_frame, "Timeout:", var_timeout, 100, 2000, 100, 6, "ms")
    tk.Label(config_frame, text="(soltar tecla automatico)", font=("Segoe UI", 8),
             fg="#999999").grid(row=6, column=2, pady=8, sticky="w")

    # Modo Simples
    tk.Label(config_frame, text="Modo:", font=("Segoe UI", 10, "bold"), anchor="w").grid(
        row=7, column=0, pady=8, sticky="w"
    )
    var_modo_simples = tk.BooleanVar(value=config.get("modo_simples_ativado", False))
    tk.Checkbutton(config_frame, text="Ativar Modo Simples (desativa gestos e mouse)",
                   variable=var_modo_simples,
                   font=("Segoe UI", 9)).grid(row=7, column=1, pady=8, sticky="w", padx=10)

    # Tecla Sair
    tk.Label(config_frame, text="Tecla Sair:", font=("Segoe UI", 10, "bold"), anchor="w").grid(
        row=8, column=0, pady=8, sticky="w"
    )
    btn_sair = tk.Button(
        config_frame, text=EXIT_KEY_NAME, width=10,
        font=("Segoe UI", 9), cursor="hand2"
    )
    btn_sair.grid(row=8, column=1, pady=8, sticky="w", padx=10)
    btn_sair.config(command=lambda: capturar_ctrl_tecla(btn_sair, var_exit_key, var_exit_key_name))

    # Tecla Config
    tk.Label(config_frame, text="Tecla Config:", font=("Segoe UI", 10, "bold"), anchor="w").grid(
        row=9, column=0, pady=8, sticky="w"
    )
    btn_config = tk.Button(
        config_frame, text=CONFIG_KEY_NAME, width=10,
        font=("Segoe UI", 9), cursor="hand2"
    )
    btn_config.grid(row=9, column=1, pady=8, sticky="w", padx=10)
    btn_config.config(command=lambda: capturar_ctrl_tecla(btn_config, var_config_key, var_config_key_name))

    # Atualiza texto dos botoes com valores carregados
    btn_sair.config(text=var_exit_key_name.get())
    btn_config.config(text=var_config_key_name.get())

    # Info
    tk.Label(
        config_frame,
        text="\nDica: Se o controle estiver 'travando', aumente o Debounce.\n"
             "Se as pincas nao funcionarem bem, ajuste a Distancia da Pinca.",
        font=("Segoe UI", 9), fg="#666666", justify=tk.LEFT
    ).grid(row=10, column=0, columnspan=3, pady=15, sticky="w")

    # --- BOTOES INFERIORES ---
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

        config["simples"] = {}
        for zone_id in SIMPLE_ZONE_LABELS:
            config["simples"][zone_id] = {
                "acao": normalize_key(simple_state.get(zone_id)),
                "continuo": simple_continuous[zone_id].get()
            }
        config["modo_simples_ativado"] = var_modo_simples.get()

        # Salva configuracoes
        config["settings"] = {
            "exibir_camera": var_exibir_camera.get(),
            "camera_topmost": var_camera_topmost.get(),
            "camera_id": var_camera_id.get(),
            "smooth_factor": var_smooth.get(),
            "debounce_frames": var_debounce.get(),
            "pinch_distance": var_pinch.get(),
            "key_release_timeout": var_timeout.get(),
            "exit_key": var_exit_key.get(),
            "exit_key_name": var_exit_key_name.get(),
            "config_key": var_config_key.get(),
            "config_key_name": var_config_key_name.get(),
        }

        salvar_config(config)
        config["start"] = True
        root.destroy()

    def cancelar():
        config["start"] = False
        root.destroy()

    def copiar_configs():
        """Monta o JSON das configs atuais e copia para a area de transferencia."""
        cfg = {
            "left": {},
            "right": {},
            "simples": {},
            "modo_simples_ativado": False,
            "settings": {}
        }
        for gest in GESTURE_LABELS:
            cfg["left"][gest] = {
                "acao": normalize_key(left_state.get(gest)),
                "continuo": left_continuous[gest].get()
            }
            cfg["right"][gest] = {
                "acao": normalize_key(right_state.get(gest)),
                "continuo": right_continuous[gest].get()
            }
        for zone_id in SIMPLE_ZONE_LABELS:
            cfg["simples"][zone_id] = {
                "acao": normalize_key(simple_state.get(zone_id)),
                "continuo": simple_continuous[zone_id].get()
            }
        cfg["modo_simples_ativado"] = var_modo_simples.get()
        cfg["settings"] = {
            "exibir_camera": var_exibir_camera.get(),
            "camera_topmost": var_camera_topmost.get(),
            "camera_id": var_camera_id.get(),
            "smooth_factor": var_smooth.get(),
            "debounce_frames": var_debounce.get(),
            "pinch_distance": var_pinch.get(),
            "key_release_timeout": var_timeout.get(),
            "exit_key": var_exit_key.get(),
            "exit_key_name": var_exit_key_name.get(),
            "config_key": var_config_key.get(),
            "config_key_name": var_config_key_name.get(),
        }
        texto = json.dumps(cfg, indent=2, ensure_ascii=False)
        root.clipboard_clear()
        root.clipboard_append(texto)
        btn_copiar.config(text="Copiado!", bg="#C8E6C9")
        root.after(1500, lambda: btn_copiar.config(text="Copiar Configs", bg="SystemButtonFace"))

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

    btn_copiar = tk.Button(
        button_frame,
        text="Copiar Configs",
        command=copiar_configs,
        width=14,
        height=2,
        font=("Segoe UI", 10),
        cursor="hand2"
    )
    btn_copiar.grid(row=0, column=1, padx=10)

    tk.Button(
        button_frame,
        text="Cancelar",
        command=cancelar,
        width=14,
        height=2,
        font=("Segoe UI", 10),
        cursor="hand2"
    ).grid(row=0, column=2, padx=10)

    root.mainloop()

    if not config["start"]:
        return None

    return config
