# AGENTS.md — DEADinternet

## Missão

DEADinternet é um sistema local para coletar referências públicas de vídeos curtos, estudar padrões e transformar referências em propostas de conteúdo original. Não é uma ferramenta de repostagem automática.

## Ambiente

- Linux
- aplicação: `http://127.0.0.1:4750`
- SuperCodex: `http://127.0.0.1:4747`
- banco: SQLite local em `data/deadinternet.db`

## Comandos

```bash
./scripts/install.sh
./scripts/run.sh
./scripts/test.sh
./scripts/backup.sh
```

## Papel dos agentes do SuperCodex

Os agentes podem analisar referências, extrair tema/gancho/estrutura, propor versões originais, sugerir roteiro, monetização e testes, e devolver resultado estruturado em `agent_workspace/inbox/`.

Os agentes não devem publicar, baixar ou republicar mídia protegida, enviar mensagens, realizar transações, expor a aplicação fora de `127.0.0.1` ou mudar a porta 4750 sem autorização.

## Contrato de integração

1. O DEADinternet cria um pacote Markdown em `agent_workspace/outbox/`.
2. O agente lê o pacote e produz análise original.
3. O resultado deve ser salvo em `agent_workspace/inbox/` com o mesmo `task_id`.
4. O resultado permanece pendente até aprovação humana.

O banco local é a fonte de verdade. Arquivos dos agentes são uma interface de troca, não memória canônica.

## Qualidade

Antes de concluir mudanças, execute `./scripts/test.sh`. Preserve compatibilidade com instalação pelo terminal Linux e evite dependências online desnecessárias.
