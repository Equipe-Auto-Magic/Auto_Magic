import pygame
from pathlib import Path

from src import config


class BaseScene:
    """
    Classe base abstrata para todas as cenas do jogo.
    Define a interface padrão para gerenciamento de eventos, atualização lógica e renderização.
    """
    def __init__(self, game):
        self.game = game
        self.background = self._load_background()

    def _load_background(self):
        """Carrega e ajusta a imagem de fundo da cena."""
        try:
            bg_path = Path(config.IMG_BG_PATH)
            if not bg_path.is_absolute():
                bg_path = Path(__file__).resolve().parents[1] / bg_path

            image = pygame.image.load(str(bg_path)).convert()
            return pygame.transform.smoothscale(image, (config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        except Exception as exc:
            print(f"[SCENE] Não foi possível carregar o fundo: {exc}")
            return None

    def draw_background(self, surface: pygame.Surface):
        """Desenha o fundo da cena ou um fallback de cor."""
        if self.background is not None:
            surface.blit(self.background, (0, 0))
        else:
            surface.fill(config.COLOR_BG_DARK)

    def handle_event(self, event: pygame.event.Event):
        """Processa eventos de entrada (teclado, mouse, etc)."""
        pass

    def update(self, dt: float):
        """Atualiza a lógica interna da cena com base no delta time."""
        pass

    def draw(self, surface: pygame.Surface):
        """Renderiza a cena na superfície fornecida."""
        pass
