# 🎨 Levantamento Completo para Redesign de Layout - SISInfo V2

**Data:** 02/12/2025  
**Objetivo:** Documentação completa para planejamento de redesign de layout  
**Status:** ✅ Levantamento concluído - **NÃO IMPLEMENTAR AINDA**

---

## 📋 Índice

1. [Descobertas Importantes](#descobertas-importantes)
2. [Formsets e Inline Forms](#formsets-e-inline-forms)
3. [Forms Padrão do Django](#forms-padrão-do-django)
4. [Backup de Templates](#backup-de-templates)
5. [Inventário de Páginas](#inventário-de-páginas)
6. [Análise do Layout Atual](#análise-do-layout-atual)
7. [Planejamento de Redesign](#planejamento-de-redesign)
8. [Node.js e Ferramentas](#nodejs-e-ferramentas)
9. [Roadmap de Implementação](#roadmap-de-implementação)

> [!NOTE]
> **Especificações de UX/UI Detalhadas**  
> Para detalhes completos de melhorias de interface, experiência do usuário e implementação de componentes avançados, consulte:
> - **[UX_UI_SPECIFICATION.md](UX_UI_SPECIFICATION.md)** - Especificações detalhadas por página
> - **[ADVANCED_IMPLEMENTATION.md](ADVANCED_IMPLEMENTATION.md)** - Implementação técnica completa
>
> Este documento (REDESIGN_VISUAL_GUIDE.md) contém o levantamento e análise. Os documentos acima contêm as especificações de implementação.

---

## 🔍 Descobertas Importantes

### ✅ Formsets Inline Encontrados

Contrário ao relatório inicial, **EXISTEM formsets inline** implementados:

1. **`MaterialReportFormset`** (reports/forms.py)
   - Inline de `MaterialReport` em `Report`
   - Permite adicionar múltiplos materiais em um laudo
   - Configuração: `extra=1`, `can_delete=True`, `min_num=1`
   
2. **`ContactInlineForm`** (bidding_supplier/forms.py)
   - Inline de `Contact` em `Supplier`
   - Permite adicionar múltiplos contatos para um fornecedor
   - Configuração: `extra=1`, `can_delete=True`, `min_num=1`

> [!IMPORTANT]
> **Correção do Relatório Anterior:**  
> O app `bidding_supplier` **TEM formulários** (`SupplierForm` e `ContactForm`).  
> O app `reports` **TEM formulário de materiais** (`MaterialReportForm` + formset).

---

## 📝 Formsets e Inline Forms

### Formsets Implementados

#### 1. MaterialReportFormset

**Localização:** `reports/forms.py:112-120`

```python
MaterialReportFormset = inlineformset_factory(
    Report,
    MaterialReport,
    form=MaterialReportForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True
)
```

**Uso:**
- Criação de laudos: `reports/views.py` (linha 44, 59)
- Atualização de laudos: `reports/views.py` (linha 87)
- Service layer: `reports/services.py`

**Campos do Form:**
- `id` (HiddenInput)
- `material_bidding` (Select com queryset filtrado por status='1')
- `quantity` (IntegerField)

**Customizações:**
- Label customizado mostrando "Material - Licitação"
- Filtra apenas materiais ativos
- Usa `select_related` para otimização

#### 2. ContactInlineForm

**Localização:** `bidding_supplier/forms.py:46-54`

```python
ContactInlineForm = inlineformset_factory(
    Supplier,
    Contact,
    form=ContactForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)
```

**Uso:**
- Criação de fornecedores: `bidding_supplier/views.py` (linha 26)
- Atualização de fornecedores: `bidding_supplier/views.py` (linha 38)
- Service layer: `bidding_supplier/services.py`

**Campos do Form:**
- `id` (HiddenInput)
- `kind` (Select: Email/Telefone)
- `value` (CharField)
- `whatsapp` (BooleanField com classe `sr-only peer`)

---

## 🔐 Forms Padrão do Django (authenticate)

### Forms em Uso

O app `authenticate` usa forms customizados que **herdam** dos forms padrão do Django:

#### 1. AuthenticationFormCustom

**Herda de:** `django.contrib.auth.forms.AuthenticationForm`

**Localização:** `authenticate/forms.py:86-94`

**Customizações Atuais:**
- Aplica estilos Tailwind CSS via `FormStyleMixin`
- Placeholders vazios
- Classes CSS para tema dark/light

**Possíveis Melhorias:**
```python
class AuthenticationFormCustom(FormStyleMixin, AuthenticationForm):
    # Adicionar campo "Lembrar-me"
    remember_me = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-blue-600'})
    )
    
    # Adicionar validação customizada
    def clean(self):
        cleaned_data = super().clean()
        # Adicionar lógica de tentativas de login
        # Adicionar verificação de conta ativa
        return cleaned_data
```

#### 2. PasswordChangeCustomForm

**Herda de:** `django.contrib.auth.forms.PasswordChangeForm`

**Localização:** `authenticate/forms.py:97-100`

**Customizações Atuais:**
- Apenas aplica estilos via `FormStyleMixin`

**Possíveis Melhorias:**
```python
class PasswordChangeCustomForm(FormStyleMixin, PasswordChangeForm):
    def clean_new_password2(self):
        password = super().clean_new_password2()
        # Adicionar validação de força de senha
        # Adicionar verificação de senha anterior
        return password
```

#### 3. UserCreationForm

**Herda de:** `forms.ModelForm` (não usa o padrão do Django)

**Customizações:**
- Usa `CapitalizeFieldMixin` para capitalizar nomes
- Validação de CNPJ (ops, não tem CNPJ em ProfessionalUser)
- Campos de permissão (`is_tech`, `is_admin`)

#### 4. UserChangeForm

**Herda de:** `forms.ModelForm`

**Campos Faltantes:** `is_tech`, `is_admin`, `is_active`

**Recomendação:**
```python
class UserChangeForm(FormStyleMixin, forms.ModelForm):
    class Meta:
        model = ProfessionalUser
        fields = [
            "first_name", "last_name", "username",
            "email", "registration",
            "is_tech", "is_admin", "is_active"  # ADICIONAR
        ]
```

### Forms de Recuperação de Senha

O projeto usa os forms padrão do Django sem customização:
- `PasswordResetForm`
- `SetPasswordForm`

**Templates:**
- `password_reset.html` - Solicitar reset
- `password_reset_done.html` - Confirmação de envio
- `password_reset_confirm_view.html` - Definir nova senha
- `password_reset_complete.html` - Conclusão

**Possíveis Melhorias:**
- Customizar forms com estilos Tailwind
- Adicionar validação de email
- Adicionar tempo de expiração customizado
- Adicionar verificação de segurança (2FA futuro)

---

## 💾 Backup de Templates

### ✅ Backup Concluído

**Localização:** `backup/templates/`

**Estrutura:**
```
backup/templates/
├── authenticate/          (11 templates)
├── base/                  (8 templates + includes)
├── bidding_procurement/   (8 templates + includes)
├── bidding_supplier/      (3 templates)
├── dashboard/             (1 template)
├── organizational_structure/ (6 templates + includes)
└── reports/               (6 templates)
```

**Total:** 48 templates HTML

**Comando usado:**
```bash
cp -r authenticate/templates backup/templates/authenticate
cp -r bidding_procurement/templates backup/templates/bidding_procurement
cp -r bidding_supplier/templates backup/templates/bidding_supplier
cp -r dashboard/templates backup/templates/dashboard
cp -r organizational_structure/templates backup/templates/organizational_structure
cp -r reports/templates backup/templates/reports
cp -r templates backup/templates/base
```

---

## 📄 Inventário Completo de Páginas

### App: authenticate (11 páginas)

| Template | Rota | Descrição | Formulário |
|----------|------|-----------|------------|
| `login.html` | `/login/` | Página de login | AuthenticationFormCustom |
| `register_user.html` | `/register/` | Cadastro de usuário | UserCreationForm |
| `profiles.html` | `/profiles/` | Lista de usuários | - |
| `profile_professional.html` | `/profile/<slug>/` | Perfil de usuário | UserChangeForm |
| `users.html` | `/users/` | Gerenciamento de usuários | - |
| `change_password.html` | `/change-password/` | Trocar senha | PasswordChangeCustomForm |
| `password_reset.html` | `/password-reset/` | Solicitar reset | PasswordResetForm |
| `password_reset_done.html` | `/password-reset/done/` | Confirmação | - |
| `password_reset_confirm_view.html` | `/reset/<uidb64>/<token>/` | Definir nova senha | SetPasswordForm |
| `password_reset_complete.html` | `/reset/done/` | Conclusão | - |
| `templatetags/render_field.html` | - | Template tag | - |

### App: bidding_procurement (8 páginas)

| Template | Rota | Descrição | Formulário |
|----------|------|-----------|------------|
| `biddings.html` | `/procurement/licitacoes/` | Lista de licitações | BiddingForm |
| `bidding_detail.html` | `/procurement/licitacao/<slug>/` | Detalhes da licitação | MaterialBiddingForm |
| `materials.html` | `/procurement/materiais/` | Lista de materiais | MaterialForm |
| `material_detail.html` | `/procurement/material/<slug>/` | Detalhes do material | - |
| `include/_table_material.html` | - | Tabela de materiais | - |
| `include/_form_material.html` | - | Form de material inline | - |
| `include/_table_material_list.html` | - | Lista de materiais | - |
| `include/_form_material_generic.html` | - | Form genérico | - |

### App: bidding_supplier (3 páginas)

| Template | Rota | Descrição | Formulário |
|----------|------|-----------|------------|
| `suppliers.html` | `/suppliers/` | Lista de fornecedores | SupplierForm |
| `supllier.html` | `/supplier/<slug>/` | Detalhes do fornecedor | - |
| `supplier_update.html` | `/supplier/<slug>/update/` | Editar fornecedor | SupplierForm + ContactInlineForm |

### App: organizational_structure (6 páginas)

| Template | Rota | Descrição | Formulário |
|----------|------|-----------|------------|
| `diretorias.html` | `/structure/diretorias/` | Lista de diretorias | DirectionForm |
| `diretoria_detail.html` | `/structure/diretoria/<slug>/` | Detalhes da diretoria | - |
| `setores.html` | `/structure/setores/` | Lista de setores | SectorForm |
| `setor_detail.html` | `/structure/setor/<slug>/` | Detalhes do setor | - |
| `include/_search_setor.html` | - | Busca de setores | - |
| `include/_table_setor.html` | - | Tabela de setores | - |

### App: reports (6 páginas)

| Template | Rota | Descrição | Formulário |
|----------|------|-----------|------------|
| `reports.html` | `/reports/` | Lista de laudos | - |
| `register_reports.html` | `/reports/register/` | Criar laudo | ReportForm + MaterialReportFormset |
| `update_report.html` | `/reports/<slug>/update/` | Editar laudo | ReportUpdateForm + MaterialReportFormset |
| `report.html` | `/reports/<slug>/` | Visualizar laudo | - |
| `pdf_template.html` | `/reports/<slug>/pdf/` | PDF do laudo | - |
| `pdf_download_template.html` | `/reports/<slug>/download/` | Download PDF | - |

### App: dashboard (1 página)

| Template | Rota | Descrição | Formulário |
|----------|------|-----------|------------|
| `index.html` | `/` | Dashboard principal | - |

### Templates Base (8 arquivos)

| Template | Descrição |
|----------|-----------|
| `_base.html` | Template base principal |
| `_base_external.html` | Template para páginas externas (login) |
| `include/_nav.html` | Navegação sidebar |
| `include/_footer.html` | Rodapé |
| `include/_css.html` | Includes de CSS |
| `include/_js.html` | Includes de JavaScript |
| `include/_favicon.html` | Favicon |
| `include/_alert.html` | Alertas/mensagens |
| `include/_pagination.html` | Paginação |
| `400.html`, `403.html`, `404.html`, `500.html` | Páginas de erro |

---

## 🎨 Análise do Layout Atual

### Estrutura Base

**Template:** `templates/_base.html`

```html
<body>
  <header>
    {% include "include/_nav.html" %}  <!-- Sidebar -->
  </header>
  <main>
    <div class="p-4 sm:ml-64">  <!-- Margin left para sidebar -->
      <div class="p-4 border-2 border-gray-200 border-dashed rounded-lg dark:border-gray-700 mt-14">
        {% block content %}{% endblock %}
      </div>
    </div>
  </main>
  <footer>
    {% include "include/_footer.html" %}
  </footer>
</body>
```

### Navegação Atual

**Sidebar:** Flowbite sidebar component
- Posição: Fixa à esquerda
- Largura: `sm:ml-64` (256px)
- Tema: Suporta dark mode
- Logo: `static/img/logo/logo.png`

### Página de Login Atual

**Template:** `authenticate/templates/login.html`

**Características:**
- Background: `bg-blue-700` (azul sólido)
- Layout: Centralizado com flexbox
- Logo: 80x80px
- Título: "SISInfo V2"
- Campos: Username e Password com floating labels
- Link: "Esqueceu a senha?"
- Botão: Azul com ícone de upload
- Flowbite CDN: 2.2.0

**Problemas Identificados:**
- Background muito simples (azul sólido)
- Sem opção de tema claro/escuro
- Design datado
- Sem animações
- Sem responsividade otimizada para mobile

---

## 🌈 Planejamento de Redesign

### Tema Catppuccin

#### Paletas Disponíveis

**Catppuccin Mocha (Dark):**
```css
--ctp-mocha-rosewater: #f5e0dc;
--ctp-mocha-flamingo: #f2cdcd;
--ctp-mocha-pink: #f5c2e7;
--ctp-mocha-mauve: #cba6f7;
--ctp-mocha-red: #f38ba8;
--ctp-mocha-maroon: #eba0ac;
--ctp-mocha-peach: #fab387;
--ctp-mocha-yellow: #f9e2af;
--ctp-mocha-green: #a6e3a1;
--ctp-mocha-teal: #94e2d5;
--ctp-mocha-sky: #89dceb;
--ctp-mocha-sapphire: #74c7ec;
--ctp-mocha-blue: #89b4fa;
--ctp-mocha-lavender: #b4befe;
--ctp-mocha-text: #cdd6f4;
--ctp-mocha-subtext1: #bac2de;
--ctp-mocha-subtext0: #a6adc8;
--ctp-mocha-overlay2: #9399b2;
--ctp-mocha-overlay1: #7f849c;
--ctp-mocha-overlay0: #6c7086;
--ctp-mocha-surface2: #585b70;
--ctp-mocha-surface1: #45475a;
--ctp-mocha-surface0: #313244;
--ctp-mocha-base: #1e1e2e;
--ctp-mocha-mantle: #181825;
--ctp-mocha-crust: #11111b;
```

**Catppuccin Latte (Light):**
```css
--ctp-latte-rosewater: #dc8a78;
--ctp-latte-flamingo: #dd7878;
--ctp-latte-pink: #ea76cb;
--ctp-latte-mauve: #8839ef;
--ctp-latte-red: #d20f39;
--ctp-latte-maroon: #e64553;
--ctp-latte-peach: #fe640b;
--ctp-latte-yellow: #df8e1d;
--ctp-latte-green: #40a02b;
--ctp-latte-teal: #179299;
--ctp-latte-sky: #04a5e5;
--ctp-latte-sapphire: #209fb5;
--ctp-latte-blue: #1e66f5;
--ctp-latte-lavender: #7287fd;
--ctp-latte-text: #4c4f69;
--ctp-latte-subtext1: #5c5f77;
--ctp-latte-subtext0: #6c6f85;
--ctp-latte-overlay2: #7c7f93;
--ctp-latte-overlay1: #8c8fa1;
--ctp-latte-overlay0: #9ca0b0;
--ctp-latte-surface2: #acb0be;
--ctp-latte-surface1: #bcc0cc;
--ctp-latte-surface0: #ccd0da;
--ctp-latte-base: #eff1f5;
--ctp-latte-mantle: #e6e9ef;
--ctp-latte-crust: #dce0e8;
```

### Nova Página de Login

**Conceito:**

1. **Background Animado:**
   - Gradient animado com cores Catppuccin
   - Partículas flutuantes (opcional)
   - Efeito glassmorphism no card

2. **Card de Login:**
   ```html
   <div class="backdrop-blur-lg bg-white/30 dark:bg-ctp-mocha-base/30 
               rounded-2xl shadow-2xl p-8 w-full max-w-md">
     <!-- Logo centralizada -->
     <!-- Título com gradient -->
     <!-- Campos com floating labels -->
     <!-- Toggle tema claro/escuro -->
     <!-- Botão com hover effects -->
   </div>
   ```

3. **Animações:**
   - Fade in do card
   - Slide up dos campos
   - Hover effects nos botões
   - Transição suave de tema

4. **Responsividade:**
   - Mobile first
   - Breakpoints: sm, md, lg, xl
   - Touch-friendly (botões maiores em mobile)

### Nova Página de Recovery Password

**Fluxo:**

1. **Solicitar Reset:**
   - Email input com validação
   - Animação de envio
   - Feedback visual

2. **Email Enviado:**
   - Ícone de sucesso animado
   - Mensagem clara
   - Botão para reenviar (com cooldown)

3. **Definir Nova Senha:**
   - Indicador de força de senha
   - Requisitos visíveis
   - Confirmação de senha

4. **Conclusão:**
   - Animação de sucesso
   - Redirecionamento automático

### Sistema de Tema Claro/Escuro

**Implementação:**

```javascript
// Detectar preferência do sistema
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

// Salvar preferência no localStorage
localStorage.setItem('theme', 'dark' | 'light');

// Toggle theme
function toggleTheme() {
  const html = document.documentElement;
  const currentTheme = html.classList.contains('dark') ? 'dark' : 'light';
  const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
  
  html.classList.remove(currentTheme);
  html.classList.add(newTheme);
  localStorage.setItem('theme', newTheme);
}
```

**Botão Toggle:**
- Posição: Navbar (canto superior direito)
- Ícone: Sol/Lua
- Animação: Rotação suave

### Componentes Reutilizáveis

#### 1. Card Component
```html
<div class="bg-white dark:bg-ctp-mocha-surface0 rounded-lg shadow-lg p-6">
  <!-- Conteúdo -->
</div>
```

#### 2. Button Component
```html
<button class="bg-ctp-mocha-blue hover:bg-ctp-mocha-sapphire 
               dark:bg-ctp-mocha-mauve dark:hover:bg-ctp-mocha-pink
               text-white font-semibold py-2 px-4 rounded-lg
               transition-all duration-300 ease-in-out
               transform hover:scale-105">
  Texto
</button>
```

#### 3. Input Component
```html
<div class="relative">
  <input type="text" 
         class="peer block w-full px-3 py-2 
                bg-transparent border-b-2 
                border-ctp-mocha-overlay0 
                focus:border-ctp-mocha-blue
                dark:text-ctp-mocha-text
                transition-colors duration-300"
         placeholder=" ">
  <label class="absolute left-0 -top-3.5 
                text-ctp-mocha-subtext0 
                text-sm peer-placeholder-shown:text-base 
                peer-placeholder-shown:top-2 
                transition-all">
    Label
  </label>
</div>
```

### Responsividade

**Breakpoints:**
```css
/* Mobile first */
.container { width: 100%; }

/* sm: 640px */
@media (min-width: 640px) {
  .container { max-width: 640px; }
}

/* md: 768px */
@media (min-width: 768px) {
  .container { max-width: 768px; }
  .sidebar { display: block; }
}

/* lg: 1024px */
@media (min-width: 1024px) {
  .container { max-width: 1024px; }
}

/* xl: 1280px */
@media (min-width: 1280px) {
  .container { max-width: 1280px; }
}
```

**Sidebar Responsiva:**
- Mobile: Hidden por padrão, toggle button
- Tablet: Sidebar colapsável
- Desktop: Sidebar fixa

---

## 🛠️ Node.js e Ferramentas

### Package.json Atual

```json
{
  "scripts": {
    "dev": "npx tailwindcss -i static/tailwindcss/input.css -o static/css/djangotw-ui.css --watch"
  },
  "devDependencies": {
    "prettier": "^3.0.3",
    "prettier-plugin-tailwind-css": "^1.5.0",
    "tailwindcss": "^3.3.5"
  },
  "dependencies": {
    "flowbite": "^2.0.0"
  }
}
```

### Melhorias Recomendadas com Node.js

#### 1. Build Tools

**Adicionar Vite:**
```json
{
  "devDependencies": {
    "vite": "^5.0.0",
    "@vitejs/plugin-legacy": "^5.0.0"
  }
}
```

**Benefícios:**
- Hot Module Replacement (HMR)
- Build otimizado
- Code splitting automático
- Suporte a ES modules

#### 2. CSS Processing

**Adicionar PostCSS plugins:**
```json
{
  "devDependencies": {
    "autoprefixer": "^10.4.16",
    "cssnano": "^6.0.1",
    "postcss-import": "^15.1.0"
  }
}
```

**Benefícios:**
- Autoprefixer para compatibilidade
- Minificação de CSS
- Import de arquivos CSS

#### 3. JavaScript Tools

**Adicionar:**
```json
{
  "devDependencies": {
    "esbuild": "^0.19.0",
    "terser": "^5.24.0",
    "@babel/core": "^7.23.0",
    "@babel/preset-env": "^7.23.0"
  }
}
```

**Benefícios:**
- Transpilação para navegadores antigos
- Minificação de JavaScript
- Tree shaking

#### 4. Linting e Formatação

**Adicionar ESLint:**
```json
{
  "devDependencies": {
    "eslint": "^8.54.0",
    "eslint-config-prettier": "^9.0.0",
    "eslint-plugin-tailwindcss": "^3.13.0"
  }
}
```

#### 5. Animações

**Adicionar bibliotecas:**
```json
{
  "dependencies": {
    "gsap": "^3.12.0",
    "aos": "^2.3.4",
    "particles.js": "^2.0.0"
  }
}
```

**Uso:**
- GSAP: Animações complexas
- AOS: Scroll animations
- Particles.js: Background animado

#### 6. Icons

**Adicionar:**
```json
{
  "dependencies": {
    "lucide": "^0.294.0",
    "@iconify/tailwind": "^0.1.4"
  }
}
```

#### 7. Catppuccin

**Adicionar plugin Tailwind:**
```json
{
  "devDependencies": {
    "@catppuccin/tailwindcss": "^0.1.6"
  }
}
```

**Configuração tailwind.config.js:**
```javascript
module.exports = {
  plugins: [
    require("@catppuccin/tailwindcss")({
      prefix: "ctp",
      defaultFlavour: "mocha",
    }),
  ],
}
```

### Scripts Recomendados

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "tailwind:watch": "npx tailwindcss -i static/tailwindcss/input.css -o static/css/djangotw-ui.css --watch",
    "tailwind:build": "npx tailwindcss -i static/tailwindcss/input.css -o static/css/djangotw-ui.css --minify",
    "format": "prettier --write \"**/*.{js,css,html}\"",
    "lint": "eslint \"**/*.js\"",
    "lint:fix": "eslint \"**/*.js\" --fix"
  }
}
```

---

## 🗺️ Roadmap de Implementação

### Fase 1: Preparação (1-2 dias)

- [x] ✅ Backup de templates
- [ ] Instalar dependências Node.js
- [ ] Configurar Catppuccin Tailwind plugin
- [ ] Criar variáveis CSS customizadas
- [ ] Configurar tema claro/escuro base

### Fase 2: Sistema de Temas (2-3 dias)

- [ ] Implementar toggle de tema
- [ ] Criar CSS variables para Catppuccin
- [ ] Atualizar `_base.html` com suporte a tema
- [ ] Testar em todos os navegadores
- [ ] Adicionar persistência de preferência

### Fase 3: Redesign de Login (2-3 dias)

- [ ] Criar novo `login.html`
- [ ] Background animado com gradient
- [ ] Card com glassmorphism
- [ ] Animações de entrada
- [ ] Responsividade mobile
- [ ] Testar em dispositivos reais

### Fase 4: Redesign de Password Recovery (2 dias)

- [ ] Atualizar `password_reset.html`
- [ ] Atualizar `password_reset_done.html`
- [ ] Atualizar `password_reset_confirm_view.html`
- [ ] Atualizar `password_reset_complete.html`
- [ ] Adicionar indicador de força de senha
- [ ] Animações de feedback

### Fase 5: Componentes Reutilizáveis (3-4 dias)

- [ ] Criar `components/button.html`
- [ ] Criar `components/card.html`
- [ ] Criar `components/input.html`
- [ ] Criar `components/select.html`
- [ ] Criar `components/modal.html`
- [ ] Documentar componentes

### Fase 6: Atualizar Templates Existentes (5-7 dias)

- [ ] Atualizar `_nav.html` (sidebar)
- [ ] Atualizar `_footer.html`
- [ ] Atualizar `index.html` (dashboard)
- [ ] Atualizar templates de authenticate
- [ ] Atualizar templates de bidding_procurement
- [ ] Atualizar templates de bidding_supplier
- [ ] Atualizar templates de organizational_structure
- [ ] Atualizar templates de reports

### Fase 7: Responsividade (2-3 dias)

- [ ] Testar em mobile (320px, 375px, 414px)
- [ ] Testar em tablet (768px, 1024px)
- [ ] Testar em desktop (1280px, 1920px)
- [ ] Ajustar breakpoints
- [ ] Otimizar sidebar mobile

### Fase 8: Animações e Polish (2-3 dias)

- [ ] Adicionar scroll animations (AOS)
- [ ] Adicionar micro-interactions
- [ ] Adicionar loading states
- [ ] Adicionar skeleton screens
- [ ] Otimizar performance

### Fase 9: Testes e Ajustes (2-3 dias)

- [ ] Testes de usabilidade
- [ ] Testes de acessibilidade (WCAG)
- [ ] Testes de performance (Lighthouse)
- [ ] Ajustes de UX
- [ ] Correção de bugs

### Fase 10: Deploy (1 dia)

- [ ] Build de produção
- [ ] Minificação de assets
- [ ] Testes em staging
- [ ] Deploy em produção
- [ ] Monitoramento

---

## 📊 Estimativas

**Tempo Total:** 22-31 dias úteis (~4-6 semanas)

**Prioridades:**
1. 🔴 **Alta:** Fases 1-4 (sistema de temas e login)
2. 🟡 **Média:** Fases 5-7 (componentes e responsividade)
3. 🟢 **Baixa:** Fases 8-10 (polish e deploy)

---

## ✅ Checklist de Verificação

### Antes de Começar

- [x] Backup de templates realizado
- [ ] Dependências Node.js instaladas
- [ ] Catppuccin plugin configurado
- [ ] Ambiente de desenvolvimento testado

### Durante Implementação

- [ ] Testar em múltiplos navegadores
- [ ] Testar em múltiplos dispositivos
- [ ] Validar acessibilidade
- [ ] Documentar mudanças
- [ ] Commitar frequentemente

### Antes do Deploy

- [ ] Build de produção testado
- [ ] Performance otimizada
- [ ] Sem erros de console
- [ ] Testes de usabilidade aprovados
- [ ] Documentação atualizada

---

## 📝 Notas Finais

> [!WARNING]
> **NÃO IMPLEMENTAR AINDA!**  
> Este documento é apenas para planejamento. Aguardar aprovação antes de iniciar qualquer fase.

> [!NOTE]
> **Manter Logo Atual:**  
> A logo em `static/img/logo/logo.png` será mantida no novo design.

> [!TIP]
> **Sugestão de Ordem:**  
> Começar pelas páginas de autenticação (login, password recovery) pois são as mais visíveis e impactantes para os usuários.

---

**Documento criado em:** 02/12/2025  
**Última atualização:** 02/12/2025  
**Versão:** 1.0  
**Status:** ✅ Completo - Aguardando aprovação
