# =========================================================================
# VisionControl - Detecção de Gestos (Otimizado)
# =========================================================================
import math
from config import PINCH_DISTANCE, GESTURE_LABELS

# Índices dos landmarks do MediaPipe Hands
IDX_PONTA_INDICADOR = 8
IDX_JUNTA_INDICADOR = 6
IDX_PONTA_MEDIO = 12
IDX_JUNTA_MEDIO = 10
IDX_PONTA_ANELAR = 16
IDX_JUNTA_ANELAR = 14
IDX_PONTA_MINIMO = 20
IDX_JUNTA_MINIMO = 18
IDX_PONTA_POLEGAR = 4


def distance(point_a, point_b):
    """Calcula distância euclidiana entre dois pontos (evita sqrt quando possível)."""
    dx = point_a.x - point_b.x
    dy = point_a.y - point_b.y
    return math.sqrt(dx * dx + dy * dy)


def distance_sq(point_a, point_b):
    """Distância ao quadrado (mais rápido, para comparações)."""
    dx = point_a.x - point_b.x
    dy = point_a.y - point_b.y
    return dx * dx + dy * dy


def get_open_fingers(landmarks):
    """Verifica quais dedos (exceto polegar) estão abertos."""
    return {
        "indicador": landmarks[IDX_PONTA_INDICADOR].y < landmarks[IDX_JUNTA_INDICADOR].y,
        "medio": landmarks[IDX_PONTA_MEDIO].y < landmarks[IDX_JUNTA_MEDIO].y,
        "anelar": landmarks[IDX_PONTA_ANELAR].y < landmarks[IDX_JUNTA_ANELAR].y,
        "minimo": landmarks[IDX_PONTA_MINIMO].y < landmarks[IDX_JUNTA_MINIMO].y,
    }


def detectar_gesto(landmarks):
    """
    Detecta o gesto baseado nos landmarks da mão.
    Retorna: NEUTRO, 1_DEDO, 2_DEDOS, 3_DEDOS, 4_DEDOS,
             PINCA_INDICADOR, PINCA_MEDIO, PINCA_ANELAR, PINCA_MINIMO
    """
    fingers = get_open_fingers(landmarks)
    indicador = fingers["indicador"]
    medio = fingers["medio"]
    anelar = fingers["anelar"]
    minimo = fingers["minimo"]

    finger_count = indicador + medio + anelar + minimo

    # Punho fechado = neutro
    if finger_count == 0:
        return "NEUTRO"

    thumb_tip = landmarks[IDX_PONTA_POLEGAR]

    # Calcula distâncias ao quadrado para pinças (mais eficiente)
    d_ind_sq = distance_sq(thumb_tip, landmarks[IDX_PONTA_INDICADOR])
    d_med_sq = distance_sq(thumb_tip, landmarks[IDX_PONTA_MEDIO])
    d_ane_sq = distance_sq(thumb_tip, landmarks[IDX_PONTA_ANELAR])
    d_min_sq = distance_sq(thumb_tip, landmarks[IDX_PONTA_MINIMO])

    pinch_dist_sq = PINCH_DISTANCE * PINCH_DISTANCE

    # Verifica se alguma pinça está ativa
    if d_ind_sq < pinch_dist_sq:
        return "PINCA_INDICADOR"
    if d_med_sq < pinch_dist_sq:
        return "PINCA_MEDIO"
    if d_ane_sq < pinch_dist_sq:
        return "PINCA_ANELAR"
    if d_min_sq < pinch_dist_sq:
        return "PINCA_MINIMO"

    # Se não for pinça, conta dedos abertos
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
    """Converte ID do gesto para texto legível."""
    if gesture_id == "NEUTRO":
        return "Neutro"
    return GESTURE_LABELS.get(gesture_id, "Desconhecido")
