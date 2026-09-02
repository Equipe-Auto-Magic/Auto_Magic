import pygame
import sys
from src import config
from src.scenes.menu_scene import MenuScene

class Game:
    """
    Classe Principal do Jogo.
    Inicializa o Pygame, gerencia fontes, controla a taxa de quadros (60 FPS),
    executa o loop principal de eventos e gerencia a máquina de estados de cenas.
    """
    def __init__(self):
        pygame.init()
        pygame.font.init()

        # Configuração da Janela
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption(config.WINDOW_TITLE)

        # Relógio para controle de FPS (60 FPS)
        self.clock = pygame.time.Clock()
        self.is_running = True

        # Carregamento de Fontes de Sistema de Alta Qualidade
        font_names = ["Segoe UI", "Arial", "Helvetica", "sans-serif"]
        self.font_title = pygame.font.SysFont(font_names, 48, bold=True)
        self.font_large = pygame.font.SysFont(font_names, 32, bold=True)
        self.font_bold = pygame.font.SysFont(font_names, 22, bold=True)
        self.font_medium = pygame.font.SysFont(font_names, 20)
        self.font_small = pygame.font.SysFont(font_names, 14, bold=True)

        # Cena Inicial: Menu Principal
        self.current_scene = MenuScene(self)

    def change_scene(self, new_scene):
        """Altera a cena atual do jogo."""
        self.current_scene = new_scene

    def run(self):
        """Loop Principal da Aplicação (Eventos -> Lógica -> Renderização @ 60 FPS)."""
        while self.is_running:
            # Tempo decorrido em segundos desde o último frame (Delta Time)
            dt = self.clock.tick(config.FPS) / 1000.0

            # 1. Processamento de Eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                else:
                    self.current_scene.handle_event(event)

            # 2. Atualização Lógica
            self.current_scene.update(dt)

            # 3. Renderização
            self.current_scene.draw(self.screen)
            pygame.display.flip()

        pygame.quit()
        sys.exit()
