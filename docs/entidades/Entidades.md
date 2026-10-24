# Entidades do Jogo

## Estrutura

Cada combatente é uma `Entity`, um contêiner composto por componentes de posição,
vida, movimento, combate, seleção de alvo e apresentação. Herói, Mago e inimigos
compartilham essa estrutura; seus atributos e sua equipe definem suas diferenças.
As responsabilidades dos componentes estão descritas em
[Componentes](../componentes/Componentes.md).

## Aliados

| Entidade | Papel e comportamento no MVP | Perfil configurado |
| --- | --- | --- |
| **Herói** | Combatente corpo a corpo da linha de frente. Avança até o inimigo vivo mais próximo e ataca quando a recarga termina. | 240 HP, 18 de dano, velocidade 120, alcance 45 e recarga de 1,5 s. |
| **Mago** | Aliado de longo alcance, posicionado atrás do Herói no início das salas. Busca alvos e ataca com alcance maior e recarga mais longa. | 80 HP, 12 de dano, velocidade 90, alcance 350 e recarga de 2 s. |

O Mago pode avançar até o alvo se ele estiver além do alcance; o código não implementa
uma regra para manter distância ou permanecer sempre na retaguarda.

## Inimigos

Os inimigos são criados no início de cada sala a partir das configurações de fase.
Cada um usa o perfil de combate `Warrior` (corpo a corpo) ou `Mage` (à distância),
com atributos definidos para o encontro.

| Fase e sala | Inimigos |
| --- | --- |
| Floresta Sombria — Entrada da Floresta | Goblin Soldado (`Warrior`), Goblin Curandeiro (`Mage`), Goblin Batedor (`Warrior`) |
| Floresta Sombria — Clareira dos Guardiões | Guarda Corrompido (`Warrior`), Invocador Noturno (`Mage`), Cão Corrompido (`Warrior`) |
| Santuário Oculto — Ponte das Brumas | Cavaleiro Negro (`Warrior`), Feiticeiro Sombrio (`Mage`), Sentinela das Brumas (`Mage`) |
| Santuário Oculto — Câmara do Lorde Bruxo | Golem Protetor (`Warrior`), Lorde Bruxo (`Mage`), Acólito do Lorde (`Mage`) |

Cada sala combina inimigos corpo a corpo e à distância. As configurações também
definem prioridades de alvo: linha de frente (alvo mais próximo), retaguarda (alvo
mais distante) ou vulnerável (menor proporção de vida). Os nomes indicam identidade,
mas não acrescentam habilidades próprias: o Goblin Curandeiro não cura e o Lorde
Bruxo ainda não tem mecânicas exclusivas de chefe.

## Ciclo e interação

Durante a batalha, cada combatente procura o adversário vivo mais próximo. Fora do
alcance, move-se em sua direção; ao alcançá-lo, para e prepara o ataque enquanto a
recarga avança. Quando está pronto, a `BattleScene` aplica o dano. A unidade pode
passar pelos estados **andando**, **preparando**, **atacando** e **morto**.

Após um inimigo atingir um aliado, o jogador tem 1 segundo para clicar no aliado
ferido e recuperar 50% do dano recente recebido. O Rally não ultrapassa a vida
máxima, não revive aliados e destaca visualmente o aliado com recuperação disponível.
Após um aliado atingir um inimigo, o jogador tem 1 segundo para clicar nesse inimigo
e ativar um Critical, adicionando 25% do dano do golpe recente. A ação tem recarga
global de 5 segundos e destaca os inimigos com uma janela ativa.

O `StageManager` monta cada sala e configura as equipes oponentes; a `BattleScene`
atualiza e desenha as entidades e coordena os ataques. A morte de um aliado ativa
Fúria, aumentando em 25% o dano dos aliados sobreviventes.

## Observação sobre as classes

No fluxo atual, Herói, Mago e inimigos são instanciados como `Entity` e recebem seus
componentes. As classes `Warrior` e `Mage` também existem em `src/entity.py`, mas a
batalha atual não instancia os combatentes por essas subclasses: a configuração
`Warrior`/`Mage` dos inimigos seleciona seus valores padrão de velocidade e alcance.

## Referências

- [Apresentação das entidades](./Auto_Magic_Entidades_Slides.pdf)
- [Componentes](../componentes/Componentes.md)
- [`src/entity.py`](../../src/entity.py): entidade, componentes e estados.
- [`src/stage_data.py`](../../src/stage_data.py): inimigos, atributos e salas.
- [`src/stage_manager.py`](../../src/stage_manager.py): criação das equipes e progressão.
- [`src/scenes/battle_scene.py`](../../src/scenes/battle_scene.py): aliados e resolução do combate.
