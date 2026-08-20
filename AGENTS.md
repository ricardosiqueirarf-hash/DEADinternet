# AGENTS.md — DEADinternet

## Escopo atual

O projeto principal do repositório é o **Meme Radar**, localizado em `projects/meme-radar/`. Leia também `projects/meme-radar/AGENTS.md` antes de alterar esse projeto.

O código antigo na raiz é uma aplicação FastAPI experimental preservada como legado. Não mova, remova ou misture seus arquivos com o Meme Radar sem uma migração aprovada e testada.

## Meme Radar

- linguagem: Python;
- arquivo principal: `projects/meme-radar/meme_radar.py`;
- fonte inicial: Reddit;
- objetivo: coletar conteúdo público de comédia ácida, observar métricas, deduplicar e ranquear candidatos;
- IA: opcional e somente nos finalistas;
- fora do escopo: edição e publicação automática.

## Ambiente legado

- aplicação: `http://127.0.0.1:4750`;
- SuperCodex: `http://127.0.0.1:4747`;
- banco: SQLite local em `data/deadinternet.db`.

## Papel do AGENTE · Meme Radar

O agente deve trabalhar em um clone próprio deste repositório, atualizar a `main`, criar branch exclusiva, implementar, testar, revisar o diff, abrir Pull Request e só então integrar. Não deve editar arquivos instalados, o clone técnico do LinuxP ou outros workspaces.

O agente pode:

- desenvolver coletores de fontes públicas;
- melhorar deduplicação e ranking;
- estruturar relatórios e finalistas;
- diagnosticar falhas de fonte;
- propor uso opcional de IA depois do ranking.

O agente não pode, sem autorização explícita:

- publicar ou editar mídia;
- baixar e republicar conteúdo protegido;
- criar ou expor credenciais;
- ativar tarefas recorrentes;
- enviar conteúdo a serviços de IA;
- mudar escopo para outras redes sociais;
- alterar o LinuxP ou o SuperCodex.

## Testes do Meme Radar

```bash
cd projects/meme-radar
python3 -m py_compile meme_radar.py tests/test_meme_radar.py
python3 -m unittest discover -s tests -p 'test_*.py'
```

## Aplicação legada

Os comandos abaixo continuam válidos apenas para a aplicação FastAPI da raiz:

```bash
./scripts/install.sh
./scripts/run.sh
./scripts/test.sh
./scripts/backup.sh
```

O banco local da aplicação antiga continua sendo sua fonte de verdade. Os arquivos `agent_workspace/outbox/` e `agent_workspace/inbox/` são apenas interface de troca, não memória canônica.
