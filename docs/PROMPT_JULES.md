# 🤖 Prompt para Jules.google - Redesign SISInfo V2

## 📋 COPIE E COLE ESTE PROMPT PARA O JULES:

---

Olá! Sou o desenvolvedor do **SISInfo V2**, uma aplicação Django para gestão de TI municipal. Preciso que você implemente um redesign completo do layout seguindo a documentação que preparei.

## 📚 Documentação Disponível

Você tem acesso a 4 documentos principais na pasta `docs/` (que deve estar no zip):

1. **ADVANCED_IMPLEMENTATION.md** (Guia Técnico Principal)
   - Remoção completa de Flowbite (12 arquivos)
   - Menu retrátil moderno com Alpine.js
   - Gráficos com ApexCharts
   - WebSockets com Django Channels

2. **COMPLETE_DESIGN_SPEC.md** (Especificação de Design)
   - Detalhes de todas as 53 páginas
   - Layouts específicos (Login Split Screen, Dashboard)
   - Design System (Cores, Tipografia)

3. **REDESIGN_VISUAL_GUIDE.md**
   - Levantamento do projeto e inventário

4. **COLABORACAO_JULES.md**
   - Workflow e checklist

## 🎯 Seu Objetivo

Implementar o redesign seguindo **EXATAMENTE** o guia `ADVANCED_IMPLEMENTATION.md` e `COMPLETE_DESIGN_SPEC.md`, priorizando:

### Fase 1: Remoção de Flowbite (OBRIGATÓRIO)
- [ ] Remover Flowbite do `package.json` e `tailwind.config.js`
- [ ] Instalar Alpine.js
- [ ] Substituir todos os componentes Flowbite por Alpine.js
- [ ] Atualizar `templates/include/_nav.html` com novo sidebar retrátil

### Fase 2: Identidade Visual (Azul Institucional)
- [ ] Configurar Tailwind com a paleta **Azul Institucional** (#1D4ED8)
- [ ] Implementar Login com layout "Split Screen" (ver spec)
- [ ] Ajustar Sidebar para ter toggle de tema (Claro/Escuro)

### Fase 3: Dashboard Moderno
- [ ] **REMOVER** cards de contadores simples (Laudos, Materiais, Setores)
- [ ] **CRIAR** Gráfico Principal: "Laudos por Setor" (Largura total, ApexCharts)
- [ ] **CRIAR** Filtro de Data (Select) para o gráfico (via HTMX)
- [ ] **CRIAR** Calendário (FullCalendar) e Gráfico de Top Materiais

### Fase 4: Core Features
- [ ] Refazer lista de Laudos com filtros HTMX
- [ ] Implementar Formset dinâmico para Materiais (Criar Laudo)
- [ ] Implementar Modal de Cadastro Rápido de Setor

## 🔧 Stack Tecnológica

**Atual:**
- Django 5.2.6
- Tailwind CSS 3.3.5
- Flowbite 2.0.0 ❌ (REMOVER)

**Adicionar:**
- Alpine.js 3.x ✅
- ApexCharts 3.45+ ✅
- HTMX 1.9+ ✅
- FullCalendar 6.1+ ✅

## 📂 Estrutura do Projeto

```
sisinfo-v2/
├── core/                    # Configurações
├── authenticate/            # Login, Reset
├── reports/                 # Laudos (Core)
├── dashboard/               # Home
├── templates/               # Templates base
│   └── include/
│       ├── _nav.html       # ⚠️ PRINCIPAL ARQUIVO A MODIFICAR
├── docs/                    # 📚 DOCUMENTAÇÃO (No ZIP)
└── backup/                  # 💾 Backup dos templates originais
```

## ⚠️ IMPORTANTE - Leia Antes de Começar

1. **Backup já existe:** Todos os templates estão em `backup/templates/`
2. **Não quebre funcionalidades:** Mantenha os formulários funcionando
3. **Siga o guia:** Use o código exato do `ADVANCED_IMPLEMENTATION.md`
4. **Design:** Siga o `COMPLETE_DESIGN_SPEC.md` para layouts
5. **Cores:** Use Azul Institucional (#1D4ED8), não use cores vibrantes/neon.

## 🚀 Como Começar

### 1. Criar sua branch
```bash
git checkout -b feat/redesign-implementation
```

### 2. Ler documentação
- Comece por `ADVANCED_IMPLEMENTATION.md` para o setup técnico.
- Consulte `COMPLETE_DESIGN_SPEC.md` para o layout de cada página.

### 3. Implementar fase por fase
- Fase 1: Flowbite → Alpine.js
- Fase 2: Login e Sidebar
- Fase 3: Dashboard
- Fase 4: Laudos

### 4. Testar localmente
```bash
npm install
pip install -r requirements.txt
python manage.py migrate
npm run dev &
python manage.py runserver
```

## 📝 Arquivos Principais a Modificar

### Obrigatórios:
1. `package.json` - Remover Flowbite, adicionar Alpine/HTMX
2. `tailwind.config.js` - Remover plugin Flowbite, configurar cores
3. `templates/include/_nav.html` - Novo sidebar retrátil
4. `authenticate/templates/login.html` - Novo layout split screen
5. `dashboard/templates/index.html` - Novo dashboard com gráficos

## 🎨 Tema (Azul Institucional)

Use as cores definidas em `COMPLETE_DESIGN_SPEC.md`:
- **Primary:** `#1D4ED8` (Blue 700)
- **Secondary:** `#1E3A8A` (Blue 900)
- **Background:** `#F3F4F6` (Gray 100)

## ✅ Checklist de Validação

- [ ] Flowbite completamente removido
- [ ] Alpine.js e HTMX funcionando
- [ ] Sidebar retrátil funcionando
- [ ] Login com layout novo (Azul)
- [ ] Dashboard sem cards simples, com gráficos grandes
- [ ] Responsivo em mobile

---

**Pronto para começar?** 🚀

Leia `docs/ADVANCED_IMPLEMENTATION.md` e comece pela **Fase 1**.
Boa sorte!
