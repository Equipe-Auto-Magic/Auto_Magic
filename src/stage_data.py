"""
Módulo de Configuração de Fases e Salas (Data-Driven) e Fábrica de Inimigos.
Permite definir estruturas completas de estágios e salas sem instanciar inimigos antecipadamente.
"""
from dataclasses import dataclass, field
from typing import List, Optional
from src import config
from src.entity import (
    Entity,
    TransformComponent,
    HealthComponent,
    MovementComponent,
    CombatComponent,
    TargetingComponent,
    SpriteComponent,
    Warrior,
    Mage
)


@dataclass
class EnemyConfig:
    """Configuração declarativa para instanciar um inimigo."""
    name: str
    unit_class: str  # "Warrior" ou "Mage"
    max_hp: int
    attack_damage: int
    attack_cooldown: float = config.ATTACK_COOLDOWN_DEFAULT
    # Deslocamentos relativos para layout do lado direito
    offset_x: int = 0
    offset_y: int = 0
    speed: Optional[float] = None
    attack_range: Optional[float] = None
    target_preference: str = "nearest"


@dataclass
class RoomConfig:
    """Configuração de uma sala contendo sua lista de inimigos a serem criados."""
    room_number: int
    name: str
    enemies: List[EnemyConfig] = field(default_factory=list)


@dataclass
class StageConfig:
    """Configuração de uma fase contendo sequência de salas."""
    stage_number: int
    name: str
    rooms: List[RoomConfig] = field(default_factory=list)


class EnemyFactory:
    """Fábrica para instanciar inimigos apenas quando a sala for iniciada usando o Padrão de Componentes."""

    @staticmethod
    def create_enemy(cfg: EnemyConfig, base_x: int = 0, base_y: int = config.GROUND_Y) -> Entity:
        """Cria uma Entity vazia e acopla seus componentes de dados, lógica e renderização."""
        pos_x = base_x + cfg.offset_x
        pos_y = base_y + cfg.offset_y

        is_mage = cfg.unit_class.lower() == "mage"

        # Resolução de velocidade e alcance
        if cfg.speed is not None:
            speed = cfg.speed
        else:
            speed = config.MAGE_SPEED if is_mage else config.WARRIOR_SPEED

        if cfg.attack_range is not None:
            attack_range = cfg.attack_range
        else:
            attack_range = config.MAGE_ATTACK_RANGE if is_mage else config.WARRIOR_ATTACK_RANGE

        # Instanciação modular por componentes
        inimigo = Entity(name=cfg.name, team="inimigo")
        inimigo.add_component(TransformComponent(x=pos_x, y=pos_y, width=100, height=140))
        inimigo.add_component(HealthComponent(max_hp=cfg.max_hp))
        inimigo.add_component(MovementComponent(speed=speed, default_direction=-1.0))
        inimigo.add_component(CombatComponent(dano=cfg.attack_damage, alcance=attack_range, cooldown=cfg.attack_cooldown))
        inimigo.add_component(TargetingComponent(target_preference=cfg.target_preference))
        inimigo.add_component(SpriteComponent(width=100, height=140, color=config.COLOR_ENEMY, shadow_color=config.COLOR_ENEMY_SHADOW))

        return inimigo


def get_default_stages() -> List[StageConfig]:
    """
    Retorna a progressão padrão de fases e salas do jogo.
    Fase 1: 2 salas (Iniciação e Desafio)
    Fase 2: 2 salas (Emboscada e Chefe Bruxo)
    """
    return [
        StageConfig(
            stage_number=1,
            name="Floresta Sombria",
            rooms=[
                RoomConfig(
                    room_number=1,
                    name="Entrada da Floresta",
                    enemies=[
                        EnemyConfig(
                            name="Goblin Soldado",
                            unit_class="Warrior",
                            max_hp=42,
                            attack_damage=6,
                            offset_x=0,
                            offset_y=0,
                            target_preference="frontline",
                        ),
                        EnemyConfig(
                            name="Goblin Curandeiro",
                            unit_class="Mage",
                            max_hp=28,
                            attack_damage=5,
                            attack_cooldown=2.4,
                            offset_x=-120,
                            offset_y=-25,
                            target_preference="backline",
                        ),
                        EnemyConfig(
                            name="Goblin Batedor",
                            unit_class="Warrior",
                            max_hp=34,
                            attack_damage=5,
                            attack_cooldown=1.8,
                            offset_x=-240,
                            offset_y=25,
                            target_preference="vulnerable",
                        ),
                    ]
                ),
                RoomConfig(
                    room_number=2,
                    name="Clareira dos Guardiões",
                    enemies=[
                        EnemyConfig(
                            name="Guarda Corrompido",
                            unit_class="Warrior",
                            max_hp=58,
                            attack_damage=9,
                            offset_x=0,
                            offset_y=-10,
                            target_preference="frontline",
                        ),
                        EnemyConfig(
                            name="Invocador Noturno",
                            unit_class="Mage",
                            max_hp=40,
                            attack_damage=7,
                            attack_cooldown=2.2,
                            offset_x=-120,
                            offset_y=10,
                            target_preference="backline",
                        ),
                        EnemyConfig(
                            name="Cão Corrompido",
                            unit_class="Warrior",
                            max_hp=46,
                            attack_damage=8,
                            attack_cooldown=1.7,
                            offset_x=-240,
                            offset_y=25,
                            target_preference="vulnerable",
                        ),
                    ]
                )
            ]
        ),
        StageConfig(
            stage_number=2,
            name="Santuário Oculto",
            rooms=[
                RoomConfig(
                    room_number=1,
                    name="Ponte das Brumas",
                    enemies=[
                        EnemyConfig(
                            name="Cavaleiro Negro",
                            unit_class="Warrior",
                            max_hp=74,
                            attack_damage=11,
                            offset_x=0,
                            offset_y=0,
                            target_preference="frontline",
                        ),
                        EnemyConfig(
                            name="Feiticeiro Sombrio",
                            unit_class="Mage",
                            max_hp=48,
                            attack_damage=8,
                            attack_cooldown=2.0,
                            offset_x=-120,
                            offset_y=-25,
                            target_preference="backline",
                        ),
                        EnemyConfig(
                            name="Sentinela das Brumas",
                            unit_class="Mage",
                            max_hp=52,
                            attack_damage=9,
                            attack_cooldown=2.1,
                            offset_x=-240,
                            offset_y=25,
                            target_preference="vulnerable",
                        ),
                    ]
                ),
                RoomConfig(
                    room_number=2,
                    name="Câmara do Lorde Bruxo",
                    enemies=[
                        EnemyConfig(
                            name="Golem Protetor",
                            unit_class="Warrior",
                            max_hp=92,
                            attack_damage=12,
                            offset_x=0,
                            offset_y=0,
                            target_preference="frontline",
                        ),
                        EnemyConfig(
                            name="Lorde Bruxo",
                            unit_class="Mage",
                            max_hp=76,
                            attack_damage=10,
                            attack_cooldown=1.9,
                            offset_x=-120,
                            offset_y=-25,
                            target_preference="backline",
                        ),
                        EnemyConfig(
                            name="Acólito do Lorde",
                            unit_class="Mage",
                            max_hp=60,
                            attack_damage=10,
                            attack_cooldown=2.0,
                            offset_x=-240,
                            offset_y=25,
                            target_preference="vulnerable",
                        ),
                    ]
                )
            ]
        )
    ]
