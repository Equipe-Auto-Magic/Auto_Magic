# Auto Magic

**Auto Magic** é um RPG de fantasia com combate automático, desenvolvido em Python
com Pygame-CE. O jogador conduz uma equipe de heróis por uma floresta ameaçada por
forças sombrias. A equipe luta sozinha; a estratégia está em escolher os heróis e
prepará-los para cada encontro.

## A aventura

Uma força sombria corrompe as criaturas da Floresta Sombria e avança em direção ao
Santuário Oculto. Um guerreiro e um mago partem para investigar a ameaça e enfrentar
o Lorde Bruxo. A campanha planejada é curta: duas regiões e quatro salas, com
encontros progressivamente mais difíceis.

Antes de cada batalha, a visão do jogo é permitir que o jogador examine os inimigos
e organize sua equipe. Quando o combate começa, os heróis escolhem alvos, avançam
até o alcance de ataque e lutam automaticamente. O jogador acompanha a vida, a
recarga e os estados dos combatentes, e ajusta a formação antes do próximo encontro.

O elenco poderá crescer com classes de estilos diferentes — como Duelist, Hunter e
Mage — para formar equipes pequenas de dois ou três personagens. O MVP atual é mais
enxuto: usa um Herói e um Mago fixos, sem seleção de elenco ou tela de preparação.

## Estado atual do MVP

- Menu principal com os botões **Jogar** e **Sair**.
- Combate automático entre dois aliados fixos e os inimigos de cada sala.
- Inimigos corpo a corpo e de longo alcance podem priorizar a linha de frente, a
  retaguarda ou o aliado com menor proporção de vida.
- Rally: após um aliado receber dano, clique nele em até um segundo para recuperar
  50% do dano recente, sem exceder a vida máxima.
- Critical: após um aliado atingir um inimigo, clique nesse inimigo em até um
  segundo para aplicar um bônus de dano de 25%. Há uma recarga global de cinco
  segundos entre Criticals.
- Indicadores de vida, dano, recarga e estado, além de números flutuantes de dano e
  feedback visual para ataque, dano e derrota.
- Cada sala tem três inimigos, combinando combatentes corpo a corpo e de longo
  alcance.
- Duas fases com duas salas cada: Floresta Sombria e Santuário Oculto.
- A vida dos aliados persiste entre as salas; quando um aliado cai, os sobreviventes
  recebem um aumento de 25% no dano.
- Transição de dois segundos entre salas; vitória ou derrota retorna ao menu após
  três segundos.
- `Esc` durante a batalha retorna imediatamente ao menu.

O MVP ainda não tem seleção de heróis, preparação tática, pausa, revanche por botão,
pontuação, salvamento, áudio ou integração dos sprites de personagens com a arena.
Os combatentes são desenhados com formas coloridas. A história, a preparação de
equipe e as melhorias visuais e sonoras fazem parte da direção planejada, não do
fluxo jogável atual.

## Fases e encontros

| Região | Sala | Inimigos |
| --- | --- | --- |
| Floresta Sombria | Entrada da Floresta | Goblin Soldado, Goblin Curandeiro e Goblin Batedor |
| Floresta Sombria | Clareira dos Guardiões | Guarda Corrompido, Invocador Noturno e Cão Corrompido |
| Santuário Oculto | Ponte das Brumas | Cavaleiro Negro, Feiticeiro Sombrio e Sentinela das Brumas |
| Santuário Oculto | Câmara do Lorde Bruxo | Golem Protetor, Lorde Bruxo e Acólito do Lorde |

Os inimigos usam arquétipos de combate corpo a corpo ou à distância e podem escolher
alvos por proximidade, retaguarda ou vulnerabilidade. O Goblin Curandeiro não cura,
e o Lorde Bruxo ainda não possui uma mecânica exclusiva de chefe; ambos atacam
segundo os parâmetros de suas classes.

## Executar

Requer Python 3 e Pygame-CE (`pygame-ce>=2.5.0`).

```bash
python -m pip install -r requirements.txt
python main.py
```

No Windows, também é possível iniciar com `run.bat`.

## Estrutura do projeto

```text
.
├── main.py
├── requirements.txt
├── run.bat
├── assets/
│   └── images/
├── docs/
│   ├── componentes/
│   │   └── Componentes.md
│   ├── arquitetura/
│   │   ├── diagrama_arquitetura.puml
│   │   └── diagrama_fluxo_eventos.puml
│   ├── entidades/
│   │   ├── Apresentacao_Entidades_Auto_Magic.pdf
│   │   └── Entidades.md
│   └── sgdd/
│       └── SGDD_Auto_Magic.md
└── src/
    ├── config.py
    ├── entity.py
    ├── events.py
    ├── game.py
    ├── stage_data.py
    ├── stage_manager.py
    └── scenes/
        ├── base_scene.py
        ├── menu_scene.py
        └── battle_scene.py
```

- [SGDD — Auto Magic](docs/sgdd/SGDD_Auto_Magic.md): visão e fluxo planejado do jogo.
- [Componentes do jogo](docs/componentes/Componentes.md): responsabilidades dos componentes e sua interação no combate.
- [Diagrama UML de classes](docs/arquitetura/diagrama_arquitetura.puml): estrutura do jogo, cenas, entidades, componentes e progressão.
- [Diagrama UML de eventos](docs/arquitetura/diagrama_fluxo_eventos.puml): sequência do dano, eventos Observer e reações manuais.
- [Entidades do jogo](docs/entidades/Entidades.md): perfis, comportamento e inimigos do MVP.
- [Apresentação das entidades](docs/entidades/Apresentacao_Entidades_Auto_Magic.pdf): visão visual dos combatentes e de seu ciclo de comportamento.
- `src/stage_data.py`: configuração das fases, salas e inimigos.
- `src/entity.py`: entidades e componentes de vida, movimento, combate e apresentação.
- `src/stage_manager.py`: progressão entre salas, fases e resultados.
- `src/events.py`: eventos do jogo e habilidade passiva de fúria.
- `src/scenes/`: menu e cena de batalha.
- `assets/images/`: imagens de personagens e cenários; a integração dos personagens
  à arena ainda está pendente.

O loop principal usa atualizações de lógica em passo fixo de 1/60 segundo e limita
a renderização a 60 FPS. O jogo é local e para um jogador; multiplayer, contas,
ranking online e publicação em redes sociais estão fora do escopo atual.
