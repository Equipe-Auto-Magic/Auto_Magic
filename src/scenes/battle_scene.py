import pygame
from src import config
from src.entity import Warrior, Mage
from src.scenes.base_scene import BaseScene
from src.events import gerenciador_eventos, BuffDeFuria

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

        # Guerreiros nascem nos extremos opostos da tela
        hero_x = 180
        mage_x = hero_x - 120 # Mago fica atrás do herói
        enemy_x = config.SCREEN_WIDTH - 80 - 100  # desconta a largura do sprite
        enemyMage_x = enemy_x + 120 # Bruxo fica atrás do inimigo
        ground_y = 380

        # --- Sistema de Grupos / Times (Facções) ---
        self.time_aliados = []
        self.time_inimigos = []

        # Criação dos Personagens
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
            attack_cooldown=2.0, # Mago ataca um pouco mais lento
            default_direction=1.0,
            team="aliado"
        )

        self.enemy = Warrior(
            name="Inimigo",
            max_hp=110,
            attack_damage=15,
            x=enemy_x,
            y=ground_y,
            color=config.COLOR_ENEMY,
            shadow_color=config.COLOR_ENEMY_SHADOW,
            attack_cooldown=config.ATTACK_COOLDOWN_DEFAULT,
            default_direction=-1.0,
            team="inimigo"
        )

        self.enemyMage = Mage(
            name="Bruxo",
            max_hp=90,
            attack_damage=10,
            x=enemyMage_x,
            y=ground_y,
            color=config.COLOR_ENEMY,
            shadow_color=config.COLOR_ENEMY_SHADOW,
            attack_cooldown=2.0,
            default_direction=-1.0,
            team="inimigo"
        )

        # Atribuição Automática aos Times (cada entidade recebe a referência dinâmica do time adversário)
        self.adicionar_aliado(self.hero)
        self.adicionar_aliado(self.mage)
        self.adicionar_inimigo(self.enemy)
        self.adicionar_inimigo(self.enemyMage)

        # Habilidade Passiva (Padrão Observer): BuffDeFuria
        self.buff_furia = BuffDeFuria(self.time_aliados, self)
        gerenciador_eventos.inscrever("entidade_morta", self.buff_furia)

        # Estado da Batalha
        self.is_battle_over = False
        self.result_message = ""
        self.result_color = config.COLOR_TEXT_PRIMARY
        self.return_timer = config.RESULT_SCREEN_DELAY

        # Lista de textos flutuantes de dano
        self.floating_texts = []

        print("\n==========================================")
        print("⚔️  A BATALHA AUTOMÁTICA COMEÇOU!")
        for e in self.time_aliados:
            print(f"Aliado:  {e.name:<8} HP: {e.max_hp} | ATK: {e.attack_damage} | VEL: {e.speed}px/s | ALCANCE: {e.attack_range}px")
        for e in self.time_inimigos:
            print(f"Inimigo: {e.name:<8} HP: {e.max_hp} | ATK: {e.attack_damage} | VEL: {e.speed}px/s | ALCANCE: {e.attack_range}px")
        print("==========================================\n")

    def cleanup(self):
        """Limpa inscrições de observadores para evitar retenção de referências."""
        if hasattr(self, 'buff_furia'):
            gerenciador_eventos.desinscrever("entidade_morta", self.buff_furia)

    def adicionar_aliado(self, entidade):
        """Adiciona uma entidade ao time aliado e vincula a referência do time inimigo."""
        entidade.set_opponent_team(self.time_inimigos)
        self.time_aliados.append(entidade)
        return entidade

    def adicionar_inimigo(self, entidade):
        """Adiciona uma entidade ao time inimigo e vincula a referência do time aliado."""
        entidade.set_opponent_team(self.time_aliados)
        self.time_inimigos.append(entidade)
        return entidade

    def todas_entidades(self):
        """Retorna lista com todas as entidades de ambos os times."""
        return self.time_aliados + self.time_inimigos

    def handle_event(self, event: pygame.event.Event):
        # Permite retornar antecipadamente pressionando ESC
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            from src.scenes.menu_scene import MenuScene
            self.game.change_scene(MenuScene(self.game))

    def update(self, dt: float):
        # Se a batalha acabou, conta o tempo para retornar ao Menu e mantém animações
        if self.is_battle_over:
            self.return_timer -= dt
            if self.return_timer <= 0:
                print("[BATALHA] Retornando ao Menu Principal...\n")
                from src.scenes.menu_scene import MenuScene
                self.game.change_scene(MenuScene(self.game))
                return

            # Mantém atualização dos personagens (caminhada pós-vitória) e textos
            for entidade in self.todas_entidades():
                entidade.update(dt)

            for ft in self.floating_texts[:]:
                ft.update(dt)
                if ft.is_dead():
                    self.floating_texts.remove(ft)
            return

        # Atualiza autonomamente o estado de todas as entidades de ambos os times
        for entidade in self.todas_entidades():
            entidade.update(dt)

        # Atualiza textos flutuantes
        for ft in self.floating_texts[:]:
            ft.update(dt)
            if ft.is_dead():
                self.floating_texts.remove(ft)

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

        # --- VERIFICAÇÃO DE CONDIÇÃO DE FIM DA BATALHA POR TIMES ---
        if not self.is_battle_over:
            aliados_vivos = any(e.is_alive() for e in self.time_aliados)
            inimigos_vivos = any(e.is_alive() for e in self.time_inimigos)

            if not aliados_vivos or not inimigos_vivos:
                self.is_battle_over = True

                if not aliados_vivos and not inimigos_vivos:
                    self.result_message = "EMPATE!"
                    self.result_color = config.COLOR_TEXT_GOLD
                elif aliados_vivos:
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

        sub_surf = self.game.font_small.render("Guerreiros avançam em direção um ao outro antes de atacar", True, config.COLOR_TEXT_MUTED)
        sub_rect = sub_surf.get_rect(center=(config.SCREEN_WIDTH // 2, 80))
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
