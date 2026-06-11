# VisionControl - Controle de Jogos por Gestos

Controle jogos usando a webcam e gestos das maos, com deteccao via MediaPipe.

## Instalacao

```bash
pip install -r requirements.txt
```

## Como usar

```bash
python main.py
```

### Passo 1: Configurar gestos

Na aba **Mao Esquerda** e **Mao Direita**:
- **Clique no botao da tecla** e pressione a tecla desejada (ESC limpa)
- Use os botoes **Esq / Dir** para configurar cliques do mouse
- **"Segurar" marcado**: a tecla fica pressionada enquanto o gesto estiver ativo (modo continuo)
- **"Segurar" desmarcado**: a tecla da um unico clique na transicao do gesto (modo pulso)

### Passo 2: Ajustar configuracoes

Na aba **Configuracoes**:

| Opcao | Descricao |
|-------|-----------|
| **Exibir janela da camera** | Liga/desliga a visualizacao da camera |
| **Camera sempre por cima** | Janela fica sobre todas as outras (jogos em tela cheia) |
| **Camera ID** | Seleciona qual camera usar (0, 1, 2...) |
| **Sensib. Mouse** | Quanto maior, mais rapido o mouse se move (0.05 a 1.0) |
| **Debounce** | Frames necessarios para confirmar um gesto (1-10) |
| **Dist. Pinca** | Distancia para detectar pinca (menor = mais preciso) |
| **Timeout** | Tempo para soltar tecla automaticamente se travar (ms) |

### Passo 3: Iniciar

Clique em **Iniciar VisionControl**. A janela da camera aparecera em um canto.

## Controles durante o jogo

| | Mao Esquerda (lado esquerdo da camera) | Mao Direita (lado direito da camera) |
|---|---|---|
| **1 dedo** | W (frente) | - |
| **2 dedos** | A (esquerda) | R |
| **3 dedos** | D (direita) | Tab |
| **4 dedos** | S (tras) | 1 |
| **Pinca Indicador** | Espaco | Clique Esquerdo Mouse |
| **Pinca Medio** | Shift | Clique Direito Mouse |
| **Pinca Anelar** | Ctrl | 2 |
| **Pinca Minimo** | E | 3 |
| **Punho fechado** | Neutro (sem acao) | Neutro (sem acao) |

- A **mao direita** sempre controla o mouse, independente do gesto
- O sistema usa **debounce** para evitar acionamentos acidentais
- **Teclas modificadoras** (Ctrl, Shift, Alt) tem protecao anti-trava

## Dicas

- **Para movimentacao** (WASD): mantenha "Segurar" marcado - as teclas ficam pressionadas enquanto voce mantem o gesto
- **Para acoes unicas** (recarregar, trocar arma): desmarque "Segurar" - a tecla clica uma vez por gesto
- Ajuste o **Debounce** se o controle estiver alternando gestos rapido demais
- Ajuste a **Sensib. Mouse** se o cursor estiver muito lento ou rapido
- Ative **"Camera por cima"** para ver a camera enquanto joga em tela cheia

## Encerramento

- **ESC** na janela da camera, ou
- **CTRL + C** no terminal

Todas as teclas e botoes do mouse sao soltos automaticamente.

## Dependencias

- `opencv-python` - Captura e exibicao da camera
- `mediapipe` - Deteccao de maos e gestos
- `pynput` - Controle de teclado e mouse (mais robusto que pydirectinput)
- `pyautogui` - Movimento do mouse
