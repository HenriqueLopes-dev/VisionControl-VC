import cv2
import mediapipe as mp

# Importa tudo dos seus outros módulos que acabamos de criar
from config import *
from gestos import *
from controles import *

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