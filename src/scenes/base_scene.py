import pygame

class BaseScene:
    """
    Classe base abstrata para todas as cenas do jogo.
    Define a interface padrão para gerenciamento de eventos, atualização lógica e renderização.
    """
    def __init__(self, game):
        self.game = game

    def handle_event(self, event: pygame.event.Event):
        """Processa eventos de entrada (teclado, mouse, etc)."""
        pass

    def update(self, dt: float):
        """Atualiza a lógica interna da cena com base no delta time."""
        pass

    def draw(self, surface: pygame.Surface):
        """Renderiza a cena na superfície fornecida."""
        pass
