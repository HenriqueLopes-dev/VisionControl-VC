# 🎮 VisionControl

Sistema de controle de jogos utilizando Visão Computacional.

O projeto utiliza uma webcam para capturar os movimentos das mãos do usuário e traduzir gestos em comandos de teclado e mouse, permitindo controlar jogos sem o uso de periféricos tradicionais.

## 📌 Objetivo

Desenvolver uma solução capaz de interpretar gestos em tempo real e convertê-los em ações dentro de jogos digitais.

A proposta é funcionar com qualquer jogo compatível com teclado e mouse, sem necessidade de modificações internas no jogo.

Exemplos:

- Minecraft
- Call of Duty
- GTA
- Jogos de corrida
- Jogos de plataforma
- Outros jogos para PC

---

## 🚀 Funcionalidades

### Controle de Movimento

A mão posicionada na área esquerda da câmera é responsável pelos comandos de teclado:

| Gesto | Comando |
|---------|---------|
| Punho fechado | Espaço |
| 1 dedo | W |
| 2 dedos | A |
| 3 dedos | S |
| 4 dedos | D |

### Controle de Mouse

A mão posicionada na área direita da câmera é responsável pelo mouse:

| Gesto | Ação |
|---------|---------|
| Indicador levantado | Movimento do cursor |
| Mão fechada | Clique esquerdo |
| Mão aberta | Clique direito |

### Recursos

- Rastreamento de mãos em tempo real
- Controle de mouse por movimento da mão
- Simulação de teclado
- Simulação de cliques
- Exibição opcional da câmera para depuração
- Baixa latência

---

## 🛠 Tecnologias Utilizadas

- Python 3.11
- OpenCV
- MediaPipe
- PyAutoGUI
- PyDirectInput

---

## 📦 Clonando o Projeto

Clone o repositório:

```bash
git clone https://github.com/SEU-USUARIO/visioncontrol.git
```

Entre na pasta:

```bash
cd visioncontrol
```

---

## 🐍 Criando a Virtual Environment

### Windows

Criar ambiente virtual:

```bash
python -m venv venv
```

Ativar ambiente virtual:

```bash
venv\Scripts\activate
```

Após ativar, deverá aparecer algo semelhante:

```bash
(venv) C:\Projetos\visioncontrol>
```

---

## 📥 Instalando as Dependências

Com a venv ativada:

```bash
pip install -r requirements.txt
```

---

## ▶ Executando

Com a venv ativada:

```bash
python main.py
```

---

## ⚙ Configuração

No início do arquivo existe a variável:

```python
EXIBIR_CAMERA = True
```

### True

Abre uma janela exibindo:

- câmera
- landmarks da mão
- gestos detectados

Útil para testes.

### False

Executa o reconhecimento em segundo plano.

Reduz o consumo de CPU e melhora o desempenho durante os jogos.

---

## 📋 Requisitos

- Python 3.11
- Webcam
- Windows 10 ou superior

---

## 🔒 Observações

O projeto utiliza:

- PyDirectInput
- PyAutoGUI

para simular teclado e mouse.

Alguns jogos com sistemas anti-cheat podem bloquear entradas simuladas.

---

## 👨‍💻 Equipe

- Caio Henrique Carvalho de Paiva
- Luiz Felipe Loro Piva
- Flavio de Carvalho Cury
- Henrique Luiz de Almeida Lopes

---

## 📄 Licença

Projeto desenvolvido para fins acadêmicos.