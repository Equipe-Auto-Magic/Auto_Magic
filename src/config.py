"""
Configurações globais e constantes do jogo Auto-Magic.
"""

from pathlib import Path

# Configurações da Janela
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 720
PROJECT_ROOT = Path(__file__).resolve().parent.parent
IMG_BG_PATH = str(PROJECT_ROOT / "src" / "assets" / "images" / "backgrounds" / "bg-flore.jpg")
BACKGROUND_IMAGES = [
    str(PROJECT_ROOT / "src" / "assets" / "images" / "backgrounds" / "bg-flore.jpg"),
    str(PROJECT_ROOT / "src" / "assets" / "images" / "backgrounds" / "bg-floresta-magica.png"),
    str(PROJECT_ROOT / "src" / "assets" / "images" / "backgrounds" / "bg-floresta-noturna.png"),
    str(PROJECT_ROOT / "src" / "assets" / "images" / "backgrounds" / "bg-floresta-outono.png"),
]
WINDOW_TITLE = "Auto-Magic: Auto Battler RPG (MVP)"
FPS = 60
STAGE_TRANSITION_DELAY = 2.0        # Segundos de transição entre salas

# Paleta de Cores (Estilo Dark / Cyber Fantasy)
COLOR_BG_DARK = (15, 18, 28)
COLOR_BG_CARD = (25, 32, 48)
COLOR_BG_ARENA = (20, 26, 38)
COLOR_PANEL_BORDER = (45, 58, 85)

# Cores dos Personagens
COLOR_HERO = (45, 156, 219)        # Azul Ciano Vibrante
COLOR_HERO_SHADOW = (20, 80, 130)
COLOR_ENEMY = (235, 87, 87)        # Vermelho Carmesim
COLOR_ENEMY_SHADOW = (130, 30, 30)
COLOR_MAGE = (150, 120, 25)         # Amarelo Dourado
COLOR_MAGE_SHADOW = (150, 120, 0)

# Cores da Interface e Barras de HP
COLOR_HP_HIGH = (46, 204, 113)     # Verde
COLOR_HP_MEDIUM = (241, 196, 15)   # Amarelo
COLOR_HP_LOW = (231, 76, 60)       # Vermelho
COLOR_HP_BG = (35, 42, 58)
COLOR_HP_BORDER = (60, 70, 95)

# Cores de Texto e UI
COLOR_TEXT_PRIMARY = (245, 247, 250)
COLOR_TEXT_SECONDARY = (160, 175, 200)
COLOR_TEXT_GOLD = (255, 215, 0)
COLOR_TEXT_MUTED = (100, 115, 140)

# Cores de Botões
COLOR_BUTTON_IDLE = (35, 45, 68)
COLOR_BUTTON_HOVER = (55, 75, 115)
COLOR_BUTTON_TEXT = (245, 247, 250)
COLOR_BUTTON_BORDER = (75, 100, 150)
COLOR_BUTTON_BORDER_HOVER = (100, 140, 210)

# Configurações de Gameplay
ATTACK_COOLDOWN_DEFAULT = 1.5      # Segundos entre cada ataque
RESULT_SCREEN_DELAY = 3.0          # Segundos para retornar ao menu após o fim da batalha

# Configurações de Movimentação e Alcance
# Guerreiro
WARRIOR_SPEED = 120                # Velocidade do Guerreiro (pixels por segundo)
WARRIOR_ATTACK_RANGE = 45         # Distância melee para iniciar ataque (pixels)
# Mago
MAGE_SPEED = 90
MAGE_ATTACK_RANGE = 350