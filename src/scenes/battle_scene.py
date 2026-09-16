import pygame
from src import config
from src.entity import Warrior, Mage
from src.scenes.base_scene import BaseScene
from src.events import gerenciador_eventos, BuffDeFuria
from src.stage_manager import StageManager, StageState


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

        # 1. Aliados são criados uma ÚNICA vez no início da batalha
        self.hero = Warrior(
            name="Herói",
            max_hp=50,
            attack_damage=18,
            x=hero_x,
            y=ground_y,
            color=config.COLOR_HERO,
            shadow_color=config.COLOR_HERO_SHADOW,
            attack_cooldown=config.ATTACK_COOLDOWN_DEFAULT,
            default_direction=1.0,
            team="aliado"
        )

        self.mage = Mage(
            name="Mago",
            max_hp=30,
            attack_damage=12,
            x=mage_x,
            y=ground_y,
            color=config.COLOR_MAGE,
            shadow_color=config.COLOR_MAGE_SHADOW,
            attack_cooldown=2.0,  # Mago ataca um pouco mais lento
            default_direction=1.0,
            team="aliado"
        )

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
                target.take_damage(attacker.attack_damage)
                attacker.reset_cooldown()

                is_mage = isinstance(attacker, Mage)
                icon = "✨" if is_mage else "⚔️"
                color = config.COLOR_MAGE if is_mage else config.COLOR_HP_LOW

                print(f"{icon}  [COMBATE] {attacker.name} causou {attacker.attack_damage} de dano! "
                      f"(HP {target.name}: {target.current_hp}/{target.max_hp})")

                # Texto flutuante posicionado dinamicamente sobre o alvo
                offset_x = 50 if is_mage else 30
                offset_y = -30 if is_mage else -10
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
