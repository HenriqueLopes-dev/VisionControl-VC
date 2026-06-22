# =========================================================================
# VisionControl - Controle de Input com Failsafe
# =========================================================================
import time
import threading
import pyautogui
from pynput.keyboard import Controller as KeyboardController, Key
from pynput.mouse import Controller as MouseController, Button


# Desabilita a pausa de seguranca do pyautogui
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0


class InputController:
    """
    Controlador centralizado de input com failsafe.
    Thread-safe, com watchdog automatico para soltar teclas presas.
    """

    # Mapeamento de teclas especiais para pynput Key
    SPECIAL_KEYS = {
        "space": Key.space,
        "enter": Key.enter,
        "ctrl": Key.ctrl,
        "ctrlleft": Key.ctrl_l,
        "ctrlright": Key.ctrl_r,
        "shift": Key.shift,
        "shiftleft": Key.shift_l,
        "shiftright": Key.shift_r,
        "alt": Key.alt,
        "altleft": Key.alt_l,
        "altright": Key.alt_r,
        "win": Key.cmd,
        "tab": Key.tab,
        "backspace": Key.backspace,
        "delete": Key.delete,
        "escape": Key.esc,
        "up": Key.up,
        "down": Key.down,
        "left": Key.left,
        "right": Key.right,
        "pageup": Key.page_up,
        "pagedown": Key.page_down,
        "home": Key.home,
        "end": Key.end,
        "insert": Key.insert,
        "f1": Key.f1, "f2": Key.f2, "f3": Key.f3, "f4": Key.f4,
        "f5": Key.f5, "f6": Key.f6, "f7": Key.f7, "f8": Key.f8,
        "f9": Key.f9, "f10": Key.f10, "f11": Key.f11, "f12": Key.f12,
        "print": Key.print_screen,
        "scrolllock": Key.scroll_lock,
        "pause": Key.pause,
        "numlock": Key.num_lock,
        "capslock": Key.caps_lock,
    }

    def __init__(self, settings=None):
        self.kb = KeyboardController()
        self.mouse = MouseController()
        self.settings = settings or {}

        # Timeout para soltar teclas automaticamente (ms -> segundos)
        timeout_ms = self.settings.get("key_release_timeout", 500)
        self._timeout_secs = timeout_ms / 1000.0

        # Estado atual das teclas pressionadas: {key_name: last_press_time}
        self._pressed_keys = {}
        self._pressed_mouse = set()

        # Lock para thread-safety (RLock permite reentrancia, evita deadlock)
        self._lock = threading.RLock()

        # Gesto atual confirmado para cada mao
        self._current_left_gesture = "NEUTRO"
        self._current_right_gesture = "NEUTRO"

        # Controle de pulso (clique unico) - registra que ja disparou
        self._pulse_fired_left = {}
        self._pulse_fired_right = {}

        # Modo Simples - estado das zonas
        self._simple_zone_active = set()      # zonas atualmente ocupadas
        self._simple_pulse_fired = set()      # zonas que ja dispararam pulso

        # Posicao suavizada do mouse
        self._mouse_x = None
        self._mouse_y = None
        self._smooth_factor = self.settings.get("smooth_factor", 0.35)
        self._mouse_area = (
            self.settings.get("mouse_area_x_min", 0.50),
            self.settings.get("mouse_area_x_max", 0.95),
            self.settings.get("mouse_area_y_min", 0.15),
            self.settings.get("mouse_area_y_max", 0.85),
        )

        # Watchdog
        self._watchdog_running = False
        self._watchdog_thread = None

    # =====================================================================
    # WATCHDOG
    # =====================================================================

    def start_watchdog(self):
        self._watchdog_running = True
        self._watchdog_thread = threading.Thread(target=self._watchdog_loop, daemon=True)
        self._watchdog_thread.start()

    def stop_watchdog(self):
        self._watchdog_running = False

    def _watchdog_loop(self):
        while self._watchdog_running:
            time.sleep(0.1)
            with self._lock:
                now = time.time()
                stale = [k for k, t in self._pressed_keys.items()
                         if (now - t) > self._timeout_secs]
                for key in stale:
                    key_obj = self._resolve_key(key)
                    if key_obj:
                        try:
                            self.kb.release(key_obj)
                        except Exception:
                            pass
                    self._pressed_keys.pop(key, None)

    # =====================================================================
    # KEY HELPERS
    # =====================================================================

    def _resolve_key(self, key_name):
        if not key_name:
            return None
        key_name = key_name.lower().strip()
        if key_name in self.SPECIAL_KEYS:
            return self.SPECIAL_KEYS[key_name]
        if len(key_name) == 1:
            return key_name
        return None

    def _press_key(self, key_name):
        """Pressiona a tecla a cada chamada para garantir que permaneca pressionada."""
        with self._lock:
            key = self._resolve_key(key_name)
            if key is None:
                return
            try:
                self.kb.press(key)
                self._pressed_keys[key_name] = time.time()
            except Exception:
                pass

    def _release_key(self, key_name):
        with self._lock:
            if key_name not in self._pressed_keys:
                return
            key = self._resolve_key(key_name)
            if key:
                try:
                    self.kb.release(key)
                except Exception:
                    pass
            self._pressed_keys.pop(key_name, None)

    def _release_all_keys(self):
        with self._lock:
            for key in list(self._pressed_keys.keys()):
                key_obj = self._resolve_key(key)
                if key_obj:
                    try:
                        self.kb.release(key_obj)
                    except Exception:
                        pass
            self._pressed_keys.clear()
            # Seguranca: solta todos os modificadores tambem
            for mod in [Key.ctrl, Key.ctrl_l, Key.ctrl_r,
                        Key.shift, Key.shift_l, Key.shift_r,
                        Key.alt, Key.alt_l, Key.alt_r]:
                try:
                    self.kb.release(mod)
                except Exception:
                    pass

    def _tap_key_async(self, key_name, duration=0.05):
        """Tap em thread separada para nao bloquear o loop principal."""
        def _do():
            key = self._resolve_key(key_name)
            if key is None:
                return
            try:
                self.kb.press(key)
                time.sleep(duration)
                self.kb.release(key)
            except Exception:
                pass
        threading.Thread(target=_do, daemon=True).start()

    # =====================================================================
    # MOUSE HELPERS
    # =====================================================================

    def _press_mouse(self, button_name):
        with self._lock:
            if button_name in self._pressed_mouse:
                return
            button = Button.left if button_name == "mouse_left" else Button.right
            try:
                self.mouse.press(button)
                self._pressed_mouse.add(button_name)
            except Exception:
                pass

    def _release_mouse(self, button_name):
        with self._lock:
            if button_name not in self._pressed_mouse:
                return
            button = Button.left if button_name == "mouse_left" else Button.right
            try:
                self.mouse.release(button)
            except Exception:
                pass
            self._pressed_mouse.discard(button_name)

    def release_all_mouse(self):
        with self._lock:
            for btn in list(self._pressed_mouse):
                button = Button.left if btn == "mouse_left" else Button.right
                try:
                    self.mouse.release(button)
                except Exception:
                    pass
            self._pressed_mouse.clear()
            try:
                self.mouse.release(Button.left)
                self.mouse.release(Button.right)
            except Exception:
                pass

    def release_all(self):
        """Solta TUDO."""
        self._release_all_keys()
        self.release_all_mouse()
        self._pulse_fired_left.clear()
        self._pulse_fired_right.clear()
        self._simple_zone_active.clear()
        self._simple_pulse_fired.clear()

    # =====================================================================
    # MOUSE MOVEMENT
    # =====================================================================

    def mover_mouse_pela_palma(self, landmarks):
        """Move o mouse baseado na posicao da palma, com suavizacao."""
        palm_x = landmarks[9].x
        palm_y = landmarks[9].y

        screen_w, screen_h = pyautogui.size()
        ax_min, ax_max, ay_min, ay_max = self._mouse_area

        rel_x = (palm_x - ax_min) / (ax_max - ax_min)
        rel_y = (palm_y - ay_min) / (ay_max - ay_min)
        rel_x = max(0.0, min(1.0, rel_x))
        rel_y = max(0.0, min(1.0, rel_y))

        target_x = int(rel_x * screen_w)
        target_y = int(rel_y * screen_h)

        if self._mouse_x is None:
            self._mouse_x = target_x
            self._mouse_y = target_y
        else:
            self._mouse_x += self._smooth_factor * (target_x - self._mouse_x)
            self._mouse_y += self._smooth_factor * (target_y - self._mouse_y)

        try:
            pyautogui.moveTo(int(self._mouse_x), int(self._mouse_y), duration=0)
        except Exception:
            pass

    # =====================================================================
    # ACOES DAS MAOS - Chamado a CADA frame para manter teclas pressionadas
    # =====================================================================

    def tick_mao_esquerda(self, config, gesture_id):
        """
        Chamado a CADA frame processado. Mantem teclas pressionadas no modo continuo.
        Retorna (texto_acao, texto_gesto).
        """
        cfg = config.get("left", {})
        action_cfg = cfg.get(gesture_id, {"acao": None, "continuo": True})
        key = action_cfg.get("acao")
        is_continuous = action_cfg.get("continuo", True)

        # Transicao para NEUTRO
        if gesture_id == "NEUTRO":
            if self._current_left_gesture != "NEUTRO":
                self._release_all_keys()
                self._pulse_fired_left.clear()
                self._current_left_gesture = "NEUTRO"
            return "Nenhum", "Neutro"

        # Mudou de gesto
        if gesture_id != self._current_left_gesture:
            self._release_all_keys()
            self._pulse_fired_left.clear()
            self._current_left_gesture = gesture_id

        if not key:
            return "Nenhum", self._gesto_label(gesture_id)

        if is_continuous:
            # MODO CONTINUO: segura a tecla a cada frame (mantem pressionada)
            self._press_key(key)
            return f"Segurando: {key.upper()}", self._gesto_label(gesture_id)
        else:
            # MODO PULSO: clique unico na transicao
            if not self._pulse_fired_left.get(gesture_id, False):
                self._pulse_fired_left[gesture_id] = True
                self._tap_key_async(key)
                return f"Clique: {key.upper()}", self._gesto_label(gesture_id)
            return f"Aguardando...", self._gesto_label(gesture_id)

    def tick_mao_direita(self, config, gesture_id):
        """
        Chamado a CADA frame processado. Mantem botoes pressionados no modo continuo.
        Retorna (texto_acao, texto_gesto).
        """
        cfg = config.get("right", {})
        action_cfg = cfg.get(gesture_id, {"acao": None, "continuo": True})
        key = action_cfg.get("acao")
        is_continuous = action_cfg.get("continuo", True)

        # Transicao para NEUTRO
        if gesture_id == "NEUTRO":
            if self._current_right_gesture != "NEUTRO":
                self.release_all_mouse()
                self._pulse_fired_right.clear()
                self._current_right_gesture = "NEUTRO"
            return "Nenhum", "Neutro"

        # Mudou de gesto
        if gesture_id != self._current_right_gesture:
            self.release_all_mouse()
            self._pulse_fired_right.clear()
            self._current_right_gesture = gesture_id

        if not key:
            return "Nenhum", self._gesto_label(gesture_id)

        # Mouse click
        if key in ("mouse_left", "mouse_right"):
            self._press_mouse(key)
            return "Clique Mouse", self._gesto_label(gesture_id)

        # Tecla de teclado
        if is_continuous:
            self._press_key(key)
            return f"Segurando: {key.upper()}", self._gesto_label(gesture_id)
        else:
            if not self._pulse_fired_right.get(gesture_id, False):
                self._pulse_fired_right[gesture_id] = True
                self._tap_key_async(key)
                return f"Clique: {key.upper()}", self._gesto_label(gesture_id)
            return f"Aguardando...", self._gesto_label(gesture_id)

    # =====================================================================
    # MODO SIMPLES - Zonas na tela
    # =====================================================================

    def tick_modo_simples(self, config_simples, zonas_ocupadas):
        """
        Chamado a CADA frame quando o modo simples esta ativo.
        zonas_ocupadas: dict {zone_id: True/False} indicando se ha mao dentro.
        """
        for zone_id, ocupada in zonas_ocupadas.items():
            cfg = config_simples.get(zone_id, {"acao": None, "continuo": False})
            key = cfg.get("acao")
            is_continuous = cfg.get("continuo", False)

            if not key:
                continue

            if ocupada:
                if is_continuous:
                    self._press_key(key)
                    self._simple_zone_active.add(zone_id)
                else:
                    if zone_id not in self._simple_pulse_fired:
                        self._simple_pulse_fired.add(zone_id)
                        self._tap_key_async(key)
            else:
                if zone_id in self._simple_zone_active:
                    self._release_key(key)
                    self._simple_zone_active.discard(zone_id)
                self._simple_pulse_fired.discard(zone_id)

    def on_mao_sumiu(self, side):
        """Chamado quando uma mao some da tela."""
        if side == "left":
            if self._current_left_gesture != "NEUTRO":
                self._release_all_keys()
                self._pulse_fired_left.clear()
                self._current_left_gesture = "NEUTRO"
        elif side == "right":
            if self._current_right_gesture != "NEUTRO":
                self.release_all_mouse()
                self._pulse_fired_right.clear()
                self._current_right_gesture = "NEUTRO"

    @staticmethod
    def _gesto_label(gesture_id):
        labels = {
            "1_DEDO": "1 dedo", "2_DEDOS": "2 dedos",
            "3_DEDOS": "3 dedos", "4_DEDOS": "4 dedos",
            "PINCA_INDICADOR": "Pinca Ind.", "PINCA_MEDIO": "Pinca Med.",
            "PINCA_ANELAR": "Pinca Ane.", "PINCA_MINIMO": "Pinca Min."
        }
        return labels.get(gesture_id, gesture_id)
