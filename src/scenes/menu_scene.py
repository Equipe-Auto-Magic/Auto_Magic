import pygame
import sys
from src import config
from src.scenes.base_scene import BaseScene

class Button:
    """Componente Reutilizável de Botão Interativo com Efeito Hover."""
    def __init__(self, x: int, y: int, width: int, height: int, text: str, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.is_hovered = False

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered and self.action:
                self.action()

    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        # Determina as cores baseadas no estado de Hover
        bg_color = config.COLOR_BUTTON_HOVER if self.is_hovered else config.COLOR_BUTTON_IDLE
        border_color = config.COLOR_BUTTON_BORDER_HOVER if self.is_hovered else config.COLOR_BUTTON_BORDER

        # Sombra do botão
        shadow_rect = self.rect.copy()
        shadow_rect.y += 4
        pygame.draw.rect(surface, (10, 12, 20), shadow_rect, border_radius=10)

        # Corpo do botão
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, border_color, self.rect, width=2, border_radius=10)

        # Texto do botão
        text_color = config.COLOR_TEXT_GOLD if self.is_hovered else config.COLOR_BUTTON_TEXT
        text_surf = font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)


class MenuScene(BaseScene):
    """Cena do Menu Principal do Jogo."""
    def __init__(self, game):
        super().__init__(game)
        
        # Dimensões e Posições dos Botões
        btn_w, btn_h = 240, 60
        center_x = config.SCREEN_WIDTH // 2 - btn_w // 2
        start_y = 380

        # Instanciação dos Botões 'Jogar' e 'Sair'
        self.btn_play = Button(
            x=center_x, 
            y=start_y, 
            width=btn_w, 
            height=btn_h, 
            text="Jogar", 
            action=self.on_click_play
        )
        
        self.btn_quit = Button(
            x=center_x, 
            y=start_y + 90, 
            width=btn_w, 
            height=btn_h, 
            text="Sair", 
            action=self.on_click_quit
        )

        self.buttons = [self.btn_play, self.btn_quit]

    def on_click_play(self):
        """Muda o estado do jogo para a cena de batalha."""
        from src.scenes.battle_scene import BattleScene
        print("[MENU] Transicionando para a cena de batalha...")
        self.game.change_scene(BattleScene(self.game))

    def on_click_quit(self):
        """Encerra a aplicação."""
        print("[MENU] Encerrando o jogo...")
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    def handle_event(self, event: pygame.event.Event):
        for btn in self.buttons:
            btn.handle_event(event)

    def update(self, dt: float):
        pass

    def draw(self, surface: pygame.Surface):
        # Preenchimento de Fundo
        surface.fill(config.COLOR_BG_DARK)

        # Painel Central Decorativo
        panel_rect = pygame.Rect(config.SCREEN_WIDTH // 2 - 300, 80, 600, 560)
        pygame.draw.rect(surface, config.COLOR_BG_CARD, panel_rect, border_radius=20)
        pygame.draw.rect(surface, config.COLOR_PANEL_BORDER, panel_rect, width=2, border_radius=20)

        # Título Principal
        title_surf = self.game.font_title.render("AUTO-MAGIC", True, config.COLOR_TEXT_GOLD)
        title_rect = title_surf.get_rect(center=(config.SCREEN_WIDTH // 2, 170))
        surface.blit(title_surf, title_rect)

        # Subtítulo
        subtitle_surf = self.game.font_medium.render("Auto Battler RPG — MVP", True, config.COLOR_TEXT_SECONDARY)
        subtitle_rect = subtitle_surf.get_rect(center=(config.SCREEN_WIDTH // 2, 230))
        surface.blit(subtitle_surf, subtitle_rect)

        # Divisor Decorativo
        line_y = 270
        pygame.draw.line(surface, config.COLOR_PANEL_BORDER, 
                         (config.SCREEN_WIDTH // 2 - 200, line_y), 
                         (config.SCREEN_WIDTH // 2 + 200, line_y), width=2)

        # Renderiza Botões
        for btn in self.buttons:
            btn.draw(surface, self.game.font_large)
