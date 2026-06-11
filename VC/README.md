# VisionControl - Controle de Jogos por Gestos (Refatorado)

Controle jogos usando a webcam e gestos das mãos, com detecção via MediaPipe.

## O que mudou nesta versão

### Problemas corrigidos
- **Teclas especiais (Ctrl/Shift/Alt) nao ficam mais presas** - Sistema de watchdog monitora e solta automaticamente
- **Modo Continuo vs Pulso funciona corretamente** - Checkbox "Segurar" na configuracao controla o comportamento
- **Performance otimizada** - Frame skipping, model_complexity=0, e processamento eficiente
- **Arquitetura limpa** - Codigo reorganizado em classes com responsabilidade unica
- **Debounce robusto** - Gestos precisam ser confirmados por N frames antes de ativar
- **Failsafe automatico** - Teclas sao soltas apos timeout se algo der errado

## Instalacao

```bash
pip install -r requirements.txt
```

## Como usar

1. Execute:
```bash
python main.py
```

2. Configure os gestos na interface que abrir:
   - **Clique no botao da tecla** e pressione a tecla desejada
   - **ESC** limpa a tecla
   - **"Segurar"** marcado = tecla fica pressionada enquanto o gesto estiver ativo
   - **"Segurar"** desmarcado = tecla da um unico clique na transicao do gesto
   - Use **m. Esq / m. Dir** para configurar cliques do mouse

3. Clique em **Iniciar VisionControl**

4. Na janela da camera:
   - **Mao esquerda** (lado esquerdo da tela): Comandos do jogo (WASD, etc)
   - **Mao direita** (lado direito da tela): Controla o mouse + acoes secundarias
   - **Punho fechado** = neutro (sem acao)
   - **ESC** na janela para fechar

## Configuracao dos gestos padrao

### Mao Esquerda (Movimentacao)
| Gesto | Acao Padrao | Continuo |
|-------|------------|----------|
| 1 dedo | W (frente) | Sim |
| 2 dedos | A (esquerda) | Sim |
| 3 dedos | D (direita) | Sim |
| 4 dedos | S (tras) | Sim |
| Pinca Indicador | Espaco | Sim |
| Pinca Medio | Shift | Sim |
| Pinca Anelar | Ctrl | Sim |
| Pinca Minimo | E | Sim |

### Mao Direita (Mouse + Acoes)
| Gesto | Acao Padrao | Continuo |
|-------|------------|----------|
| 1 dedo | Nenhum | - |
| 2 dedos | R | Sim |
| 3 dedos | Tab | Sim |
| 4 dedos | 1 | Sim |
| Pinca Indicador | Clique Esq Mouse | Sim |
| Pinca Medio | Clique Dir Mouse | Sim |
| Pinca Anelar | 2 | Sim |
| Pinca Minimo | 3 | Sim |

## Dicas

- Para **acoes unicas** (ex: recarregar, trocar arma), desmarque "Segurar"
- Para **movimentacao**, mantenha "Segurar" marcado
- A **mao direita** sempre controla o mouse, independente do gesto
- Posicione a camera de frente, com boa iluminacao
- A deteccao usa o lado da tela para separar mao esquerda/direita

## Encerramento seguro

- **ESC** na janela da camera, ou
- **CTRL + C** no terminal

Todas as teclas e botoes do mouse serao soltos automaticamente.
