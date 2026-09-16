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
        self.window = pygame.Window(
            config.WINDOW_TITLE,
            size=(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        )
        self.screen = self.window.get_surface()

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
        if hasattr(self.current_scene, "cleanup"):
            self.current_scene.cleanup()
        self.current_scene = new_scene

    def run(self):
        """Loop principal com atualização de lógica em passo fixo de 60 FPS."""
        fixed_dt = 1.0 / config.FPS
        lag = 0.0

        while self.is_running:
            # Mede o tempo real decorrido e limita a renderização a 60 FPS.
            elapsed = self.clock.tick(config.FPS) / 1000.0
            lag += elapsed

            # 1. Processamento de Eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                else:
                    self.current_scene.handle_event(event)

            # 2. Atualização Lógica em passos constantes
            while lag >= fixed_dt:
                self.current_scene.update(fixed_dt)
                lag -= fixed_dt

            # 3. Renderização
            self.current_scene.draw(self.screen)
            self.window.flip()

        self.window.destroy()
        pygame.quit()
        sys.exit()
