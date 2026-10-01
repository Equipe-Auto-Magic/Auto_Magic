"""
Módulo de Entidades e Componentes do Auto-Battler.
A classe Entity atua puramente como contêiner modular de componentes.
"""
from typing import Dict, Type, TypeVar, Optional, Any, List
import pygame
from src import config
from src.events import gerenciador_eventos

T = TypeVar('T', bound='Component')


class Component:
    """Classe base para todos os componentes do sistema."""
    def __init__(self):
        self.entity: Optional['Entity'] = None

    def update(self, dt: float) -> None:
        """Executa atualização lógica do componente."""
        pass

    def draw(self, surface: pygame.Surface, font_bold: pygame.font.Font, font_small: pygame.font.Font) -> None:
        """Executa renderização do componente visual."""
        pass


class Entity:
    """
    Entidade base do jogo estruturada puramente como contêiner de componentes.
    Elimina classes monolíticas pesadas e desacopla renderização e regras de combate.
    """
    def __init__(self, name: str = "Entidade", team: str = "aliado"):
        self.name: str = name
        self.team: str = team
        self._components: Dict[Type[Component], Component] = {}

    def add_component(self, component: Component) -> 'Entity':
        """Registra um componente nesta entidade e vincula a referência reversa."""
        component.entity = self
        self._components[type(component)] = component
        return self

    def get_component(self, component_type: Type[T]) -> Optional[T]:
        """Obtém um componente registrado pelo seu tipo ou None caso não exista."""
        comp = self._components.get(component_type)
        if comp is not None:
            return comp
        # Suporte a polimorfismo/subclasses
        for c_type, comp_inst in self._components.items():
            if issubclass(c_type, component_type):
                return comp_inst
        return None

    def update(self, dt: float) -> None:
        """Percorre todos os componentes iterando o método update(dt) se implementado."""
        for component in list(self._components.values()):
            component.update(dt)

    def draw(self, surface: pygame.Surface, font_bold: pygame.font.Font, font_small: pygame.font.Font) -> None:
        """Percorre todos os componentes chamando o draw() dos componentes visuais."""
        for component in list(self._components.values()):
            component.draw(surface, font_bold, font_small)

    # ------------------------------------------------------------------
    # Propriedades e Métodos Facilitadores de Compatibilidade
    # ------------------------------------------------------------------

    @property
    def x(self) -> float:
        transform = self.get_component(TransformComponent)
        return transform.x if transform else 0.0

    @x.setter
    def x(self, val: float):
        transform = self.get_component(TransformComponent)
        if transform:
            transform.x = float(val)

    @property
    def y(self) -> float:
        transform = self.get_component(TransformComponent)
        return transform.y if transform else 0.0

    @y.setter
    def y(self, val: float):
        transform = self.get_component(TransformComponent)
        if transform:
            transform.y = float(val)

    @property
    def width(self) -> int:
        sprite = self.get_component(SpriteComponent)
        return sprite.width if sprite else 100

    @property
    def height(self) -> int:
        sprite = self.get_component(SpriteComponent)
        return sprite.height if sprite else 140

    @property
    def rect(self) -> pygame.Rect:
        transform = self.get_component(TransformComponent)
        if transform:
            return transform.rect
        return pygame.Rect(0, 0, 100, 140)

    @property
    def current_hp(self) -> int:
        health = self.get_component(HealthComponent)
        return health.current_hp if health else 0

    @current_hp.setter
    def current_hp(self, val: int):
        health = self.get_component(HealthComponent)
        if health:
            health.current_hp = val

    @property
    def max_hp(self) -> int:
        health = self.get_component(HealthComponent)
        return health.max_hp if health else 0

    @property
    def attack_damage(self) -> int:
        combat = self.get_component(CombatComponent)
        return combat.damage if combat else 0

    @attack_damage.setter
    def attack_damage(self, val: int):
        combat = self.get_component(CombatComponent)
        if combat:
            combat.damage = val

    @property
    def attack_cooldown(self) -> float:
        combat = self.get_component(CombatComponent)
        return combat.cooldown if combat else 1.5

    @property
    def cooldown_timer(self) -> float:
        combat = self.get_component(CombatComponent)
        return combat.cooldown_timer if combat else 0.0

    @cooldown_timer.setter
    def cooldown_timer(self, val: float):
        combat = self.get_component(CombatComponent)
        if combat:
            combat.cooldown_timer = val

    @property
    def speed(self) -> float:
        movement = self.get_component(MovementComponent)
        return movement.speed if movement else 0.0

    @property
    def attack_range(self) -> float:
        combat = self.get_component(CombatComponent)
        return combat.attack_range if combat else 0.0

    @property
    def state(self) -> str:
        health = self.get_component(HealthComponent)
        if health and not health.is_alive():
            return "morto"
        targeting = self.get_component(TargetingComponent)
        if targeting:
            return targeting.state
        return "andando"

    @state.setter
    def state(self, val: str):
        targeting = self.get_component(TargetingComponent)
        if targeting:
            targeting.state = val

    @property
    def target(self) -> Optional['Entity']:
        targeting = self.get_component(TargetingComponent)
        return targeting.target if targeting else None

    @target.setter
    def target(self, val: Optional['Entity']):
        targeting = self.get_component(TargetingComponent)
        if targeting:
            targeting.target = val

    @property
    def flash_timer(self) -> float:
        sprite = self.get_component(SpriteComponent)
        return sprite.flash_timer if sprite else 0.0

    @flash_timer.setter
    def flash_timer(self, val: float):
        sprite = self.get_component(SpriteComponent)
        if sprite:
            sprite.flash_timer = val

    def is_alive(self) -> bool:
        """Verifica se a entidade está viva através de seu HealthComponent."""
        health = self.get_component(HealthComponent)
        return health.is_alive() if health else False

    def take_damage(self, amount: int) -> None:
        """Encaminha o recebimento de dano para o HealthComponent."""
        health = self.get_component(HealthComponent)
        if health:
            health.take_damage(amount)
        sprite = self.get_component(SpriteComponent)
        if sprite:
            sprite.trigger_flash()

    def can_attack(self) -> bool:
        """Verifica disponibilidade de ataque via CombatComponent."""
        combat = self.get_component(CombatComponent)
        return combat.can_attack() if combat else False

    def reset_cooldown(self) -> None:
        """Reinicia o temporizador de ataque."""
        combat = self.get_component(CombatComponent)
        if combat:
            combat.reset_cooldown()

    def set_opponent_team(self, opponent_team: List['Entity']) -> None:
        """Configura a lista de oponentes no TargetingComponent."""
        targeting = self.get_component(TargetingComponent)
        if targeting:
            targeting.set_opponent_team(opponent_team)

    def set_opponents(self, opponents: List['Entity']) -> None:
        """Alias para set_opponent_team."""
        self.set_opponent_team(opponents)


