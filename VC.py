import cv2
import mediapipe as mp
import pydirectinput
import pyautogui

# =========================================================================
# CONFIGURAÇÃO DE TESTE: Mude para False para esconder a câmera e poupar CPU
# =========================================================================
EXIBIR_CAMERA = True  # True = Janela aberta com pontos da mão | False = Invisível
# =========================================================================

# Desativar o fail-safe do pyautogui
pyautogui.FAILSAFE = False

# Configurações do MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)
mp_draw = mp.solutions.drawing_utils

# Resolução do monitor
screen_width, screen_height = pyautogui.size()

# Inicializa a captura da webcam
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("--------------------------------------------------")
print(f"VisionControl Iniciado! Exibir Câmera: {EXIBIR_CAMERA}")
print("Teclado (Esq): 0=Espaço | 1=W | 2=A | 3=S | 4=D")
if EXIBIR_CAMERA:
    print("Pressione 'ESC' na janela da câmera para fechar.")
else:
    print("Para fechar, clique aqui no terminal e aperte CTRL + C")
print("--------------------------------------------------")

# Estados do Teclado e Mouse
current_key = None
prev_mouse_x, prev_mouse_y = 0, 0
smooth_factor = 0.35

left_clicked = False
right_clicked = False

def release_all_keys():
    global current_key
    if current_key:
        pydirectinput.keyUp(current_key)
        current_key = None

def release_mouse_clicks():
    global left_clicked, right_clicked
    if left_clicked:
        pydirectinput.mouseUp(button='left')
        left_clicked = False
    if right_clicked:
        pydirectinput.mouseUp(button='right')
        right_clicked = False

try:
    while cap.isOpened():
        success, frame = cap.read()
        if not success: break

        frame = cv2.flip(frame, 1) 
        frame_h, frame_w, _ = frame.shape  # <-- LINHA CORRIGIDA AQUI!
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        has_left_hand = False  
        has_right_hand = False 

        keyboard_gesture = "Nenhum"
        mouse_action = "Parado"

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                if EXIBIR_CAMERA:
                    mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                landmarks = hand_landmarks.landmark
                wrist_x = landmarks[0].x

                # Estado de abertura dos 4 dedos principais
                indicador_aberto = landmarks[8].y < landmarks[6].y
                meio_aberto = landmarks[12].y < landmarks[10].y
                anelar_aberto = landmarks[16].y < landmarks[14].y
                minimo_aberto = landmarks[20].y < landmarks[18].y

                # =========================================================================
                # MÃO DIREITA (MOUSE) - Lado direito da tela (> 0.5)
                # =========================================================================
                if wrist_x > 0.5:
                    has_right_hand = True
                    
                    if indicador_aberto and not meio_aberto and not anelar_aberto and not minimo_aberto:
                        mouse_action = "Movendo Livremente"
                        release_mouse_clicks() 
                        
                        idx_x = landmarks[8].x
                        idx_y = landmarks[8].y
                        cam_box_x = (idx_x - 0.55) / 0.35
                        cam_box_y = (idx_y - 0.2) / 0.6
                        
                        cam_box_x = max(0.0, min(1.0, cam_box_x))
                        cam_box_y = max(0.0, min(1.0, cam_box_y))

                        target_mouse_x = int(cam_box_x * screen_width)
                        target_mouse_y = int(cam_box_y * screen_height)

                        mouse_x = int(prev_mouse_x + (target_mouse_x - prev_mouse_x) * smooth_factor)
                        mouse_y = int(prev_mouse_y + (target_mouse_y - prev_mouse_y) * smooth_factor)
                        
                        if abs(mouse_x - prev_mouse_x) > 3 or abs(mouse_y - prev_mouse_y) > 3:
                            pydirectinput.moveTo(mouse_x, mouse_y)
                            prev_mouse_x, prev_mouse_y = mouse_x, mouse_y

                    elif not indicador_aberto and not meio_aberto and not anelar_aberto and not minimo_aberto:
                        mouse_action = "Clique Esquerdo"
                        if not left_clicked:
                            if right_clicked: pydirectinput.mouseUp(button='right'); right_clicked = False
                            pydirectinput.mouseDown(button='left')
                            left_clicked = True

                    elif indicador_aberto and meio_aberto and anelar_aberto and minimo_aberto:
                        mouse_action = "Clique Direito"
                        if not right_clicked:
                            if left_clicked: pydirectinput.mouseUp(button='left'); left_clicked = False
                            pydirectinput.mouseDown(button='right')
                            right_clicked = True
                    else:
                        release_mouse_clicks()

                # =========================================================================
                # MÃO ESQUERDA (TECLADO) - Lado esquerdo da tela (< 0.5)
                # =========================================================================
                else:
                    has_left_hand = True

                    if not indicador_aberto and not meio_aberto and not anelar_aberto and not minimo_aberto:
                        keyboard_gesture = "Espaco"
                        if current_key != 'space':
                            release_all_keys()
                            pydirectinput.keyDown('space')
                            current_key = 'space'
                    
                    elif indicador_aberto and not meio_aberto and not anelar_aberto and not minimo_aberto:
                        keyboard_gesture = "W"
                        if current_key != 'w':
                            release_all_keys()
                            pydirectinput.keyDown('w')
                            current_key = 'w'
                            
                    elif indicador_aberto and meio_aberto and not anelar_aberto and not minimo_aberto:
                        keyboard_gesture = "A"
                        if current_key != 'a':
                            release_all_keys()
                            pydirectinput.keyDown('a')
                            current_key = 'a'
                            
                    elif indicador_aberto and meio_aberto and anelar_aberto and not minimo_aberto:
                        keyboard_gesture = "S"
                        if current_key != 's':
                            release_all_keys()
                            pydirectinput.keyDown('s')
                            current_key = 's'
                            
                    elif indicador_aberto and meio_aberto and anelar_aberto and minimo_aberto:
                        keyboard_gesture = "D"
                        if current_key != 'd':
                            release_all_keys()
                            pydirectinput.keyDown('d')
                            current_key = 'd'
                    else:
                        release_all_keys()

        if not has_left_hand: release_all_keys()
        if not has_right_hand: release_mouse_clicks()

        # Renderização condicional da janela do OpenCV
        if EXIBIR_CAMERA:
            cv2.putText(frame, f"Teclado (Esq): {keyboard_gesture}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(frame, f"Mouse (Dir): {mouse_action}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            cv2.line(frame, (frame_w // 2, 0), (frame_w // 2, frame_h), (255, 255, 255), 1)
            cv2.imshow("VisionControl - Modo Teste", frame)
            
            if cv2.waitKey(1) & 0xFF == 27: 
                break
        else:
            cv2.waitKey(1)

except KeyboardInterrupt:
    print("\nEncerrando de forma segura pelo terminal...")

# Reset e limpeza final
release_all_keys()
release_mouse_clicks()
cap.release()
cv2.destroyAllWindows()