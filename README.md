# 🎮 VisionControl

Sistema de controle de jogos utilizando Visão Computacional.

O projeto utiliza uma webcam para capturar os movimentos das mãos do usuário e traduzir gestos em comandos de teclado e mouse, permitindo controlar jogos sem o uso de periféricos tradicionais.

A proposta é criar uma solução genérica, capaz de funcionar com diferentes jogos de computador sem necessidade de alteração interna no jogo. O sistema interpreta os gestos em tempo real e simula entradas de teclado e mouse.

---

## 📌 Objetivo

Desenvolver um sistema capaz de reconhecer gestos das mãos por meio da câmera e convertê-los em comandos utilizados em jogos digitais.

O sistema pode ser utilizado em jogos que aceitam comandos de teclado e mouse, como:

- Minecraft
- Call of Duty
- GTA
- Jogos de corrida
- Jogos de plataforma
- Outros jogos para PC

---

## 🚀 Funcionalidades

- Detecção de mãos em tempo real
- Reconhecimento de gestos por quantidade de dedos
- Reconhecimento de pinças entre polegar e dedos
- Simulação de teclado
- Simulação de mouse
- Controle do cursor pela mão direita
- Mouse funcionando continuamente enquanto comandos são executados
- Hub inicial para configurar os comandos antes de iniciar o controle
- Mão fechada configurada como gesto neutro
- Exibição opcional da câmera para testes e depuração

---

## 🧠 Como Funciona

Ao iniciar o programa, é aberto um hub de configuração.

Nesse hub, o usuário pode escolher qual tecla ou ação será executada para cada gesto.

Depois de iniciar o VisionControl, a câmera passa a reconhecer duas áreas principais:

- **Mão esquerda:** comandos principais de teclado
- **Mão direita:** controle do mouse e ações extras

A tela da câmera é dividida em duas zonas:

| Zona | Função |
|---|---|
| Lado esquerdo | Comandos de teclado |
| Lado direito | Mouse e ações adicionais |

---

## ✋ Gesto Neutro

A mão fechada não executa nenhuma ação.

Isso evita comandos acidentais durante o jogo, já que abrir e fechar a mão naturalmente poderia atrapalhar a jogabilidade.

| Gesto | Ação |
|---|---|
| Mão fechada | Neutro |

---

## 🕹️ Mão Esquerda — Comandos Principais

Por padrão, a mão esquerda é usada para os comandos principais de movimentação e ações do jogo.

| Gesto | Comando padrão |
|---|---|
| Mão fechada | Neutro |
| 1 dedo aberto | W |
| 2 dedos abertos | A |
| 3 dedos abertos | D |
| 4 dedos abertos | S |
| Pinça polegar + indicador | Espaço |
| Pinça polegar + médio | Shift esquerdo |
| Pinça polegar + anelar | Ctrl esquerdo |
| Pinça polegar + mínimo | E |

---

## 🖱️ Mão Direita — Mouse e Ações

A mão direita controla o mouse continuamente.

O movimento do cursor é feito pelo centro da palma da mão, permitindo que o jogador continue mirando mesmo enquanto executa cliques ou comandos.

| Gesto | Ação padrão |
|---|---|
| Movimento da palma | Movimento do mouse |
| Mão fechada | Neutro |
| Pinça polegar + indicador | Clique esquerdo |
| Pinça polegar + médio | Clique direito |
| 2 dedos abertos | R |
| 3 dedos abertos | TAB |
| 4 dedos abertos | 1 |
| Pinça polegar + anelar | 2 |
| Pinça polegar + mínimo | 3 |

---

## 🎯 Exemplo de Uso em Jogos

Em um jogo de tiro, por exemplo:

- A mão direita controla a mira
- A pinça com indicador executa o clique esquerdo para atirar
- A mira continua funcionando mesmo durante o clique
- A mão esquerda pode controlar movimentação com W, A, S e D
- Outros gestos podem ser usados para pular, correr, recarregar ou trocar de arma

---

## ⚙️ Hub de Configuração

Antes do controle começar, o sistema abre uma janela de configuração.

Nessa janela, o usuário pode alterar os comandos associados a cada gesto.

Teclas disponíveis no hub:

- W
- A
- S
- D
- E
- R
- TAB
- 1
- 2
- 3
- 4
- Espaço
- Ctrl esquerdo
- Shift esquerdo
- Alt esquerdo

A mão direita também permite configurar:

- Clique esquerdo
- Clique direito

---

## 🛠 Tecnologias Utilizadas

- Python 3.11
- OpenCV
- MediaPipe
- PyAutoGUI
- PyDirectInput
- Tkinter

---

## 📦 Clonando o Projeto

Clone o repositório:

```bash
git clone https://github.com/SEU-USUARIO/visioncontrol.git
```

Entre na pasta do projeto:

```bash
cd visioncontrol
```

---

## 🐍 Criando a Virtual Environment

É recomendado utilizar uma virtual environment para evitar conflito com outros projetos Python.

### Windows

Crie a venv:

```bash
python -m venv venv
```

Ative a venv:

```bash
venv\Scripts\activate
```

Após ativar, o terminal deve ficar parecido com:

```bash
(venv) C:\Projetos\visioncontrol>
```

---

## 📥 Instalando as Dependências

Com a venv ativada, instale os pacotes necessários:

```bash
pip install -r requirements.txt
```

---

## 📄 requirements.txt

O arquivo `requirements.txt` deve conter:

```txt
opencv-python==4.10.0.84
mediapipe==0.10.14
pydirectinput==1.0.4
pyautogui==0.9.54
```

---

## ▶️ Executando o Projeto

Com a venv ativada, execute:

```bash
python main.py
```

Ao iniciar, o hub de configuração será aberto.

Depois de configurar os comandos, clique em:

```txt
Iniciar VisionControl
```

---

## 👨‍💻 Equipe

- Caio Henrique Carvalho de Paiva
- Luiz Felipe Loro Piva
- Flavio de Carvalho Cury
- Henrique Luiz de Almeida Lopes

---

## 📄 Licença

Projeto desenvolvido para fins acadêmicos.
