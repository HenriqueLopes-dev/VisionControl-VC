# =========================================================================
# VisionControl - Main (Otimizado)
# =========================================================================
import cv2
import mediapipe as mp
import time

from config import (
    CAMERA_WIDTH, CAMERA_HEIGHT, DEBOUNCE_FRAMES, PINCH_DISTANCE,
    SIMPLE_ZONE_LABELS
)
from gestos import detectar_gesto
from controles import InputController

# Resolucao interna reduzida para processamento mais rapido
PROC_W = 320
PROC_H = 240

# WND_PROP_TOPMOST pode nao existir em builds antigas do OpenCV
_WND_PROP_TOPMOST = getattr(cv2, 'WND_PROP_TOPMOST', 5)


class VisionControlApp:
    """Aplicacao principal com processamento otimizado."""

    def __init__(self, config):
        self.config = config
        self.settings = config.get("settings", {})

        # Configuracoes dinamicas
        self.exibir_camera = self.settings.get("exibir_camera", True)
        self.camera_topmost = self.settings.get("camera_topmost", True)
        self.camera_id = self.settings.get("camera_id", 0)
        self.debounce_frames = self.settings.get("debounce_frames", DEBOUNCE_FRAMES)
        self.pinch_distance = self.settings.get("pinch_distance", PINCH_DISTANCE)
        self.modo_simples_ativado = config.get("modo_simples_ativado", False)
        self.config_simples = config.get("simples", {})

        # Atualiza o modulo gestos com a distancia de pinca customizada
        import gestos
        gestos.PINCH_DISTANCE = self.pinch_distance

        # Input controller com settings
        self.input_ctrl = InputController(self.settings)

        # MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6,
            model_complexity=0
        )

        # Camera
        self.cap = cv2.VideoCapture(self.camera_id)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        # Estado
        self.running = True
        self.frame_count = 0
        self.skip_frames = 1

        # Tolerancia a perda de mao (frames)
        self.HAND_LOST_THRESHOLD = 5
        self.left_lost_frames = 0
        self.right_lost_frames = 0

        # Debounce de gestos
        self.buffer_left = {"gesto": "NEUTRO", "frames": 0, "confirmed": "NEUTRO"}
        self.buffer_right = {"gesto": "NEUTRO", "frames": 0, "confirmed": "NEUTRO"}

        # HUD
        self.hud_left_gesto = "Neutro"
        self.hud_left_acao = "Nenhum"
        self.hud_right_gesto = "Neutro"
        self.hud_right_acao = "Nenhum"
        self.simple_zone_ativa = {z: False for z in SIMPLE_ZONE_LABELS}
        self.simple_zone_hover = {z: False for z in SIMPLE_ZONE_LABELS}

        # FPS
        self.fps = 0
        self.fps_last_time = time.time()
        self.fps_counter = 0

        # Landmarks para desenho (evita flickering entre frames processados)
        self.last_hand_landmarks = []

        # Zonas do Modo Simples (normalizadas 0-1)
        self.SIMPLE_ZONES = {
            "S_CIMA": {"x_min": 0.28, "x_max": 0.72, "y_min": 0.02, "y_max": 0.22},
            "S_BAIXO": {"x_min": 0.28, "x_max": 0.72, "y_min": 0.78, "y_max": 0.98},
            "S_ESQUERDA": {"x_min": 0.02, "x_max": 0.22, "y_min": 0.28, "y_max": 0.72},
            "S_DIREITA": {"x_min": 0.78, "x_max": 0.98, "y_min": 0.28, "y_max": 0.72},
        }

    def start(self):
        print("=" * 50)
        print("VisionControl iniciado!")
        print(f"Camera ID: {self.camera_id}")
        print(f"Exibir camera: {self.exibir_camera}")
        print(f"Topmost: {self.camera_topmost}")
        print(f"Debounce: {self.debounce_frames} frames")
        print(f"Dist. pinca: {self.pinch_distance}")
        if self.modo_simples_ativado:
            print("MODO SIMPLES ATIVO (gestos e mouse desativados)")
        else:
            print("Punho fechado = neutro")
            print("Mao direita = mouse + acoes")
        print("ESC na janela para fechar | CTRL + C no terminal")
        print("=" * 50)

        self.input_ctrl.start_watchdog()

        # Cria janela e configura topmost ANTES do loop
        if self.exibir_camera:
            cv2.namedWindow("VisionControl", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("VisionControl", 480, 360)

        try:
            if not self.cap.isOpened():
                print("ERRO: Nao foi possivel abrir a camera.")
                print("Verifique se a camera esta conectada e nao esta em uso por outro aplicativo.")
                return
            self._main_loop()
        except KeyboardInterrupt:
            print("\nEncerrando pelo terminal...")
        finally:
            self.shutdown()

    def _main_loop(self):
        print("Loop principal iniciado.")
        while self.running and self.cap.isOpened():
            success, frame = self.cap.read()
            if not success:
                continue

            frame = cv2.flip(frame, 1)
            frame_h, frame_w = frame.shape[:2]

            # FPS counter
            self.fps_counter += 1
            now = time.time()
            if now - self.fps_last_time >= 1.0:
                self.fps = self.fps_counter
                self.fps_counter = 0
                self.fps_last_time = now

            # Processa gestos
            self.frame_count += 1
            if self.frame_count % (self.skip_frames + 1) == 0:
                self._process_frame(frame, frame_w, frame_h)

            # Exibicao
            if self.exibir_camera:
                self._draw_hud(frame, frame_w, frame_h)
                cv2.imshow("VisionControl", frame)
                if self.camera_topmost:
                    cv2.setWindowProperty("VisionControl", _WND_PROP_TOPMOST, 1)
                if cv2.waitKey(1) & 0xFF == 27:
                    self.running = False
                    break
            else:
                cv2.waitKey(1)

    def _process_frame(self, frame, frame_w, frame_h):
        # Reduz frame para processamento mais rapido
        small = cv2.resize(frame, (PROC_W, PROC_H))
        rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)

        self.last_hand_landmarks = []

        if self.modo_simples_ativado:
            zonas = {z: False for z in SIMPLE_ZONE_LABELS}
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    landmarks = hand_landmarks.landmark
                    self.last_hand_landmarks.append(hand_landmarks)
                    cx = sum(lm.x for lm in landmarks) / len(landmarks)
                    cy = sum(lm.y for lm in landmarks) / len(landmarks)
                    for zone_id, rect in self.SIMPLE_ZONES.items():
                        if rect["x_min"] <= cx <= rect["x_max"] and rect["y_min"] <= cy <= rect["y_max"]:
                            zonas[zone_id] = True
            self.simple_zone_hover = zonas
            self.input_ctrl.tick_modo_simples(self.config_simples, zonas)
            return

        has_left = False
        has_right = False
        left_gesture_raw = "NEUTRO"
        right_gesture_raw = "NEUTRO"

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                landmarks = hand_landmarks.landmark
                wrist_x = landmarks[0].x
                gesture = detectar_gesto(landmarks)

                self.last_hand_landmarks.append(hand_landmarks)

                if wrist_x > 0.5:
                    has_right = True
                    right_gesture_raw = gesture
                    self.input_ctrl.mover_mouse_pela_palma(landmarks)
                else:
                    has_left = True
                    left_gesture_raw = gesture

        # Debounce
        confirmed_left = self._debounce(self.buffer_left, left_gesture_raw)
        confirmed_right = self._debounce(self.buffer_right, right_gesture_raw)

        # Aplica acoes a CADA frame (modo continuo funciona assim)
        if has_left:
            self.left_lost_frames = 0
            acao, gesto = self.input_ctrl.tick_mao_esquerda(self.config, confirmed_left)
            self.hud_left_acao = acao
            self.hud_left_gesto = gesto
        else:
            self.left_lost_frames += 1
            if self.left_lost_frames < self.HAND_LOST_THRESHOLD:
                active = self.buffer_left["confirmed"]
                if active != "NEUTRO":
                    acao, gesto = self.input_ctrl.tick_mao_esquerda(self.config, active)
                    self.hud_left_acao = acao
                    self.hud_left_gesto = gesto
            else:
                if self.buffer_left["confirmed"] != "NEUTRO":
                    confirmed_left = self._debounce(self.buffer_left, left_gesture_raw)
                    if self.buffer_left["confirmed"] == "NEUTRO":
                        self.input_ctrl.on_mao_sumiu("left")
                        self.hud_left_acao = "Nenhum"
                        self.hud_left_gesto = "Neutro"

        if has_right:
            self.right_lost_frames = 0
            acao, gesto = self.input_ctrl.tick_mao_direita(self.config, confirmed_right)
            self.hud_right_acao = acao
            self.hud_right_gesto = gesto
        else:
            self.right_lost_frames += 1
            if self.right_lost_frames < self.HAND_LOST_THRESHOLD:
                active = self.buffer_right["confirmed"]
                if active != "NEUTRO":
                    acao, gesto = self.input_ctrl.tick_mao_direita(self.config, active)
                    self.hud_right_acao = acao
                    self.hud_right_gesto = gesto
            else:
                if self.buffer_right["confirmed"] != "NEUTRO":
                    confirmed_right = self._debounce(self.buffer_right, right_gesture_raw)
                    if self.buffer_right["confirmed"] == "NEUTRO":
                        self.input_ctrl.on_mao_sumiu("right")
                        self.hud_right_acao = "Nenhum"
                        self.hud_right_gesto = "Neutro"

    def _debounce(self, buffer, raw_gesture):
        if raw_gesture == buffer["gesto"]:
            buffer["frames"] += 1
        else:
            buffer["gesto"] = raw_gesture
            buffer["frames"] = 1

        if buffer["frames"] >= self.debounce_frames:
            buffer["confirmed"] = raw_gesture
            return raw_gesture

        return buffer.get("confirmed", "NEUTRO")

    def _draw_hud(self, frame, frame_w, frame_h):
        # Desenha landmarks salvos (executa todo frame, sem flickering)
        for hand_landmarks in self.last_hand_landmarks:
            self.mp_draw.draw_landmarks(
                frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS,
                self.mp_draw.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=3),
                self.mp_draw.DrawingSpec(color=(0, 165, 255), thickness=2)
            )

        if self.modo_simples_ativado:
            self._draw_simple_zones(frame, frame_w, frame_h)
            return

        # Overlay escuro para melhor legibilidade
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (frame_w, 85), (0, 0, 0), -1)
        cv2.rectangle(overlay, (0, frame_h - 30), (frame_w, frame_h), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)

        # Linha divisoria branca
        mid_x = frame_w // 2
        cv2.line(frame, (mid_x, 0), (mid_x, 85), (255, 255, 255), 2)

        white = (255, 255, 255)

        # Cabeçalhos
        cv2.putText(frame, "MAO ESQUERDA", (10, 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, white, 2)
        cv2.putText(frame, "MAO DIREITA", (mid_x + 10, 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, white, 2)

        # Info esquerda
        cv2.putText(frame, f"Gesto: {self.hud_left_gesto}", (10, 45),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, white, 1)
        cv2.putText(frame, f"Acao: {self.hud_left_acao}", (10, 68),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, white, 1)

        # Info direita
        cv2.putText(frame, f"Gesto: {self.hud_right_gesto}", (mid_x + 10, 45),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, white, 1)
        cv2.putText(frame, f"Acao: {self.hud_right_acao}", (mid_x + 10, 68),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, white, 1)

        # Barra inferior
        cv2.putText(frame, f"FPS: {self.fps}", (10, frame_h - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, white, 1)
        cv2.putText(frame, "ESC para sair", (frame_w - 110, frame_h - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)

    def _draw_simple_zones(self, frame, frame_w, frame_h):
        """Desenha as 4 zonas do Modo Simples na tela com 1 overlay unico."""
        overlay = frame.copy()

        for zone_id in SIMPLE_ZONE_LABELS:
            z = self.SIMPLE_ZONES[zone_id]
            x1 = int(z["x_min"] * frame_w)
            x2 = int(z["x_max"] * frame_w)
            y1 = int(z["y_min"] * frame_h)
            y2 = int(z["y_max"] * frame_h)

            is_active = self.simple_zone_hover.get(zone_id, False)
            color = (0, 255, 0) if is_active else (50, 50, 50)

            cv2.rectangle(overlay, (x1, y1), (x2, y2), color, -1)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            cfg = self.config_simples.get(zone_id, {})
            key = cfg.get("acao")
            label = SIMPLE_ZONE_LABELS[zone_id]
            if key:
                label += f" [{key.upper()}]"
            text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
            tx = (x1 + x2 - text_size[0]) // 2
            ty = (y1 + y2 + 5) // 2
            cv2.putText(frame, label, (tx, ty),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)

        white = (255, 255, 255)
        cv2.putText(frame, "MODO SIMPLES", (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        cv2.putText(frame, f"FPS: {self.fps}", (10, frame_h - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, white, 1)
        cv2.putText(frame, "ESC para sair", (frame_w - 110, frame_h - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)

    def shutdown(self):
        print("Desligando...")
        self.running = False
        self.input_ctrl.stop_watchdog()
        self.input_ctrl.release_all()
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        self.hands.close()
        print("VisionControl encerrado.")


# =========================================================================
# ENTRY POINT
# =========================================================================
if __name__ == "__main__":
    from config import abrir_hub_configuracao

    config = abrir_hub_configuracao()
    if config is None:
        print("VisionControl cancelado pelo usuario.")
        raise SystemExit

    app = VisionControlApp(config)
    app.start()
