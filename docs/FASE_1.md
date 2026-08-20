# Fase 1 — Radar Local de Conteúdo

## 1. Objetivo

Construir um sistema local, executado em Linux, capaz de:

1. receber referências de Reels, TikTok e Shorts;
2. armazenar metadados localmente;
3. organizar e classificar cada referência;
4. gerar uma pontuação de oportunidade;
5. permitir seleção manual dos melhores temas;
6. formar uma base confiável para as próximas fases.

A Fase 1 termina antes da geração automática de vídeos.

---

## 2. Resultado esperado

Ao final desta fase, o usuário deverá conseguir abrir um painel local no navegador, adicionar uma URL e visualizar a referência dentro de um funil com os estados:

```text
capturado
→ enriquecido
→ avaliado
→ selecionado
→ descartado
```

O sistema deverá responder:

- qual conteúdo foi encontrado;
- qual é o tema;
- qual é o gancho;
- qual é o formato;
- por que ele pode funcionar;
- qual seria o potencial de monetização;
- se vale a pena transformar a referência em conteúdo original.

---

## 3. Princípio da fase

A coleta serve para estudar:

- temas;
- ganchos;
- estruturas narrativas;
- padrões visuais;
- sinais públicos de desempenho;
- comentários e dúvidas da audiência.

O sistema não terá, nesta fase, um fluxo automático de republicação de vídeos protegidos.

---

## 4. Arquitetura

```text
Internet
   ↓
Coleta manual ou assistida
   ↓
API local FastAPI
   ↓
SQLite local
   ↓
Classificador por regras
   ↓
Painel web local
```

### Componentes

| Componente | Tecnologia inicial | Local/online |
|---|---|---|
| Backend | FastAPI | Local |
| Banco | SQLite | Local |
| Interface | HTML + CSS + JavaScript | Local |
| Agendador | cron ou systemd timer | Local |
| Coleta de URLs | formulário/manual | Local |
| Consulta das plataformas | navegador/internet | Online |
| Arquivos temporários | sistema de arquivos Linux | Local |
| Backup | script local + destino opcional | Híbrido |

---

## 5. Por que SQLite

SQLite é suficiente para a Fase 1 porque:

- existe apenas um operador;
- o volume inicial será pequeno;
- não exige servidor de banco;
- o banco é um único arquivo;
- backup e restauração são simples;
- a migração futura para PostgreSQL é direta usando uma camada ORM.

Arquivo previsto:

```text
data/deadinternet.db
```

O arquivo não deve ser versionado no Git.

---

## 6. Estrutura do repositório

```text
DEADinternet/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   │   └── reference.py
│   ├── schemas/
│   │   └── reference.py
│   ├── services/
│   │   ├── classifier.py
│   │   ├── scorer.py
│   │   └── extractor.py
│   ├── routes/
│   │   ├── references.py
│   │   └── dashboard.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   └── reference_form.html
│   └── static/
│       ├── css/
│       └── js/
├── data/
│   └── .gitkeep
├── storage/
│   ├── thumbnails/
│   ├── transcripts/
│   └── exports/
├── scripts/
│   ├── init_db.py
│   ├── backup.sh
│   └── run_dev.sh
├── tests/
├── docs/
│   └── FASE_1.md
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

---

## 7. Modelo de dados inicial

### Tabela `references`

| Campo | Tipo | Função |
|---|---|---|
| id | integer | identificador |
| platform | text | instagram, tiktok ou youtube |
| url | text unique | URL da publicação |
| creator_name | text | nome do perfil |
| caption | text | legenda pública |
| title | text | título interno |
| published_at | datetime | data da publicação |
| collected_at | datetime | data da coleta |
| views | integer | visualizações conhecidas |
| likes | integer | curtidas conhecidas |
| comments | integer | comentários conhecidos |
| shares | integer nullable | compartilhamentos conhecidos |
| duration_seconds | real nullable | duração |
| language | text nullable | idioma percebido |
| topic | text nullable | tema principal |
| hook | text nullable | gancho observado |
| format_type | text nullable | história, lista, reação, explicação etc. |
| monetization_path | text nullable | afiliado, produto, alcance, serviço etc. |
| source_notes | text nullable | observações manuais |
| status | text | estado no funil |
| score | real | nota de oportunidade |
| created_at | datetime | criação local |
| updated_at | datetime | atualização local |

### Status permitidos

```text
captured
enriched
scored
selected
discarded
```

---

## 8. Entrada de dados

### MVP da coleta

Na primeira versão, o usuário cola manualmente a URL e preenche apenas os dados essenciais:

- plataforma;
- URL;
- visualizações;
- curtidas;
- comentários;
- legenda;
- observação.

O sistema calcula automaticamente:

- taxa de curtidas;
- taxa de comentários;
- score inicial;
- possível formato;
- possível caminho de monetização.

### Motivo para começar manualmente

A automação de coleta é a parte mais instável do sistema por depender de plataformas externas. A entrada manual permite validar primeiro:

- o banco;
- o painel;
- o modelo de classificação;
- o score;
- o fluxo de decisão.

Só depois a coleta automática deve ser adicionada.

---

## 9. Sistema de pontuação inicial

A nota será de 0 a 100.

```text
score =
  alcance_relativo        × 0,30
