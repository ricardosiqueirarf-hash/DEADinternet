# DEADinternet

Repositório de experimentos locais para estudar conteúdo público e transformar sinais observáveis em análises revisáveis.

## Projeto principal — Meme Radar

O escopo corrigido está em [`projects/meme-radar/`](projects/meme-radar/):

- linguagem: Python;
- arquivo principal: `projects/meme-radar/meme_radar.py`;
- fonte inicial: Reddit;
- objetivo: coletar conteúdo público de comédia ácida, analisar métricas, remover duplicados e ranquear candidatos;
- IA: opcional e somente nos finalistas;
- fora do escopo: edição e publicação automática.

## Aplicação legada na raiz

A raiz ainda contém a primeira aplicação FastAPI experimental, voltada ao cadastro manual de referências de vídeos curtos:

- FastAPI em `127.0.0.1:4750`;
- SQLite local;
- dashboard web;
- fila de tarefas para agentes do SuperCodex.

Ela foi preservada para não quebrar o histórico, mas não define o escopo atual do Meme Radar.

## Instalação da aplicação legada

```bash
git clone https://github.com/ricardosiqueirarf-hash/DEADinternet.git
cd DEADinternet
chmod +x scripts/*.sh
./scripts/install.sh
./scripts/run.sh
```

## Executar o Meme Radar

```bash
cd projects/meme-radar
cp config.example.json config.json
python3 meme_radar.py --config config.json
python3 -m unittest discover -s tests -p 'test_*.py'
```

## SuperCodex

O LinuxP provisiona um workspace dedicado chamado `AGENTE · Meme Radar`. Esse agente deve manter um clone próprio em `Repositorio/DEADinternet`, trabalhar por branch e Pull Request e limitar suas alterações ao repositório do projeto.

Nenhum componente publica conteúdo automaticamente. Resultados coletados e análises de IA permanecem pendentes de revisão humana.
