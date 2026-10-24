# Componentes do Jogo

O Auto Magic organiza os combatentes pelo padrão de componentes: uma entidade reúne
peças independentes que cuidam de dados, comportamento e apresentação. Assim, heróis,
mago e inimigos compartilham a mesma estrutura, mas podem ter atributos e equipes
diferentes.

## Entidade e componentes

A `Entity` funciona como contêiner: identifica a unidade e mantém seus componentes.
No jogo, cada combatente é montado com estes seis componentes:

| Componente | Responsabilidade |
| --- | --- |
| `TargetingComponent` | Escolhe um adversário vivo conforme a preferência configurada (mais próximo, retaguarda ou menor proporção de vida) e controla o estado da unidade: andando, preparando o ataque, atacando ou morta. Quando há um alvo fora de alcance, indica a direção do movimento; quando não há alvo, usa a direção padrão. |
| `TransformComponent` | Guarda a posição e as dimensões da unidade, além dos limites usados para calcular distâncias e posicionamento. |
| `MovementComponent` | Desloca a unidade de acordo com sua velocidade e com a direção definida pelo componente de alvo. |
| `HealthComponent` | Controla a vida atual e máxima, aplica dano e identifica quando a unidade morre. Após aplicar dano, publica `dano_recebido` com atacante, alvo e quantidade efetiva; a morte também gera `entidade_morta`. |
| `CombatComponent` | Guarda dano, alcance e tempo de recarga. Determina quando a unidade está pronta para atacar, desde que tenha um alvo válido e esteja no alcance. |
| `SpriteComponent` | Apresenta a unidade e seu estado, incluindo nome, vida, recarga, dano e feedback visual de ataque e dano. Unidades derrotadas deixam de ser desenhadas. |

No MVP, o `SpriteComponent` desenha os combatentes com formas e cores; os sprites
definitivos ainda não estão integrados à arena.

## Como os componentes trabalham juntos

1. O `TargetingComponent` localiza um adversário vivo e verifica a distância.
2. Se o alvo estiver fora do alcance, o componente de alvo define a direção; o
   `MovementComponent` atualiza a posição guardada no `TransformComponent`.
3. Ao chegar ao alcance, a unidade para e entra no estado de preparação. O
   `CombatComponent` avança a recarga e sinaliza quando o ataque está pronto.
4. A `BattleScene` coordena o ataque e informa o atacante ao aplicar dano. O
   `HealthComponent` do alvo atualiza a vida e publica `dano_recebido`; a morte,
   quando ocorre, publica também `entidade_morta`.
5. Como observadora de `dano_recebido`, a `BattleScene` registra janelas de reação:
   o jogador pode clicar no aliado ferido para ativar Rally ou no inimigo atingido
   para ativar Critical. O evento registra o resultado do dano, mas não delega a
   alteração de vida ao observador.

## Composição e coordenação

Herói, mago e inimigos usam os mesmos seis tipos de componentes. Velocidade, vida,
dano, alcance, recarga, cores e equipe são definidos conforme cada unidade, sem
precisar criar um sistema de combate separado para cada tipo.

Essa organização em **controle** (alvos e estados), **física e regras** (posição,
movimento, vida e combate) e **gráfico** (apresentação) é apenas um agrupamento
explicativo: não corresponde a três componentes ou classes agregadoras no código.
A `BattleScene` coordena o ciclo da batalha e observa os eventos de dano para
registrar as reações. O `StageManager` observa mortes para verificar vitória,
derrota e progressão de salas. Cada componente mantém sua responsabilidade
específica; o EventBus comunica resultados sem fazer os componentes conhecerem
diretamente esses sistemas.

## Referências no código

- [`src/entity.py`](../../src/entity.py): entidade, componentes e estados das unidades.
- [`src/events.py`](../../src/events.py): EventBus e estrutura dos eventos observados.
- [`src/scenes/battle_scene.py`](../../src/scenes/battle_scene.py): criação dos aliados, atualização da batalha e aplicação do dano.
- [`src/stage_data.py`](../../src/stage_data.py): configuração e criação dos inimigos.
