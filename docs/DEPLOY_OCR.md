# Plano de Deploy - OCR com Supabase

Checklist detalhado para deploy do sistema de OCR em produção.

**Data:** 2024-12-20

---

## ✅ Pré-requisitos

- [ ] Conta no [Supabase](https://supabase.com) (Free Tier ou superior)
- [ ] Chaves API do Gemini (mínimo 5 recomendado)
- [ ] Node.js 18+ instalado localmente
- [ ] Supabase CLI instalado (`npm install -g supabase`)
- [ ] Acesso ao servidor de produção (Vercel, Railway, etc.)

---

## 📋 Checklist de Deploy

### 1. Supabase Cloud - Criar Projeto

```bash
# Status: [ ]
```

1. Acesse https://supabase.com/dashboard
2. Clique em "New Project"
3. Configure:
   - Nome: `sisinfo-ocr` (ou similar)
   - Database password: (anote!)
   - Região: São Paulo (`sa-east-1`) se disponível
4. Aguarde criação (~2 min)
5. Anote as credenciais em Settings → API:
   - `SUPABASE_URL`: https://xxx.supabase.co
   - `SUPABASE_ANON_KEY`: eyJ...
   - `SUPABASE_SERVICE_ROLE_KEY`: eyJ...

---

### 2. Criar Storage Bucket

```bash
# Status: [ ]
```

1. No Dashboard: **Storage** → **New Bucket**
2. Nome: `ocr-images`
3. **Public bucket**: ✅ Sim
4. Clique em "Create bucket"

---

### 3. Configurar Políticas de Storage

```bash
# Status: [ ]
```

1. **Storage** → **ocr-images** → **Policies**
2. Criar política para leitura pública:
   - Nome: `Public read access`
   - Operação: SELECT
   - Template: "Allow access with no restrictions"

As políticas de INSERT e DELETE já funcionam com service_role key.

---

### 4. Deploy da Edge Function

```bash
# Status: [ ]
```

Execute no terminal:

```bash
# 1. Entrar na pasta do projeto
cd /home/patrese/projetos/prefeitura/sisinfo-v2

# 2. Login no Supabase (abre browser)
npx supabase login

# 3. Linkar ao projeto
# Substitua XXX pelo Project Reference (em Settings → General)
npx supabase link --project-ref XXX

# 4. Deploy da função
npx supabase functions deploy process-ocr

# 5. Configurar secrets
npx supabase secrets set GEMINI_API_KEY="key1,key2,key3,key4,key5"
```

---

### 5. Testar Edge Function

```bash
# Status: [ ]
```

No Supabase Dashboard:
1. **Edge Functions** → **process-ocr**
2. Verificar se está **Active**
3. Verificar logs para erros

---

### 6. Configurar Django (.env de Produção)

```bash
# Status: [ ]
```

Adicione ao `.env` de produção (Vercel/Railway):

```bash
# Supabase Produção
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...

# Habilitar Supabase Storage
USE_SUPABASE_STORAGE=True

# Gemini (as mesmas chaves)
GEMINI_API_KEY=key1,key2,key3,key4,key5
```

---

### 7. Aplicar Migração

```bash
# Status: [ ]
```

A migração `0011_add_image_hash_to_ocrjob` precisa ser aplicada:

```bash
# Em produção
python manage.py migrate fiscal
```

---

### 8. Teste End-to-End

```bash
# Status: [ ]
```

1. Acesse a aplicação em produção
2. Vá em **Notas Fiscais** → **Upload**
3. Faça upload de uma imagem de nota fiscal
4. Verifique:
   - [ ] Upload funciona (não dá timeout)
   - [ ] Polling mostra progresso
   - [ ] Dados são extraídos corretamente
   - [ ] Imagem aparece na tela de criação
   - [ ] Após salvar, imagem aparece nos detalhes

---

## ⚠️ Possíveis Erros e Soluções

### Erro: "Edge Function not found"

**Causa:** Função não foi deployada corretamente.

**Solução:**
```bash
npx supabase functions deploy process-ocr --no-verify-jwt
```

---

### Erro: "CORS error" no frontend

**Causa:** Edge Function bloqueando origin.

**Solução:** A função já tem headers CORS configurados. Verifique se está usando a URL correta.

---

### Erro: "Storage bucket not found"

**Causa:** Bucket `ocr-images` não foi criado.

**Solução:** Criar manualmente no Dashboard → Storage.

---

### Erro: "Invalid API key" na Edge Function

**Causa:** Secrets não configurados.

**Solução:**
```bash
npx supabase secrets set GEMINI_API_KEY="key1,key2,key3"
```

---

### Erro: Imagem não aparece nos detalhes

**Causa:** Bucket não é público.

**Solução:** 
1. Storage → ocr-images → Settings
2. Marcar como **Public bucket**

---

## 🔄 Rollback

Se algo der errado:

### Opção 1: Desabilitar Supabase

```bash
# No .env de produção
USE_SUPABASE_STORAGE=False
```

Isso volta para o processamento local (mais lento, pode dar timeout na Vercel).

### Opção 2: Remover Edge Function

```bash
npx supabase functions delete process-ocr
```

---

## 📊 Monitoramento Pós-Deploy

### Diário
- Verificar logs no Supabase Dashboard
- Verificar se há jobs travados

### Semanal
- Limpar jobs antigos:
  ```bash
  python manage.py clean_ocr_jobs --days 7 --with-images
  ```

### Mensal
- Verificar uso do Storage
- Verificar quota das chaves Gemini

---

## ✅ Checklist Final

- [ ] Supabase projeto criado
- [ ] Bucket `ocr-images` criado e público
- [ ] Edge Function `process-ocr` deployada
- [ ] Secrets configurados (GEMINI_API_KEY)
- [ ] Variáveis no .env de produção
- [ ] Migração aplicada
- [ ] Teste end-to-end bem-sucedido

---

**Responsável:** Diretoria de TI  
**Contato:** ti@novohorizonte.sp.gov.br
