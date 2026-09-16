"""
Módulo de Eventos e Padrão de Projeto Observer para o Auto-Battler.
Contém a infraestrutura do EventBus, a classe base Observador e as Habilidades Passivas.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List


class Observador(ABC):
    """Interface/Classe Base para todos os Observadores do jogo."""

    @abstractmethod
    def ao_notificar(self, evento: str, dados: Any) -> None:
        """Método executado quando um evento no qual este observador está inscrito é disparado."""
        pass


class EventBus:
    """
    Gerenciador Central de Eventos (Subject/Publisher).
    Permite inscrever, desinscrever e notificar observadores para eventos específicos.
    """

    def __init__(self):
        self._observadores: Dict[str, List[Observador]] = {}

    def inscrever(self, evento: str, observador: Observador) -> None:
        """Inscreve um observador em um determinado canal de evento."""
        if evento not in self._observadores:
            self._observadores[evento] = []
        if observador not in self._observadores[evento]:
            self._observadores[evento].append(observador)

    def desinscrever(self, evento: str, observador: Observador) -> None:
        """Remove a inscrição de um observador de um determinado canal de evento."""
        if evento in self._observadores and observador in self._observadores[evento]:
            self._observadores[evento].remove(observador)

    def notificar(self, evento: str, dados: Any) -> None:
        """Notifica todos os observadores inscritos no evento fornecido."""
        if evento in self._observadores:
            # Cria cópia superficial para evitar problemas caso um observador se desinscreva durante a notificação
            for obs in list(self._observadores[evento]):
                obs.ao_notificar(evento, dados)


# Instância global do Gerenciador de Eventos
gerenciador_eventos = EventBus()
GerenciadorEventos = EventBus  # Alias para compatibilidade


class BuffDeFuria(Observador):
    """
    Habilidade Passiva baseada no padrão Observer:
    Quando uma entidade do time Aliado morre, aumenta o dano de todos os
    aliados vivos restantes em 50% (efeito de fúria/vingança).
    """

    def __init__(self, time_aliados: list, cena_batalha=None):
        self.time_aliados = time_aliados
        self.cena_batalha = cena_batalha

    def ao_notificar(self, evento: str, dados: Any) -> None:
        if evento == "entidade_morta":
            entidade_morta = dados
            # Verifica se a entidade que morreu pertence ao time aliado
            time_entidade = getattr(entidade_morta, "team", None)
            e_aliado = time_entidade == "aliado" or entidade_morta in self.time_aliados

            if e_aliado:
                print("Aliado caiu! Fúria ativada: Dano aumentado!")

                # Aplica o buff de 50% a todos os aliados vivos restantes
                for aliado in self.time_aliados:
                    if aliado != entidade_morta and aliado.is_alive():
                        dano_anterior = aliado.attack_damage
                        aliado.attack_damage = int(aliado.attack_damage * 1.5)
                        print(f"[BUFF DE FURIA] {aliado.name}: ATK aumentado de {dano_anterior} para {aliado.attack_damage} (+50%)!")

                        # Se a cena de batalha foi fornecida, gera um texto flutuante comemorativo
                        if self.cena_batalha and hasattr(self.cena_batalha, "floating_texts"):
                            from src.scenes.battle_scene import FloatingText
                            from src import config
                            self.cena_batalha.floating_texts.append(
                                FloatingText(
                                    "FÚRIA! +50% ATK",
                                    int(aliado.x) + 10,
                                    int(aliado.y) - 40,
                                    config.COLOR_TEXT_GOLD
                                )
                            )