+ engajamento             × 0,20
+ força_do_gancho         × 0,20
+ facilidade_de_recriar   × 0,15
+ potencial_de_monetizar  × 0,15
```

### Critérios manuais

Cada referência receberá notas de 0 a 10 para:

- força do gancho;
- facilidade de recriação original;
- potencial de monetização.

### Critérios calculados

Quando existirem dados suficientes:

```text
like_rate = likes / views
comment_rate = comments / views
```

O cálculo deve aceitar dados ausentes sem quebrar.

---

## 10. Painel local

URL prevista:

```text
http://127.0.0.1:8000
```

### Tela principal

Deve mostrar:

- total de referências;
- referências por plataforma;
- referências por status;
- média do score;
- top 10 oportunidades;
- últimas referências adicionadas.

### Lista de referências

Filtros:

- plataforma;
- status;
- tema;
- formato;
- score mínimo;
- data da coleta.

### Tela de detalhe

Deve permitir:

- abrir a publicação original;
- editar os dados;
- preencher classificação;
- recalcular score;
- selecionar;
- descartar;
- adicionar observações.

---

## 11. Fluxo operacional no Linux

### Inicialização do ambiente

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Executar em desenvolvimento

```bash
./scripts/run_dev.sh
```

Ou diretamente:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Banco

```bash
python scripts/init_db.py
```

### Backup manual

```bash
./scripts/backup.sh
```

### Serviço futuro com systemd

Na Fase 1, rodar manualmente é suficiente. Depois, o backend poderá ser instalado como serviço do usuário:

```text
~/.config/systemd/user/deadinternet.service
```

Isso evita depender de servidor externo e permite iniciar o sistema junto com a sessão Linux.

---

## 12. Backup

Estratégia mínima:

1. copiar `data/deadinternet.db`;
2. compactar os arquivos relevantes de `storage/`;
3. gerar pasta com data e hora;
4. manter os últimos 7 backups locais;
5. permitir sincronização opcional para Google Drive, NAS ou HD externo.

Exemplo:

```text
backups/2026-08-19_220000/
├── deadinternet.db
└── storage.tar.gz
```

---

## 13. O que fica fora da Fase 1

Não será implementado agora:

- download automático de vídeos;
- repostagem;
- publicação automática;
- geração de roteiro por IA;
- TTS;
- edição com FFmpeg;
- coleta automática contínua;
- análise de retenção;
- integração com TikTok Shop;
- monetização automática;
- banco em nuvem;
- autenticação multiusuário.

Esses itens ficam para fases seguintes.

---

## 14. Critérios de conclusão

A Fase 1 estará concluída quando:

- [ ] o sistema iniciar no Linux com um comando;
- [ ] o banco SQLite for criado automaticamente;
- [ ] for possível cadastrar uma referência;
- [ ] URLs duplicadas forem bloqueadas;
- [ ] for possível editar e excluir uma referência;
- [ ] o score for calculado;
- [ ] o dashboard mostrar dados reais;
- [ ] filtros funcionarem;
- [ ] referências puderem ser selecionadas ou descartadas;
- [ ] o backup local funcionar;
- [ ] existirem testes mínimos para banco e score;

---

## 15. Ordem de implementação

### Sprint 1 — Fundação

- estrutura do projeto;
- ambiente Python;
- FastAPI;
- SQLite;
- modelo `Reference`;
- criação automática do banco;

### Sprint 2 — CRUD

- cadastrar;
- listar;
- editar;
- excluir;
- validar URL duplicada;

### Sprint 3 — Inteligência básica

- classificador por regras;
- score;
- estados do funil;
- seleção e descarte;

### Sprint 4 — Painel

- indicadores;
- filtros;
- top oportunidades;
- tela de detalhes;

### Sprint 5 — Operação Linux

- scripts de execução;
- backup;
- documentação;
- testes;

---

## 16. Decisão técnica principal

A Fase 1 será deliberadamente simples:

> FastAPI + SQLite + interface web local + entrada manual assistida.

O objetivo não é automatizar tudo de imediato. O objetivo é validar o núcleo do sistema antes de adicionar scraping, agentes e geração automática de conteúdo.
