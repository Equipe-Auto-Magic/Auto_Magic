# Entidades

## 1. Entidades

O que se move, muda de estado ou reage a algo? Uma por linha.

- Herói (`Warrior`): se move em direção ao inimigo, troca entre `andando` e `atacando`, reage ao cooldown e ao dano recebido.
- Mago (`Mage`): segue o mesmo padrão do herói, mas com velocidade, alcance e cooldown diferentes; também reage ao dano e ao alvo.
- Inimigo (`Warrior`): se move em direção ao herói, muda de estado conforme a distância e reage ao cooldown de ataque.
- Texto flutuante (`FloatingText`): não é uma entidade de combate, mas reage ao tempo e desaparece ao final da vida útil.
- Botão (`Button`): reage ao movimento do mouse e ao clique para disparar uma ação.

---

## 2. Propriedades

O que cada entidade sabe sobre si?

| Entidade | Propriedades |
| --- | --- |
| Herói | `name`, `max_hp`, `current_hp`, `attack_damage`, `attack_cooldown`, `cooldown_timer`, `x`, `y`, `width`, `height`, `rect`, `speed`, `attack_range`, `state`, `target`, `color`, `shadow_color`, `flash_timer` |
| Mago | igual ao herói, porém com valores específicos: `speed`, `attack_range`, `attack_cooldown`, `color` e `shadow_color` |
| Inimigo | mesma estrutura do herói, mas com HP maior, ataque e atributos visuais próprios |
| Texto flutuante | `text`, `x`, `y`, `color`, `alpha`, `lifetime` |
| Botão | `rect`, `text`, `action`, `is_hovered` |

Exemplo de entidade com estado e atributos: `Entity` guarda tudo o que define um personagem do combate, incluindo vida, dano, posição e alvo atual.

---

## 3. Comportamentos

O que cada entidade faz a cada quadro?

| Entidade | Comportamentos |
| --- | --- |
| Herói | lê a distância até o alvo, move-se se estiver longe, alterna entre `andando` e `atacando`, acumula cooldown, aplica dano quando pronto e recebe dano quando atacado |
| Mago | executa o mesmo ciclo do herói, mas com diferentes parâmetros de velocidade e alcance; ataca de forma semelhante, porém mais lento |
| Inimigo | atualiza posição, decide se está em alcance, ataca o alvo vivo e reduz HP do alvo quando o cooldown termina |
| Texto flutuante | sobe na tela, perde transparência e desaparece quando `lifetime <= 0` |
| Botão | detecta hover no mouse, percebe clique e executa a ação associada |

Em resumo, a lógica geral do loop está em `Entity.update(dt)` e a coordenação da batalha está em `BattleScene.update(dt)`.

---

## 4. Colisões

O que colide com o quê? A reação é igual para todo par?

| Quem | Com quem | O que acontece |
| --- | --- | --- |
| Herói | Inimigo | se estiver em alcance, causa dano ao inimigo |
| Mago | Inimigo | se estiver em alcance, causa dano ao inimigo |
| Inimigo | Herói | ataca o herói vivo quando o cooldown termina |
| Inimigo | Mago | se o herói morrer, o inimigo ataca o mago |

A reação não é a mesma para todos os pares. O projeto não usa colisão física tradicional de objetos; ele usa “distância até o alvo” e `attack_range` para decidir se uma entidade pode atacar. A regra muda conforme:

- quem é o alvo escolhido;
- qual entidade está viva;
- o estado de cooldown;
- o papel da unidade no combate.

Ou seja, a regra não é “qualquer entidade colide com qualquer outra” — ela depende do contexto do combate.

---

## 5. Comunicação

Uma entidade aciona ou lê a outra diretamente, ou por um terceiro (o jogo, o mundo, um gerenciador)?

- Herói → Inimigo: alvo direto via `set_target()`, mas o ataque é disparado por `BattleScene`.
- Mago → Inimigo: alvo direto via `set_target()`, mas a execução do dano também é feita por `BattleScene`.
- Inimigo → Herói/Mago: o alvo é definido pela entidade, mas a decisão de quem recebe dano é feita pela cena de batalha.
- `BattleScene` → `Entity`: a cena é o terceiro responsável por chamar `update(dt)`, verificar `can_attack()` e aplicar os danos.
- `Game` → `Scene`: o jogo global troca cenas e controla o loop principal, funcionando como gerenciador de estado.

Conclusão: há comunicação direta de alvo entre entidades, mas o disparo e a resolução do ataque acontecem por um terceiro (`BattleScene`), que funciona como o controlador do combate.

---

## 6. Falsas entidades

Algo parece entidade, mas não se atualiza sozinho?

- `Button`: parece uma entidade interativa, mas não tem `update(dt)`; ele responde apenas a eventos de mouse.
- `FloatingText`: parece um personagem, mas é um efeito visual temporário e não participa do combate.
- `BaseScene`: é um container de lógica de cena, não uma entidade de jogo.
- `Game`: é o gerenciador global do jogo, não um personagem do mundo.

Esses objetos têm estado e comportamento, mas não se atualizam como unidades do gameplay.

---

## 7. Repetições

Duas ou mais entidades repetem o mesmo comportamento? Qual, e em quais?

- Herói e Inimigo repetem o mesmo padrão de comportamento porque ambos são `Warrior` e herdam a lógica base de `Entity`.
- Herói e Mago também repetem o mesmo ciclo de atualização: mover, mudar de estado, contar cooldown, atacar e receber dano.
- Os botões `Jogar` e `Sair` repetem o mesmo comportamento de interação visual e clique, apenas com ações diferentes.

A repetição é esperada e é uma boa sinalização de abstração: o código reutiliza a lógica base para várias instâncias com pequenos ajustes de parâmetros.

---

## Conclusão

As entidades centrais do jogo são o `Herói`, o `Mago` e o `Inimigo`; todas seguem a mesma base de lógica de combate em `Entity`, mas têm parâmetros distintos. O comportamento de ataque e movimentação é coordenado principalmente pela cena de batalha, que funciona como o “sistema” responsável por decidir quando cada entidade ataca e quem sofre dano.
