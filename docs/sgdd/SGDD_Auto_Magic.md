# SGDD — Auto Magic

## 1. Visão Geral

* **Título:** Auto Magic
* **Gênero:** RPG de fantasia tático com combate automático.
* **Plataforma/Tecnologia:** PC / Local para um jogador (Python com Pygame-CE).
* **Resumo:** O jogador conduz uma equipe de heróis por uma floresta ameaçada por forças sombrias, preparando combatentes antes de cada batalha e acompanhando a luta. A ação é resolvida autonomamente pelas unidades; a estratégia nasce da escolha da equipe, de seus atributos e do posicionamento.

---

## 2. Fluxo do Jogo e Experiência do Jogador

### 2.1 Tela de Abertura e Introdução

* Ao iniciar o aplicativo, exibe-se a **Tela de Abertura** `[Música: Tema de Abertura / Menus]` contendo o logotipo do jogo e os botões de interação `[UI: Botões Jogar e Sair]`.
* O jogador clica em **Jogar** `[som: clique de botão]`.
* É aberta a **Tela de Apresentação Narrativa** `[UI: Caixa de Texto / Ilustração]`, introduzindo o avanço das forças sombrias em direção ao Santuário Oculto e a missão do Herói e do Mago. O jogador avança clicando em **Continuar** `[som: clique de botão]`.

### 2.2 Fase de Preparação

* Antes de cada confronto, exibe-se a **Tela de Preparação** `[UI: Painel Tático de Equipe]`.
* O jogador visualiza os inimigos designados para a próxima sala `[UI: Cards de Inimigos]`.
* O jogador organiza a formação da equipe (linha de frente e retaguarda) `[Ação: Posicionamento de Heróis]`.
* Ao confirmar, clica no botão de iniciar a luta `[som: início de batalha]`.

### 2.3 Fase de Batalha (Combate Automático)

* A arena carrega o cenário correspondente à fase `[Música: Tema da Região]`.
* Cada unidade identifica alvos vivos; os inimigos podem priorizar proximidade, retaguarda ou vulnerabilidade.
* Unidades corpo a corpo deslocam-se `[Animação: Andar]` até o alcance de ataque; unidades de longo alcance disparam de posições seguras.
* Ao atingir o alcance, a unidade aguarda o tempo de recarga `[UI: Barra de Cooldown]` para desferir o golpe `[Animação: Ataque / Lançamento de Magia]` `[som: ataque físico ou magia]`.
* O alvo atingido sofre impacto `[Animação: Dano / Impacto]` `[som: receber dano]`, exibindo um indicador numérico flutuante `[UI: Números de Dano]`.
* A vida das unidades é acompanhada em tempo real por barras dedicadas `[UI: Barra de Vida]`.
* Após um aliado receber dano, o jogador pode clicar nele em até 1 segundo para ativar **Rally**, recuperando 50% do dano recente sem exceder a vida máxima.
* Após um aliado atingir um inimigo, o jogador pode clicar nesse inimigo em até 1 segundo para ativar **Critical**, adicionando 25% do dano do golpe. A ação tem recarga global de 5 segundos.
* Quando um aliado é derrotado `[Animação: Morte]` `[som: morte de aliado]`, os sobreviventes entram em **Fúria** `[Efeito Visual: Aura Vermelha nos Heróis]` `[som: ativação de fúria]`, recebendo um bônus de 25% no dano.
* Quando um inimigo é abatido `[Animação: Morte]` `[som: morte de inimigo]`, ele fica fora de combate.

### 2.4 Progressão de Salas e Transições

* Derrotar todos os inimigos da sala conclui o encontro `[som: vitória na sala]`.
* A equipe avança para a próxima sala **mantendo a vida restante** do combate anterior.
* O ciclo de preparação e combate se repete pelas quatro salas da campanha, com três inimigos em cada encontro:
1. **Floresta Sombria** `[Música: Tema da Floresta]` — Entrada da Floresta e Clareira dos Guardiões (Goblins e Guardas Corrompidos).
2. **Santuário Oculto** `[Música: Tema do Santuário]` — Ponte das Brumas e Câmara do Lorde Bruxo (Guardiões e o Boss Lorde Bruxo).



### 2.5 Pausa e Encerramentos

* Pressionar `Esc` durante a batalha abre o menu de pausa `[UI: Tela de Pausa]` `[som: pausa]`, permitindo retomar o jogo ou sair para o menu principal com confirmação.
* **Vitória Global (Derrota do Lorde Bruxo):** Exibe a **Tela de Vitória** `[Música: Tema de Vitória]` `[UI: Painel de Sucesso]`, com opções de revanche ou retorno ao menu.
* **Derrota (Morte de todos os heróis):** Exibe a **Tela de Game Over** `[Música: Tema de Derrota]` `[UI: Painel de Fracasso]`, com botões de tentar novamente ou voltar ao menu `[som: clique de botão]`.

---

## 3. Listas Mapeadas de Elementos (Visão do Produto Final)

### 🎨 Arte & UI

