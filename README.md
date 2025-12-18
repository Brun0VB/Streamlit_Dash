# Steam Wishlist Price Tracker

Um aplicativo Streamlit para rastrear e visualizar o histórico de preços dos jogos da sua wishlist da Steam.

## 📋 Sobre o Projeto

Este projeto permite que você:
- Sincronize sua wishlist da Steam
- Acompanhe o histórico de preços dos jogos
- Visualize gráficos interativos de variação de preços

## 🚀 Funcionalidades

- **Sincronização com Steam**: Busca automaticamente os jogos da sua wishlist
- **Histórico de Preços**: Coleta e armazena dados históricos de preços via ITAD API
- **Visualização Gráfica**: Gráficos interativos com Altair para análise de tendências
- **Filtros Temporais**: Visualize dados dos últimos 3, 6, 12 meses ou período completo
- **Banco de Dados Local**: Armazenamento eficiente com SQLite

## 🛠️ Tecnologias Utilizadas

- **Python 3.13**
- **Streamlit** - Interface web
- **Altair** - Visualização de dados
- **Pandas** - Manipulação de dados
- **SQLite** - Banco de dados
- **Steam Web API** - Dados da Steam
- **IsThereAnyDeal API** - Histórico de preços

## 📦 Instalação

### Pré-requisitos

- Python 3.13 ou superior
- Conta Steam
- Steam Web API Key ([obtenha aqui](https://steamcommunity.com/dev/apikey))
- ITAD API Key ([obtenha aqui](https://isthereanydeal.com/dev/app/))

### Configuração

1. Clone o repositório:
```bash
git clone <seu-repositorio>
cd streamlit-project
```

2. Instale as dependências:
```bash
pip install -e .
```

3. Crie um arquivo `.env` na raiz do projeto:
```env
STEAMID=seu_steam_id
WEBAPIKEY=sua_steam_api_key
ITAD_API_KEY=sua_itad_api_key
```

4. Execute o aplicativo:
```bash
streamlit run main.py
```

## 📖 Como Usar

### 1. Aba SteamData

**Buscar WishList**: 
- Sincroniza sua wishlist da Steam
- Salva os jogos no banco de dados local

**Load Prices**: 
- Atualiza os preços atuais de todos os jogos

**Buscar Histórico Completo (ITAD)**: 
- Coleta o histórico de preços dos últimos 12 meses para todos os jogos
- Processo pode levar alguns minutos devido ao rate limiting da API

**Buscar Histórico Individual**: 
- Selecione um jogo específico para atualizar seu histórico

### 2. Aba WishList

- Visualize gráficos de histórico de preços
- Selecione um jogo para ver sua evolução de preços
- Escolha o período de visualização (3, 6, 12 meses ou Max)

## 🗄️ Estrutura do Banco de Dados

O projeto utiliza duas tabelas principais:

**wishlist_games**:
- `appid` (PRIMARY KEY): ID do jogo na Steam
- `name`: Nome do jogo

**wishlist_prices**:
- `id` (AUTOINCREMENT): ID único do registro
- `game_id` (FOREIGN KEY): Referência ao jogo
- `price`: Preço do jogo
- `currency`: Moeda (BRL)
- `fetch_date`: Data/hora da coleta

## 📁 Estrutura do Projeto

```
streamlit-project/
├── main.py                 # Aplicação principal Streamlit
├── steam.py               # Cliente da Steam API
├── itad_integration.py    # Cliente da ITAD API
├── data.py                # Gerenciamento do banco de dados
├── ui.py                  # Componentes da interface
├── utils.py               # Funções auxiliares
├── pyproject.toml         # Configuração do projeto
├── .env                   # Variáveis de ambiente (criar)
└── wishlist.db           # Banco de dados SQLite (gerado automaticamente)
```

## 🔧 Melhorias Futuras

- [ ] Otimizar queries com `executemany()`
- [ ] Adicionar notificações de queda de preço

## ⚠️ Limitações

- Histórico limitado aos últimos 12 meses
- Preços podem não estar disponíveis para todos os jogos
- Apenas jogos da Steam são suportados
  
---

**Nota**: Este projeto não é afiliado à Valve Corporation, Steam ou IsThereAnyDeal.