# ----------------------------------------------------------------------
# Componentes Modulares de Dados, Lógica e Visual
# ----------------------------------------------------------------------

class TransformComponent(Component):
    """
    Guarda apenas x e y (posição no mundo) e retângulo de colisão/bounds.
    """
    def __init__(self, x: float, y: float, width: int = 100, height: int = 140):
        super().__init__()
        self._x: float = float(x)
        self._y: float = float(y)
        self.width: int = width
        self.height: int = height
        self.rect: pygame.Rect = pygame.Rect(int(x), int(y), width, height)

    @property
    def x(self) -> float:
        return self._x

    @x.setter
    def x(self, val: float):
        self._x = float(val)
        self.rect.x = int(self._x)

    @property
    def y(self) -> float:
        return self._y

    @y.setter
    def y(self, val: float):
        self._y = float(val)
        self.rect.y = int(self._y)

    @property
    def center_x(self) -> float:
        return self._x + self.width / 2.0

    @property
    def center_y(self) -> float:
        return self._y + self.height / 2.0


class HealthComponent(Component):
    """
    Guarda hp_max, hp_atual e estado (morto ou vivo).
    Gerencia a lógica de receber dano e disparar eventos de morte via EventBus.
    """
    def __init__(self, max_hp: int):
        super().__init__()
        self.max_hp: int = max_hp
        self.current_hp: int = max_hp
        self.state: str = "vivo"

    def is_alive(self) -> bool:
        return self.current_hp > 0 and self.state != "morto"

    def take_damage(self, amount: int) -> None:
        if not self.is_alive():
            return

        self.current_hp = max(0, self.current_hp - amount)
        if self.current_hp <= 0:
            self.state = "morto"
            if self.entity is not None:
                # Gatilho de Evento (Emissor): notifica a morte da entidade dona
                gerenciador_eventos.notificar("entidade_morta", self.entity)

    def get_hp_percentage(self) -> float:
        if self.max_hp <= 0:
            return 0.0
        return max(0.0, min(1.0, self.current_hp / self.max_hp))

    def get_hp_color(self) -> tuple:
        pct = self.get_hp_percentage()
        if pct > 0.5:
            return config.COLOR_HP_HIGH
        elif pct > 0.25:
            return config.COLOR_HP_MEDIUM
        else:
            return config.COLOR_HP_LOW


