# Supabase Storage - Documentação

Sistema de armazenamento de imagens usando Supabase Storage.

**Última atualização:** 2024-12-27

---

## Visão Geral

O SISInfo V2 utiliza o **Supabase Storage** para armazenar imagens e documentos. Todos os buckets são hardcoded no código para simplificação.

---

## Buckets Utilizados

| Bucket | Propósito | Arquivos |
|--------|-----------|----------|
| `ocr-images` | Notas fiscais (OCR) | Imagens de NF para extração via Gemini |
| `delivery-documents` | Fichas de entrega | Documentos assinados de recebimento |

---

## Configuração

### Variáveis de Ambiente

```bash
# Obrigatórios para Storage
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...
```

> **Nota:** Não é necessário configurar nomes de buckets - são hardcoded no código.

### Criar Buckets no Supabase Dashboard

1. Acesse **Storage** → **New Bucket**
2. Crie cada bucket como **público**:
   - `ocr-images`
   - `delivery-documents`

---

## Arquitetura

```
┌──────────────┐     ┌─────────────────┐     ┌──────────────────┐
│   Upload     │────▶│  Edge Function  │────▶│   ocr-images     │
│  (Django)    │     │  (process-ocr)  │     │   (bucket)       │
└──────────────┘     └─────────────────┘     └──────────────────┘

┌──────────────┐     ┌─────────────────────────────────────────┐
│   Upload     │────▶│          delivery-documents             │
│ (Assinatura) │     │              (bucket)                   │
└──────────────┘     └─────────────────────────────────────────┘
```

---

## Funções no Código

### `fiscal/services/storage.py`

| Função | Descrição |
|--------|-----------|
| `is_supabase_configured()` | Verifica se Supabase está configurado |
| `delete_image_from_storage(path)` | Deleta imagem do bucket `ocr-images` |
| `check_image_exists(filename)` | Verifica se imagem existe |
| `cleanup_ocr_job(job_id)` | Limpa job OCR e sua imagem |
| `cleanup_stale_jobs(hours)` | Limpa jobs órfãos |

### `fiscal/views/delivery.py`

| Função | Descrição |
|--------|-----------|
| `upload_signed_document(file, pk)` | Upload para `delivery-documents` |

---

## Comandos de Manutenção

### Limpeza de Jobs OCR

```bash
# Ver o que seria deletado
python manage.py clean_ocr_jobs --dry-run

# Deletar jobs + imagens (> 7 dias)
python manage.py clean_ocr_jobs --days 7 --with-images

# Deletar jobs travados (> 1 hora)
python manage.py clean_ocr_jobs --stale
```

### Limpeza de Imagens Órfãs

```bash
python manage.py clean_orphan_images
```

---

## URLs de Acesso

### Formato das URLs Públicas

```
{SUPABASE_URL}/storage/v1/object/public/{bucket}/{filename}
```

**Exemplos:**
- OCR: `https://xxx.supabase.co/storage/v1/object/public/ocr-images/abc123.jpg`
- Delivery: `https://xxx.supabase.co/storage/v1/object/public/delivery-documents/456_def.jpg`

---

## Troubleshooting

### Imagem não aparece

1. Verificar se bucket é público
2. Verificar campo `photo` ou `signed_document` no banco
3. Testar URL diretamente no navegador

### Erro de upload

1. Verificar `SUPABASE_SERVICE_ROLE_KEY`
2. Verificar se bucket existe
3. Verificar logs do Supabase Dashboard

---

## Referências

- [Supabase Storage Docs](https://supabase.com/docs/guides/storage)
- [docs/OCR.md](OCR.md) - Sistema de OCR