* **Telas e Menus:**
* Tela de Abertura (Logotipo *Auto Magic* + Fundo Artístico + UI de Botões).
* Tela de Apresentação Narrativa (Ilustração de fundo + Caixa de texto).
* Tela de Preparação (Painel de seleção/posicionamento + Visualizador de inimigos).
* Tela de Pausa (Menu sobreposto com opções de Retomar/Sair).
* Telas Finais (Painéis de Vitória e Game Over com botões de ação).


* **Cenários (Backgrounds):**
* Fundo da Floresta Sombria (Entrada e Clareira).
* Fundo do Santuário Oculto (Ponte e Câmara do Boss).
* Outros cenários.


* **Personagens e Animações (Sprite Sheets):**
* **Heróis (Duelist, Hunter, Mage, etc):** Animações de Parado/Idle, Andar, Preparar/Cooldown, Ataque, Magia, Dano, Morte.
* **Inimigos (Goblin, Guarda, Invocador, Guardião, Lorde Bruxo, etc):** Animações de Parado, Andar, Ataque, Dano, Morte.


* **Elementos de Interface e Efeitos Visuais (VFX):**
* Barras de Vida e Barras de Cooldown dinâmicas.
* Números flutuantes de dano.
* Indicadores de estado e alvos.
* Destaques e contadores das janelas de Rally e Critical.
* Efeito visual de Fúria (Aura de luz vermelha nos sobreviventes).
* Partículas e projéteis mágicos.



### 🎵 Música & Efeitos Sonoros (SFX)

* **Trilhas Sonoras:**
* Tema da Tela de Abertura e Menus.
* Trilha Sonora da Floresta Sombria.
* Trilha Sonora do Santuário Oculto e Batalha Final.
* Trilha de Vitória.
* Trilha de Game Over.


* **Efeitos Sonoros (SFX):**
* `SFX_Clique`: Som de seleção em botões.
* `SFX_Inicio_Batalha`: Sinal sonoro ao confirmar a formação.
* `SFX_Ataque_Fisico`: Som de impacto de golpes corpo a corpo.
* `SFX_Ataque_Magico`: Som de disparo de feitiços e projéteis.
* `SFX_Dano`: Ruído de impacto na armadura/corpo.
* `SFX_Morte_Heroi`: Som de queda de um aliado.
* `SFX_Morte_Inimigo`: Som de derrota de um oponente.
* `SFX_Furia`: Acionamento do efeito de bônus de dano.
* `SFX_Pausa`: Ruído de abertura do menu de pausa.



### 💻 Programação

* Gerenciador de Estados da Aplicação (Abertura ➔ História ➔ Preparação ➔ Batalha ➔ Pausa ➔ Resultado).
* Sistema de IA para aquisição automática de alvos por proximidade, retaguarda ou vulnerabilidade.
* Janelas temporizadas de Rally e Critical com recarga global para Critical.
* Máquina de estados das unidades de combate (Movimento, Recarga, Ataque, Morte).
* Sistema de persistência de HP entre as salas da campanha.
* Sistema de gatilho para o estado de Fúria (ao perder um aliado).
* Controle de fluxo das 4 salas e spawner progressivo de inimigos/Boss.
* Gerenciador de áudio e reprodução de trilhas/SFX.

---

## 4. Status de Desenvolvimento: Recorte do MVP Atual

*Esta seção isola o que está entregue nesta versão de testes, permitindo que o documento principal permaneça estável enquanto o jogo evolui.*

### ✅ O que já está implementado no MVP:

* **Fluxo Principal:** Menu inicial funcional com botões de jogar e sair, além de transições de telas e condições de vitória/derrota.
* **Combate Automático:** Lógica de movimento, verificação de alcance, temporizadores de recarga, cálculo de dano e fim de rodada.
* **Reações Manuais:** Rally ao clicar no aliado ferido (50% do dano recente em até 1 segundo) e Critical ao clicar no inimigo atingido (bônus de 25%, janela de 1 segundo e recarga global de 5 segundos).
* **Escopo Inicial:** Equipe fixa composta por **1 Herói** (corpo a corpo) e **1 Mago** (longo alcance), combatendo três inimigos por sala ao longo de 2 fases.
* **Alvos dos Inimigos:** Preferência configurável por linha de frente, retaguarda ou aliado com menor proporção de vida.
* **Interface Básica:** Fundos de cenário, painéis de UI e indicadores de combate em funcionamento (utilizando formas geométricas provisórias para os personagens).

### ⏳ Pendente para a Versão Final (Backlog):

* **Substituição de Assets Visuais:** Trocar as formas geométricas atuais pelos *spritesheets* definitivos e animações dos heróis e inimigos.
* **Motor de Áudio:** Conectar os arquivos de música e efeitos sonoros descritos na lista de som.
* **Tela de Preparação Avançada:** Desenvolver a interface interativa de seleção de elenco e posicionamento estratégico antes das batalhas.
* **Mecânicas Complementares:** Seleção e posicionamento da equipe, pausa, integração de sprites e áudio, além de mecânicas exclusivas para o Lorde Bruxo.
