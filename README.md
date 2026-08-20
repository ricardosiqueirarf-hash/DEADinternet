# DEADinternet

Sistema local-first para descobrir tendências, transformar referências em ideias originais e operar um pipeline de conteúdo curto para Reels, TikTok e Shorts.

## Princípio central

O sistema coleta **metadados, padrões, temas e sinais de desempenho**. Ele não deve depender de republicação automática de conteúdo protegido. A saída do pipeline será conteúdo novo, produzido a partir de roteiro, narração e assets próprios ou licenciados.

## Estado atual

**Fase 1 — Radar local de conteúdo**

Objetivo: provar que conseguimos coletar referências, organizar os dados, pontuar oportunidades e selecionar manualmente os melhores temas para produção.

A especificação completa está em [`docs/FASE_1.md`](docs/FASE_1.md).

## Arquitetura inicial

- Python 3.12+
- SQLite local
- FastAPI
- interface web local
- coleta manual e importação assistida
- jobs locais
- armazenamento de arquivos fora do Git

## Regra de arquitetura

> Local por padrão. Serviço online apenas quando a função depender diretamente de uma plataforma externa ou exigir disponibilidade pública.

## Fases previstas

1. Radar local de conteúdo
2. Geração assistida de briefing e roteiro
3. Produção semiautomática de assets e vídeos
4. Publicação e coleta de métricas
5. Aprendizado e otimização do pipeline
