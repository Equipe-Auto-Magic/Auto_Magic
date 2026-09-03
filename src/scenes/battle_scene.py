import pygame
from src import config
from src.entity import Entity
from src.scenes.base_scene import BaseScene

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
    """Cena de Batalha (Auto Battler RPG)."""
    def __init__(self, game):
        super().__init__(game)
        
        # Posições dos Personagens na Arena
        hero_x = 220
        enemy_x = config.SCREEN_WIDTH - 220 - 100
        ground_y = 380

        # Criação das Entidades (Herói à esquerda, Inimigo à direita)
        self.hero = Entity(
            name="Herói", 
            max_hp=50, 
            attack_damage=18, 
            x=hero_x, 
            y=ground_y,
            color=config.COLOR_HERO,
            shadow_color=config.COLOR_HERO_SHADOW,
            attack_cooldown=config.ATTACK_COOLDOWN_DEFAULT
        )

        self.enemy = Entity(
            name="Inimigo", 
            max_hp=110, 
            attack_damage=15, 
            x=enemy_x, 
            y=ground_y,
            color=config.COLOR_ENEMY,
            shadow_color=config.COLOR_ENEMY_SHADOW,
            attack_cooldown=config.ATTACK_COOLDOWN_DEFAULT
        )

        # Estado da Batalha
        self.is_battle_over = False
        self.result_message = ""
        self.result_color = config.COLOR_TEXT_PRIMARY
        self.return_timer = config.RESULT_SCREEN_DELAY

        # Lista de textos flutuantes de dano
        self.floating_texts = []

        print("\n==========================================")
        print("⚔️  A BATALHA AUTOMÁTICA COMEÇOU!")
        print(f"Herói HP: {self.hero.max_hp} | ATK: {self.hero.attack_damage}")
        print(f"Inimigo HP: {self.enemy.max_hp} | ATK: {self.enemy.attack_damage}")
        print("==========================================\n")

    def handle_event(self, event: pygame.event.Event):
        # Permite retornar antecipadamente pressionando ESC
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            from src.scenes.menu_scene import MenuScene
            self.game.change_scene(MenuScene(self.game))

    def update(self, dt: float):
        # Se a batalha acabou, apenas conta o tempo para retornar ao Menu
        if self.is_battle_over:
            self.return_timer -= dt
            if self.return_timer <= 0:
                print("[BATALHA] Retornando ao Menu Principal...\n")
                from src.scenes.menu_scene import MenuScene
                self.game.change_scene(MenuScene(self.game))
            return

        # Atualiza o estado das entidades (acumula o cooldown de ataque)
        self.hero.update(dt)
        self.enemy.update(dt)

        # Atualiza textos flutuantes
        for ft in self.floating_texts[:]:
            ft.update(dt)
            if ft.is_dead():
                self.floating_texts.remove(ft)

        # --- LOOP DE COMBATE BASEADO EM COOLDOWN (1.5s) ---
        # Ambos atacam simultaneamente se ambos estiverem prontos
        hero_ready = self.hero.can_attack()
        enemy_ready = self.enemy.can_attack()

        if hero_ready or enemy_ready:
            # Herói causa dano ao Inimigo
            if hero_ready:
                self.enemy.take_damage(self.hero.attack_damage)
                self.hero.reset_cooldown()
                print(f"⚔️ [COMBATE] Herói causou {self.hero.attack_damage} de dano a Inimigo! (HP Inimigo: {self.enemy.current_hp}/{self.enemy.max_hp})")
                
                # Adiciona texto flutuante de dano no inimigo
                self.floating_texts.append(
                    FloatingText(f"-{self.hero.attack_damage}", self.enemy.x + 30, self.enemy.y - 10, config.COLOR_HP_LOW)
                )

            # Inimigo causa dano ao Herói
            if enemy_ready:
                self.hero.take_damage(self.enemy.attack_damage)
                self.enemy.reset_cooldown()
                print(f"⚔️ [COMBATE] Inimigo causou {self.enemy.attack_damage} de dano a Herói! (HP Herói: {self.hero.current_hp}/{self.hero.max_hp})")
                
                # Adiciona texto flutuante de dano no herói
                self.floating_texts.append(
                    FloatingText(f"-{self.enemy.attack_damage}", self.hero.x + 30, self.hero.y - 10, config.COLOR_HP_LOW)
                )

            # --- VERIFICAÇÃO DE CONDIÇÃO DE FIM DA BATALHA ---
            if not self.hero.is_alive() or not self.enemy.is_alive():
                self.is_battle_over = True
                
                if not self.hero.is_alive() and not self.enemy.is_alive():
                    self.result_message = "EMPATE!"
                    self.result_color = config.COLOR_TEXT_GOLD
                elif self.hero.is_alive():
                    self.result_message = "VITÓRIA!"
                    self.result_color = config.COLOR_HP_HIGH
                else:
                    self.result_message = "DERROTA!"
                    self.result_color = config.COLOR_HP_LOW

                print(f"\n🏆 [FIM DE COMBATE] Resultado: {self.result_message}")
                print(f"Retornando ao Menu Principal em {config.RESULT_SCREEN_DELAY} segundos...\n")

    def draw(self, surface: pygame.Surface):
        # Fundo da Cena
        self.draw_background(surface)

        # Header do Modo de Jogo
        header_surf = self.game.font_large.render("CAMPO DE BATALHA", True, config.COLOR_TEXT_PRIMARY)
        header_rect = header_surf.get_rect(center=(config.SCREEN_WIDTH // 2, 45))
        surface.blit(header_surf, header_rect)

        sub_surf = self.game.font_small.render("Combate Resolvido Automaticamente via Cooldown (1.5s)", True, config.COLOR_TEXT_MUTED)
        sub_rect = sub_surf.get_rect(center=(config.SCREEN_WIDTH // 2, 80))
        surface.blit(sub_surf, sub_rect)

        # VS Central Icon/Text
        vs_surf = self.game.font_title.render("VS", True, config.COLOR_PANEL_BORDER)
        vs_rect = vs_surf.get_rect(center=(config.SCREEN_WIDTH // 2, 450))
        surface.blit(vs_surf, vs_rect)

        # Desenha Entidades (Herói e Inimigo com Barras de HP)
        self.hero.draw(surface, self.game.font_bold, self.game.font_small)
        self.enemy.draw(surface, self.game.font_bold, self.game.font_small)

        # Desenha Textos Flutuantes de Dano
        for ft in self.floating_texts:
            surf = self.game.font_large.render(ft.text, True, ft.color)
            surf.set_alpha(ft.alpha)
            surface.blit(surf, (ft.x, ft.y))

        # --- TELA DE VITÓRIA / DERROTA (OVERLAY FINAL) ---
        if self.is_battle_over:
            # Overlay translúcido de fundo
            overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((10, 12, 20, 200))
            surface.blit(overlay, (0, 0))

            # Banner do Resultado
            banner_rect = pygame.Rect(config.SCREEN_WIDTH // 2 - 280, config.SCREEN_HEIGHT // 2 - 100, 560, 200)
            pygame.draw.rect(surface, config.COLOR_BG_CARD, banner_rect, border_radius=16)
            pygame.draw.rect(surface, self.result_color, banner_rect, width=3, border_radius=16)

            # Texto Principal ("VITÓRIA!" / "DERROTA!")
            res_surf = self.game.font_title.render(self.result_message, True, self.result_color)
            res_rect = res_surf.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 - 30))
            surface.blit(res_surf, res_rect)

            # Contagem Regressiva para retornar ao menu
            countdown_text = f"Retornando ao Menu em {max(1, int(self.return_timer + 0.9))}s..."
            cnt_surf = self.game.font_medium.render(countdown_text, True, config.COLOR_TEXT_SECONDARY)
            cnt_rect = cnt_surf.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 + 40))
            surface.blit(cnt_surf, cnt_rect)
