# AGENTS.md — Meme Radar

## Missão

Manter o projeto Meme Radar em `projects/meme-radar/` como coletor e analisador de conteúdo público. A fonte inicial é Reddit. O sistema coleta metadados públicos, remove duplicados, calcula ranking e prepara finalistas para revisão humana.

## Fonte de verdade

- código: repositório `ricardosiqueirarf-hash/DEADinternet`;
- projeto: `projects/meme-radar/`;
- arquivo principal: `meme_radar.py`;
- configuração local: `config.json`, nunca versionada com segredos;
- relatórios coletados: dados locais, não devem entrar no Git sem decisão explícita.

## Fora do escopo

- publicação automática;
- edição automática de mídia;
- republicação de conteúdo protegido;
- compra de anúncios;
- envio de mensagens;
- criação silenciosa de credenciais;
- IA em todos os itens coletados.

IA pode ser proposta apenas para finalistas já deduplicados e ranqueados, com custo, modelo e dados enviados claramente informados antes da ativação.

## Fluxo de engenharia

1. atualizar a `main`;
2. diagnosticar antes de editar;
3. criar branch exclusiva;
4. implementar a menor mudança suficiente;
5. executar os testes;
6. revisar o diff e dados sensíveis;
7. abrir Pull Request;
8. integrar somente após validação;
9. nunca editar o clone instalado ou outro workspace.

## Comandos mínimos

```bash
cd projects/meme-radar
python3 -m py_compile meme_radar.py tests/test_meme_radar.py
python3 -m unittest discover -s tests -p 'test_*.py'
```

## Coleta

Respeite limites, políticas e respostas das fontes. Falhas de rede ou bloqueios devem ser relatados, não contornados de forma clandestina. Não armazene cookies, tokens ou credenciais no repositório.
