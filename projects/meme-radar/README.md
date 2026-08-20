# Meme Radar

Projeto Python para coletar conteúdos públicos de comédia ácida, observar métricas, remover duplicados e ranquear os melhores candidatos para revisão humana.

## Escopo

- fonte inicial: Reddit;
- coleta apenas conteúdo público;
- ranking determinístico por métricas públicas e recência;
- deduplicação por URL canônica ou título normalizado;
- IA opcional somente depois da seleção dos finalistas;
- sem edição automática;
- sem publicação automática;
- sem download ou republicação automática de mídia protegida.

## Arquivo principal

```text
meme_radar.py
```

## Execução

```bash
cd projects/meme-radar
cp config.example.json config.json
python3 meme_radar.py --config config.json
```

Ou diretamente:

```bash
python3 meme_radar.py \
  --subreddit darkhumorandjokes \
  --subreddit memes \
  --listing hot \
  --limit 25 \
  --top 30 \
  --output data/latest.json
```

Alguns acessos públicos do Reddit podem exigir autenticação ou um `User-Agent` mais específico. O agente deve diagnosticar isso antes de adicionar credenciais ou dependências. Para personalizar o cabeçalho:

```bash
export MEME_RADAR_USER_AGENT='MemeRadar/0.1 by u/seu_usuario'
```

## Saída

O relatório JSON contém:

- metadados da coleta;
- comunidades consultadas;
- falhas por comunidade;
- contagem bruta e final;
- candidatos deduplicados em ordem de ranking;
- marcações explícitas de que IA e publicação automática não foram usadas.

## Testes

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

## Integração com o SuperCodex

O workspace `AGENTE · Meme Radar` deve usar um clone próprio do repositório em `Repositorio/DEADinternet`. O agente pode analisar, implementar, testar e abrir Pull Requests, mas não deve publicar conteúdo, criar credenciais ou ativar coleta recorrente sem autorização explícita.
