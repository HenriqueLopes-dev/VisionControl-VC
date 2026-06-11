# =========================================================================
# VisionControl - Controle de Input com Failsafe
# =========================================================================
import time
import threading
import pyautogui
from pynput.keyboard import Controller as KeyboardController, Key
from pynput.mouse import Controller as MouseController, Button

from config import (
    SMOOTH_FACTOR, MOUSE_AREA_X_MIN, MOUSE_AREA_X_MAX,
    MOUSE_AREA_Y_MIN, MOUSE_AREA_Y_MAX, KEY_RELEASE_TIMEOUT,
    MODIFIER_KEYS
)

# Desabilita a pausa de segurança do pyautogui
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0


class InputController:
    """
    Controlador centralizado de input com failsafe.
    Resolve problemas de teclas presas e implementa modo contínuo/pulso correto.
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
        "f1": Key.f1,
        "f2": Key.f2,
        "f3": Key.f3,
        "f4": Key.f4,
        "f5": Key.f5,
        "f6": Key.f6,
        "f7": Key.f7,
        "f8": Key.f8,
        "f9": Key.f9,
        "f10": Key.f10,
        "f11": Key.f11,
        "f12": Key.f12,
        "print": Key.print_screen,
        "scrolllock": Key.scroll_lock,
        "pause": Key.pause,
        "numlock": Key.num_lock,
        "capslock": Key.caps_lock,
    }

    def __init__(self):
        self.kb = KeyboardController()
        self.mouse = MouseController()

        # Estado atual das teclas pressionadas: {key_name: last_press_time}
        self._pressed_keys = {}
        self._pressed_mouse = set()

        # Lock para thread-safety (RLock permite reentrância, evita deadlock)
        self._lock = threading.RLock()

        # Controle de gestos anteriores para detectar mudanças
        self._last_left_gesture = "NEUTRO"
        self._last_right_gesture = "NEUTRO"

        # Controle de pulso (clique único)
        self._pulse_fired = {}  # {gesture_id: True} - evita repetir pulso

        # Posição suavizada do mouse
        self._mouse_x = None
        self._mouse_y = None

        # Thread de watchdog para soltar teclas presas
        self._watchdog_running = False
        self._watchdog_thread = None

        # Contador de frames para moduladores (evita repetir muito rápido)
        self._frame_counter = 0

    def start_watchdog(self):
        """Inicia thread que monitora e solta teclas presas."""
        self._watchdog_running = True
        self._watchdog_thread = threading.Thread(target=self._watchdog_loop, daemon=True)
        self._watchdog_thread.start()

    def stop_watchdog(self):
        """Para a thread de watchdog."""
        self._watchdog_running = False

    def _watchdog_loop(self):
        """Loop que verifica periodicamente se há teclas pressionadas há muito tempo."""
        while self._watchdog_running:
            time.sleep(0.1)  # Verifica a cada 100ms
            with self._lock:
                now = time.time()
                timeout_secs = KEY_RELEASE_TIMEOUT / 1000.0
                stale_keys = [
                    k for k, t in self._pressed_keys.items()
                    if (now - t) > timeout_secs
                ]
                for key in stale_keys:
                    key_obj = self._resolve_key(key)
                    if key_obj is not None:
                        try:
                            self.kb.release(key_obj)
                        except Exception:
                            pass
                    self._pressed_keys.pop(key, None)

    def _resolve_key(self, key_name):
        """Converte nome de tecla para objeto Key do pynput."""
        if not key_name:
            return None
        key_name = key_name.lower().strip()

        # Tecla especial
        if key_name in self.SPECIAL_KEYS:
            return self.SPECIAL_KEYS[key_name]

        # Tecla alfanumérica simples (ex: 'a', '1', '-')
        if len(key_name) == 1:
            return key_name

        return None

    def _press_key(self, key_name):
        """Pressiona uma tecla se não estiver já pressionada. Thread-safe."""
        with self._lock:
            if key_name in self._pressed_keys:
                # Atualiza timestamp para manter viva
                self._pressed_keys[key_name] = time.time()
                return

            key = self._resolve_key(key_name)
            if key is None:
                return

            try:
                self.kb.press(key)
                self._pressed_keys[key_name] = time.time()
            except Exception:
                pass

    def _release_key(self, key_name):
        """Solta uma tecla específica. Thread-safe."""
        with self._lock:
            if key_name not in self._pressed_keys:
                return

            key = self._resolve_key(key_name)
            if key is None:
                self._pressed_keys.pop(key_name, None)
                return

            try:
                self.kb.release(key)
            except Exception:
                pass
            finally:
                self._pressed_keys.pop(key_name, None)

    def release_all_keys(self, side="all"):
        """Solta todas as teclas. side pode ser 'left', 'right' ou 'all'. Thread-safe."""
        with self._lock:
            keys_to_release = list(self._pressed_keys.keys())
            for key in keys_to_release:
                # Evita double-lock já que _release_key também pega o lock
                key_obj = self._resolve_key(key)
                if key_obj is not None:
                    try:
                        self.kb.release(key_obj)
                    except Exception:
                        pass
                self._pressed_keys.pop(key, None)

            # Sempre solta modificadores de segurança
            for mod in [Key.ctrl, Key.ctrl_l, Key.ctrl_r,
                        Key.shift, Key.shift_l, Key.shift_r,
                        Key.alt, Key.alt_l, Key.alt_r]:
                try:
                    self.kb.release(mod)
                except Exception:
                    pass

    def _press_mouse(self, button_name):
        """Pressiona botão do mouse. Thread-safe."""
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
        """Solta botão do mouse. Thread-safe."""
        with self._lock:
            if button_name not in self._pressed_mouse:
                return

            button = Button.left if button_name == "mouse_left" else Button.right
            try:
                self.mouse.release(button)
            except Exception:
                pass
            finally:
                self._pressed_mouse.discard(button_name)

    def release_all_mouse(self):
        """Solta todos os botões do mouse. Thread-safe."""
        with self._lock:
            for btn in list(self._pressed_mouse):
                button = Button.left if btn == "mouse_left" else Button.right
                try:
                    self.mouse.release(button)
                except Exception:
                    pass
            self._pressed_mouse.clear()
            # Garantia extra
            try:
                self.mouse.release(Button.left)
                self.mouse.release(Button.right)
            except Exception:
                pass

    def release_all(self):
        """Solta TUDO (teclas + mouse)."""
        self.release_all_keys()
        self.release_all_mouse()
        self._pulse_fired.clear()

    # =====================================================================
    # AÇÕES DAS MÃOS
    # =====================================================================

    def aplicar_acao_mao_esquerda(self, config, gesture_id):
        """
        Processa a ação da mão esquerda baseada no gesto detectado.
        Retorna texto descrevendo a ação aplicada.
        """
        cfg = config.get("left", {})
        action_cfg = cfg.get(gesture_id, {"acao": None, "continuo": True})
        key = action_cfg.get("acao")
        is_continuous = action_cfg.get("continuo", True)

        if gesture_id == "NEUTRO" or not key:
            # Solta todas as teclas da mão esquerda quando vai para neutro
            self.release_all_keys()
            self._pulse_fired.pop("left", None)
            return "Nenhum"

        if is_continuous:
            # MODO CONTÍNUO: segura a tecla enquanto o gesto estiver ativo
            self._press_key(key)
            return f"Segurando: {key.upper()}"
        else:
            # MODO PULSO: dá um clique único na transição
            pulse_key = f"left_{gesture_id}"
            if not self._pulse_fired.get(pulse_key, False):
                self._pulse_fired[pulse_key] = True
                # Dá um tap rápido
                self._tap_key(key)
                return f"Clique: {key.upper()}"
            return f"Aguardando..."

    def aplicar_acao_mao_direita(self, config, gesture_id):
        """
        Processa a ação da mão direita baseada no gesto detectado.
        A mão direita também controla o mouse.
        """
        cfg = config.get("right", {})
        action_cfg = cfg.get(gesture_id, {"acao": None, "continuo": True})
        key = action_cfg.get("acao")
        is_continuous = action_cfg.get("continuo", True)

        if gesture_id == "NEUTRO" or not key:
            self.release_all_mouse()
            # Não solta teclas aqui para não interferir com a mão esquerda
            self._pulse_fired.pop("right", None)
            return "Nenhum"

        # Se for ação de mouse
        if key in ("mouse_left", "mouse_right"):
            self._press_mouse(key)
            return "Clique Mouse"

        # Se for tecla de teclado
        if is_continuous:
            self._press_key(key)
            return f"Segurando: {key.upper()}"
        else:
            pulse_key = f"right_{gesture_id}"
            if not self._pulse_fired.get(pulse_key, False):
                self._pulse_fired[pulse_key] = True
                self._tap_key(key)
                return f"Clique: {key.upper()}"
            return f"Aguardando..."

    def _tap_key(self, key_name, duration=0.05):
        """Dá um tap rápido em uma tecla (press + release após duration).
        Executa em thread separada para não bloquear o loop principal."""
        def _do_tap():
            key = self._resolve_key(key_name)
            if key is None:
                return
            try:
                self.kb.press(key)
                time.sleep(duration)
                self.kb.release(key)
            except Exception:
                pass

        t = threading.Thread(target=_do_tap, daemon=True)
        t.start()

    # =====================================================================
    # MOUSE
    # =====================================================================

    def mover_mouse_pela_palma(self, landmarks):
        """Move o mouse baseado na posição da palma, com suavização."""
        import pyautogui

        # Ponto de referência: base do polegar (landmark 0 = pulso, 9 = base médio)
        palm_x = landmarks[9].x
        palm_y = landmarks[9].y

        # Converte posição normalizada para coordenadas da tela
        screen_w, screen_h = pyautogui.size()

        # Mapeia a área ativa do mouse
        rel_x = (palm_x - MOUSE_AREA_X_MIN) / (MOUSE_AREA_X_MAX - MOUSE_AREA_X_MIN)
        rel_y = (palm_y - MOUSE_AREA_Y_MIN) / (MOUSE_AREA_Y_MAX - MOUSE_AREA_Y_MIN)

        rel_x = max(0.0, min(1.0, rel_x))
        rel_y = max(0.0, min(1.0, rel_y))

        target_x = int(rel_x * screen_w)
        target_y = int(rel_y * screen_h)

        # Suavização exponencial
        if self._mouse_x is None:
            self._mouse_x = target_x
            self._mouse_y = target_y
        else:
            self._mouse_x += SMOOTH_FACTOR * (target_x - self._mouse_x)
            self._mouse_y += SMOOTH_FACTOR * (target_y - self._mouse_y)

        try:
            pyautogui.moveTo(int(self._mouse_x), int(self._mouse_y), duration=0)
        except Exception:
            pass

    # =====================================================================
    # GERENCIAMENTO DE TRANSIÇÕES
    # =====================================================================

    def processar_transicao_esquerda(self, config, gesture_id):
        """
        Processa a transição de gesto da mão esquerda.
        Retorna (texto_acao, texto_gesto).
        """
        if gesture_id != self._last_left_gesture:
            # Mudou de gesto: solta teclas anteriores e reseta pulso
            self.release_all_keys()
            self._pulse_fired.pop("left", None)
            # Limpa pulses específicos da mão esquerda
            for k in list(self._pulse_fired.keys()):
                if k.startswith("left_"):
                    del self._pulse_fired[k]
            self._last_left_gesture = gesture_id

        if gesture_id == "NEUTRO":
            return "Nenhum", "Neutro"

        acao_texto = self.aplicar_acao_mao_esquerda(config, gesture_id)
        gesto_texto = {
            "1_DEDO": "1 dedo", "2_DEDOS": "2 dedos",
            "3_DEDOS": "3 dedos", "4_DEDOS": "4 dedos",
            "PINCA_INDICADOR": "Pinça Ind.", "PINCA_MEDIO": "Pinça Méd.",
            "PINCA_ANELAR": "Pinça Ane.", "PINCA_MINIMO": "Pinça Mín."
        }.get(gesture_id, gesture_id)

        return acao_texto, gesto_texto

    def processar_transicao_direita(self, config, gesture_id):
        """
        Processa a transição de gesto da mão direita.
        Retorna (texto_acao, texto_gesto).
        """
        if gesture_id != self._last_right_gesture:
            # Mudou de gesto: solta mouse e reseta pulso
            self.release_all_mouse()
            for k in list(self._pulse_fired.keys()):
                if k.startswith("right_"):
                    del self._pulse_fired[k]
            self._last_right_gesture = gesture_id

        if gesture_id == "NEUTRO":
            return "Nenhum", "Neutro"

        acao_texto = self.aplicar_acao_mao_direita(config, gesture_id)
        gesto_texto = {
            "1_DEDO": "1 dedo", "2_DEDOS": "2 dedos",
            "3_DEDOS": "3 dedos", "4_DEDOS": "4 dedos",
            "PINCA_INDICADOR": "Pinça Ind.", "PINCA_MEDIO": "Pinça Méd.",
            "PINCA_ANELAR": "Pinça Ane.", "PINCA_MINIMO": "Pinça Mín."
        }.get(gesture_id, gesture_id)

        return acao_texto, gesto_texto

    def on_mao_sumiu(self, side):
        """Chamado quando uma mão some da tela."""
        if side == "left":
            if self._last_left_gesture != "NEUTRO":
                self.release_all_keys()
                self._last_left_gesture = "NEUTRO"
        elif side == "right":
            if self._last_right_gesture != "NEUTRO":
                self.release_all_mouse()
                self._last_right_gesture = "NEUTRO"
