import unittest
from types import SimpleNamespace

import pygame

from src import config
from src.entity import (
    Entity,
    HealthComponent,
    SpriteComponent,
    TargetingComponent,
    TransformComponent,
)
from src.events import gerenciador_eventos
from src.scenes.battle_scene import (
    BattleScene,
    CriticalOpportunity,
    RallyOpportunity,
)
from src.stage_data import get_default_stages
from src.stage_manager import StageState


def make_entity(name, team, hp, x):
    entity = Entity(name=name, team=team)
    entity.add_component(TransformComponent(x=x, y=100))
    entity.add_component(HealthComponent(max_hp=hp))
    entity.add_component(TargetingComponent())
    return entity


def make_scene():
    scene = BattleScene.__new__(BattleScene)
    scene.stage_manager = SimpleNamespace(state=StageState.COMBATE)
    scene.rally_opportunities = []
    scene.critical_opportunities = []
    scene.critical_cooldown_timer = 0.0
    scene.floating_texts = []
    return scene


class ReactionMechanicsTests(unittest.TestCase):
    def test_damage_event_creates_reaction_opportunities(self):
        scene = make_scene()
        ally = make_entity("Herói", "aliado", hp=100, x=100)
        enemy = make_entity("Goblin", "inimigo", hp=50, x=500)
        gerenciador_eventos.inscrever("dano_recebido", scene)

        try:
            ally.take_damage(20, attacker=enemy)
            enemy.take_damage(12, attacker=ally)
        finally:
            gerenciador_eventos.desinscrever("dano_recebido", scene)

        self.assertEqual(ally.current_hp, 80)
        self.assertEqual(len(scene.rally_opportunities), 1)
        self.assertIs(scene.rally_opportunities[0].attacker, enemy)
        self.assertEqual(scene.rally_opportunities[0].damage_taken, 20)
        self.assertEqual(len(scene.critical_opportunities), 1)
        self.assertIs(scene.critical_opportunities[0].attacker, ally)
        self.assertEqual(scene.critical_opportunities[0].damage_dealt, 12)

    def test_damage_event_reports_only_effective_positive_damage(self):
        class DamageObserver:
            def __init__(self):
                self.events = []

            def ao_notificar(self, evento, dados):
                self.events.append(dados)

        observer = DamageObserver()
        target = make_entity("Herói", "aliado", hp=10, x=100)
        source = make_entity("Goblin", "inimigo", hp=50, x=500)
        gerenciador_eventos.inscrever("dano_recebido", observer)

        try:
            self.assertEqual(target.take_damage(20, attacker=source), 10)
            self.assertEqual(target.take_damage(1, attacker=source), 0)
            self.assertEqual(target.take_damage(0, attacker=source), 0)
        finally:
            gerenciador_eventos.desinscrever("dano_recebido", observer)

        self.assertEqual(len(observer.events), 1)
        self.assertEqual(observer.events[0].amount, 10)
        self.assertIs(observer.events[0].target, target)
        self.assertIs(observer.events[0].attacker, source)

    def test_dead_entity_is_not_drawn_on_the_battlefield(self):
        entity = Entity(name="Goblin", team="inimigo")
        entity.add_component(TransformComponent(x=100, y=100))
        entity.add_component(HealthComponent(max_hp=10))
        sprite = SpriteComponent()
        entity.add_component(sprite)
        entity.take_damage(10)
        surface = pygame.Surface((300, 300))
        background_color = (20, 30, 40)
        surface.fill(background_color)

        sprite.draw(surface, None, None)

        self.assertEqual(surface.get_at((105, 110))[:3], background_color)

    def test_rally_heals_half_recent_damage_and_consumes_window(self):
        scene = make_scene()
        ally = make_entity("Herói", "aliado", hp=100, x=100)
        enemy = make_entity("Goblin", "inimigo", hp=50, x=500)
        ally.current_hp = 50
        scene.rally_opportunities.extend([
            RallyOpportunity(enemy, ally, 10, config.RALLY_WINDOW_SECONDS),
            RallyOpportunity(enemy, ally, 20, config.RALLY_WINDOW_SECONDS),
        ])

        scene._try_rally(ally)

        self.assertEqual(ally.current_hp, 65)
        self.assertEqual(scene.rally_opportunities, [])
        self.assertEqual(scene.floating_texts[0].text, "RALLY +15")

    def test_rally_does_not_exceed_max_hp(self):
        scene = make_scene()
        ally = make_entity("Herói", "aliado", hp=100, x=100)
        enemy = make_entity("Goblin", "inimigo", hp=50, x=500)
        ally.current_hp = 95
        scene.rally_opportunities.append(
            RallyOpportunity(enemy, ally, 30, config.RALLY_WINDOW_SECONDS)
        )

        scene._try_rally(ally)

        self.assertEqual(ally.current_hp, ally.max_hp)
        self.assertEqual(scene.floating_texts[0].text, "RALLY +5")

    def test_clicking_recently_damaged_ally_activates_rally(self):
        scene = make_scene()
        ally = make_entity("Herói", "aliado", hp=100, x=100)
        enemy = make_entity("Goblin", "inimigo", hp=50, x=500)
        ally.current_hp = 50
        scene.time_aliados = [ally]
        scene.time_inimigos = [enemy]
        scene.rally_opportunities.append(
            RallyOpportunity(enemy, ally, 20, config.RALLY_WINDOW_SECONDS)
        )

        scene._handle_reaction_click(ally.rect.center)

        self.assertEqual(ally.current_hp, 60)

    def test_critical_adds_bonus_damage_and_starts_global_cooldown(self):
        scene = make_scene()
        ally = make_entity("Herói", "aliado", hp=100, x=100)
        enemy = make_entity("Goblin", "inimigo", hp=50, x=500)
        scene.critical_opportunities.append(
            CriticalOpportunity(ally, enemy, 12, config.CRITICAL_WINDOW_SECONDS)
        )

        scene._try_critical(enemy)

        self.assertEqual(enemy.current_hp, 47)
        self.assertEqual(
            scene.critical_cooldown_timer,
            config.CRITICAL_COOLDOWN_SECONDS,
        )
        self.assertEqual(scene.floating_texts[0].text, "CRITICAL Herói -3")
        self.assertEqual(scene.critical_opportunities, [])

    def test_critical_requires_a_recent_hit_on_the_clicked_enemy(self):
        scene = make_scene()
        ally = make_entity("Herói", "aliado", hp=100, x=100)
        hit_enemy = make_entity("Goblin", "inimigo", hp=50, x=500)
        other_enemy = make_entity("Invocador", "inimigo", hp=50, x=700)
        scene.critical_opportunities.append(
            CriticalOpportunity(ally, hit_enemy, 12, config.CRITICAL_WINDOW_SECONDS)
        )

        scene._try_critical(other_enemy)

        self.assertEqual(other_enemy.current_hp, other_enemy.max_hp)
        self.assertEqual(scene.critical_cooldown_timer, 0.0)

    def test_clicking_enemy_during_ally_hit_window_activates_critical(self):
        scene = make_scene()
        ally = make_entity("Herói", "aliado", hp=100, x=100)
        enemy = make_entity("Goblin", "inimigo", hp=50, x=500)
        scene.time_aliados = [ally]
        scene.time_inimigos = [enemy]
        scene.critical_opportunities.append(
            CriticalOpportunity(ally, enemy, 12, config.CRITICAL_WINDOW_SECONDS)
        )

        scene._handle_reaction_click(enemy.rect.center)

        self.assertEqual(enemy.current_hp, 47)
        self.assertEqual(scene.critical_cooldown_timer, config.CRITICAL_COOLDOWN_SECONDS)

    def test_critical_cannot_be_reused_during_global_cooldown(self):
        scene = make_scene()
        ally = make_entity("Herói", "aliado", hp=100, x=100)
        first_enemy = make_entity("Goblin", "inimigo", hp=50, x=500)
        second_enemy = make_entity("Invocador", "inimigo", hp=50, x=700)
        scene.critical_opportunities.extend([
            CriticalOpportunity(ally, first_enemy, 12, config.CRITICAL_WINDOW_SECONDS),
            CriticalOpportunity(ally, second_enemy, 12, config.CRITICAL_WINDOW_SECONDS),
        ])

        scene._try_critical(first_enemy)
        scene._try_critical(second_enemy)

        self.assertEqual(first_enemy.current_hp, 47)
        self.assertEqual(second_enemy.current_hp, second_enemy.max_hp)

    def test_critical_window_survives_attacker_death(self):
        scene = make_scene()
        ally = make_entity("Herói", "aliado", hp=100, x=100)
        enemy = make_entity("Goblin", "inimigo", hp=50, x=500)
        scene.critical_opportunities.append(
            CriticalOpportunity(ally, enemy, 12, config.CRITICAL_WINDOW_SECONDS)
        )
        ally.take_damage(ally.current_hp)

        scene._try_critical(enemy)

        self.assertEqual(enemy.current_hp, 47)

    def test_reaction_windows_expire(self):
        scene = make_scene()
        ally = make_entity("Herói", "aliado", hp=100, x=100)
        enemy = make_entity("Goblin", "inimigo", hp=50, x=500)
        scene.rally_opportunities.append(
            RallyOpportunity(enemy, ally, 10, config.RALLY_WINDOW_SECONDS)
        )
        scene.critical_opportunities.append(
            CriticalOpportunity(ally, enemy, 10, config.CRITICAL_WINDOW_SECONDS)
        )

        scene._update_reaction_opportunities(1.01, blocked=False)

        self.assertEqual(scene.rally_opportunities, [])
        self.assertEqual(scene.critical_opportunities, [])

    def test_target_preferences_choose_frontline_backline_or_vulnerable(self):
        actor = make_entity("Inimigo", "inimigo", hp=100, x=900)
        frontline = make_entity("Herói", "aliado", hp=100, x=400)
        backline = make_entity("Mago", "aliado", hp=100, x=100)
        targets = [frontline, backline]

        targeting = actor.get_component(TargetingComponent)
        targeting.set_opponent_team(targets)
        self.assertIs(targeting.target, frontline)

        targeting.target_preference = "backline"
        self.assertIs(targeting.find_target(), backline)

        backline.current_hp = 50
        targeting.target_preference = "vulnerable"
        self.assertIs(targeting.find_target(), backline)

    def test_every_room_has_three_enemies_with_targeting_variety(self):
        stages = get_default_stages()
        rooms = [room for stage in stages for room in stage.rooms]

        self.assertEqual(len(rooms), 4)
        for room in rooms:
            with self.subTest(room=room.name):
                self.assertEqual(len(room.enemies), 3)
                self.assertTrue(any(
                    enemy.unit_class.lower() == "mage"
                    for enemy in room.enemies
                ))
                self.assertTrue(any(
                    enemy.target_preference == "backline"
                    for enemy in room.enemies
                ))
                self.assertTrue(any(
                    enemy.target_preference == "vulnerable"
                    for enemy in room.enemies
                ))


if __name__ == "__main__":
    unittest.main()
