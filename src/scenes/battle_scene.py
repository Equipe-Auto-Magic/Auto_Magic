from dataclasses import dataclass
import pygame
from src import config
from src.entity import (
    Entity,
    TransformComponent,
    HealthComponent,
    MovementComponent,
    CombatComponent,
    TargetingComponent,
    SpriteComponent,
    RenderComponent,
    Warrior,
    Mage
)
from src.scenes.base_scene import BaseScene
from src.events import gerenciador_eventos, BuffDeFuria
from src.stage_manager import StageManager, StageState


@dataclass
class RallyOpportunity:
    attacker: Entity
    ally: Entity
    damage_taken: int
    time_left: float


@dataclass
class CriticalOpportunity:
    attacker: Entity
    enemy: Entity
    damage_dealt: int
    time_left: float


class FloatingText:
    """Texto flutuante para animação de dano na tela."""
    def __init__(self, text: str, x: int, y: int, color=config.COLOR_HP_LOW):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.alpha = 255
        self.lifetime = 1.0  # dura 1 segundo

    def update(self, dt: float):
        self.y -= 30 * dt    # Sobe 30px/s
        self.lifetime -= dt
        self.alpha = max(0, int(255 * (self.lifetime / 1.0)))

    def is_dead(self) -> bool:
        return self.lifetime <= 0


