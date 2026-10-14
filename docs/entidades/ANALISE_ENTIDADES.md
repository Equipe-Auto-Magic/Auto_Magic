# Análise de entidades do jogo Auto-Magic

## Contexto geral

O projeto já está organizado em torno de 3 camadas principais:

- `Game`: mantém o loop principal e troca cenas.
- `Scene`: gerencia estado, input e renderização da tela atual.
- `Entity`: representa personagens do combate, com HP, ataque, cooldown, posição e comportamento de aproximação/ataque.

Isso significa que as entidades de gameplay não são objetos totalmente independentes: a cena de batalha (`BattleScene`) atua como coordenadora, decide quem ataca e quando, e os personagens só reagem aos dados que a cena lhe entrega.

---

## 1) O que se move, muda de estado ou reage a algo?

### Entidades de gameplay

As entidades que realmente têm comportamento ativo e reagem ao mundo são as subclasses de `Entity`:

- `Warrior`
- `Mage`
- A própria classe base `Entity`

Essas entidades:

- se movem em direção ao alvo (`_move_towards_target`)
- mudam de estado entre `andando` e `atacando`
- acumulam cooldown de ataque
- recebem dano e ficam em estado de "flash" visual
- podem morrer (HP chega a zero)

### Exemplos concretos do projeto

- `self.hero.update(dt)`
- `self.mage.update(dt)`
- `self.enemy.update(dt)`

Tudo isso acontece dentro de `BattleScene.update()`. Ou seja, a entidade não é um cérebro inteiro; ela recebe um delta time e executa sua lógica interna.

### Outros objetos que reagem

Há também objetos com estado dinâmico, embora não sejam entidades de combate:

- `FloatingText`: sobe, perde alpha e se apaga.
- `Button`: muda de hover quando o mouse passa por cima.
- `Game`: troca de cena e controla o loop principal.

Esses objetos reagem, mas não são “entidades do combate” no sentido de unidades jogáveis/inimigas.

### Pensando em implementações futuras

O próprio código já sugere extensões naturais:

- `Archer` ou `RangedUnit`: se move menos ou mantém distância
- `Tank`: HP maior, velocidade menor, alcance mais curto
- `Boss`: múltiplos alvos, padrões de ataque ou resistência
- `Projectile`: entidade que se move por si só e colide com alvos

A estrutura atual de `Entity` já está pronta para isso porque separa:

- estado interno
- movimento
- alcance de ataque
- alvo
- UI e comportamento de combate

---

## 2) O que cada entidade sabe sobre si, ou seja, suas propriedades?

### `Entity` (base)

A classe base guarda tudo o que define o “personagem”:

- `name`: nome do personagem
- `max_hp`: vida máxima
- `current_hp`: vida atual
- `attack_damage`: dano por ataque
- `attack_cooldown`: tempo entre ataques
- `cooldown_timer`: tempo acumulado no cooldown atual
- `x`, `y`: posição no mundo
- `width`, `height`: dimensão visual
- `rect`: retângulo de colisão/posição
- `color`, `shadow_color`: identidade visual
- `flash_timer`: indicador de dano recebido
- `shake_offset_x`, `shake_offset_y`: efeitos visuais de impacto
- `speed`: velocidade de movimento
- `attack_range`: distância mínima para atacar
- `state`: `andando` ou `atacando`
- `target`: entidade-alvo atual

Além disso, há métodos auxiliares:

- `get_hp_percentage()`
- `get_hp_color()`
- `is_alive()`

### `Warrior`

O guerreiro apenas configura valores específicos da base:

- `speed = WARRIOR_SPEED`
- `attack_range = WARRIOR_ATTACK_RANGE`

### `Mage`

O mago também usa a base, mas com outro perfil:

- `speed = MAGE_SPEED`
- `attack_range = MAGE_ATTACK_RANGE`
- ataque mais lento (`attack_cooldown = 2.0` no exemplo)

### `FloatingText`

Não é uma entidade de combate, mas é uma entidade visual com estado próprio:

- `text`: mensagem a mostrar
- `x`, `y`: posição
- `color`: cor da fonte
- `alpha`: transparência
- `lifetime`: tempo de vida

### `Button`

É um objeto de UI, com dados de interação:

- `rect`
- `text`
- `action`
- `is_hovered`

### Pensando em implementações futuras