class MovementComponent(Component):
    """
    Recebe velocidade e direção padrão.
    No update, move a entidade baseada na direção fornecida pelo TargetingComponent.
    """
    def __init__(self, speed: float = 0.0, default_direction: float = 1.0):
        super().__init__()
        self.speed: float = float(speed)
        self.default_direction: float = float(default_direction)
        self.current_direction: float = 0.0

    def move(self, direction: float, dt: float) -> None:
        """Aplica o movimento no TransformComponent de acordo com a velocidade e delta time."""
        if not self.entity or self.speed <= 0:
            return
        transform = self.entity.get_component(TransformComponent)
        if transform:
            transform.x += direction * self.speed * dt

    def update(self, dt: float) -> None:
        """Se houver direção contínua definida e a entidade puder andar, aplica o deslocamento."""
        health = self.entity.get_component(HealthComponent) if self.entity else None
        if health and not health.is_alive():
            return

        if self.current_direction != 0.0:
            self.move(self.current_direction, dt)


class CombatComponent(Component):
    """
    Guarda dano, alcance e cooldown.
    Contém a lógica do temporizador e a execução de causar dano a um alvo.
    """
    def __init__(self, dano: int, alcance: float, cooldown: float = config.ATTACK_COOLDOWN_DEFAULT):
        super().__init__()
        self.damage: int = dano
        self.attack_range: float = float(alcance)
        self.cooldown: float = float(cooldown)
        self.cooldown_timer: float = 0.0

    def update(self, dt: float) -> None:
        health = self.entity.get_component(HealthComponent) if self.entity else None
        if health and not health.is_alive():
            self.cooldown_timer = 0.0
            return

        # Acumula cooldown apenas se a entidade estiver em estado de ataque
        targeting = self.entity.get_component(TargetingComponent) if self.entity else None
        if targeting and targeting.state == "atacando":
            self.cooldown_timer += dt
        elif targeting and targeting.state == "andando":
            self.cooldown_timer = 0.0

    def can_attack(self) -> bool:
        health = self.entity.get_component(HealthComponent) if self.entity else None
        if not health or not health.is_alive():
            return False

        targeting = self.entity.get_component(TargetingComponent) if self.entity else None
        if not targeting or targeting.state != "atacando" or targeting.target is None:
            return False

        if not targeting.target.is_alive():
            return False

        return self.cooldown_timer >= self.cooldown

    def attack(self, target: Entity) -> int:
        """Causa dano direto ao alvo e reinicia o temporizador."""
        if self.can_attack() and target is not None:
            target.take_damage(self.damage)
            self.reset_cooldown()
            return self.damage
        return 0

    def reset_cooldown(self) -> None:
        if self.cooldown > 0:
            self.cooldown_timer %= self.cooldown
        else:
            self.cooldown_timer = 0.0


