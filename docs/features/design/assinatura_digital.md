# Assinatura Digital de PDFs

Design para implementação futura de assinatura digital no SISInfo V2.

**Status:** 📋 Levantamento  
**Última atualização:** 2025-12-28

---

## Objetivo

Permitir que usuários autorizados assinem digitalmente documentos PDF gerados pelo sistema, garantindo:
- **Integridade** - Documento não foi alterado após assinatura
- **Autenticidade** - Identifica quem assinou
- **Não-repúdio** - Assinante não pode negar a assinatura
- **Imutabilidade** - Após assinado, documento fica bloqueado para edições

---

## Escopo

### Fase 1 - Documentos Internos
| Documento | Model | Status |
|-----------|-------|--------|
| Laudos Técnicos | `Report` | 🎯 Prioritário |
| Fichas de Entrega | `DeliveryNote` | 🎯 Prioritário |

### Fase 2 - Futuro
| Documento | Model | Status |
|-----------|-------|--------|
| Notas Fiscais | `Invoice` | ⏸️ A analisar |

---

## Requisitos Funcionais

### RF01 - Assinatura Manual pelo Usuário
- Usuário autorizado escolhe quando assinar
- Botão "Assinar Documento" na interface
- Confirmação antes de assinar (ação irreversível)

### RF02 - Bloqueio Após Assinatura
- Documento assinado **não permite**:
  - Gerar novo PDF
  - Editar dados do registro
  - Excluir o registro
- Campo `signed_at` (datetime) no model
- Campo `signed_by` (FK para User) no model
- Campo `signed_pdf_url` (URL do Google Drive)

### RF03 - Armazenamento no Google Drive
- PDFs assinados salvos no Google Drive
- Estrutura de pastas: `SISInfo/PDFs Assinados/{ano}/{tipo}/`
- Economiza storage do Supabase
- Facilita auditoria e backup externo

### RF04 - Visualização
- Indicador visual de "Documento Assinado" ✅
- Link para download do PDF assinado
- Exibir quem assinou e quando

---

## Requisitos Não-Funcionais

### RNF01 - Tipo de Assinatura
- **Assinatura Avançada** (certificado autoassinado)
- Validade: Controle interno
- Não requer ICP-Brasil (economia de custos)

### RNF02 - Processamento Assíncrono
- Assinatura via QStash (não bloqueia UI)
- Feedback de status: "Processando...", "Assinado", "Erro"

### RNF03 - Certificado
- Certificado A1 (.p12) gerado pela Prefeitura
- Armazenado como variável de ambiente (base64)
- Um certificado por instalação (não por usuário)

---

## Arquitetura Proposta

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Usuário   │────▶│   Django    │────▶│   QStash    │
│  Assinar    │     │  View       │     │   Queue     │
└─────────────┘     └─────────────┘     └─────────────┘
                                              │
                           ┌──────────────────┘
                           ▼
                    ┌─────────────┐
                    │  Endpoint   │
                    │ /api/sign/  │
                    └─────────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
   │  Gerar PDF  │  │  pyHanko    │  │Google Drive │
   │ (Browserless)│  │  Assinar   │  │   Upload    │
   └─────────────┘  └─────────────┘  └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   Update    │
                    │   Model     │
                    └─────────────┘
```

---

## Stack Técnica

| Componente | Tecnologia | Função |
|------------|------------|--------|
| **Assinatura** | pyHanko | Biblioteca Python para assinatura digital |
| **PDF** | Browserless.io + Playwright | Geração do PDF (já usado no projeto) |
| **Queue** | QStash | Processamento assíncrono |
| **Storage** | Google Drive API | Armazenamento dos PDFs assinados |
| **Certificado** | OpenSSL | Geração de certificado autoassinado |

---

## pyHanko - Visão Geral

### O que é?
Biblioteca Python para assinatura digital de PDFs seguindo padrões PAdES (PDF Advanced Electronic Signatures).

### Instalação
```bash
pip install pyhanko[pkcs11,image-support]
```

### Exemplo Básico
```python
from pyhanko.sign import signers, fields
from pyhanko.pdf_utils.reader import PdfFileReader
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter

# Carregar certificado
signer = signers.SimpleSigner.load_pkcs12(
    pfx_file='certificado.p12',
    passphrase=b'senha_do_certificado'
)

# Abrir PDF
with open('documento.pdf', 'rb') as pdf_file:
    reader = PdfFileReader(pdf_file)
    writer = IncrementalPdfFileWriter(reader)
    
    # Assinar
    out = signers.sign_pdf(
        writer,
        signature_meta=signers.PdfSignatureMetadata(field_name='Signature1'),
        signer=signer,
    )
    
    # Salvar PDF assinado
    with open('documento_assinado.pdf', 'wb') as output:
        output.write(out.getvalue())
```

### Recursos do pyHanko
- ✅ Assinatura invisível (metadados)
- ✅ Assinatura visível (carimbo no PDF)
- ✅ Múltiplas assinaturas
- ✅ Timestamp (carimbo de tempo)
- ✅ Validação de assinaturas
- ✅ Suporte a certificados ICP-Brasil

### Links Úteis
- [Documentação Oficial](https://pyhanko.readthedocs.io/)
- [GitHub](https://github.com/MatthiasValvekens/pyHanko)
- [Exemplos](https://pyhanko.readthedocs.io/en/latest/cli-guide/signing.html)

---

## Gerando Certificado Autoassinado

Para controle interno, podemos gerar nosso próprio certificado:

```bash
# Gerar chave privada
openssl genrsa -out prefeitura_key.pem 2048

