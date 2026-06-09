import math
from config import PINCH_DISTANCE, GESTURE_LABELS

# =========================================================================
# FUNÇÕES DE GESTOS
# =========================================================================

def distance(point_a, point_b):
    return math.sqrt(
        (point_a.x - point_b.x) ** 2 +
        (point_a.y - point_b.y) ** 2
    )

def get_open_fingers(landmarks):
    indicador_aberto = landmarks[8].y < landmarks[6].y
    medio_aberto = landmarks[12].y < landmarks[10].y
    anelar_aberto = landmarks[16].y < landmarks[14].y
    minimo_aberto = landmarks[20].y < landmarks[18].y

    return {
        "indicador": indicador_aberto,
        "medio": medio_aberto,
        "anelar": anelar_aberto,
        "minimo": minimo_aberto,
    }

def detectar_gesto(landmarks):
    fingers = get_open_fingers(landmarks)

    indicador = fingers["indicador"]
    medio = fingers["medio"]
    anelar = fingers["anelar"]
    minimo = fingers["minimo"]

    finger_count = sum([
        indicador,
        medio,
        anelar,
        minimo,
    ])

    # Punho fechado é sempre neutro
    if finger_count == 0:
        return "NEUTRO"

    thumb_tip = landmarks[4]

    # Pinças têm prioridade
    if distance(thumb_tip, landmarks[8]) < PINCH_DISTANCE:
        return "PINCA_INDICADOR"

    if distance(thumb_tip, landmarks[12]) < PINCH_DISTANCE:
        return "PINCA_MEDIO"

    if distance(thumb_tip, landmarks[16]) < PINCH_DISTANCE:
        return "PINCA_ANELAR"

    if distance(thumb_tip, landmarks[20]) < PINCH_DISTANCE:
        return "PINCA_MINIMO"

    if finger_count == 1:
        return "1_DEDO"

    if finger_count == 2:
        return "2_DEDOS"

    if finger_count == 3:
        return "3_DEDOS"

    if finger_count == 4:
        return "4_DEDOS"

    return "NEUTRO"

def gesture_to_text(gesture_id):
    if gesture_id == "NEUTRO":
        return "Neutro"

    return GESTURE_LABELS.get(gesture_id, "Desconhecido")