# Sistema de OCR - Notas Fiscais

Documentação do sistema de OCR para leitura automática de notas fiscais.

**Última atualização:** 2025-12-28

---

## Visão Geral

O sistema utiliza **Google Gemini Vision API** para extração de dados de imagens de notas fiscais. O processamento é **assíncrono** via Supabase Edge Functions para contornar o limite de 10s da Vercel.

### Arquitetura

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           FLUXO DE OCR                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  [1] Upload     [2] Storage      [3] Edge Function    [4] Callback      │
│  ─────────      ─────────        ────────────────     ────────          │
│                                                                          │
│  Django ──────► Supabase ──────► process-ocr ──────► Django             │
│  (3s)           Storage          (Gemini API)        (webhook)          │
│                 (ocr-images)     (até 150s)                             │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Configuração

### Variáveis de Ambiente

```bash
# Supabase
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...

# Gemini API (múltiplas chaves separadas por vírgula)
GEMINI_API_KEY=key1,key2,key3
```

### Chaves API Gemini

O sistema suporta **múltiplas chaves** com rotação automática:

1. Chaves são testadas em sequência
2. Quando uma esgota quota, marca no banco e tenta a próxima
3. Status das chaves reseta automaticamente à meia-noite

---

## Deploy em Produção

### Deploy Automático (GitHub Actions)

O deploy da Edge Function é **automático** via GitHub Actions:

- **Trigger:** Push na branch `main` que altere arquivos em `supabase/functions/`
- **Workflow:** `.github/workflows/deploy-edge-function.yml`

```yaml
on:
  push:
    branches: [main]
    paths:
      - 'supabase/functions/**'
  workflow_dispatch: # Permite rodar manualmente
```

### Secrets Necessários no GitHub

Configure em **Settings → Secrets → Actions**:

| Secret | Descrição |
|--------|-----------|
| `SUPABASE_ACCESS_TOKEN` | Token de acesso (Dashboard → Access Tokens) |
| `SUPABASE_PROJECT_REF` | Referência do projeto (ex: `abcdefghij`) |
| `GEMINI_API_KEY` | Chaves do Gemini separadas por vírgula |

### Deploy Manual (se necessário)

```bash
# Login no Supabase
npx supabase login

# Linkar ao projeto
npx supabase link --project-ref SEU_PROJECT_REF

# Deploy da função
npx supabase functions deploy process-ocr --no-verify-jwt

# Configurar secrets
npx supabase secrets set GEMINI_API_KEY="key1,key2,key3"
```

---

## Configuração do Supabase

### Criar Bucket de Storage

1. **Storage** → **New Bucket**
2. Nome: `ocr-images`
3. **Público**: Sim

### Políticas de Storage

```sql
-- Permitir leitura pública
CREATE POLICY "Public read access"
ON storage.objects FOR SELECT
USING (bucket_id = 'ocr-images');

-- Permitir upload (service role)
CREATE POLICY "Service role upload"
ON storage.objects FOR INSERT
WITH CHECK (bucket_id = 'ocr-images');

-- Permitir deleção (service role)
CREATE POLICY "Service role delete"
ON storage.objects FOR DELETE
USING (bucket_id = 'ocr-images');
```

---

## Desenvolvimento Local

### Com Supabase Local

```bash
# Iniciar Supabase local (Docker)
npx supabase start

# Serve da função para testes
npx supabase functions serve process-ocr --no-verify-jwt
```

Configure no `.env`:
```bash
SUPABASE_URL=http://127.0.0.1:54321
CALLBACK_BASE_URL=http://host.docker.internal:8000
```

---

## Estrutura de Arquivos

```
fiscal/
├── views/ocr.py           # Views de OCR (submit, status, cancel)
├── services/
│   ├── ocr.py             # InvoiceOCRService (Gemini API)
│   └── storage.py         # Funções de Storage
├── models.py              # OCRJob model
└── management/commands/
    └── clean_ocr_jobs.py  # Limpeza de jobs órfãos

supabase/functions/
└── process-ocr/
    └── index.ts           # Edge Function (Gemini + callback)

.github/workflows/
└── deploy-edge-function.yml  # CI/CD para Edge Functions
```

---

## Comandos de Manutenção

```bash
# Ver o que seria deletado
python manage.py clean_ocr_jobs --dry-run

# Deletar jobs > 7 dias
python manage.py clean_ocr_jobs --days 7

# Deletar jobs travados (> 1h)
python manage.py clean_ocr_jobs --stale

# Deletar jobs + imagens
python manage.py clean_ocr_jobs --with-images --stale
```

---

## Troubleshooting

### Imagem não aparece na nota
1. Verificar se bucket `ocr-images` é público
2. Verificar campo `Invoice.photo`
3. Testar URL diretamente

### OCR travando em "processing"
1. Ver logs no Supabase Dashboard → Edge Functions
2. Verificar chaves Gemini
3. Usar `--stale` para limpar jobs travados

### Erro de quota (429)
- Sistema rotaciona automaticamente
- Aguardar reset à meia-noite ou adicionar mais chaves

---

**Última revisão:** 2025-12-28  
**Responsável:** Diretoria de TI