class TargetingComponent(Component):
    """
    Cérebro da IA autônoma.
    No update(dt), busca o inimigo vivo mais próximo nas listas de time oponente.
    Calcula a distância:
    - Se for maior que o alcance: ordena o MovementComponent a andar e reseta cooldown.
    - Se for menor ou igual: ordena o CombatComponent a atacar.
    """
    def __init__(self, opponent_team: Optional[List[Entity]] = None):
        super().__init__()
        self.opponent_team: List[Entity] = opponent_team if opponent_team is not None else []
        self.target: Optional[Entity] = None
        self.state: str = "andando"  # 'andando' | 'atacando' | 'morto'

    def set_opponent_team(self, team: List[Entity]) -> None:
        self.opponent_team = team
        self.target = self.find_target()

    def find_target(self) -> Optional[Entity]:
        """Busca o adversário mais próximo que esteja vivo."""
        if not self.entity:
            return None

        living = [
            opp for opp in self.opponent_team
            if opp is not None and opp.is_alive()
        ]
        if not living:
            return None

        self_transform = self.entity.get_component(TransformComponent)
        if not self_transform:
            return living[0]

        return min(
            living,
            key=lambda opp: abs(opp.rect.centerx - self_transform.rect.centerx)
        )

    def get_distance_to(self, target: Entity) -> float:
        """Calcula distância horizontal borda a borda até o alvo."""
        if not self.entity:
            return 0.0
        self_trans = self.entity.get_component(TransformComponent)
        target_trans = target.get_component(TransformComponent)
        if not self_trans or not target_trans:
            return 0.0

        if target_trans.x >= self_trans.x:
            dist = target_trans.x - (self_trans.x + self_trans.width)
        else:
            dist = self_trans.x - (target_trans.x + target_trans.width)
        return max(0.0, dist)

    def update(self, dt: float) -> None:
        if not self.entity:
            return

        health = self.entity.get_component(HealthComponent)
        if health and not health.is_alive():
            self.state = "morto"
            self.target = None
            movement = self.entity.get_component(MovementComponent)
            if movement:
                movement.current_direction = 0.0
            return

        combat = self.entity.get_component(CombatComponent)
        movement = self.entity.get_component(MovementComponent)
        self_trans = self.entity.get_component(TransformComponent)

        self.target = self.find_target()

        if self.target is not None:
            dist = self.get_distance_to(self.target)
            attack_range = combat.attack_range if combat else 0.0

            if dist > attack_range:
                # Distância maior: caminha em direção ao alvo
                self.state = "andando"
                if movement and movement.speed > 0 and self_trans:
                    target_center = self.target.rect.centerx
                    direction = 1.0 if target_center > self_trans.center_x else -1.0
                    movement.current_direction = direction
                else:
                    if movement:
                        movement.current_direction = 0.0
            else:
                # Distância menor ou igual: engaja combate
                self.state = "atacando"
                if movement:
                    movement.current_direction = 0.0
        else:
            # Sem alvos vivos na sala: caminha na direção padrão
            self.state = "andando"
            if movement and movement.speed > 0:
                movement.current_direction = movement.default_direction
            elif movement:
                movement.current_direction = 0.0


