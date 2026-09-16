"""
Módulo de Gerenciamento de Fases, Salas e Ciclo de Vida da Batalha.
Implementa o padrão Observer para reagir a 'entidade_morta', controla estados
de COMBATE, TRANSICAO, FASE_CONCLUIDA, JOGO_CONCLUIDO e DERROTA sem transições duplas.
"""
import random
from typing import List, Optional
from src import config
from src.events import Observador, gerenciador_eventos
from src.stage_data import StageConfig, RoomConfig, EnemyFactory, get_default_stages
from src.entity import Entity


class StageState:
    COMBATE = "COMBATE"
    TRANSICAO = "TRANSICAO"
    FASE_CONCLUIDA = "FASE_CONCLUIDA"
    JOGO_CONCLUIDO = "JOGO_CONCLUIDO"
    DERROTA = "DERROTA"


class StageManager(Observador):
    """
    Gerenciador de Fases e Salas.
    Responsabilidades:
    - Controlar a progressão de salas e fases.
    - Preservar instâncias de aliados, mantendo current_hp e atributos.
    - Criar sob demanda os inimigos de cada sala (EnemyFactory).
    - Alternar backgrounds evitando repetições imediatas.
    - Controlar transições temporizadas sem time.sleep.
    - Notificar 'fase_concluida' ao terminar as salas de uma fase.
    - Prevenir transições duplas via máquina de estados rigorosa.
    - Se desinscrever no cleanup para não vazar observers.
    """

    def __init__(self, time_aliados: List[Entity], time_inimigos: List[Entity], scene):
        self.time_aliados = time_aliados
        self.time_inimigos = time_inimigos
        self.scene = scene

        # Configuração de fases (Data-Driven)
        self.stages: List[StageConfig] = get_default_stages()
        self.current_stage_idx: int = 0
        self.current_room_idx: int = 0

        # Máquina de estados
        self.state: str = StageState.COMBATE

        # Temporizadores para transições
        self.transition_timer: float = 0.0
        self.result_timer: float = config.RESULT_SCREEN_DELAY

        # Histórico de background para evitar repetir imediatamente
        self.last_bg_path: Optional[str] = None

        # Mensagens para renderização de status na UI
        self.status_message: str = ""
        self.result_message: str = ""
        self.result_color = config.COLOR_TEXT_PRIMARY

        # Inscreve-se no EventBus para reagir à morte de entidades
        gerenciador_eventos.inscrever("entidade_morta", self)

        # Inicia a primeira sala
        self._iniciar_sala_atual(is_first_room=True)

    def cleanup(self):
        """Desinscreve o gerenciador do EventBus para evitar acúmulo de observers."""
        gerenciador_eventos.desinscrever("entidade_morta", self)

    # ------------------------------------------------------------------
    # Propriedades de conveniência
    # ------------------------------------------------------------------

    @property
    def current_stage(self) -> StageConfig:
        return self.stages[self.current_stage_idx]

    @property
    def current_room(self) -> RoomConfig:
        return self.current_stage.rooms[self.current_room_idx]

    @property
    def total_stages(self) -> int:
        return len(self.stages)

    @property
    def total_rooms_in_current_stage(self) -> int:
        return len(self.current_stage.rooms)

    # ------------------------------------------------------------------
    # Controle de Salas e Transições
    # ------------------------------------------------------------------

    def _escolher_novo_background(self):
        """Seleciona um background aleatório da lista, evitando repetir o anterior."""
        opcoes = config.BACKGROUND_IMAGES
        if not opcoes:
            return

        if len(opcoes) == 1:
            escolhido = opcoes[0]
        else:
            candidatos = [bg for bg in opcoes if bg != self.last_bg_path]
            escolhido = random.choice(candidatos if candidatos else opcoes)

        self.last_bg_path = escolhido
        if hasattr(self.scene, "set_background"):
            self.scene.set_background(escolhido)

    def _iniciar_sala_atual(self, is_first_room: bool = False):
        """Configura os combatentes e ambiente para a sala atual."""
        self.state = StageState.COMBATE
        self.status_message = ""

        # Alterna background
        self._escolher_novo_background()

        # 1. Reposiciona e reseta temporários dos aliados (mantendo objetos e HP)
        base_hero_x = 180
        base_ground_y = config.GROUND_Y

        for i, aliado in enumerate(self.time_aliados):
            # Posicionamento à esquerda com pequenos deslocamentos
            # Ex: Herói na frente (x=180), segundo aliado atrás (x=60)
            desloc_x = -(i * 120) if i > 0 else 0
            desloc_y = (i % 2) * 10
            aliado.x = float(base_hero_x + desloc_x)
            aliado.y = float(base_ground_y + desloc_y)
            aliado.rect.x = int(aliado.x)
            aliado.rect.y = int(aliado.y)

            # Reseta apenas estados temporários de batalha
            aliado.target = None
            aliado.cooldown_timer = 0.0
            aliado.flash_timer = 0.0
            if aliado.is_alive():
                aliado.state = 'andando' if aliado.speed > 0 else 'atacando'

        # 2. Limpa o time inimigo anterior
        self.time_inimigos.clear()

        # 3. Cria sob demanda apenas os inimigos da sala atual
        room_cfg = self.current_room
        base_enemy_x = config.SCREEN_WIDTH - 80 - 100
        for enemy_cfg in room_cfg.enemies:
            inimigo = EnemyFactory.create_enemy(enemy_cfg, base_x=base_enemy_x, base_y=base_ground_y)
            self.time_inimigos.append(inimigo)

        # 4. Atualiza as referências mútuas de oponentes
        for aliado in self.time_aliados:
            aliado.set_opponent_team(self.time_inimigos)
        for inimigo in self.time_inimigos:
            inimigo.set_opponent_team(self.time_aliados)

        print(f"\n==========================================")
        print(f"[FASE {self.current_stage.stage_number}] {self.current_stage.name} - Sala {room_cfg.room_number}/{self.total_rooms_in_current_stage}: {room_cfg.name}")
        print(f"Aliados vivos: {[a.name + f' (HP {a.current_hp}/{a.max_hp})' for a in self.time_aliados if a.is_alive()]}")
        print(f"Inimigos na sala: {[e.name + f' (HP {e.max_hp})' for e in self.time_inimigos]}")
        print("==========================================\n")

    # ------------------------------------------------------------------
    # Reação a Eventos (Observer)
    # ------------------------------------------------------------------

    def ao_notificar(self, evento: str, dados: any) -> None:
        """Chamado quando um evento é disparado pelo EventBus."""
        if evento == "entidade_morta":
            # Realiza checagem segura logo após uma morte
            self._verificar_condicoes_combate()

    def _verificar_condicoes_combate(self):
        """
        Verifica se a sala foi limpa ou se os aliados foram derrotados.
        Garante que apenas inimigos VIVOS sejam considerados.
        Previne transições duplas se já não estiver em COMBATE.
        """
        if self.state != StageState.COMBATE:
            return

        aliados_vivos = any(a.is_alive() for a in self.time_aliados)
        inimigos_vivos = any(e.is_alive() for e in self.time_inimigos)

        if not aliados_vivos and not inimigos_vivos:
            # Empate ou aniquilação mútua: tratado como derrota
            self.state = StageState.DERROTA
            self.result_message = "EMPATE / DERROTA!"
            self.result_color = config.COLOR_TEXT_GOLD
            print("\n[FIM DE JOGO] Todos os combatentes cairam.")
            return

        if not aliados_vivos:
            self.state = StageState.DERROTA
            self.result_message = "DERROTA!"
            self.result_color = config.COLOR_HP_LOW
            print("\n[DERROTA] O time aliado foi eliminado.")
            return

        if not inimigos_vivos:
            # Todos os inimigos da sala morreram!
            self._concluir_sala()

    def _concluir_sala(self):
        """Executado quando a sala atual é vencida."""
        is_last_room_of_stage = (self.current_room_idx + 1 >= self.total_rooms_in_current_stage)
        is_last_stage = (self.current_stage_idx + 1 >= self.total_stages)

        if is_last_room_of_stage and is_last_stage:
            # Vitória absoluta do jogo!
            self.state = StageState.JOGO_CONCLUIDO
            self.result_message = "VITORIA COMPLETA!"
            self.result_color = config.COLOR_HP_HIGH
            print("\n[VITORIA TOTAL] Todas as fases e salas foram concluidas!")
            return

        if is_last_room_of_stage:
            # Última sala da fase atual: dispara evento de fase concluída
            self.state = StageState.FASE_CONCLUIDA
            self.transition_timer = config.STAGE_TRANSITION_DELAY
            self.status_message = f"Fase {self.current_stage.stage_number} Concluida! Avancando..."
            print(f"\n[FASE CONCLUIDA] Fase {self.current_stage.stage_number} finalizada! Disparando evento 'fase_concluida'...")
            gerenciador_eventos.notificar("fase_concluida", {
                "stage": self.current_stage,
                "stage_number": self.current_stage.stage_number,
                "aliados": self.time_aliados
            })
            return

        # Apenas próxima sala da mesma fase
        self.state = StageState.TRANSICAO
        self.transition_timer = config.STAGE_TRANSITION_DELAY
        self.status_message = f"Sala {self.current_room.room_number} Limpa! Avancando..."
        print(f"\n[SALA CONCLUIDA] Sala {self.current_room.room_number} limpa! Preparando proxima sala...")

    # ------------------------------------------------------------------
    # Loop de Atualização Lógica
    # ------------------------------------------------------------------

    def update(self, dt: float) -> Optional[str]:
        """
        Atualiza timers de transição e encerramento.
        Retorna 'MENU' caso deva retornar ao menu principal.
        """
        # Checagem contínua caso algum estado de vida mude fora do evento
        if self.state == StageState.COMBATE:
            self._verificar_condicoes_combate()

        # Tratamento de Transição de Sala ou de Fase
        if self.state in (StageState.TRANSICAO, StageState.FASE_CONCLUIDA):
            self.transition_timer -= dt
            if self.transition_timer <= 0:
                if self.state == StageState.FASE_CONCLUIDA:
                    self.current_stage_idx += 1
                    self.current_room_idx = 0
                else:
                    self.current_room_idx += 1
                self._iniciar_sala_atual()

        # Tratamento de Fim de Jogo (Vitória final ou Derrota)
        elif self.state in (StageState.JOGO_CONCLUIDO, StageState.DERROTA):
            self.result_timer -= dt
            if self.result_timer <= 0:
                return "MENU"

        return None
