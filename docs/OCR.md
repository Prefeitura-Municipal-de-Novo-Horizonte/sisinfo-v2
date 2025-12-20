# Sistema de OCR - Notas Fiscais

Documentação do sistema de OCR para leitura automática de notas fiscais.

**Última atualização:** 2024-12-20

---

## 📋 Visão Geral

O sistema utiliza **Google Gemini Vision API** para extração de dados de imagens de notas fiscais. O processamento é **assíncrono** via Supabase Edge Functions para contornar o limite de 10s da Vercel.

### Arquitetura

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           FLUXO DE OCR                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  [1] Upload     [2] Storage      [3] Edge Function    [4] Polling       │
│  ─────────      ─────────        ────────────────     ────────          │
│                                                                          │
│  Django ──────► Supabase ──────► process-ocr ──────► Django             │
│  (3s)           Storage          (Gemini API)        (status)           │
│                 (bucket)         (até 150s)                              │
│                                                                          │
│           ┌─────────────────────────────────────────────────┐           │
│           │  [5] Resultado salvo no OCRJob via callback     │           │
│           └─────────────────────────────────────────────────┘           │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## ⚙️ Configuração

### Variáveis de Ambiente

```bash
# Supabase (obrigatório em produção)
SUPABASE_URL="https://seu-projeto.supabase.co"
SUPABASE_ANON_KEY="eyJ..."
SUPABASE_SERVICE_ROLE_KEY="eyJ..."

# Gemini API (múltiplas chaves separadas por vírgula)
GEMINI_API_KEY="key1,key2,key3,key4,key5"

# Opcional: desabilitar Supabase para dev local
USE_SUPABASE_STORAGE=False
```

### Chaves API Gemini

O sistema suporta **múltiplas chaves** com rotação automática:

1. Chaves são testadas em sequência
2. Quando uma esgota quota, marca no banco e tenta a próxima
3. Status das chaves reseta automaticamente à meia-noite

---

## 🚀 Deploy em Produção (Supabase Cloud)

### 1. Criar Projeto no Supabase

1. Acesse [supabase.com](https://supabase.com) e crie um projeto
2. Anote as credenciais:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `SUPABASE_SERVICE_ROLE_KEY`

### 2. Criar Bucket de Storage

No Supabase Dashboard:

1. **Storage** → **New Bucket**
2. Nome: `ocr-images`
3. **Público**: Sim (para exibir imagens no frontend)

### 3. Configurar Políticas de Storage

```sql
-- Permitir leitura pública
CREATE POLICY "Public read access"
ON storage.objects FOR SELECT
USING (bucket_id = 'ocr-images');

-- Permitir upload autenticado (service role)
CREATE POLICY "Service role upload"
ON storage.objects FOR INSERT
WITH CHECK (bucket_id = 'ocr-images');

-- Permitir deleção autenticado (service role)
CREATE POLICY "Service role delete"
ON storage.objects FOR DELETE
USING (bucket_id = 'ocr-images');
```

### 4. Deploy da Edge Function

```bash
# Na raiz do projeto
cd /caminho/para/sisinfo-v2

# Login no Supabase
npx supabase login

# Linkar ao projeto
npx supabase link --project-ref SEU_PROJECT_REF

# Deploy da função
npx supabase functions deploy process-ocr
```

### 5. Configurar Secrets da Edge Function

```bash
# Definir chaves Gemini
npx supabase secrets set GEMINI_API_KEY="key1,key2,key3..."
```

### 6. Configurar Variáveis no Django (.env produção)

```bash
# Supabase Produção
SUPABASE_URL="https://SEU_PROJECT.supabase.co"
SUPABASE_ANON_KEY="eyJ..."
SUPABASE_SERVICE_ROLE_KEY="eyJ..."

# Importante: habilitar Supabase Storage
USE_SUPABASE_STORAGE=True
```

---

## 🧪 Desenvolvimento Local

### Usando Supabase Local

```bash
# Iniciar Supabase local (Docker)
npx supabase start

# Após iniciar, anote as credenciais locais
# API URL: http://127.0.0.1:54321
# anon key: eyJ...
# service_role key: eyJ...

# Serve da função para testes
npx supabase functions serve process-ocr --no-verify-jwt
```

### Sem Supabase (Modo Local)

Defina no `.env`:
```bash
USE_SUPABASE_STORAGE=False
```

O sistema usará processamento local com `InvoiceOCRService`.

---

## 📁 Estrutura de Arquivos

```
fiscal/
├── views/
│   └── ocr.py              # Views de OCR (submit, status, cancel)
├── services/
│   ├── ocr.py              # InvoiceOCRService (Gemini API)
│   └── storage.py          # Funções de Storage (delete, check)
├── models.py               # OCRJob model
└── management/
    └── commands/
        └── clean_ocr_jobs.py  # Limpeza de jobs órfãos

supabase/
└── functions/
    └── process-ocr/
        └── index.ts        # Edge Function (Gemini + callback)
```

---

## 🔧 Comandos de Manutenção

### Limpeza de Jobs Órfãos

```bash
# Ver o que seria deletado
python manage.py clean_ocr_jobs --dry-run

# Deletar jobs completados/falhos > 7 dias
python manage.py clean_ocr_jobs --days 7

# Deletar jobs travados (pending/processing > 1h)
python manage.py clean_ocr_jobs --stale

# Deletar jobs + imagens do Storage
python manage.py clean_ocr_jobs --with-images --stale
```

---

## 🔍 Troubleshooting

### Imagem não aparece na nota

1. Verifique se o bucket `ocr-images` é público
2. Verifique se a Invoice tem o campo `photo` preenchido
3. Teste a URL diretamente no navegador

### OCR travando em "processing"

1. Verifique logs da Edge Function no Supabase Dashboard
2. Verifique se as chaves Gemini estão válidas
3. Use `--stale` para limpar jobs travados

### Erro de quota (429)

O sistema rotaciona automaticamente entre as chaves. Se todas esgotarem:
- Aguarde reset à meia-noite
- Ou adicione mais chaves no `.env`

---

## 📊 Monitoramento

### No Supabase Dashboard

- **Edge Functions** → Logs e métricas
- **Storage** → Uso do bucket
- **Database** → (se usando Supabase DB)

### No Django Admin

- `/admin/fiscal/ocrjob/` - Ver todos os jobs
- Filtrar por status para identificar problemas

---

**Última revisão:** 2024-12-20
**Responsável:** Diretoria de TI
