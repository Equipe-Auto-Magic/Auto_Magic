import pygame
import math
from src import config

class Entity:
    """
    Classe base de uma entidade do jogo (Herói ou Inimigo).

    Atributos de Combate:
        max_hp, current_hp, attack_damage, attack_cooldown

    Atributos de Movimentação (novos):
        speed        -- velocidade em pixels/segundo (0 = estático)
        attack_range -- distância em pixels para iniciar ataque
        state        -- 'andando' | 'atacando'
        target       -- referência à entidade alvo (Entity | None)

    Arquitetura Escalável:
        A lógica de aproximação vive em _move_towards_target(), um método
        protegido que subclasses podem sobrescrever (ex: Atirador pode querer
        MANTER distância em vez de se aproximar).
        speed=0 por padrão mantém Entity base completamente estática —
        ideal para Magos/Atiradores que atacam de longe sem andar.
    """
    def __init__(self, name: str, max_hp: int, attack_damage: int,
                 x: int, y: int, width: int = 100, height: int = 140,
                 color=config.COLOR_HERO, shadow_color=config.COLOR_HERO_SHADOW,
                 attack_cooldown: float = config.ATTACK_COOLDOWN_DEFAULT,
                 speed: float = 0.0,
                 attack_range: float = 0.0):
        self.name = name
        self.max_hp = max_hp
        self.current_hp = max_hp
        self.attack_damage = attack_damage
        self.attack_cooldown = attack_cooldown
        self.cooldown_timer = 0.0

        # Posição e Dimensões (x/y como float para movimento suave)
        self.x = float(x)
        self.y = float(y)
        self.width = width
        self.height = height
        self.rect = pygame.Rect(int(x), int(y), width, height)

        # Cores e Estilo
        self.color = color
        self.shadow_color = shadow_color

        # Efeitos visuais simples
        self.flash_timer = 0.0
        self.shake_offset_x = 0
        self.shake_offset_y = 0

        # --- Atributos de Movimentação e Estado ---
        self.speed = speed               # pixels por segundo
        self.attack_range = attack_range # distância em pixels para atacar
        self.state = 'andando' if speed > 0 else 'atacando'
        self.target: 'Entity | None' = None

    # ------------------------------------------------------------------
    # Alvo
    # ------------------------------------------------------------------

    def set_target(self, target: 'Entity'):
        """Define o alvo desta entidade."""
        self.target = target

    # ------------------------------------------------------------------
    # Movimentação (método protegido — subclasses podem sobrescrever)
    # ------------------------------------------------------------------

    def _move_towards_target(self, dt: float):
        """
        Aproxima a entidade do alvo se a distância for maior que attack_range.
        - Enquanto andando: pausa o cooldown de ataque (reinicia para 0).
        - Ao alcançar o alvo: muda estado para 'atacando' e permite o combate.

        Subclasses como Atirador podem sobrescrever para MANTER distância.
        Entidades com speed=0 nunca ativam este método (já nascem em 'atacando').
        """
        if self.target is None or not self.target.is_alive() or self.speed == 0:
            return

        # Distância entre as bordas dos retângulos (borda a borda, não centro)
        dist = abs(self.target.x - self.x) - self.width

        if dist > self.attack_range:
            self.state = 'andando'
            # Pausa o cooldown enquanto em movimento
            self.cooldown_timer = 0.0
            direction = 1.0 if self.target.x > self.x else -1.0
            self.x += direction * self.speed * dt
            self.rect.x = int(self.x)
        else:
            self.state = 'atacando'

    # ------------------------------------------------------------------
    # Update principal
    # ------------------------------------------------------------------

    def update(self, dt: float):
        """Atualiza movimentação, estado e temporizadores da entidade."""
        if not self.is_alive():
            return

        # 1. Movimentação e verificação de alcance
        self._move_towards_target(dt)

        # 2. Acumula cooldown SOMENTE quando em estado de ataque
        if self.state == 'atacando':
            self.cooldown_timer += dt

        # 3. Efeito de piscar (flash de dano)
        if self.flash_timer > 0:
            self.flash_timer -= dt

    # ------------------------------------------------------------------
    # Combate
    # ------------------------------------------------------------------

    def can_attack(self) -> bool:
        """Verifica se está em alcance, vivo e com cooldown completo."""
        return (self.is_alive()
                and self.state == 'atacando'
                and self.cooldown_timer >= self.attack_cooldown)

    def reset_cooldown(self):
        """Reinicia o temporizador de ataque mantendo eventual tempo residual."""
        self.cooldown_timer %= self.attack_cooldown

    def take_damage(self, amount: int):
        """Aplica dano à entidade, garantindo que o HP não fique negativo."""
        self.current_hp = max(0, self.current_hp - amount)
        self.flash_timer = 0.2  # Efeito visual de flash por 200ms

    def is_alive(self) -> bool:
        """Retorna True se o personagem tiver HP superior a 0."""
        return self.current_hp > 0

    # ------------------------------------------------------------------
    # Helpers de UI
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Renderização
    # ------------------------------------------------------------------

    def draw(self, surface: pygame.Surface, font_bold: pygame.font.Font, font_small: pygame.font.Font):
        """Desenha o corpo do personagem, nome, barra de vida e medidor de cooldown."""
        draw_x = int(self.x) + self.shake_offset_x
        draw_y = int(self.y) + self.shake_offset_y

        # Sombra sob o personagem
        shadow_rect = pygame.Rect(draw_x + 5, draw_y + 10, self.width, self.height)
        pygame.draw.rect(surface, self.shadow_color, shadow_rect, border_radius=12)

        # Corpo do Personagem (retângulo estilizado com cantos arredondados)
        main_color = (255, 255, 255) if self.flash_timer > 0 else self.color
        char_rect = pygame.Rect(draw_x, draw_y, self.width, self.height)
        pygame.draw.rect(surface, main_color, char_rect, border_radius=12)
        pygame.draw.rect(surface, config.COLOR_PANEL_BORDER, char_rect, width=2, border_radius=12)

        # Indicador de Estado ('→' andando | '⚔' atacando)
        state_icon = "→" if self.state == 'andando' else "⚔"
        state_surf = font_small.render(state_icon, True, config.COLOR_TEXT_GOLD)
        state_rect = state_surf.get_rect(center=(draw_x + self.width // 2, draw_y - self.height + 70))
        surface.blit(state_surf, state_rect)

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

            # Progresso do Cooldown (0.0 até 1.0) — congelado enquanto andando
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


# ----------------------------------------------------------------------
# Subclasses de Entidade
# ----------------------------------------------------------------------

class Warrior(Entity):
    """
    Guerreiro corpo-a-corpo.

    Herda toda a lógica de Entity. Nasce com velocidade e alcance melee
    configurados via config.py. Para balancear basta alterar as constantes
    WARRIOR_SPEED e WARRIOR_ATTACK_RANGE.

    Futuras classes derivadas:
        class Mage(Entity):    speed=0, attack_range=350, ...
        class Archer(Entity):  speed=0, attack_range=500, ...
    """
    def __init__(self, name: str, max_hp: int, attack_damage: int,
                 x: int, y: int, **kwargs):
        super().__init__(
            name=name,
            max_hp=max_hp,
            attack_damage=attack_damage,
            x=x,
            y=y,
            speed=config.WARRIOR_SPEED,
            attack_range=config.WARRIOR_ATTACK_RANGE,
            **kwargs
        )
class Mage(Entity):
    """
    Mago corpo-a-corpo.

    Herda toda a lógica de Entity. Nasce com velocidade e alcance melee
    configurados via config.py. Para balancear basta alterar as constantes
    MAGE_SPEED e MAGE_ATTACK_RANGE.

    Futuras classes derivadas:
        class Mage(Entity):    speed=0, attack_range=350, ...
        class Archer(Entity):  speed=0, attack_range=500, ...
    """
    def __init__(self, name: str, max_hp: int, attack_damage: int,
                 x: int, y: int, **kwargs):
        super().__init__(
            name=name,
            max_hp=max_hp,
            attack_damage=attack_damage,
            x=x,
            y=y,
            speed=config.MAGE_SPEED,
            attack_range=config.MAGE_ATTACK_RANGE,
            **kwargs
        )