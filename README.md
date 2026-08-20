# DEADinternet

Radar local para estudar referências de Reels, TikTok e Shorts e transformar padrões observados em ideias de conteúdo original.

## Estado atual — Fase 1 executável

- FastAPI em `127.0.0.1:4750`;
- SQLite local;
- cadastro, listagem, edição, exclusão e filtros via API;
- dashboard web;
- score determinístico de oportunidade;
- fila de tarefas para agentes do SuperCodex;
- backup local e testes.

## Instalação no Linux

```bash
git clone https://github.com/ricardosiqueirarf-hash/DEADinternet.git
cd DEADinternet
chmod +x scripts/*.sh
./scripts/install.sh
./scripts/run.sh
```

Abra `http://127.0.0.1:4750`. O SuperCodex continua separado em `http://127.0.0.1:4747`.

## Usando com SuperCodex

1. No SuperCodex, crie um ambiente cuja pasta raiz seja o clone do `DEADinternet`.
2. O SuperCodex carregará o `AGENTS.md` da raiz.
3. No dashboard, use **Enviar ao SuperCodex**.
4. O sistema criará um pacote em `agent_workspace/outbox/`.
5. Peça ao agente para processar os pacotes pendentes e salvar cada resposta em `agent_workspace/inbox/<task_id>.json`.
6. Revise o resultado antes de incorporá-lo ao conteúdo.

O DEADinternet não chama diretamente uma API de IA. A inteligência fica nos agentes do SuperCodex; o DEADinternet mantém banco, fluxo e auditoria local.

## Comandos

```bash
./scripts/run.sh
./scripts/test.sh
./scripts/backup.sh
```

## API principal

- `GET /health`
- `GET/POST /api/references`
- `GET/PATCH/DELETE /api/references/{id}`
- `POST /api/references/{id}/score`
- `POST /api/references/{id}/agent-task`
- `GET /api/stats`

A coleta serve para estudar temas, ganchos, formatos e sinais públicos. O projeto não inclui republicação automática de conteúdo protegido.

Veja também: [`docs/FASE_1.md`](docs/FASE_1.md).
