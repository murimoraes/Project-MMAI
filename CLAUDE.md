# TELEMETRY FIGHT LAB — MMA Analyzer

## Visão Geral
Plataforma de inteligência de combate que transforma footages do YouTube em telemetria estratégica para suporte em camp de lutas.

## Estrutura de Módulos

| Módulo | Path | Responsabilidade |
|--------|------|-----------------|
| Ingestão | `/ingestion/` | Download e versionamento via yt-dlp |
| Visão | `/cv_engine/` | Extração de pose (MediaPipe) → `.parquet` |
| Inteligência | `/brain/` | Análise de padrões + Assinatura de Luta (Claude) |
| Interface | `/ui_brutalist/` | Dashboard Next.js — densidade de dados |

## Workflow de Execução

```bash
# 1. Ingestão
python ingestion/downloader.py --url <youtube_url> --fighter <nome>

# 2. Processamento CV
python cv_engine/pose_extractor.py --manifest data_raw/manifest.json

# 3. Análise de Padrões
python brain/pattern_recognition.py --fighter <nome> --opponent <nome>

# 4. Dashboard
cd ui_brutalist && npm run dev
```

## Variáveis de Ambiente

Crie um `.env` na raiz:
```
ANTHROPIC_API_KEY=sk-ant-...
```

## Tech Stack

- **Python 3.10+** — processamento e análise
- **yt-dlp** — extração de vídeo
- **MediaPipe + OpenCV** — keypoints e geometria de combate
- **Apache Parquet** — storage colunar (token-friendly)
- **Next.js + Tailwind** — interface de telemetria
- **Claude API (claude-sonnet-4-6)** — raciocínio tático

## Design System (Brutalist-Utility)

- **Font dados**: JetBrains Mono
- **Font alertas**: Inter Black
- **Background**: `#1a1a1a` (Asfalto)
- **Texto**: `#ffffff`
- **Alertas**: `#ccff00` (Neon Limão)
- **Bordas**: 2px sólido, sem sombras, sem gradientes

## Dados

- `data_raw/` — vídeos brutos + `manifest.json` (gitignored)
- `data_processed/` — arquivos `.parquet` com coordenadas (gitignored)