class SpriteComponent(Component):
    """
    Componente visual e de renderização (Render/SpriteComponent).
    Lê as informações de TransformComponent para desenhar na tela,
    verifica o HealthComponent para aplicar os 50% de opacidade (Alpha = 128) caso esteja morto,
    e desenha nome, barras de vida e cooldown de ataque.
    """
    def __init__(self, width: int = 100, height: int = 140,
                 color=config.COLOR_HERO, shadow_color=config.COLOR_HERO_SHADOW):
        super().__init__()
        self.width: int = width
        self.height: int = height
        self.color = color
        self.shadow_color = shadow_color
        self.flash_timer: float = 0.0
        self.shake_offset_x: int = 0
        self.shake_offset_y: int = 0

    def trigger_flash(self, duration: float = 0.2) -> None:
        self.flash_timer = duration

    def update(self, dt: float) -> None:
        if self.flash_timer > 0:
            self.flash_timer -= dt

    def draw(self, surface: pygame.Surface, font_bold: pygame.font.Font, font_small: pygame.font.Font) -> None:
        if not self.entity:
            return

        transform = self.entity.get_component(TransformComponent)
        health = self.entity.get_component(HealthComponent)
        combat = self.entity.get_component(CombatComponent)
        targeting = self.entity.get_component(TargetingComponent)

        draw_x = int(transform.x if transform else 0) + self.shake_offset_x
        draw_y = int(transform.y if transform else 0) + self.shake_offset_y

        is_dead = health is not None and not health.is_alive()

        # Superfície do sprite com suporte a transparência (Alpha)
        sprite_w = self.width + 10
        sprite_h = self.height + 15
        sprite_surf = pygame.Surface((sprite_w, sprite_h), pygame.SRCALPHA)

        # Sombra sob o personagem
        shadow_rect = pygame.Rect(5, 10, self.width, self.height)
        pygame.draw.rect(sprite_surf, self.shadow_color, shadow_rect, border_radius=12)

        # Corpo estilizado
        main_color = (255, 255, 255) if (self.flash_timer > 0 and not is_dead) else self.color
        char_rect = pygame.Rect(0, 0, self.width, self.height)
        pygame.draw.rect(sprite_surf, main_color, char_rect, border_radius=12)
        pygame.draw.rect(sprite_surf, config.COLOR_PANEL_BORDER, char_rect, width=2, border_radius=12)

        # 50% de opacidade caso esteja morto
        if is_dead:
            sprite_surf.set_alpha(128)

        surface.blit(sprite_surf, (draw_x, draw_y))

        # Elementos de UI sobre a entidade
        if not is_dead:
            current_state = targeting.state if targeting else "andando"
            state_icon = "→" if current_state == "andando" else "⚔"
            state_surf = font_small.render(state_icon, True, config.COLOR_TEXT_GOLD)
            state_rect = state_surf.get_rect(center=(draw_x + self.width // 2, draw_y - self.height + 70))
            surface.blit(state_surf, state_rect)

            # Nome
            name_surf = font_bold.render(self.entity.name, True, config.COLOR_TEXT_PRIMARY)
            name_rect = name_surf.get_rect(center=(draw_x + self.width // 2, draw_y - 45))
            surface.blit(name_surf, name_rect)

            # Barra de Vida (HP)
            if health:
                bar_width = 130
                bar_height = 16
                bar_x = draw_x + (self.width - bar_width) // 2
                bar_y = draw_y - 25

                bg_bar_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
                pygame.draw.rect(surface, config.COLOR_HP_BG, bg_bar_rect, border_radius=8)

                hp_pct = health.get_hp_percentage()
                fill_width = int(bar_width * hp_pct)
                if fill_width > 0:
                    fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
                    pygame.draw.rect(surface, health.get_hp_color(), fill_rect, border_radius=8)

                pygame.draw.rect(surface, config.COLOR_HP_BORDER, bg_bar_rect, width=2, border_radius=8)

                hp_str = f"{health.current_hp}/{health.max_hp}"
                hp_surf = font_small.render(hp_str, True, config.COLOR_TEXT_PRIMARY)
                hp_rect = hp_surf.get_rect(center=bg_bar_rect.center)
                surface.blit(hp_surf, hp_rect)

            # Barra de Cooldown de Ataque
            if combat:
                cd_bar_width = self.width
                cd_bar_height = 6
                cd_bar_x = draw_x
                cd_bar_y = draw_y + self.height + 10

                cd_bg_rect = pygame.Rect(cd_bar_x, cd_bar_y, cd_bar_width, cd_bar_height)
                pygame.draw.rect(surface, config.COLOR_HP_BG, cd_bg_rect, border_radius=3)

                cd_pct = min(1.0, combat.cooldown_timer / combat.cooldown) if combat.cooldown > 0 else 1.0
                cd_fill_width = int(cd_bar_width * cd_pct)
                if cd_fill_width > 0:
                    cd_fill_rect = pygame.Rect(cd_bar_x, cd_bar_y, cd_fill_width, cd_bar_height)
                    pygame.draw.rect(surface, config.COLOR_TEXT_GOLD, cd_fill_rect, border_radius=3)

                dmg_str = f"ATK: {combat.damage}"
                dmg_surf = font_small.render(dmg_str, True, config.COLOR_TEXT_SECONDARY)
                dmg_rect = dmg_surf.get_rect(center=(draw_x + self.width // 2, cd_bar_y + 18))
                surface.blit(dmg_surf, dmg_rect)
        else:
            name_surf = font_small.render(self.entity.name, True, config.COLOR_TEXT_MUTED)
            name_surf.set_alpha(128)
            name_rect = name_surf.get_rect(center=(draw_x + self.width // 2, draw_y - 20))
            surface.blit(name_surf, name_rect)


# Alias para SpriteComponent
RenderComponent = SpriteComponent


# ----------------------------------------------------------------------
# Fábrica de Montagem de Entidades (Factory Functions)
# ----------------------------------------------------------------------

def criar_guerreiro(name: str, max_hp: int, attack_damage: int, x: float, y: float,
                    color=config.COLOR_HERO, shadow_color=config.COLOR_HERO_SHADOW,
                    speed: float = config.WARRIOR_SPEED,
                    attack_range: float = config.WARRIOR_ATTACK_RANGE,
                    attack_cooldown: float = config.ATTACK_COOLDOWN_DEFAULT,
                    default_direction: float = 1.0,
                    team: str = "aliado",
                    opponent_team: Optional[List[Entity]] = None) -> Entity:
    """Instancia uma Entity vazia e adiciona os componentes do Guerreiro."""
    entidade = Entity(name=name, team=team)
    entidade.add_component(TransformComponent(x=x, y=y, width=100, height=140))
    entidade.add_component(HealthComponent(max_hp=max_hp))
    entidade.add_component(MovementComponent(speed=speed, default_direction=default_direction))
    entidade.add_component(CombatComponent(dano=attack_damage, alcance=attack_range, cooldown=attack_cooldown))
    entidade.add_component(TargetingComponent(opponent_team=opponent_team))
    entidade.add_component(SpriteComponent(width=100, height=140, color=color, shadow_color=shadow_color))
    return entidade


def criar_mago(name: str, max_hp: int, attack_damage: int, x: float, y: float,
               color=config.COLOR_MAGE, shadow_color=config.COLOR_MAGE_SHADOW,
               speed: float = config.MAGE_SPEED,
               attack_range: float = config.MAGE_ATTACK_RANGE,
               attack_cooldown: float = 2.0,
               default_direction: float = 1.0,
               team: str = "aliado",
               opponent_team: Optional[List[Entity]] = None) -> Entity:
    """Instancia uma Entity vazia e adiciona os componentes do Mago."""
    entidade = Entity(name=name, team=team)
    entidade.add_component(TransformComponent(x=x, y=y, width=100, height=140))
    entidade.add_component(HealthComponent(max_hp=max_hp))
    entidade.add_component(MovementComponent(speed=speed, default_direction=default_direction))
    entidade.add_component(CombatComponent(dano=attack_damage, alcance=attack_range, cooldown=attack_cooldown))
    entidade.add_component(TargetingComponent(opponent_team=opponent_team))
    entidade.add_component(SpriteComponent(width=100, height=140, color=color, shadow_color=shadow_color))
    return entidade


# Classes de fábrica para compatibilidade com instanciação anterior Warrior(...) e Mage(...)
class Warrior(Entity):
    def __init__(self, name: str, max_hp: int, attack_damage: int, x: float, y: float,
                 speed: float = config.WARRIOR_SPEED,
                 attack_range: float = config.WARRIOR_ATTACK_RANGE,
                 color=config.COLOR_HERO,
                 shadow_color=config.COLOR_HERO_SHADOW,
                 attack_cooldown: float = config.ATTACK_COOLDOWN_DEFAULT,
                 default_direction: float = 1.0,
                 team: str = "aliado",
                 opponent_team: Optional[List[Entity]] = None, **kwargs):
        super().__init__(name=name, team=team)
        self.add_component(TransformComponent(x=x, y=y, width=100, height=140))
        self.add_component(HealthComponent(max_hp=max_hp))
        self.add_component(MovementComponent(speed=speed, default_direction=default_direction))
        self.add_component(CombatComponent(dano=attack_damage, alcance=attack_range, cooldown=attack_cooldown))
        self.add_component(TargetingComponent(opponent_team=opponent_team))
        self.add_component(SpriteComponent(width=100, height=140, color=color, shadow_color=shadow_color))


class Mage(Entity):
    def __init__(self, name: str, max_hp: int, attack_damage: int, x: float, y: float,
                 speed: float = config.MAGE_SPEED,
                 attack_range: float = config.MAGE_ATTACK_RANGE,
                 color=config.COLOR_MAGE,
                 shadow_color=config.COLOR_MAGE_SHADOW,
                 attack_cooldown: float = 2.0,
                 default_direction: float = 1.0,
                 team: str = "aliado",
                 opponent_team: Optional[List[Entity]] = None, **kwargs):
        super().__init__(name=name, team=team)
        self.add_component(TransformComponent(x=x, y=y, width=100, height=140))
        self.add_component(HealthComponent(max_hp=max_hp))
        self.add_component(MovementComponent(speed=speed, default_direction=default_direction))
        self.add_component(CombatComponent(dano=attack_damage, alcance=attack_range, cooldown=attack_cooldown))
        self.add_component(TargetingComponent(opponent_team=opponent_team))
        self.add_component(SpriteComponent(width=100, height=140, color=color, shadow_color=shadow_color))