class BattleScene(BaseScene):
    """Cena de Batalha com Sistema de Fases e Salas (Auto Battler RPG)."""

    def __init__(self, game):
        super().__init__(game)

        ground_y = config.GROUND_Y
        hero_x = 180
        mage_x = hero_x - 120  # Mago fica atrás do herói

        # --- Sistema de Grupos / Times (Facções) ---
        self.time_aliados = []
        self.time_inimigos = []
        self.rally_opportunities = []
        self.critical_opportunities = []
        self.critical_cooldown_timer = 0.0

        # 1. Aliados são criados uma ÚNICA vez no início da batalha usando o Padrão de Componentes
        self.hero = Entity(name="Herói", team="aliado")
        self.hero.add_component(TransformComponent(x=hero_x, y=ground_y, width=100, height=140))
        self.hero.add_component(HealthComponent(max_hp=240))
        self.hero.add_component(MovementComponent(speed=config.WARRIOR_SPEED, default_direction=1.0))
        self.hero.add_component(CombatComponent(dano=18, alcance=config.WARRIOR_ATTACK_RANGE, cooldown=config.ATTACK_COOLDOWN_DEFAULT))
        self.hero.add_component(TargetingComponent())
        self.hero.add_component(SpriteComponent(width=100, height=140, color=config.COLOR_HERO, shadow_color=config.COLOR_HERO_SHADOW))

        self.mage = Entity(name="Mago", team="aliado")
        self.mage.add_component(TransformComponent(x=mage_x, y=ground_y, width=100, height=140))
        self.mage.add_component(HealthComponent(max_hp=80))
        self.mage.add_component(MovementComponent(speed=config.MAGE_SPEED, default_direction=1.0))
        self.mage.add_component(CombatComponent(dano=12, alcance=config.MAGE_ATTACK_RANGE, cooldown=2.0))
        self.mage.add_component(TargetingComponent())
        self.mage.add_component(SpriteComponent(width=100, height=140, color=config.COLOR_MAGE, shadow_color=config.COLOR_MAGE_SHADOW))

        self.time_aliados.append(self.hero)
        self.time_aliados.append(self.mage)

        # 2. Habilidade Passiva (Padrão Observer): BuffDeFuria
        self.buff_furia = BuffDeFuria(self.time_aliados, self)
        gerenciador_eventos.inscrever("entidade_morta", self.buff_furia)

        # 3. Gerenciador de Fases e Salas (cria inimigos sob demanda e controla progressão)
        self.stage_manager = StageManager(self.time_aliados, self.time_inimigos, self)

        # Lista de textos flutuantes de dano
        self.floating_texts = []

    def cleanup(self):
        """Limpa inscrições de observadores para evitar retenção de referências."""
        if hasattr(self, 'buff_furia'):
            gerenciador_eventos.desinscrever("entidade_morta", self.buff_furia)
        if hasattr(self, 'stage_manager'):
            self.stage_manager.cleanup()

    def todas_entidades(self):
        """Retorna lista com todas as entidades de ambos os times."""
        return self.time_aliados + self.time_inimigos

    def handle_event(self, event: pygame.event.Event):
        # Permite retornar antecipadamente pressionando ESC
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            from src.scenes.menu_scene import MenuScene
            self.game.change_scene(MenuScene(self.game))
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._handle_reaction_click(event.pos)

    def _handle_reaction_click(self, position: tuple[int, int]) -> None:
        if self.stage_manager.state != StageState.COMBATE:
            return

        ally = next(
            (ally for ally in reversed(self.time_aliados)
             if ally.is_alive() and ally.rect.collidepoint(position)),
            None
        )
        if ally is not None:
            self._try_rally(ally)
            return

        enemy = next(
            (enemy for enemy in reversed(self.time_inimigos)
             if enemy.is_alive() and enemy.rect.collidepoint(position)),
            None
        )
        if enemy is not None:
            self._try_critical(enemy)

    def _try_rally(self, ally: Entity) -> None:
        opportunities = [
            opportunity for opportunity in self.rally_opportunities
            if opportunity.ally is ally and opportunity.time_left > 0
        ]
        if not opportunities:
            return

        self.rally_opportunities = [
            opportunity for opportunity in self.rally_opportunities
            if opportunity.ally is not ally
        ]
        if not ally.is_alive():
            return

        recent_damage = sum(opportunity.damage_taken for opportunity in opportunities)
        recovery = int(recent_damage * config.RALLY_RECOVERY_RATIO)
        amount_recovered = ally.heal(recovery)
        if amount_recovered > 0:
            self.floating_texts.append(
                FloatingText(
                    f"RALLY +{amount_recovered}",
                    int(ally.x) + 10,
                    int(ally.y) - 40,
                    config.COLOR_TEXT_GOLD
                )
            )

    def _try_critical(self, enemy: Entity) -> None:
        if self.critical_cooldown_timer > 0:
            return

        opportunity = next(
            (opportunity for opportunity in reversed(self.critical_opportunities)
             if opportunity.enemy is enemy and opportunity.time_left > 0),
            None
        )
        if opportunity is None or not enemy.is_alive():
            return

        bonus_damage = int(
            opportunity.damage_dealt * (config.CRITICAL_DAMAGE_MULTIPLIER - 1.0)
        )
        if bonus_damage <= 0:
            return

        damage_dealt = enemy.take_damage(bonus_damage)
        self.critical_opportunities = [
            pending for pending in self.critical_opportunities
            if pending.enemy is not enemy
        ]
        if damage_dealt <= 0:
            return

        self.critical_cooldown_timer = config.CRITICAL_COOLDOWN_SECONDS
        self.floating_texts.append(
            FloatingText(
                f"CRITICAL {opportunity.attacker.name} -{damage_dealt}",
                int(enemy.x) + 30,
                int(enemy.y) - 40,
                config.COLOR_STATE_ATTACKING
            )
        )

    def _update_reaction_opportunities(self, dt: float, blocked: bool) -> None:
        if blocked:
            self.rally_opportunities.clear()
            self.critical_opportunities.clear()
            return

        self.critical_cooldown_timer = max(0.0, self.critical_cooldown_timer - dt)
        for opportunity in self.rally_opportunities:
            opportunity.time_left -= dt
        self.rally_opportunities = [
            opportunity for opportunity in self.rally_opportunities
            if opportunity.time_left > 0
            and opportunity.ally.is_alive()
        ]
        for opportunity in self.critical_opportunities:
            opportunity.time_left -= dt
        self.critical_opportunities = [
            opportunity for opportunity in self.critical_opportunities
            if opportunity.time_left > 0
            and opportunity.enemy.is_alive()
        ]

    def _draw_reaction_targets(self, surface: pygame.Surface) -> None:
        if self.stage_manager.state != StageState.COMBATE:
            return

        active_rallies = {}
        for opportunity in self.rally_opportunities:
            if opportunity.time_left <= 0 or not opportunity.ally.is_alive():
                continue
            active_rallies[opportunity.ally] = max(
                active_rallies.get(opportunity.ally, 0.0),
                opportunity.time_left
            )

        for ally, time_left in active_rallies.items():
            pygame.draw.rect(
                surface,
                config.COLOR_TEXT_GOLD,
                ally.rect.inflate(8, 8),
                width=3,
                border_radius=14
            )
            label = self.game.font_small.render(
                f"RALLY {time_left:.1f}s",
                True,
                config.COLOR_TEXT_GOLD
            )
            label_rect = label.get_rect(center=(ally.rect.centerx, ally.rect.top - 94))
            surface.blit(label, label_rect)

        active_criticals = {}
        for opportunity in self.critical_opportunities:
            if opportunity.time_left <= 0 or not opportunity.enemy.is_alive():
                continue
            active_criticals[opportunity.enemy] = max(
                active_criticals.get(opportunity.enemy, 0.0),
                opportunity.time_left
            )

        for enemy, time_left in active_criticals.items():
            pygame.draw.rect(
                surface,
                config.COLOR_STATE_ATTACKING,
                enemy.rect.inflate(8, 8),
                width=3,
                border_radius=14
            )
            label = self.game.font_small.render(
                f"CRITICAL {time_left:.1f}s",
                True,
                config.COLOR_STATE_ATTACKING
            )
            label_rect = label.get_rect(center=(enemy.rect.centerx, enemy.rect.top - 94))
            surface.blit(label, label_rect)

    def _draw_reaction_status(self, surface: pygame.Surface) -> None:
        if self.stage_manager.state != StageState.COMBATE:
            return

        if self.critical_cooldown_timer > 0:
            message = (
                f"Rally: clique no aliado ferido  |  "
                f"Critical recarrega em {self.critical_cooldown_timer:.1f}s"
            )
            color = config.COLOR_TEXT_SECONDARY
        else:
            message = (
                "Clique no aliado ferido: Rally  |  "
                "Clique no inimigo atingido: Critical"
            )
            color = config.COLOR_TEXT_GOLD

        label = self.game.font_small.render(message, True, color)
        rect = label.get_rect(center=(config.SCREEN_WIDTH // 2, 100))
        surface.blit(label, rect)

    def update(self, dt: float):
        # Atualiza textos flutuantes
        for ft in self.floating_texts[:]:
            ft.update(dt)
            if ft.is_dead():
                self.floating_texts.remove(ft)

        # Atualiza a máquina de estados do StageManager
        action = self.stage_manager.update(dt)
        if action == "MENU":
            print("[BATALHA] Retornando ao Menu Principal...\n")
            from src.scenes.menu_scene import MenuScene
            self.game.change_scene(MenuScene(self.game))
            return

        is_game_over = self.stage_manager.state in (StageState.JOGO_CONCLUIDO, StageState.DERROTA)
        is_transition = self.stage_manager.state in (StageState.TRANSICAO, StageState.FASE_CONCLUIDA)
        self._update_reaction_opportunities(dt, is_transition or is_game_over)

        # Atualiza movimentação/estado dos personagens
        for entidade in self.todas_entidades():
            entidade.update(dt)

        # Durante transições ou fim de jogo, o combate direto fica pausado
        if is_transition or is_game_over:
            return

        # --- LOOP DE COMBATE AUTÔNOMO ENTRE TIMES ---
        for attacker in self.todas_entidades():
            if attacker.can_attack() and attacker.target is not None and attacker.target.is_alive():
                target = attacker.target
                damage_taken = target.take_damage(attacker.attack_damage)
                if (attacker.team == "inimigo" and target.team == "aliado"
                        and damage_taken > 0 and target.is_alive()):
                    self.rally_opportunities.append(
                        RallyOpportunity(
                            attacker=attacker,
                            ally=target,
                            damage_taken=damage_taken,
                            time_left=config.RALLY_WINDOW_SECONDS
                        )
                    )
                elif (attacker.team == "aliado" and target.team == "inimigo"
                      and damage_taken > 0 and target.is_alive()):
                    self.critical_opportunities.append(
                        CriticalOpportunity(
                            attacker=attacker,
                            enemy=target,
                            damage_dealt=damage_taken,
                            time_left=config.CRITICAL_WINDOW_SECONDS
                        )
                    )
                attacker.reset_cooldown()
                attacker.trigger_attack_feedback()

                combat = attacker.get_component(CombatComponent)
                is_ranged = combat.attack_range > 100 if combat else ("Mago" in attacker.name or "Feiticeiro" in attacker.name or "Invocador" in attacker.name)
                icon = "[MAGIA]" if is_ranged else "[GOLPE]"
                color = config.COLOR_MAGE if is_ranged else config.COLOR_HP_LOW

                try:
                    print(f"{icon} [COMBATE] {attacker.name} causou {attacker.attack_damage} de dano! "
                          f"(HP {target.name}: {target.current_hp}/{target.max_hp})")
                except UnicodeEncodeError:
                    pass

                # Texto flutuante posicionado dinamicamente sobre o alvo
                offset_x = 50 if is_ranged else 30
                offset_y = -30 if is_ranged else -10
                self.floating_texts.append(
                    FloatingText(f"-{attacker.attack_damage}",
                                 int(target.x) + offset_x,
                                 int(target.y) + offset_y,
                                 color)
                )

    def draw(self, surface: pygame.Surface):
        # Fundo da Cena
        self.draw_background(surface)

        # Header com Fase e Sala Atual
        stage = self.stage_manager.current_stage
        room = self.stage_manager.current_room
        header_text = f"FASE {stage.stage_number}: {stage.name.upper()}  —  SALA {room.room_number}/{self.stage_manager.total_rooms_in_current_stage}"
        header_surf = self.game.font_large.render(header_text, True, config.COLOR_TEXT_PRIMARY)
        header_rect = header_surf.get_rect(center=(config.SCREEN_WIDTH // 2, 40))
        surface.blit(header_surf, header_rect)

        sub_surf = self.game.font_small.render(f"Sala atual: {room.name}", True, config.COLOR_TEXT_MUTED)
        sub_rect = sub_surf.get_rect(center=(config.SCREEN_WIDTH // 2, 70))
        surface.blit(sub_surf, sub_rect)

        # VS Central Icon/Text
        vs_surf = self.game.font_title.render("VS", True, config.COLOR_PANEL_BORDER)
        vs_rect = vs_surf.get_rect(center=(config.SCREEN_WIDTH // 2, 450))
        surface.blit(vs_surf, vs_rect)

        # Desenha autonomamente todas as Entidades
        for entidade in self.todas_entidades():
            entidade.draw(surface, self.game.font_bold, self.game.font_small)

        self._draw_reaction_targets(surface)
        self._draw_reaction_status(surface)

        # Desenha Textos Flutuantes de Dano
        for ft in self.floating_texts:
            surf = self.game.font_large.render(ft.text, True, ft.color)
            surf.set_alpha(ft.alpha)
            surface.blit(surf, (ft.x, ft.y))

        # --- BANNER DE TRANSIÇÃO DE SALA OU FASE ---
        if self.stage_manager.state in (StageState.TRANSICAO, StageState.FASE_CONCLUIDA):
            banner_rect = pygame.Rect(config.SCREEN_WIDTH // 2 - 250, 100, 500, 50)
            pygame.draw.rect(surface, config.COLOR_BG_CARD, banner_rect, border_radius=10)
            pygame.draw.rect(surface, config.COLOR_TEXT_GOLD, banner_rect, width=2, border_radius=10)

            msg_surf = self.game.font_bold.render(self.stage_manager.status_message, True, config.COLOR_TEXT_GOLD)
            msg_rect = msg_surf.get_rect(center=banner_rect.center)
            surface.blit(msg_surf, msg_rect)

        # --- TELA DE VITÓRIA COMPLETA / DERROTA (OVERLAY FINAL) ---
        if self.stage_manager.state in (StageState.JOGO_CONCLUIDO, StageState.DERROTA):
            overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((10, 12, 20, 200))
            surface.blit(overlay, (0, 0))

            banner_rect = pygame.Rect(config.SCREEN_WIDTH // 2 - 280, config.SCREEN_HEIGHT // 2 - 100, 560, 200)
            pygame.draw.rect(surface, config.COLOR_BG_CARD, banner_rect, border_radius=16)
            pygame.draw.rect(surface, self.stage_manager.result_color, banner_rect, width=3, border_radius=16)

            res_surf = self.game.font_title.render(self.stage_manager.result_message, True, self.stage_manager.result_color)
            res_rect = res_surf.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 - 30))
            surface.blit(res_surf, res_rect)

            countdown_text = f"Retornando ao Menu em {max(1, int(self.stage_manager.result_timer + 0.9))}s..."
            cnt_surf = self.game.font_medium.render(countdown_text, True, config.COLOR_TEXT_SECONDARY)
            cnt_rect = cnt_surf.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 + 40))
            surface.blit(cnt_surf, cnt_rect)
