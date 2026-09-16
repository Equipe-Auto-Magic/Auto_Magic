"""
Módulo de Configuração de Fases e Salas (Data-Driven) e Fábrica de Inimigos.
Permite definir estruturas completas de estágios e salas sem instanciar inimigos antecipadamente.
"""
from dataclasses import dataclass, field
from typing import List, Optional
from src import config
from src.entity import Warrior, Mage


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
    """Fábrica para instanciar inimigos apenas quando a sala for iniciada."""

    @staticmethod
    def create_enemy(cfg: EnemyConfig, base_x: int = 0, base_y: int = 380) -> Warrior | Mage:
        """Cria e posiciona a entidade no lado direito da tela."""
        pos_x = base_x + cfg.offset_x
        pos_y = base_y + cfg.offset_y

        kwargs = {
            "name": cfg.name,
            "max_hp": cfg.max_hp,
            "attack_damage": cfg.attack_damage,
            "x": pos_x,
            "y": pos_y,
            "color": config.COLOR_ENEMY,
            "shadow_color": config.COLOR_ENEMY_SHADOW,
            "attack_cooldown": cfg.attack_cooldown,
            "default_direction": -1.0,
            "team": "inimigo",
        }

        if cfg.speed is not None:
            kwargs["speed"] = cfg.speed
        if cfg.attack_range is not None:
            kwargs["attack_range"] = cfg.attack_range

        if cfg.unit_class.lower() == "mage":
            if "speed" not in kwargs:
                kwargs["speed"] = config.MAGE_SPEED
            if "attack_range" not in kwargs:
                kwargs["attack_range"] = config.MAGE_ATTACK_RANGE
            return Mage(**kwargs)
        else:
            if "speed" not in kwargs:
                kwargs["speed"] = config.WARRIOR_SPEED
            if "attack_range" not in kwargs:
                kwargs["attack_range"] = config.WARRIOR_ATTACK_RANGE
            return Warrior(**kwargs)


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
                            max_hp=45,
                            attack_damage=8,
                            offset_x=0,
                            offset_y=0
                        ),
                        EnemyConfig(
                            name="Goblin Curandeiro",
                            unit_class="Mage",
                            max_hp=30,
                            attack_damage=6,
                            attack_cooldown=2.2,
                            offset_x=120,
                            offset_y=0
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
                            max_hp=65,
                            attack_damage=12,
                            offset_x=0,
                            offset_y=-10
                        ),
                        EnemyConfig(
                            name="Invocador Noturno",
                            unit_class="Mage",
                            max_hp=45,
                            attack_damage=10,
                            attack_cooldown=2.0,
                            offset_x=130,
                            offset_y=10
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
                            max_hp=85,
                            attack_damage=14,
                            offset_x=-20,
                            offset_y=0
                        ),
                        EnemyConfig(
                            name="Feiticeiro Sombrio",
                            unit_class="Mage",
                            max_hp=50,
                            attack_damage=12,
                            attack_cooldown=1.8,
                            offset_x=110,
                            offset_y=-15
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
                            max_hp=110,
                            attack_damage=16,
                            offset_x=-30,
                            offset_y=0
                        ),
                        EnemyConfig(
                            name="Lorde Bruxo",
                            unit_class="Mage",
                            max_hp=95,
                            attack_damage=15,
                            attack_cooldown=1.7,
                            offset_x=120,
                            offset_y=0
                        ),
                    ]
                )
            ]
        )
    ]
