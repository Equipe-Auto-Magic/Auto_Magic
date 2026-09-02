import pygame
import math
from src import config

class Entity:
    """
    Representa uma entidade do jogo (Herói ou Inimigo) com atributos RPG,
    temporizador de ataque (cooldown) e métodos de renderização de UI.
    """
    def __init__(self, name: str, max_hp: int, attack_damage: int, 
                 x: int, y: int, width: int = 100, height: int = 140,
                 color=config.COLOR_HERO, shadow_color=config.COLOR_HERO_SHADOW,
                 attack_cooldown: float = config.ATTACK_COOLDOWN_DEFAULT):
        self.name = name
        self.max_hp = max_hp
        self.current_hp = max_hp
        self.attack_damage = attack_damage
        self.attack_cooldown = attack_cooldown
        self.cooldown_timer = 0.0
        
        # Posição e Dimensões
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        
        # Cores e Estilo
        self.color = color
        self.shadow_color = shadow_color
        
        # Efeitos visuais simples
        self.flash_timer = 0.0
        self.shake_offset_x = 0
        self.shake_offset_y = 0

    def update(self, dt: float):
        """Atualiza temporizadores e estados internos da entidade."""
        if not self.is_alive():
            return

        # Acumula o tempo para o ataque
        self.cooldown_timer += dt

        # Atualiza efeito de piscar (flash de dano)
        if self.flash_timer > 0:
            self.flash_timer -= dt

    def can_attack(self) -> bool:
        """Verifica se o tempo de cooldown foi atingido."""
        return self.is_alive() and self.cooldown_timer >= self.attack_cooldown

    def reset_cooldown(self):
        """Reinicia o temporizador de ataque mantendo eventual tempo restante."""
        self.cooldown_timer %= self.attack_cooldown

    def take_damage(self, amount: int):
        """Aplica dano à entidade, garantindo que o HP não fique negativo."""
        self.current_hp = max(0, self.current_hp - amount)
        self.flash_timer = 0.2  # Efeito visual de flash por 200ms

    def is_alive(self) -> bool:
        """Retorna True se o personagem tiver HP superior a 0."""
        return self.current_hp > 0

    def get_hp_percentage(self) -> float:
        """Retorna a porcentagem de vida restante entre 0.0 e 1.0."""
        if self.max_hp <= 0:
            return 0.0
        return max(0.0, min(1.0, self.current_hp / self.max_hp))

    def get_hp_color(self) -> tuple:
        """Retorna a cor apropriada para a barra de HP baseada no percentual."""
        pct = self.get_hp_percentage()
        if pct > 0.5:
            return config.COLOR_HP_HIGH
        elif pct > 0.25:
            return config.COLOR_HP_MEDIUM
        else:
            return config.COLOR_HP_LOW

    def draw(self, surface: pygame.Surface, font_bold: pygame.font.Font, font_small: pygame.font.Font):
        """Desenha o corpo do personagem, nome, barra de vida e medidor de cooldown."""
        draw_x = self.x + self.shake_offset_x
        draw_y = self.y + self.shake_offset_y

        # Sombra sob o personagem
        shadow_rect = pygame.Rect(draw_x + 5, draw_y + 10, self.width, self.height)
        pygame.draw.rect(surface, self.shadow_color, shadow_rect, border_radius=12)

        # Corpo do Personagem (retângulo estilizado com cantos arredondados)
        main_color = (255, 255, 255) if self.flash_timer > 0 else self.color
        char_rect = pygame.Rect(draw_x, draw_y, self.width, self.height)
        pygame.draw.rect(surface, main_color, char_rect, border_radius=12)
        pygame.draw.rect(surface, config.COLOR_PANEL_BORDER, char_rect, width=2, border_radius=12)

        # Nome do Personagem (Acima do retângulo)
        name_surf = font_bold.render(self.name, True, config.COLOR_TEXT_PRIMARY)
        name_rect = name_surf.get_rect(center=(draw_x + self.width // 2, draw_y - 45))
        surface.blit(name_surf, name_rect)

        # --- BARRA DE VIDA (HP) DINÂMICA ---
        bar_width = 130
        bar_height = 16
        bar_x = draw_x + (self.width - bar_width) // 2
        bar_y = draw_y - 25

        # Fundo da Barra de HP
        bg_bar_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(surface, config.COLOR_HP_BG, bg_bar_rect, border_radius=8)

        # Preenchimento dinâmico proporcional ao HP
        hp_pct = self.get_hp_percentage()
        fill_width = int(bar_width * hp_pct)
        if fill_width > 0:
            fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
            pygame.draw.rect(surface, self.get_hp_color(), fill_rect, border_radius=8)

        # Borda da Barra de HP
        pygame.draw.rect(surface, config.COLOR_HP_BORDER, bg_bar_rect, width=2, border_radius=8)

        # Texto numérico de HP (ex: "75 / 100")
        hp_str = f"{self.current_hp}/{self.max_hp}"
        hp_surf = font_small.render(hp_str, True, config.COLOR_TEXT_PRIMARY)
        hp_rect = hp_surf.get_rect(center=bg_bar_rect.center)
        surface.blit(hp_surf, hp_rect)

        # --- BARRA DE MEDIÇÃO DO COOLDOWN DE ATAQUE ---
        if self.is_alive():
            cd_bar_width = self.width
            cd_bar_height = 6
            cd_bar_x = draw_x
            cd_bar_y = draw_y + self.height + 10

            # Fundo da barra de Cooldown
            cd_bg_rect = pygame.Rect(cd_bar_x, cd_bar_y, cd_bar_width, cd_bar_height)
            pygame.draw.rect(surface, config.COLOR_HP_BG, cd_bg_rect, border_radius=3)

            # Progresso do Cooldown (0.0 até 1.0)
            cd_pct = min(1.0, self.cooldown_timer / self.attack_cooldown)
            cd_fill_width = int(cd_bar_width * cd_pct)
            if cd_fill_width > 0:
                cd_fill_rect = pygame.Rect(cd_bar_x, cd_bar_y, cd_fill_width, cd_bar_height)
                pygame.draw.rect(surface, config.COLOR_TEXT_GOLD, cd_fill_rect, border_radius=3)

            # Sub-texto com Dano de Ataque
            dmg_str = f"ATK: {self.attack_damage}"
            dmg_surf = font_small.render(dmg_str, True, config.COLOR_TEXT_SECONDARY)
            dmg_rect = dmg_surf.get_rect(center=(draw_x + self.width // 2, cd_bar_y + 18))
            surface.blit(dmg_surf, dmg_rect)