# Gerar certificado (válido por 10 anos)
openssl req -new -x509 -key prefeitura_key.pem \
  -out prefeitura_cert.pem -days 3650 \
  -subj "/C=BR/ST=SP/L=Novo Horizonte/O=Prefeitura Municipal/OU=Diretoria de TI/CN=SISInfo V2"

# Converter para PKCS12 (.p12)
openssl pkcs12 -export -out prefeitura.p12 \
  -inkey prefeitura_key.pem -in prefeitura_cert.pem \
  -passout pass:senha_segura
```

---

## Alterações no Banco de Dados

### Model: Report
```python
# reports/models.py
class Report(models.Model):
    # ... campos existentes ...
    
    # Novos campos para assinatura
    signed_at = models.DateTimeField(null=True, blank=True)
    signed_by = models.ForeignKey(
        User, 
        on_delete=models.PROTECT,
        null=True, 
        blank=True,
        related_name='signed_reports'
    )
    signed_pdf_url = models.URLField(max_length=500, blank=True)
    
    @property
    def is_signed(self):
        return self.signed_at is not None
    
    def can_edit(self):
        return not self.is_signed
```

### Model: DeliveryNote
```python
# fiscal/models.py
class DeliveryNote(models.Model):
    # ... campos existentes ...
    
    # Novos campos para assinatura
    signed_at = models.DateTimeField(null=True, blank=True)
    signed_by = models.ForeignKey(User, ...)
    signed_pdf_url = models.URLField(...)
```

---

## Google Drive vs Supabase Storage

| Aspecto | Google Drive | Supabase Storage |
|---------|--------------|------------------|
| **Custo** | 15GB grátis | Limitado no plano |
| **Acesso Externo** | Fácil compartilhar | Requer auth |
| **Integração Python** | `google-api-python-client` | SDK Supabase |
| **Backup** | Automático | Manual |
| **Migração VPS** | Manter Drive | Migrar para Supabase |

> **Decisão:** Usar Google Drive agora. Se migrar para VPS no futuro, avaliar migração para Supabase Storage ou manter híbrido.

---

## Fluxo de Usuário (UI)

### Estado: Não Assinado
```
┌─────────────────────────────────────────────┐
│ Laudo Técnico #123                          │
│ Status: ✏️ Rascunho                          │
│                                             │
│ [Editar] [Gerar PDF] [🔐 Assinar Documento] │
└─────────────────────────────────────────────┘
```

### Modal de Confirmação
```
┌─────────────────────────────────────────────┐
│ ⚠️ Confirmar Assinatura                      │
│                                             │
│ Ao assinar este documento:                  │
│ • Não será possível editá-lo                │
│ • Não será possível gerar novo PDF          │
│ • A assinatura é permanente                 │
│                                             │
│ Tem certeza que deseja continuar?           │
│                                             │
│              [Cancelar] [✅ Assinar]         │
└─────────────────────────────────────────────┘
```

### Estado: Assinado
```
┌─────────────────────────────────────────────┐
│ Laudo Técnico #123                          │
│ Status: ✅ Assinado                          │
│ Assinado por: João Silva em 28/12/2024      │
│                                             │
│ [📄 Ver PDF Assinado]                       │
└─────────────────────────────────────────────┘
```

---

## Permissões

| Ação | Quem pode? |
|------|------------|
| Assinar Laudos | Usuários com permissão `reports.can_sign_report` |
| Assinar Entregas | Usuários com permissão `fiscal.can_sign_delivery` |

---

## Endpoints Necessários

| Método | Endpoint | Função |
|--------|----------|--------|
| POST | `/api/reports/{id}/sign/` | Iniciar assinatura de laudo |
| POST | `/api/deliveries/{id}/sign/` | Iniciar assinatura de entrega |
| GET | `/api/sign-status/{job_id}/` | Status do job de assinatura |
| POST | `/api/webhooks/sign-complete/` | Callback do QStash |

---

## Variáveis de Ambiente

```bash
# Certificado (base64 do arquivo .p12)
PDF_SIGNING_CERTIFICATE_B64=<base64_do_certificado>
PDF_SIGNING_CERTIFICATE_PASSWORD=senha_do_certificado

# Google Drive (já existentes do backup)
GOOGLE_DRIVE_CREDENTIALS_B64=<base64_do_json>
GOOGLE_DRIVE_FOLDER_SIGNED_PDFS=<id_da_pasta>
```

---

## Estimativa de Implementação

| Fase | Tarefa | Esforço |
|------|--------|---------|
| 1 | Migrations (campos de assinatura) | 1h |
| 2 | Serviço de assinatura (pyHanko) | 4h |
| 3 | Integração QStash | 2h |
| 4 | Integração Google Drive | 2h |
| 5 | UI (botões, modais, status) | 4h |
| 6 | Permissões e bloqueios | 2h |
| 7 | Testes | 3h |
| **Total** | | **~18h** |

---

## Riscos e Mitigações

| Risco | Mitigação |
|-------|-----------|
| Perda do certificado | Backup em local seguro |
| Google Drive indisponível | Retry automático via QStash |
| PDF corrompido | Validação antes de assinar |
| Usuário assina por engano | Modal de confirmação obrigatório |

---

## Próximos Passos

1. [ ] Aprovar este design
2. [ ] Implementar backup no Google Drive (pré-requisito)
3. [ ] Gerar certificado autoassinado para testes
4. [ ] Criar POC com pyHanko
5. [ ] Implementar feature completa

---

## Referências

- [pyHanko Documentation](https://pyhanko.readthedocs.io/)
- [PAdES - PDF Advanced Electronic Signatures](https://en.wikipedia.org/wiki/PAdES)
- [Google Drive API Python](https://developers.google.com/drive/api/quickstart/python)
- [QStash Documentation](https://upstash.com/docs/qstash)
