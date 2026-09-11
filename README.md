# 🎮 Auto Magic — Auto Battler RPG (MVP)

> **Um dungeon crawler tático com auto battle onde a estratégia prévia determina a vitória.**

**Auto Magic** é um Produto Mínimo Viável (MVP) de um jogo 2D no estilo *Auto Battler* com elementos de RPG, construído em Python 3 utilizando a biblioteca **Pygame-CE** (Pygame Community Edition).
---

## 📋 Sobre o Projeto

### 🎯 O Jogo
**Auto Magic** é um dungeon crawler tático onde você monta uma equipe de heróis e os ordena estrategicamente para atravessar calabouços automáticos. Sem controle direto em combate, o verdadeiro desafio está em **antecipar** os inimigos, compreender as sinergias de classe e criar combinações divertidas. Esse jogo está sendo desenvolvido como um projeto para a disciplina de Programação para Jogos 1.

### 💫 Emoção & Flow
- **Sensação:** Recompensa e domínio através da maestria estratégica
- **Posição no Flow:** Centro do Canal — equilíbrio perfeito entre habilidade e desafio
- **Curva de Dificuldade:** Escalada linear com obstáculos isolados evoluindo para cenários combinados

---

## 🎲 Mecânicas Essenciais

| Mecânica | Descrição |
|----------|-----------|
| **🛡️ Sistema de Classes** | Cada personagem possui ações únicas adaptadas a situações específicas |
| **⚔️ Vantagens & Desvantagens** | Inimigos têm vulnerabilidades e resistências contra heróis específicos |
| **👁️ Previsão de Ameaças** | Visualize os inimigos antes de montar sua estratégia |

### ⚡ Mecânicas e Requisitos Foco do MVP
- **Menu Principal**: Interface limpa e responsiva com botões interativos 'Jogar' e 'Sair'.
- **Transição de Estados**: Alternância fluida entre telas (`MenuScene` <-> `BattleScene`).
- **Entidades RPG**: Classe `Entity` contendo atributos de HP Máximo, HP Atual, Dano de Ataque e Cooldowns.
- **Interface Gráfica (UI)**: Barras de vida dinâmicas acima de cada personagem com coloração adaptativa (verde/amarelo/vermelho) e indicação numérica.
- **Loop de Combate por Cooldown**: Ataques periódicos e simultâneos a cada 1.5s com exibição de logs de dano no console do terminal.
- **Condição de Fim de Batalha**: Tela overlay de **VITÓRIA!** ou **DERROTA!** e retorno automático ao Menu Principal após 3 segundos.
- **Game Loop**: Processamento de input, atualizações lógicas em delta time fixo de `1/60` segundo e renderização a 60 FPS.
---

## 🕹️ 30 Segundos de Gameplay

1️⃣ **Fase de Preparação:** Analise os ícones inimigos e arraste seus heróis para otimizar a fila com base em sinergias de classe

2️⃣ **Fase de Ação:** A batalha inicia automaticamente — acompanhe seus heróis enfrentarem os inimigos enquanto você observa a barra de progresso

---

## 🎯 Objetivos do Jogo

| Vitória | Derrota |
|--------|--------|
| Completar o último calabouço da sequência | **Sem derrota definitiva!** Volta à preparação para tentar nova estratégia |
| | Nenhuma perda de progresso, itens ou pontos |

---

## 🧠 O Desafio Central

**Preparação Estratégica** — O jogador precisa:
- ✅ Memorizar padrões inimigos
- ✅ Inferir cenários de batalha futuros
- ✅ Criar sinergias perfeitas antes da ação
- ✅ Executar **antecipação lógica** sem controle direto

---

## 🛠️ Stack Tecnológico

![Python](https://img.shields.io/badge/Python-3.x-3776ab?logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/Pygame-Community%20Edition-0078d4?logo=python&logoColor=white)

---

## 📁 Arquitetura Modular do Projeto

```text
Auto-Magic/
├── main.py                  # Ponto de entrada da aplicação
├── requirements.txt         # Dependências do projeto (pygame-ce)
├── run.bat                  # Script de execução rápida para Windows
└── src/
    ├── config.py            # Cores, dimensões da tela, FPS e constantes
    ├── entity.py            # Classe Entity (Atributos, HP, Cooldown, Desenho de UI)
    ├── game.py              # Classe Game (Loop fixo a 60 FPS, pygame.Window, Gerenciador de Cenas)
    └── scenes/
        ├── base_scene.py    # Classe base abstrata para Cenas
        ├── menu_scene.py    # Cena do Menu Principal e componentes de Botão
        └── battle_scene.py  # Arena de Batalha, Combate Automático e Telas Finais
```

### Game Loop

O loop principal mantém a renderização limitada a 60 FPS e usa um acumulador de tempo para atualizar a lógica em passos fixos de `1/60` segundo. Em cada ciclo, o jogo processa os eventos de entrada, executa zero ou mais atualizações fixas conforme o tempo acumulado e renderiza a cena atual.

---

## 🚀 Como Executar

### 1. Instalar as Dependências
Recomenda-se criar um ambiente virtual ou instalar diretamente a versão Pygame-CE:

```bash
pip install -r requirements.txt
```

### 2. Iniciar o Jogo
Execute o script principal:

```bash
python main.py
```

Ou no Windows, executando o arquivo `run.bat`:

```cmd
run.bat
```

---
## 📦 Versão 1.0 (Prova de Conceito)

### ✅ Incluído
- 🏰 Um calabouço enxuto + boss final
- 🧙 Número reduzido de personagens & inimigos
- ⚙️ Mecânicas core funcionais
- 📊 Sistema de pontuação por eficiência

### ⏭️ Futuro (Fora da V1)
- 🎨 Arte final
- 🎵 Trilha sonora original
- 📚 Conteúdo expandido

**Visual & Som:** Placeholders + formas geométricas básicas para foco máximo em programação

---

## 📅 Desenvolvimento

**Semestre:** 2026.1<br>
**Disciplina:** Programação de Jogos<br>
**Foco:** Implementação das mecânicas core e prova sólida de conceito

---

## 📝 Filosofia de Design

Falhar é aprender. Sem punições — apenas feedback estratégico. Cada derrota é uma oportunidade de testar novas combinações e refinar seu domínio sobre o jogo.