Novas entidades provavelmente receberão propriedades adicionais, por exemplo:

- `mana` / `energy`
- `armor`
- `crit_chance`
- `resistances`
- `skills` / `abilities`
- `faction` (`hero`, `enemy`, `neutral`)
- `is_ranged`, `is_tank`, `is_support`

Ou seja, a base atual está bem preparada para crescer sem quebrar a arquitetura.

---

## 3) O que cada uma faz a cada quadro, ou seja, seus comportamentos?

### Comportamento de `Entity`

O método principal é `update(dt)`, e ele faz isso:

1. Verifica se está vivo
2. Move em direção ao alvo, se houver
3. Atualiza estado (`andando` / `atacando`)
4. Incrementa cooldown quando está atacando
5. Reduz o efeito visual de flash

A interação de combate é:

- `can_attack()` verifica se está pronto para atacar
- `reset_cooldown()` repõe o temporizador
- `take_damage(amount)` reduz HP

### Comportamento de `Warrior` e `Mage`

Eles herdam o comportamento de `Entity`. A diferença é apenas nos parâmetros iniciais da unidade.

- Guerreiro: aproxima-se e ataca corpo a corpo
- Mago: também se aproxima, mas com outros valores de attack_range e cooldown

### Comportamento de `BattleScene`

A cena de batalha coordena tudo o que acontece a cada quadro:

- atualiza `hero`, `mage`, `enemy`
- verifica se algum está pronto para atacar
- aplica dano
- verifica condições de vitória/derrota
- cria textos flutuantes de dano

Essa é a parte mais relevante do controle da lógica global do jogo. Sem `BattleScene`, as entidades estariam só “soltas” sem ideia de quem ataca quem.

### Comportamento de `FloatingText`

A cada quadro:

- sobe visualmente
- reduz a vida útil
- diminui transparência

### Comportamento de `Button`

A cada evento do mouse:

- percebe se o ponteiro está em cima
- dispara uma ação quando clicado

### Pensando em implementações futuras

Uma entidade mais complexa pode ter:

- comportamento por estado (`idle`, `chasing`, `attacking`, `dead`)
- decisões baseadas em IA simples
- habilidades por cooldown
- comportamentos reativos: fugir, esquivar, curar, invocar

A arquitetura atual já dá esse passo, pois a lógica é separada do desenho visual.

---

## 4) O que colide com o quê? A reação é igual para todo par?

### Atualmente, não existe colisão física tradicional

O projeto não usa um sistema de colisão por eixo ou per-quadra. Em vez disso, a lógica de “alcançou o alvo” é baseada em distância:

```python
abs(self.target.x - self.x) - self.width
```

Essa distância é comparada com `attack_range`.

### Relação de interações

- `hero` ataca `enemy`
- `mage` ataca `enemy`
- `enemy` ataca `hero` ou `mage`

O sistema não é simétrico para todo par:

- Hero x Enemy: causa dano ao inimigo
- Mage x Enemy: causa dano ao inimigo
- Enemy x Hero: causa dano ao herói vivo
- Enemy x Mage: se o herói morrer, o inimigo ataca o mago

### Reação não é universal

A reação depende do papel da entidade no turno e da condição de sobrevivência:

- `self.enemy` não ataca qualquer unidade aleatoriamente
- o alvo é escolhido por `BattleScene.update()` conforme estado de vida
- isso torna a regra de dano dependente do contexto, e não de uma colisão genérica

### Pensando em implementações futuras

Quando o jogo crescer, o sistema de colisão deve ser mais explícito:

- `hitbox` por entidade
- `collides_with()`
- `on_collision()`
- classes de impacto por tipo de entidade

Exemplo:

- projétil colide com inimigo e causa dano
- ao tocar em tile, personagem bloqueia/afeta movimento
- arma de alcance colide com área em vez de corpo a corpo

Hoje, o jogo usa “alcance de ataque” em vez de colisão real. Isso é funcional para um MVP, mas não para um jogo mais rico.

---

## 5) Uma entidade aciona ou lê a outra direto, ou por um terceiro?

### Padrão atual: leitura via terceiro

As entidades não se olham e atacam umas às outras de forma totalmente autônoma. A coordenação está em `BattleScene`.

Fluxo real:

1. `BattleScene.update()` chama `hero.update(dt)`, `mage.update(dt)`, `enemy.update(dt)`
2. Depois, lê `can_attack()` de cada entidade
3. Se alguém está pronto, executa o ataque
4. O dano é aplicado com `take_damage()`

### Relação direta

Há sim uma referência direta entre entidades:

- `self.hero.set_target(self.enemy)`
- `self.mage.set_target(self.enemy)`
- `self.enemy.set_target(self.hero)`

Ou seja, cada unidade sabe quem é seu alvo. Isso é uma relação direta de alvo, mas o disparo do ataque ainda acontece em `BattleScene`.

### Conclusão

A arquitetura é híbrida:

- alvo é conhecido diretamente pela entidade
- o ataque em si é executado via um terceiro (`BattleScene`)

Essa separação é boa para um jogo por turnos/auto battle, porque deixa as regras de combate em um único lugar e reduz acoplamento do comportamento de cada personagem.

### Pensando em implementações futuras

Para sistemas maiores, vale pensar em:

- `CombatSystem`: processa ataques e dano centralmente
- `AIController`: decide ações com base em estado do inimigo
- `TargetingSystem`: seleciona alvos de forma escalável

Isso torna o sistema mais organizado do que deixar cada entidade decidir diretamente contra quem atacar.

---

## 6) Algo parece entidade, mas não se atualiza sozinho?

Sim: vários objetos parecem “personagens” ou “entidades” mas não têm lógica de atualização autônoma.

### `Button`

Como uma entidade visual interativa, parece um personagem, mas não segue um ciclo de update. Ele depende de `handle_event()` e `draw()`.

- não tem `update(dt)`
- não muda estado por tempo
- responde apenas a eventos externos

### `BaseScene`

Também parece um “sistema de entidade”, mas não é uma entidade de jogo. É um container de comportamento de tela.

- carrega background
- expõe interface de input e renderização
- coordena a cena atual

### `Game`

Também não é uma entidade, mas é o “orquestrador global”. Ele:

- processa eventos
- troca cenas
- mantém o loop principal

### Por que isso importa?

Porque o projeto já distingue bem entre:

- entidade de combate
- objeto de UI
- gerenciador de estado
- cena do jogo

Essa separação é importante para manutenção e futuras expansões.

---

## 7) Duas coisas repetem o mesmo comportamento?

### Resposta direta: sim

#### 1. `Hero` e `Enemy` repetem o mesmo padrão de comportamento

Embora tenham nomes, cores e atributos diferentes, ambos são `Warrior` e, portanto, herdam:

- movimento do mesmo tipo
- lógica de ataque
- cooldown
- UI de HP
- tomada de dano

O código também cria ambos de forma muito semelhante em `BattleScene.__init__()`.

#### 2. `Button` repetem o mesmo comportamento entre várias instâncias

As instâncias `btn_play` e `btn_quit` usam a mesma estrutura:

- `handle_event(event)`
- `draw(surface, font)`
- estado `is_hovered`
- `action` para executar ao clicar

Mesmo com textos e ações diferentes, o comportamento é o mesmo.

### Reuso de design

Esse aspecto é positivo, porque mostra que o código já está pensando em abstração:

- a base `Entity` reutiliza lógica para múltiplos personagens
- o tipo `Button` reutiliza comportamento para múltiplos botões

### Pensando em implementações futuras

Essa reutilização é exatamente o ponto de partida para criar:

- `RangedEntity` e `MeleeEntity`
- `UnitFactory` para gerar diferentes classes
- `ActionButton` com visual e lógica padronizados
- `Skill` e `Ability` com interface comum

---

## Conclusão

O jogo já tem um núcleo de entidades bem definido:

- `Entity` é a entidade central do combate
- `Warrior` e `Mage` são variações com comportamento compartilhado
- `BattleScene` é o sistema de coordenação que liga as entidades ao mundo
- `Button` e `FloatingText` são elementos reativos, mas não combatentes

O design atual é simples e limpo para um MVP. Ele também já está preparado para evoluir para uma arquitetura mais rica, com:

- múltiplas classes de unidade
- IA de inimigos
- habilidades por cooldown
- hitboxes e colisões reconhecidas
- sistemas de alvo e combate separados em componentes

Em outras palavras: o projeto já tem a base correta para crescer sem precisar reescrever a lógica principal.
