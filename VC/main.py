# =========================================================================
# VisionControl - Main (Otimizado)
# =========================================================================
import cv2
import mediapipe as mp
import time
import threading
import queue

from config import EXIBIR_CAMERA, CAMERA_ID, CAMERA_WIDTH, CAMERA_HEIGHT, DEBOUNCE_FRAMES
from gestos import detectar_gesto, gesture_to_text
from controles import InputController


class VisionControlApp:
    """Aplicação principal com processamento otimizado."""

    def __init__(self, config):
        self.config = config
        self.input_ctrl = InputController()

        # MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6,
            model_complexity=0  # 0=mais rápido, 1=balanceado, 2=preciso
        )

        # Câmera
        self.cap = cv2.VideoCapture(CAMERA_ID)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimiza latência

        # Estado
        self.running = True
        self.frame_count = 0
        self.skip_frames = 1  # Processa 1 frame, pula 1 (ajustável)

        # Debounce de gestos
        self.gesture_buffer_left = {"gesto": "NEUTRO", "frames": 0, "confirmed_last": "NEUTRO"}
        self.gesture_buffer_right = {"gesto": "NEUTRO", "frames": 0, "confirmed_last": "NEUTRO"}

        # Texto para HUD
        self.hud_left_gesto = "Neutro"
        self.hud_left_acao = "Nenhum"
        self.hud_right_gesto = "Neutro"
        self.hud_right_acao = "Nenhum"

        # FPS
        self.fps = 0
        self.fps_last_time = time.time()
        self.fps_counter = 0

        # Threading
        self.frame_queue = queue.Queue(maxsize=2)
        self.result_queue = queue.Queue(maxsize=2)
        self.processing_thread = None

    def start(self):
        """Inicia a aplicação."""
        print("=" * 50)
        print("VisionControl iniciado!")
        print(f"Exibir câmera: {EXIBIR_CAMERA}")
        print(f"Debounce: {DEBOUNCE_FRAMES} frames")
        print("Punho fechado = neutro")
        print("Mão direita = mouse + ações")
        print("ESC na janela para fechar")
        print("CTRL + C no terminal para encerrar")
        print("=" * 50)

        self.input_ctrl.start_watchdog()

        # Inicia thread de processamento se necessário
        # Por padrão processamos na thread principal para simplicidade
        # e evitar problemas de sincronização com OpenCV

        try:
            self._main_loop()
        except KeyboardInterrupt:
            print("\nEncerrando pelo terminal...")
        finally:
            self.shutdown()

    def _main_loop(self):
        """Loop principal otimizado."""
        while self.running and self.cap.isOpened():
            success, frame = self.cap.read()
            if not success:
                continue

            # Flip horizontal (modo espelho)
            frame = cv2.flip(frame, 1)
            frame_h, frame_w = frame.shape[:2]

            self.fps_counter += 1
            now = time.time()
            if now - self.fps_last_time >= 1.0:
                self.fps = self.fps_counter
                self.fps_counter = 0
                self.fps_last_time = now

            # Processa gestos a cada N frames para performance
            self.frame_count += 1
            if self.frame_count % (self.skip_frames + 1) == 0:
                self._process_frame(frame, frame_w, frame_h)

            # Exibição
            if EXIBIR_CAMERA:
                self._draw_hud(frame, frame_w, frame_h)
                cv2.imshow("VisionControl", frame)

                if cv2.waitKey(1) & 0xFF == 27:  # ESC
                    self.running = False
                    break
            else:
                cv2.waitKey(1)

    def _process_frame(self, frame, frame_w, frame_h):
        """Processa um frame para detectar mãos e aplicar controles."""
        # Converte para RGB (MediaPipe requer RGB)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)

        has_left = False
        has_right = False

        left_gesture_raw = "NEUTRO"
        right_gesture_raw = "NEUTRO"

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                landmarks = hand_landmarks.landmark
                wrist_x = landmarks[0].x

                gesture = detectar_gesto(landmarks)

                # Desenha landmarks (opcional, pode ser removido para mais performance)
                if EXIBIR_CAMERA:
                    self.mp_draw.draw_landmarks(
                        frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS,
                        landmark_drawing_spec=self.mp_draw.DrawingSpec(
                            color=(0, 255, 0), thickness=1, circle_radius=2
                        )
                    )

                if wrist_x > 0.5:
                    has_right = True
                    right_gesture_raw = gesture
                    # Mouse sempre segue a mão direita
                    self.input_ctrl.mover_mouse_pela_palma(landmarks)
                else:
                    has_left = True
                    left_gesture_raw = gesture

        # --- DEBOUNCE + APLICAÇÃO DE AÇÕES ---

        # Mão Esquerda
        confirmed_left = self._apply_debounce(
            self.gesture_buffer_left, left_gesture_raw
        )
        if confirmed_left != self.gesture_buffer_left["confirmed_last"]:
            self.gesture_buffer_left["confirmed_last"] = confirmed_left
            acao, gesto = self.input_ctrl.processar_transicao_esquerda(
                self.config, confirmed_left
            )
            self.hud_left_acao = acao
            self.hud_left_gesto = gesto

        # Mão Direita
        confirmed_right = self._apply_debounce(
            self.gesture_buffer_right, right_gesture_raw
        )
        if confirmed_right != self.gesture_buffer_right["confirmed_last"]:
            self.gesture_buffer_right["confirmed_last"] = confirmed_right
            acao, gesto = self.input_ctrl.processar_transicao_direita(
                self.config, confirmed_right
            )
            self.hud_right_acao = acao
            self.hud_right_gesto = gesto

        # --- MÃO SUMIU ---
        if not has_left:
            if self.gesture_buffer_left["confirmed_last"] != "NEUTRO":
                self.input_ctrl.on_mao_sumiu("left")
                self.gesture_buffer_left["confirmed_last"] = "NEUTRO"
                self.gesture_buffer_left["gesto"] = "NEUTRO"
                self.gesture_buffer_left["frames"] = 0
                self.hud_left_acao = "Nenhum"
                self.hud_left_gesto = "Neutro"

        if not has_right:
            if self.gesture_buffer_right["confirmed_last"] != "NEUTRO":
                self.input_ctrl.on_mao_sumiu("right")
                self.gesture_buffer_right["confirmed_last"] = "NEUTRO"
                self.gesture_buffer_right["gesto"] = "NEUTRO"
                self.gesture_buffer_right["frames"] = 0
                self.hud_right_acao = "Nenhum"
                self.hud_right_gesto = "Neutro"

    def _apply_debounce(self, buffer, raw_gesture):
        """
        Aplica debounce: só confirma o gesto após N frames consecutivos.
        Retorna o gesto confirmado.
        """
        if raw_gesture == buffer["gesto"]:
            buffer["frames"] += 1
        else:
            buffer["gesto"] = raw_gesture
            buffer["frames"] = 1

        if buffer["frames"] >= DEBOUNCE_FRAMES:
            return raw_gesture

        # Retorna o último confirmado se ainda não atingiu o threshold
        return buffer.get("confirmed_last", "NEUTRO")

    def _draw_hud(self, frame, frame_w, frame_h):
        """Desenha informações na tela."""
        # Linha divisória
        mid_x = frame_w // 2
        cv2.line(frame, (mid_x, 0), (mid_x, frame_h), (80, 80, 80), 1)

        # Painel esquerdo (mão esquerda)
        cv2.putText(frame, "MAO ESQUERDA", (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(frame, f"Gesto: {self.hud_left_gesto}", (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        cv2.putText(frame, f"Acao: {self.hud_left_acao}", (10, 75),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        # Painel direito (mão direita)
        cv2.putText(frame, "MAO DIREITA", (mid_x + 10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 128, 0), 2)
        cv2.putText(frame, f"Gesto: {self.hud_right_gesto}", (mid_x + 10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 128, 0), 1)
        cv2.putText(frame, f"Acao: {self.hud_right_acao}", (mid_x + 10, 75),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 128, 0), 1)

        # FPS
        cv2.putText(frame, f"FPS: {self.fps}", (10, frame_h - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        # Dica
        cv2.putText(frame, "ESC para sair", (frame_w - 130, frame_h - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)

    def shutdown(self):
        """Encerra a aplicação de forma segura."""
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
        print("VisionControl cancelado pelo usuário.")
        raise SystemExit

    app = VisionControlApp(config)
    app.start()
