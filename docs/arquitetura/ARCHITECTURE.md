# Arquitetura - SISInfo V2

Visão geral da arquitetura e decisões técnicas do sistema.

**Última atualização:** 2025-12-28

---

## Visão Geral

```
┌─────────────────────────────────────────────────────────────┐
│                         FRONTEND                             │
│  TailwindCSS + Alpine.js + HTMX + ApexCharts                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     DJANGO APPLICATION                       │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │  Views  │──│Services │──│ Models  │──│  Forms  │        │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘        │
└─────────────────────────────────────────────────────────────┘
          │                       │                │
          ▼                       ▼                ▼
┌─────────────┐       ┌─────────────────┐   ┌─────────────┐
│  Supabase   │       │   PostgreSQL    │   │   MongoDB   │
│  Storage    │       │   (Supabase)    │   │   (Atlas)   │
│ Edge Funcs  │       │    Dados App    │   │  Auditoria  │
└─────────────┘       └─────────────────┘   └─────────────┘
```

---

## Camadas

### 1. Views

Responsáveis por:
- Receber requests HTTP
- Validar permissões
- Chamar services
- Renderizar templates

```python
@login_required
def invoice_list(request):
    invoices = InvoiceService.get_user_invoices(request.user)
    return render(request, "fiscal/invoice_list.html", {"invoices": invoices})
```

### 2. Services

Responsáveis por:
- Lógica de negócio
- Operações complexas
- Integrações externas

```python
class InvoiceService:
    @staticmethod
    def process_ocr(invoice_id: int) -> dict:
        # Lógica complexa aqui
        ...
```

### 3. Models

Responsáveis por:
- Estrutura de dados
- Validações de campo
- Relacionamentos

### 4. Forms

Responsáveis por:
- Validação de entrada
- Limpeza de dados
- Apresentação de formulários

---

## Apps Django

| App | Responsabilidade |
|-----|------------------|
| `core` | Configurações, settings, views globais |
| `authenticate` | Autenticação, usuários, perfis |
| `dashboard` | Painel principal, estatísticas |
| `fiscal` | Notas fiscais, entregas, OCR |
| `reports` | Laudos técnicos, PDFs |
| `bidding_procurement` | Licitações, materiais |
| `bidding_supplier` | Fornecedores |
| `organizational_structure` | Diretorias, setores |
| `audit` | Logs de auditoria (MongoDB) |

---

## Fluxo de Dados

### Criação de Nota Fiscal com OCR

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Upload  │───▶│ Supabase │───▶│  Edge    │───▶│ Callback │
│  Imagem  │    │  Storage │    │ Function │    │  Django  │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
     │                               │               │
     │                               ▼               ▼
     │                          ┌──────────┐   ┌──────────┐
     │                          │  Gemini  │   │  Update  │
     │                          │   API    │   │  Invoice │
     │                          └──────────┘   └──────────┘
     │
     └──────────────────────────────────────────────┐
                                                    ▼
                                              ┌──────────┐
                                              │   View   │
                                              │  Result  │
                                              └──────────┘
```

---

## Autenticação

- Django authentication built-in
- Session-based (cookies)
- Login apenas por email (sem username)
- Onboarding no primeiro login

---

## Armazenamento

### PostgreSQL (Supabase)
- Dados da aplicação
- Relacionamentos
- Transações

### MongoDB Atlas
- Logs de auditoria
- Alta escrita
- Documentos flexíveis

### Supabase Storage
- Imagens de notas fiscais
- Documentos assinados
- Arquivos de entrega

---

## Decisões Técnicas

### Por que Django?
- Stack Python conhecida pela equipe
- Admin robusto out-of-the-box
- ORM maduro para PostgreSQL
- Ecossistema grande

### Por que Supabase?
- PostgreSQL gerenciado
- Storage integrado
- Edge Functions (Deno)
- Free tier generoso

### Por que MongoDB para auditoria?
- Schema flexível para logs
- Alta performance de escrita
- Fácil consultas por data/usuário
- Separação de dados operacionais

### Por que TailwindCSS?
- Utility-first CSS
- Dark mode integrado
- Customização fácil
- Build pequeno com purge

### Por que Alpine.js + HTMX?
- Reatividade sem build step
- Integração natural com Django templates
- Curva de aprendizado baixa
- Menos JavaScript para manter

---

## Deploy

### Produção (Vercel)
- Django via WSGI
- Static files via WhiteNoise
- Edge Functions no Supabase
- PostgreSQL no Supabase
- MongoDB no Atlas

### Desenvolvimento
- Django runserver
- Supabase local (Docker)
- MongoDB local (Docker)
- Hot reload TailwindCSS

---

**Responsável:** Diretoria de TI  
**Contato:** ti@novohorizonte.sp.gov.br
