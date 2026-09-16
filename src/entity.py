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
                 attack_range: float = 0.0,
                 default_direction: float = None,
                 opponent_team: list = None):
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

        # Direção padrão de movimentação (+1 para direita, -1 para esquerda)
        if default_direction is not None:
            self.default_direction = float(default_direction)
        else:
            self.default_direction = 1.0 if self.x < config.SCREEN_WIDTH / 2 else -1.0

        # Gerenciamento de Alvos e Adversários (referência à estrutura do time oponente)
        self.target: 'Entity | None' = None
        self.opponents: list['Entity'] = opponent_team if opponent_team is not None else []

    # ------------------------------------------------------------------
    # Alvos e Adversários (Sistema de Times/Facções)
    # ------------------------------------------------------------------

    def set_opponent_team(self, opponent_team: list['Entity']):
        """Define a referência à estrutura do time oponente inteiro."""
        self.opponents = opponent_team
        self.target = self.find_target()

    def set_opponents(self, opponents: list['Entity']):
        """Alias para set_opponent_team, mantendo compatibilidade."""
        self.set_opponent_team(opponents)

    def set_target(self, target):
        """Define alvo direto ou referência de lista de oponentes."""
        if isinstance(target, (list, tuple)):
            self.opponents = target
            self.target = self.find_target()
        elif target is not None:
            if target not in self.opponents:
                self.opponents.append(target)
            self.target = target
        else:
            self.target = None

    def find_target(self) -> 'Entity | None':
        """
        Busca o adversário mais próximo que esteja VIVO (HP > 0 e estado != 'morto').
        Ignora entidades mortas.
        """
        living = [
            opp for opp in self.opponents
            if opp is not None and opp.current_hp > 0 and opp.state != 'morto'
        ]
        if not living:
            return None

        # Seleciona o adversário vivo mais próximo baseado na distância entre centros
        return min(
            living,
            key=lambda opp: abs((opp.x + opp.width / 2.0) - (self.x + self.width / 2.0))
        )

    def get_distance_to(self, target: 'Entity') -> float:
        """Calcula a distância horizontal borda a borda até o alvo."""
        if target.x >= self.x:
            dist = target.x - (self.x + self.width)
        else:
            dist = self.x - (target.x + target.width)
        return max(0.0, dist)

    # ------------------------------------------------------------------
    # Update principal (Máquina de Estados)
    # ------------------------------------------------------------------

    def update(self, dt: float):
        """
        Atualiza o estado, busca de alvos, movimentação e cooldown da entidade a cada frame:
        1. Se morta (HP <= 0 ou estado 'morto'): não se move nem ataca. Timers zerados.
        2. Efeito visual de flash de dano.
        3. A) Busca de Alvo: procura adversário mais próximo que esteja VIVO.
        4. B) Reavaliação de Distância e Estado:
           - Se dist > alcance_ataque: estado 'andando', move-se até o alvo, reseta cooldown.
           - Se dist <= alcance_ataque: estado 'atacando', acumula cooldown.
        5. C) Caminhada Contínua: sem adversário vivo, mantém 'andando' na direção padrão.
        """
        # Estado de morte: não se move, não ataca e zera temporizadores
        if self.current_hp <= 0 or self.state == 'morto':
            self.state = 'morto'
            self.cooldown_timer = 0.0
            self.target = None
            return

        # Efeito visual de piscar ao receber dano
        if self.flash_timer > 0:
            self.flash_timer -= dt

        # A) Busca de Alvo: adversário mais próximo que esteja VIVO
        self.target = self.find_target()

        # B) Reavaliação de Distância e Estado
        if self.target is not None:
            dist = self.get_distance_to(self.target)

            if dist > self.attack_range:
                # Distância MAIOR que alcance_ataque: muda para 'andando'
                self.state = 'andando'
                self.cooldown_timer = 0.0  # Pausa/reseta cooldown enquanto em movimento

                # Move-se na direção do alvo
                if self.speed > 0:
                    target_center = self.target.x + self.target.width / 2.0
                    self_center = self.x + self.width / 2.0
                    direction = 1.0 if target_center > self_center else -1.0
                    self.x += direction * self.speed * dt
                    self.rect.x = int(self.x)
            else:
                # Distância MENOR OU IGUAL ao alcance_ataque: muda para 'atacando'
                self.state = 'atacando'
                self.cooldown_timer += dt
        else:
            # C) Caminhada Contínua: sem adversário vivo na tela/range
            self.state = 'andando'
            self.cooldown_timer = 0.0

            # Continua se movendo em frente na direção padrão
            if self.speed > 0:
                self.x += self.default_direction * self.speed * dt
                self.rect.x = int(self.x)

    # ------------------------------------------------------------------
    # Combate
    # ------------------------------------------------------------------

    def can_attack(self) -> bool:
        """
        Verifica se a entidade pode desferir um ataque:
        - Deve estar viva (HP > 0 e estado != 'morto')
        - Estritamente no estado 'atacando'
        - Alvo atual existente e vivo
        - Cooldown de ataque completo
        """
        return (self.is_alive()
                and self.state == 'atacando'
                and self.target is not None
                and self.target.is_alive()
                and self.cooldown_timer >= self.attack_cooldown)

    def reset_cooldown(self):
        """Reinicia o temporizador de ataque mantendo eventual tempo residual."""
        self.cooldown_timer %= self.attack_cooldown

    def take_damage(self, amount: int):
        """Aplica dano à entidade. Se HP <= 0, muda o estado para 'morto'."""
        self.current_hp = max(0, self.current_hp - amount)
        self.flash_timer = 0.2  # Efeito visual de flash por 200ms
        if self.current_hp <= 0:
            self.state = 'morto'
            self.cooldown_timer = 0.0
            self.target = None

    def is_alive(self) -> bool:
        """Retorna True se o personagem tiver HP superior a 0 e não estiver morto."""
        return self.current_hp > 0 and self.state != 'morto'

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

        # Superfície do sprite do personagem (permite controle de Alpha/Opacidade)
        sprite_w = self.width + 10
        sprite_h = self.height + 15
        sprite_surf = pygame.Surface((sprite_w, sprite_h), pygame.SRCALPHA)

        # Sombra sob o personagem (local à sprite_surf)
        shadow_rect = pygame.Rect(5, 10, self.width, self.height)
        pygame.draw.rect(sprite_surf, self.shadow_color, shadow_rect, border_radius=12)

        # Corpo do Personagem (retângulo estilizado com cantos arredondados)
        main_color = (255, 255, 255) if (self.flash_timer > 0 and self.is_alive()) else self.color
        char_rect = pygame.Rect(0, 0, self.width, self.height)
        pygame.draw.rect(sprite_surf, main_color, char_rect, border_radius=12)
        pygame.draw.rect(sprite_surf, config.COLOR_PANEL_BORDER, char_rect, width=2, border_radius=12)

        # 1. Efeito Visual de Morte: Opacidade a 50% (Alpha = 128) mantendo o corpo no chão
        if self.state == 'morto':
            sprite_surf.set_alpha(128)

        surface.blit(sprite_surf, (draw_x, draw_y))

        # Renderização de UI: ativas apenas enquanto vivo; quando morto, corpo permanece limpo no chão
        if self.state != 'morto':
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
            cd_bar_width = self.width
            cd_bar_height = 6
            cd_bar_x = draw_x
            cd_bar_y = draw_y + self.height + 10

            # Fundo da barra de Cooldown
            cd_bg_rect = pygame.Rect(cd_bar_x, cd_bar_y, cd_bar_width, cd_bar_height)
            pygame.draw.rect(surface, config.COLOR_HP_BG, cd_bg_rect, border_radius=3)

            # Progresso do Cooldown (0.0 até 1.0) — pausado/zerado enquanto andando
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
        else:
            # Nome sutilmente atenuado para identificar o corpo caído
            name_surf = font_small.render(self.name, True, config.COLOR_TEXT_MUTED)
            name_surf.set_alpha(128)
            name_rect = name_surf.get_rect(center=(draw_x + self.width // 2, draw_y - 20))
            surface.blit(name_surf, name_rect)


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
                 x: int, y: int, speed: float = config.WARRIOR_SPEED,
                 attack_range: float = config.WARRIOR_ATTACK_RANGE, **kwargs):
        super().__init__(
            name=name,
            max_hp=max_hp,
            attack_damage=attack_damage,
            x=x,
            y=y,
            speed=speed,
            attack_range=attack_range,
            **kwargs
        )
class Mage(Entity):
    """
    Mago à distância.

    Herda toda a lógica de Entity. Nasce com velocidade e alcance
    configurados via config.py. Para balancear basta alterar as constantes
    MAGE_SPEED e MAGE_ATTACK_RANGE.
    """
    def __init__(self, name: str, max_hp: int, attack_damage: int,
                 x: int, y: int, speed: float = config.MAGE_SPEED,
                 attack_range: float = config.MAGE_ATTACK_RANGE, **kwargs):
        super().__init__(
            name=name,
            max_hp=max_hp,
            attack_damage=attack_damage,
            x=x,
            y=y,
            speed=speed,
            attack_range=attack_range,
            **kwargs
        )