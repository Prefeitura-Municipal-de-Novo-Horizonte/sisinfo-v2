# UI Guide - SISInfo V2

Padrões de interface, componentes e estilos visuais.

**Última atualização:** 2025-12-28

---

## Stack Frontend

| Tecnologia | Versão | Uso |
|------------|--------|-----|
| TailwindCSS | 3.4 | Estilização |
| Alpine.js | 3.x | Reatividade/Estado |
| HTMX | 1.9 | Requisições AJAX |
| ApexCharts | - | Gráficos |

---

## Cores

### Cor Principal (Brand)

```css
brand: #1D4ED8 (azul)
```

| Variante | Hex | Uso |
|----------|-----|-----|
| `brand-50` | #eff6ff | Backgrounds sutis |
| `brand-100` | #dbeafe | Hover light |
| `brand-500` | #3b82f6 | Texto secundário |
| `brand-600` | #2563eb | Botões hover |
| `brand-700` | #1d4ed8 | **Botões, links** |
| `brand-800` | #1e40af | Pressed state |
| `brand-900` | #1e3a8a | Texto escuro |

### Cores de Status

| Status | Cor | Classes |
|--------|-----|---------|
| Sucesso | Verde | `bg-green-100 text-green-800` |
| Erro | Vermelho | `bg-red-100 text-red-800` |
| Aviso | Amarelo | `bg-yellow-100 text-yellow-800` |
| Info | Azul | `bg-blue-100 text-blue-800` |

### Dark Mode

| Elemento | Light | Dark |
|----------|-------|------|
| Background | `bg-gray-50` | `dark:bg-slate-900` |
| Card | `bg-white` | `dark:bg-slate-800` |
| Texto | `text-gray-900` | `dark:text-white` |
| Texto secundário | `text-gray-600` | `dark:text-gray-400` |
| Border | `border-gray-200` | `dark:border-slate-700` |

---

## Tipografia

### Tamanhos

| Uso | Classes |
|-----|---------|
| Título página | `text-2xl font-bold` |
| Título seção | `text-xl font-semibold` |
| Título card | `text-lg font-medium` |
| Texto normal | `text-base` |
| Texto pequeno | `text-sm` |
| Caption | `text-xs text-gray-500` |

---

## Componentes

### Botões

```html
<!-- Primário -->
<button class="px-4 py-2 bg-brand-700 text-white rounded-lg hover:bg-brand-600 
               transition-colors font-medium">
    Salvar
</button>

<!-- Secundário -->
<button class="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 
               dark:bg-slate-700 dark:text-white dark:hover:bg-slate-600 
               transition-colors font-medium">
    Cancelar
</button>

<!-- Danger -->
<button class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-500 
               transition-colors font-medium">
    Excluir
</button>

<!-- Ghost/Link -->
<button class="px-4 py-2 text-brand-700 hover:bg-brand-50 rounded-lg 
               dark:text-brand-400 dark:hover:bg-slate-800 transition-colors">
    Ver mais
</button>
```

### Cards

```html
<div class="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-gray-200 
            dark:border-slate-700 p-6">
    <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
        Título do Card
    </h3>
    <p class="text-gray-600 dark:text-gray-400">
        Conteúdo do card...
    </p>
</div>
```

### Formulários

```html
<!-- Input -->
<div class="mb-4">
    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
        Nome
    </label>
    <input type="text" 
           class="w-full px-3 py-2 border border-gray-300 rounded-lg 
                  focus:ring-2 focus:ring-brand-500 focus:border-brand-500
                  dark:bg-slate-700 dark:border-slate-600 dark:text-white">
</div>

<!-- Select -->
<select class="w-full px-3 py-2 border border-gray-300 rounded-lg 
               focus:ring-2 focus:ring-brand-500 focus:border-brand-500
               dark:bg-slate-700 dark:border-slate-600 dark:text-white">
    <option>Opção 1</option>
</select>
```

### Tabelas

```html
<div class="overflow-x-auto">
    <table class="w-full">
        <thead class="bg-gray-50 dark:bg-slate-700">
            <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 
                           dark:text-gray-400 uppercase tracking-wider">
                    Coluna
                </th>
            </tr>
        </thead>
        <tbody class="divide-y divide-gray-200 dark:divide-slate-700">
            <tr class="hover:bg-gray-50 dark:hover:bg-slate-700/50">
                <td class="px-4 py-3 text-sm text-gray-900 dark:text-white">
                    Valor
                </td>
            </tr>
        </tbody>
    </table>
</div>
```

### Badges/Tags

```html
<!-- Status -->
<span class="px-2 py-1 text-xs font-medium rounded-full 
             bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">
    Ativo
</span>

<span class="px-2 py-1 text-xs font-medium rounded-full 
             bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400">
    Pendente
</span>

<span class="px-2 py-1 text-xs font-medium rounded-full 
             bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400">
    Cancelado
</span>
```

---

## Alpine.js Patterns

### Toggle

```html
<div x-data="{ open: false }">
    <button @click="open = !open">Toggle</button>
    <div x-show="open" x-transition>Conteúdo</div>
</div>
```

### Dark Mode

```html
<div x-data="{ 
    darkMode: localStorage.getItem('theme') === 'dark',
    toggleTheme() {
        this.darkMode = !this.darkMode;
        localStorage.setItem('theme', this.darkMode ? 'dark' : 'light');
        document.documentElement.classList.toggle('dark', this.darkMode);
    }
}">
    <button @click="toggleTheme()">
        <span x-show="!darkMode">🌙</span>
        <span x-show="darkMode">☀️</span>
    </button>
</div>
```

### Loading State

```html
<button x-data="{ loading: false }" 
        @click="loading = true; $el.form.submit()"
        :disabled="loading"
        class="btn-primary">
    <span x-show="!loading">Salvar</span>
    <span x-show="loading">Salvando...</span>
</button>
```

---

## HTMX Patterns

### Load Content

```html
<div hx-get="/api/items/" 
     hx-trigger="load"
     hx-swap="innerHTML">
    Carregando...
</div>
```

### Form Submit

```html
<form hx-post="/api/create/"
      hx-swap="outerHTML"
      hx-target="#result">
    <!-- campos -->
    <button type="submit">Salvar</button>
</form>
```

### Infinite Scroll

```html
<div hx-get="/api/items/?page=2"
     hx-trigger="revealed"
     hx-swap="afterend">
    Carregando mais...
</div>
```

---

## Layout

### Container

```html
<div class="container mx-auto px-4 sm:px-6 lg:px-8">
    <!-- Conteúdo -->
</div>
```

### Grid

```html
<!-- 2 colunas em desktop -->
<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
    <div>Coluna 1</div>
    <div>Coluna 2</div>
</div>

<!-- Cards responsivos -->
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
    <!-- Cards -->
</div>
```

---

## Ícones

Usar Material Symbols ou ícones SVG inline:

```html
<!-- Material Symbols (se configurado) -->
<span class="material-symbols-outlined">home</span>

<!-- SVG Inline -->
<svg class="w-5 h-5 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
    <!-- path -->
</svg>
```

---

## Responsividade

| Breakpoint | Prefixo | Uso |
|------------|---------|-----|
| < 640px | (default) | Mobile |
| ≥ 640px | `sm:` | Mobile landscape |
| ≥ 768px | `md:` | Tablet |
| ≥ 1024px | `lg:` | Desktop |
| ≥ 1280px | `xl:` | Desktop grande |

---

**Responsável:** Diretoria de TI  
**Contato:** ti@novohorizonte.sp.gov.br
