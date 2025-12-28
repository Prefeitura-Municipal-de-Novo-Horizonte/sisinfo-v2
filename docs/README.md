# Documentação SISInfo V2

Documentação técnica do sistema SISInfo V2.

**Última atualização:** 2025-12-28

---

## 📐 Arquitetura

Decisões técnicas e visão geral dos componentes.

| Documento | Descrição |
|-----------|-----------|
| [AUDITORIA.md](arquitetura/AUDITORIA.md) | Sistema de auditoria com MongoDB Atlas |
| [STORAGE.md](arquitetura/STORAGE.md) | Armazenamento de imagens com Supabase Storage |

---

## 🏗️ Infraestrutura

Deploy, containers e ambiente de desenvolvimento.

| Documento | Descrição |
|-----------|-----------|
| [DOCKER.md](infraestrutura/DOCKER.md) | Docker Compose para desenvolvimento local |

---

## ⚙️ Features

Documentação de funcionalidades implementadas e futuras.

| Documento | Descrição |
|-----------|-----------|
| [OCR.md](features/OCR.md) | Sistema de OCR com Supabase Edge Functions e Gemini |

### Designs de Features Futuras

| Design | Descrição | Status |
|--------|-----------|--------|
| [assinatura_digital.md](features/design/assinatura_digital.md) | Assinatura digital de PDFs | 📋 Planejado |
| [ajuda_faq/](features/design/ajuda_faq/) | Página de Ajuda/FAQ | 📋 Planejado |

---

## 📋 Planejamento

Roadmap e backlog do projeto.

| Documento | Descrição |
|-----------|-----------|
| [ROADMAP.md](planejamento/ROADMAP.md) | Roadmap unificado por fases |
| [PROXIMOS_PASSOS.md](planejamento/PROXIMOS_PASSOS.md) | Backlog detalhado e comandos úteis |
| [ANALISE_PRODUCAO.md](planejamento/ANALISE_PRODUCAO.md) | Análise de gaps para produção |

---

## 📂 Dados de Teste

Dados de teste estão em `data/` na raiz do projeto:

| Pasta | Conteúdo |
|-------|----------|
| `data/licitacoes/` | JSONs de licitações extraídas |
| `data/samples/notas/` | Imagens de notas fiscais para testes de OCR |

---

## 🔗 Links Úteis

- [README.md](../README.md) - Visão geral do projeto
- [GEMINI.md](../GEMINI.md) - Contexto para assistentes de IA
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Guia de contribuição

---

**Responsável:** Diretoria de TI  
**Contato:** ti@novohorizonte.sp.gov.br
