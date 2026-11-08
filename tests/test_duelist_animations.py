import unittest

import pygame

from src import config
from src.entity import (
    Entity,
    EntityState,
    HealthComponent,
    SpriteComponent,
    TargetingComponent,
    TransformComponent,
)


class DuelistAnimationTests(unittest.TestCase):
    def make_duelist_sprite(self):
        entity = Entity(name="Herói", team="aliado")
        entity.add_component(TransformComponent(x=100, y=100))
        entity.add_component(HealthComponent(max_hp=100))
        entity.add_component(TargetingComponent())
        sprite = SpriteComponent(
            sprite_sheet_path=config.DUELIST_SPRITE_PATH,
            frame_size=config.DUELIST_FRAME_SIZE,
            animations=config.DUELIST_ANIMATIONS,
            animation_rects=config.DUELIST_ANIMATION_RECTS,
            animation_fps=config.DUELIST_ANIMATION_FPS,
        )
        entity.add_component(sprite)
        return entity, sprite

    def test_loads_duelist_frames_with_transparent_background(self):
        _, sprite = self.make_duelist_sprite()

        self.assertEqual(sprite.animation_name, "idle")
        self.assertEqual(len(sprite.animations["idle"]), 2)
        self.assertEqual(sprite.animations["idle"][0].get_size(), (40, 46))
        self.assertEqual(sprite.animations["idle"][1].get_size(), (38, 46))
        self.assertEqual(
            [frame.get_size() for frame in sprite.animations["walk"]],
            [(30, 45), (37, 45), (31, 45), (35, 45)],
        )
        self.assertEqual(
            [frame.get_size() for frame in sprite.animations["attack"]],
            [(40, 57), (54, 57), (34, 57), (36, 57), (56, 57)],
        )
        self.assertEqual(
            [frame.get_size() for frame in sprite.animations["death"]],
            [(38, 41), (46, 30)],
        )
        self.assertEqual(sprite.animations["idle"][0].get_colorkey()[:3], (82, 109, 140))

    def test_draws_duelist_without_the_sheet_background(self):
        _, sprite = self.make_duelist_sprite()
        pygame.font.init()
        font = pygame.font.Font(None, 14)
        surface = pygame.Surface((400, 400))
        background_color = (20, 30, 40)
        surface.fill(background_color)

        sprite.draw(surface, font, font)

        self.assertEqual(surface.get_at((199, 239))[:3], background_color)
        self.assertNotEqual(surface.get_at((100, 125))[:3], background_color)

    def test_selects_walk_and_idle_from_entity_state(self):
        entity, sprite = self.make_duelist_sprite()
        entity.state = EntityState.ANDANDO
        sprite.update(0.0)
        self.assertEqual(sprite.animation_name, "walk")

        entity.state = EntityState.PREPARANDO
        sprite.update(0.0)
        self.assertEqual(sprite.animation_name, "idle")

    def test_attack_animation_plays_once_then_returns_to_idle(self):
        entity, sprite = self.make_duelist_sprite()
        entity.state = EntityState.PREPARANDO
        sprite.trigger_attack_feedback()
        self.assertEqual(sprite.animation_name, "attack")

        sprite.update(0.7)

        self.assertTrue(sprite.animation_finished)
        sprite.update(0.0)
        self.assertEqual(sprite.animation_name, "idle")

    def test_dead_duelist_plays_death_frames_before_hiding(self):
        entity, sprite = self.make_duelist_sprite()
        entity.take_damage(entity.max_hp)
        sprite.update(0.0)

        self.assertEqual(sprite.animation_name, "death")
        self.assertFalse(sprite.animation_finished)

        sprite.update(0.3)

        self.assertTrue(sprite.animation_finished)

        surface = pygame.Surface((300, 300))
        background_color = (20, 30, 40)
        surface.fill(background_color)
        sprite.draw(surface, None, None)
        self.assertEqual(surface.get_at((150, 150))[:3], background_color)


if __name__ == "__main__":
    unittest.main()
