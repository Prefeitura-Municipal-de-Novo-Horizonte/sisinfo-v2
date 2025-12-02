# 🚀 Guia de Implementação Avançada - SISInfo V2

**Complemento ao REDESIGN_VISUAL_GUIDE.md**  
**Data:** 02/12/2025  
**Objetivo:** Implementações avançadas com melhores práticas 2025

---

## 📋 Índice

1. [Remoção Completa do Flowbite](#remoção-completa-do-flowbite)
2. [Menu Retrátil Moderno](#menu-retrátil-moderno)
3. [Gráficos e Visualizações](#gráficos-e-visualizações)
4. [WebSockets e Tempo Real](#websockets-e-tempo-real)
5. [Docker Compose](#docker-compose)
6. [Melhores Práticas Django 2025](#melhores-práticas-django-2025)

---

## 🗑️ Remoção Completa do Flowbite

### Arquivos Afetados (12 total)

#### Templates com Flowbite CDN:

1. `templates/include/_css.html` - CSS CDN
2. `templates/include/_js.html` - JavaScript CDN
3. `authenticate/templates/login.html`
4. `authenticate/templates/password_reset.html`
5. `authenticate/templates/password_reset_done.html`
6. `authenticate/templates/password_reset_confirm_view.html`
7. `authenticate/templates/password_reset_complete.html`
8. `reports/templates/reports.html` - Datepicker

#### Configuração:

9. `tailwind.config.js` - Plugin Flowbite
10. `package.json` - Dependência Flowbite

### Componentes Flowbite em Uso

#### 1. Sidebar (Drawer)

**Atual (_nav.html):**
```html
<!-- Flowbite Drawer -->
<button data-drawer-target="logo-sidebar" data-drawer-toggle="logo-sidebar">
  <!-- Toggle button -->
</button>

<aside id="logo-sidebar" class="...">
  <!-- Sidebar content -->
</aside>
```

**Substituir por (Tailwind Nativo):**
```html
<!-- Alpine.js para interatividade -->
<div x-data="{ sidebarOpen: false }" class="relative">
  <!-- Toggle Button -->
  <button @click="sidebarOpen = !sidebarOpen" 
          class="inline-flex items-center p-2 text-sm rounded-lg sm:hidden">
    <svg class="w-6 h-6"><!-- Icon --></svg>
  </button>

  <!-- Sidebar -->
  <aside x-show="sidebarOpen"
         x-transition:enter="transition ease-out duration-300"
         x-transition:enter-start="-translate-x-full"
         x-transition:enter-end="translate-x-0"
         x-transition:leave="transition ease-in duration-300"
         x-transition:leave-start="translate-x-0"
         x-transition:leave-end="-translate-x-full"
         @click.away="sidebarOpen = false"
         class="fixed top-0 left-0 z-40 w-64 h-screen pt-20 
                transition-transform -translate-x-full sm:translate-x-0
                bg-white dark:bg-gray-800">
    <!-- Content -->
  </aside>

  <!-- Overlay para mobile -->
  <div x-show="sidebarOpen"
       x-transition:enter="transition-opacity ease-linear duration-300"
       x-transition:enter-start="opacity-0"
       x-transition:enter-end="opacity-100"
       x-transition:leave="transition-opacity ease-linear duration-300"
       x-transition:leave-start="opacity-100"
       x-transition:leave-end="opacity-0"
       @click="sidebarOpen = false"
       class="fixed inset-0 z-30 bg-gray-900 bg-opacity-50 sm:hidden">
  </div>
</div>
```

#### 2. Dropdown Menu

**Atual:**
```html
<button data-dropdown-toggle="dropdown-user">
  <!-- Button -->
</button>
<div id="dropdown-user" class="hidden ...">
  <!-- Dropdown content -->
</div>
```

**Substituir por:**
```html
<div x-data="{ dropdownOpen: false }" class="relative">
  <button @click="dropdownOpen = !dropdownOpen"
          class="flex text-sm bg-gray-800 rounded-full">
    <img src="..." alt="user photo">
  </button>

  <div x-show="dropdownOpen"
       x-transition:enter="transition ease-out duration-100"
       x-transition:enter-start="transform opacity-0 scale-95"
       x-transition:enter-end="transform opacity-100 scale-100"
       x-transition:leave="transition ease-in duration-75"
       x-transition:leave-start="transform opacity-100 scale-100"
       x-transition:leave-end="transform opacity-0 scale-95"
       @click.away="dropdownOpen = false"
       class="absolute right-0 z-50 mt-2 w-48 bg-white rounded-md shadow-lg">
    <!-- Dropdown items -->
  </div>
</div>
```

#### 3. Collapse (Accordion)

**Atual:**
```html
<button data-collapse-toggle="dropdown-setores">
  <!-- Button -->
</button>
<ul id="dropdown-setores" class="hidden">
  <!-- Items -->
</ul>
```

**Substituir por:**
```html
<div x-data="{ expanded: false }">
  <button @click="expanded = !expanded"
          class="flex items-center w-full p-2">
    <span>Setores</span>
    <svg :class="{'rotate-180': expanded}"
         class="w-3 h-3 transition-transform duration-200">
      <!-- Arrow icon -->
    </svg>
  </button>

  <ul x-show="expanded"
      x-transition:enter="transition ease-out duration-200"
      x-transition:enter-start="opacity-0 -translate-y-1"
      x-transition:enter-end="opacity-100 translate-y-0"
      x-transition:leave="transition ease-in duration-150"
      x-transition:leave-start="opacity-100 translate-y-0"
      x-transition:leave-end="opacity-0 -translate-y-1"
      class="py-2 space-y-2">
    <!-- Items -->
  </ul>
</div>
```

#### 4. Datepicker

**Atual (reports.html):**
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/flowbite/2.2.0/datepicker.min.js"></script>
```

**Substituir por Flatpickr:**
```html
<!-- CSS -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/flatpickr/dist/flatpickr.min.css">

<!-- JS -->
<script src="https://cdn.jsdelivr.net/npm/flatpickr"></script>

<!-- Inicialização -->
<script>
flatpickr("#date-input", {
  dateFormat: "d/m/Y",
  locale: "pt",
  altInput: true,
  altFormat: "j F, Y",
  theme: "dark" // ou "light"
});
</script>
```

### Plano de Migração

#### Passo 1: Instalar Alpine.js

**package.json:**
```json
{
  "dependencies": {
    "alpinejs": "^3.13.0",
    "flatpickr": "^4.6.13"
  }
}
```

**Ou via CDN (_js.html):**
```html
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
```

#### Passo 2: Remover Flowbite

**package.json:**
```json
{
  "dependencies": {
    "flowbite": "^2.0.0"  // REMOVER
  }
}
```

**tailwind.config.js:**
```javascript
module.exports = {
  content: [
    './templates/**/*.html',
    './*/templates/**/*.html',
    './node_modules/flowbite/**/*.js'  // REMOVER
  ],
  plugins: [
    require('flowbite/plugin')  // REMOVER
  ],
}
```

#### Passo 3: Atualizar Templates

1. Substituir `_nav.html` completo
2. Remover CDN de `_css.html` e `_js.html`
3. Atualizar páginas de autenticação
4. Substituir datepicker em `reports.html`

---

## 🎯 Menu Retrátil Moderno

### Opção 1: Sidebar Colapsável (Recomendado)

**Características:**
- Desktop: Sidebar fixa com opção de colapsar
- Tablet: Sidebar colapsável por padrão
- Mobile: Drawer overlay

**Implementação Completa:**

```html
<!-- _nav.html NOVO -->
{% load static %}

<div x-data="{ 
  sidebarOpen: window.innerWidth >= 768,
  sidebarCollapsed: false 
}" 
@resize.window="sidebarOpen = window.innerWidth >= 768"
class="min-h-screen bg-gray-50 dark:bg-gray-900">

  <!-- Top Navbar -->
  <nav class="fixed top-0 z-50 w-full bg-white border-b border-gray-200 dark:bg-gray-800 dark:border-gray-700">
    <div class="px-3 py-3 lg:px-5 lg:pl-3">
      <div class="flex items-center justify-between">
        <div class="flex items-center justify-start">
          <!-- Mobile toggle -->
          <button @click="sidebarOpen = !sidebarOpen"
                  class="inline-flex items-center p-2 text-sm text-gray-500 rounded-lg md:hidden hover:bg-gray-100">
            <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M3 5a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 15a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z"></path>
            </svg>
          </button>

          <!-- Desktop collapse toggle -->
          <button @click="sidebarCollapsed = !sidebarCollapsed"
                  class="hidden md:inline-flex items-center p-2 text-sm text-gray-500 rounded-lg hover:bg-gray-100">
            <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M3 5a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 10a1 1 0 011-1h6a1 1 0 110 2H4a1 1 0 01-1-1zM3 15a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z"></path>
            </svg>
          </button>

          <!-- Logo -->
          <a href="{% url 'dashboard:index' %}" class="flex ml-2 md:mr-24">
            <img src="{% static 'img/logo/logo.png' %}" class="h-8 mr-3" alt="Logo">
            <span x-show="!sidebarCollapsed" 
                  class="self-center text-xl font-semibold sm:text-2xl whitespace-nowrap dark:text-white">
              SISInfo V2
            </span>
          </a>
        </div>

        <!-- Right side (user menu, theme toggle) -->
        <div class="flex items-center gap-4">
          <!-- Theme Toggle -->
          <button @click="toggleTheme()" 
                  class="p-2 text-gray-500 rounded-lg hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-700">
            <svg x-show="!darkMode" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <!-- Moon icon -->
              <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z"></path>
            </svg>
            <svg x-show="darkMode" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <!-- Sun icon -->
              <path fill-rule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z"></path>
            </svg>
          </button>

          <!-- User Dropdown -->
          <div x-data="{ userMenuOpen: false }" class="relative">
            <button @click="userMenuOpen = !userMenuOpen"
                    class="flex text-sm bg-gray-800 rounded-full focus:ring-4 focus:ring-gray-300">
              <img class="w-8 h-8 rounded-full" src="{% static 'img/profile-empty.png' %}" alt="user">
            </button>

            <div x-show="userMenuOpen"
                 @click.away="userMenuOpen = false"
                 x-transition
                 class="absolute right-0 z-50 mt-2 w-48 bg-white rounded-md shadow-lg dark:bg-gray-700">
              <div class="px-4 py-3">
                <p class="text-sm text-gray-900 dark:text-white">{{ request.user.fullname }}</p>
                <p class="text-sm font-medium text-gray-500 truncate dark:text-gray-400">{{ request.user.email }}</p>
              </div>
              <ul class="py-1">
                <li>
                  <a href="{% url 'authenticate:profile' %}"
                     class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-600">
                    Perfil
                  </a>
                </li>
                <li>
                  <a href="{% url 'authenticate:change_password' %}"
                     class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-600">
                    Trocar Senha
                  </a>
                </li>
                <li>
                  <a href="{% url 'authenticate:logout' %}"
                     class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-600">
                    Sair
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  </nav>

  <!-- Sidebar -->
  <aside :class="sidebarCollapsed ? 'w-16' : 'w-64'"
         x-show="sidebarOpen"
         x-transition:enter="transition-transform duration-300"
         x-transition:leave="transition-transform duration-300"
         class="fixed top-0 left-0 z-40 h-screen pt-20 transition-all
                bg-white border-r border-gray-200 
                md:translate-x-0 -translate-x-full
                dark:bg-gray-800 dark:border-gray-700">
    
    <div class="h-full px-3 pb-4 overflow-y-auto">
      <ul class="space-y-2 font-medium">
        <!-- Dashboard -->
        <li>
          <a href="{% url 'dashboard:index' %}"
             class="flex items-center p-2 text-gray-900 rounded-lg dark:text-white hover:bg-gray-100 dark:hover:bg-gray-700 group">
            <svg class="w-5 h-5 text-gray-500 transition duration-75 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white" 
                 fill="currentColor" viewBox="0 0 22 21">
              <path d="M16.975 11H10V4.025a1 1 0 0 0-1.066-.998 8.5 8.5 0 1 0 9.039 9.039.999.999 0 0 0-1-1.066h.002Z"/>
              <path d="M12.5 0c-.157 0-.311.01-.565.027A1 1 0 0 0 11 1.02V10h8.975a1 1 0 0 0 1-.935c.013-.188.028-.374.028-.565A8.51 8.51 0 0 0 12.5 0Z"/>
            </svg>
            <span x-show="!sidebarCollapsed" class="ml-3">Dashboard</span>
          </a>
        </li>

        <!-- Setores (Collapsible) -->
        <li x-data="{ setoresOpen: false }">
          <button @click="setoresOpen = !setoresOpen"
                  class="flex items-center w-full p-2 text-gray-900 rounded-lg dark:text-white hover:bg-gray-100 dark:hover:bg-gray-700 group">
            <svg class="w-5 h-5 text-gray-500 transition duration-75 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white"
                 fill="currentColor" viewBox="0 0 18 18">
              <path d="M17 16h-1V2a1 1 0 1 0 0-2H2a1 1 0 0 0 0 2v14H1a1 1 0 0 0 0 2h16a1 1 0 0 0 0-2ZM5 4a1 1 0 0 1 1-1h1a1 1 0 0 1 1 1v1a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V4Zm0 5V8a1 1 0 0 1 1-1h1a1 1 0 0 1 1 1v1a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1Zm6 7H7v-3a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v3Zm2-7a1 1 0 0 1-1 1h-1a1 1 0 0 1-1-1V8a1 1 0 0 1 1-1h1a1 1 0 0 1 1 1v1Zm0-4a1 1 0 0 1-1 1h-1a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h1a1 1 0 0 1 1 1v1Z"/>
            </svg>
            <span x-show="!sidebarCollapsed" class="flex-1 ml-3 text-left whitespace-nowrap">Setores</span>
            <svg x-show="!sidebarCollapsed" 
                 :class="{'rotate-180': setoresOpen}"
                 class="w-3 h-3 transition-transform duration-200" 
                 fill="none" viewBox="0 0 10 6">
              <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m1 1 4 4 4-4"/>
            </svg>
          </button>

          <ul x-show="setoresOpen && !sidebarCollapsed"
              x-transition
              class="py-2 space-y-2">
            <li>
              <a href="{% url 'organizational_structure:diretorias' %}"
                 class="flex items-center w-full p-2 text-gray-900 rounded-lg pl-11 dark:text-white hover:bg-gray-100 dark:hover:bg-gray-700">
                Diretorias
              </a>
            </li>
            <li>
              <a href="{% url 'organizational_structure:setores' %}"
                 class="flex items-center w-full p-2 text-gray-900 rounded-lg pl-11 dark:text-white hover:bg-gray-100 dark:hover:bg-gray-700">
                Setores
              </a>
            </li>
          </ul>
        </li>

        <!-- Mais itens... -->
      </ul>
    </div>
  </aside>

  <!-- Overlay para mobile -->
  <div x-show="sidebarOpen && window.innerWidth < 768"
       @click="sidebarOpen = false"
       x-transition:enter="transition-opacity ease-linear duration-300"
       x-transition:enter-start="opacity-0"
       x-transition:enter-end="opacity-100"
       x-transition:leave="transition-opacity ease-linear duration-300"
       x-transition:leave-start="opacity-100"
       x-transition:leave-end="opacity-0"
       class="fixed inset-0 z-30 bg-gray-900 bg-opacity-50 md:hidden">
  </div>

  <!-- Main Content -->
  <div :class="sidebarCollapsed ? 'md:ml-16' : 'md:ml-64'"
       class="p-4 transition-all duration-300">
    <div class="p-4 border-2 border-gray-200 border-dashed rounded-lg dark:border-gray-700 mt-14">
      {% block content %}{% endblock %}
    </div>
  </div>
</div>

<script>
// Theme toggle
function toggleTheme() {
  const html = document.documentElement;
  const isDark = html.classList.contains('dark');
  
  if (isDark) {
    html.classList.remove('dark');
    localStorage.setItem('theme', 'light');
  } else {
    html.classList.add('dark');
    localStorage.setItem('theme', 'dark');
  }
}

// Inicializar tema
document.addEventListener('DOMContentLoaded', () => {
  const theme = localStorage.getItem('theme') || 
                (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  
  if (theme === 'dark') {
    document.documentElement.classList.add('dark');
  }
});
</script>
```

---

## 📊 Gráficos e Visualizações

### Biblioteca Recomendada: ApexCharts

**Por quê ApexCharts?**
- ✅ Moderno e responsivo
- ✅ Suporte nativo a dark mode
- ✅ Animações suaves
- ✅ Fácil integração com Django
- ✅ Gratuito e open-source

### Instalação

**package.json:**
```json
{
  "dependencies": {
    "apexcharts": "^3.45.0"
  }
}
```

**Ou via CDN:**
```html
<script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
```

### Exemplos de Implementação

#### 1. Gráfico de Linha (Laudos por Mês)

**Template (dashboard/index.html):**
```html
<div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
  <h3 class="text-lg font-semibold mb-4 dark:text-white">Laudos por Mês</h3>
  <div id="chart-laudos-mes"></div>
</div>

<script>
const chartLaudosMes = {
  series: [{
    name: 'Laudos',
    data: {{ laudos_por_mes|safe }}  // Do Django context
  }],
  chart: {
    type: 'line',
    height: 350,
    toolbar: {
      show: false
    },
    background: 'transparent'
  },
  colors: ['#89b4fa'],  // Catppuccin blue
  stroke: {
    curve: 'smooth',
    width: 3
  },
  xaxis: {
    categories: {{ meses|safe }},
    labels: {
      style: {
        colors: '#a6adc8'  // Catppuccin subtext
      }
    }
  },
  yaxis: {
    labels: {
      style: {
        colors: '#a6adc8'
      }
    }
  },
  grid: {
    borderColor: '#45475a',  // Catppuccin surface1
    strokeDashArray: 4
  },
  theme: {
    mode: localStorage.getItem('theme') || 'dark'
  }
};

const chart = new ApexCharts(document.querySelector("#chart-laudos-mes"), chartLaudosMes);
chart.render();
</script>
```

**View (dashboard/views.py):**
```python
from django.db.models import Count
from django.db.models.functions import TruncMonth
import json

def index(request):
    # Laudos por mês (últimos 6 meses)
    laudos_stats = Report.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=180)
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    meses = [stat['month'].strftime('%b/%y') for stat in laudos_stats]
    laudos_por_mes = [stat['count'] for stat in laudos_stats]
    
    context = {
        'meses': json.dumps(meses),
        'laudos_por_mes': json.dumps(laudos_por_mes),
    }
    
    return render(request, 'index.html', context)
```

#### 2. Gráfico de Pizza (Status dos Laudos)

```html
<div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
  <h3 class="text-lg font-semibold mb-4 dark:text-white">Status dos Laudos</h3>
  <div id="chart-status-laudos"></div>
</div>

<script>
const chartStatusLaudos = {
  series: {{ status_counts|safe }},
  chart: {
    type: 'donut',
    height: 350,
    background: 'transparent'
  },
  labels: {{ status_labels|safe }},
  colors: ['#a6e3a1', '#f9e2af', '#f38ba8'],  // Catppuccin green, yellow, red
  legend: {
    position: 'bottom',
    labels: {
      colors: '#cdd6f4'  // Catppuccin text
    }
  },
  dataLabels: {
    enabled: true,
    style: {
      colors: ['#1e1e2e']  // Catppuccin base
    }
  },
  theme: {
    mode: localStorage.getItem('theme') || 'dark'
  }
};

const chartStatus = new ApexCharts(document.querySelector("#chart-status-laudos"), chartStatusLaudos);
chartStatus.render();
</script>
```

#### 3. Gráfico de Barras (Materiais Mais Usados)

```html
<div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
  <h3 class="text-lg font-semibold mb-4 dark:text-white">Top 10 Materiais</h3>
  <div id="chart-top-materiais"></div>
</div>

<script>
const chartTopMateriais = {
  series: [{
    name: 'Quantidade',
    data: {{ materiais_qtd|safe }}
  }],
  chart: {
    type: 'bar',
    height: 400,
    toolbar: {
      show: false
    },
    background: 'transparent'
  },
  plotOptions: {
    bar: {
      borderRadius: 8,
      horizontal: true,
      distributed: true
    }
  },
  colors: ['#89b4fa', '#cba6f7', '#f5c2e7', '#f38ba8', '#fab387', 
           '#f9e2af', '#a6e3a1', '#94e2d5', '#89dceb', '#74c7ec'],
  xaxis: {
    categories: {{ materiais_nomes|safe }},
    labels: {
      style: {
        colors: '#a6adc8'
      }
    }
  },
  yaxis: {
    labels: {
      style: {
        colors: '#a6adc8'
      }
    }
  },
  grid: {
    borderColor: '#45475a'
  },
  theme: {
    mode: localStorage.getItem('theme') || 'dark'
  },
  legend: {
    show: false
  }
};

const chartMateriais = new ApexCharts(document.querySelector("#chart-top-materiais"), chartTopMateriais);
chartMateriais.render();
</script>
```

### Atualização Dinâmica de Tema

```javascript
// Adicionar ao script de toggle de tema
function updateChartsTheme(theme) {
  // Atualizar todos os gráficos
  if (typeof chart !== 'undefined') {
    chart.updateOptions({
      theme: { mode: theme }
    });
  }
  if (typeof chartStatus !== 'undefined') {
    chartStatus.updateOptions({
      theme: { mode: theme }
    });
  }
  if (typeof chartMateriais !== 'undefined') {
    chartMateriais.updateOptions({
      theme: { mode: theme }
    });
  }
}

// Modificar toggleTheme()
function toggleTheme() {
  const html = document.documentElement;
  const isDark = html.classList.contains('dark');
  const newTheme = isDark ? 'light' : 'dark';
  
  if (isDark) {
    html.classList.remove('dark');
  } else {
    html.classList.add('dark');
  }
  
  localStorage.setItem('theme', newTheme);
  updateChartsTheme(newTheme);
}
```

---

## ⚡ WebSockets e Tempo Real

### Casos de Uso Identificados

1. **Notificações em Tempo Real**
   - Novo laudo criado
   - Laudo atualizado
   - Material adicionado

2. **Dashboard ao Vivo**
   - Atualização de estatísticas
   - Gráficos em tempo real

3. **Colaboração**
   - Múltiplos usuários editando

### Implementação com Django Channels

#### Instalação

**requirements.txt:**
```txt
channels==4.0.0
channels-redis==4.1.0
daphne==4.0.0
```

**Instalar:**
```bash
pip install channels channels-redis daphne
```

#### Configuração

**settings.py:**
```python
INSTALLED_APPS = [
    'daphne',  # Adicionar no topo
    # ... outros apps
    'channels',
]

ASGI_APPLICATION = 'core.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
```

**core/asgi.py:**
```python
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')

django_asgi_app = get_asgi_application()

from reports import routing as reports_routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                reports_routing.websocket_urlpatterns
            )
        )
    ),
})
```

#### Consumer (reports/consumers.py)

```python
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Report

class ReportConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'reports_updates'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'get_stats':
            stats = await self.get_report_stats()
            await self.send(text_data=json.dumps({
                'type': 'stats_update',
                'data': stats
            }))
    
    # Receive message from room group
    async def report_created(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'report_created',
            'report': event['report']
        }))
    
    async def report_updated(self, event):
        await self.send(text_data=json.dumps({
            'type': 'report_updated',
            'report': event['report']
        }))
    
    @database_sync_to_async
    def get_report_stats(self):
        from django.db.models import Count
        
        stats = Report.objects.values('status').annotate(
            count=Count('id')
        )
        
        return {
            'total': Report.objects.count(),
            'by_status': list(stats)
        }
```

#### Routing (reports/routing.py)

```python
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/reports/$', consumers.ReportConsumer.as_asgi()),
]
```

#### Signal para Enviar Notificações

**reports/signals.py:**
```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Report

@receiver(post_save, sender=Report)
def report_saved(sender, instance, created, **kwargs):
    channel_layer = get_channel_layer()
    
    event_type = 'report_created' if created else 'report_updated'
    
    async_to_sync(channel_layer.group_send)(
        'reports_updates',
        {
            'type': event_type,
            'report': {
                'id': instance.id,
                'number': instance.number_report,
                'status': instance.get_status_display(),
                'created_at': instance.created_at.isoformat(),
            }
        }
    )
```

**reports/apps.py:**
```python
from django.apps import AppConfig

class ReportsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reports'
    
    def ready(self):
        import reports.signals
```

#### Frontend (Template)

```html
<!-- dashboard/index.html -->
<div id="notifications" class="fixed top-20 right-4 z-50 space-y-2">
  <!-- Notificações aparecem aqui -->
</div>

<script>
// Conectar ao WebSocket
const reportSocket = new WebSocket(
    'ws://' + window.location.host + '/ws/reports/'
);

reportSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    
    if (data.type === 'report_created') {
        showNotification('Novo laudo criado: ' + data.report.number, 'success');
        updateDashboard();
    } else if (data.type === 'report_updated') {
        showNotification('Laudo atualizado: ' + data.report.number, 'info');
        updateDashboard();
    } else if (data.type === 'stats_update') {
        updateStats(data.data);
    }
};

reportSocket.onclose = function(e) {
    console.error('WebSocket fechado inesperadamente');
    // Reconectar após 5 segundos
    setTimeout(() => {
        location.reload();
    }, 5000);
};

function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `p-4 rounded-lg shadow-lg ${
        type === 'success' ? 'bg-green-500' : 'bg-blue-500'
    } text-white transform transition-all duration-300`;
    notification.textContent = message;
    
    document.getElementById('notifications').appendChild(notification);
    
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

function updateDashboard() {
    // Solicitar estatísticas atualizadas
    reportSocket.send(JSON.stringify({
        'type': 'get_stats'
    }));
}

function updateStats(stats) {
    // Atualizar gráficos com novos dados
    if (typeof chart !== 'undefined') {
        // Atualizar dados do gráfico
    }
}
</script>
```

#### Docker Compose com Redis

**docker-compose.yaml:**
```yaml
services:
  db:
    image: postgres:14-alpine3.20
    restart: always
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: postgres
    ports:
      - 5432:5432
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    restart: always
    ports:
      - 6379:6379
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

---

## 🐳 Docker Compose

### Configuração Completa de Desenvolvimento

**docker-compose.yaml (Expandido):**
```yaml
version: '3.8'

services:
  db:
    image: postgres:14-alpine3.20
    container_name: sisinfo_db
    restart: always
    environment:
      POSTGRES_USER: ${DB_USER:-postgres}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-postgres}
      POSTGRES_DB: ${DB_NAME:-sisinfo_db}
    ports:
      - "${DB_PORT:-5432}:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backup:/backup  # Para restore de backups
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: sisinfo_redis
    restart: always
    ports:
      - "${REDIS_PORT:-6379}:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  web:
    build: .
    container_name: sisinfo_web
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:
```

### Dockerfile

```dockerfile
FROM python:3.12-slim

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copiar projeto
COPY . .

# Coletar arquivos estáticos
RUN python manage.py collectstatic --noinput || true

# Expor porta
EXPOSE 8000

# Comando padrão
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

### Scripts de Gerenciamento

**scripts/docker-dev.sh:**
```bash
#!/bin/bash

# Iniciar ambiente de desenvolvimento
docker-compose up -d

# Aguardar serviços
echo "Aguardando serviços..."
sleep 5

# Executar migrações
docker-compose exec web python manage.py migrate

# Criar superuser (se não existir)
docker-compose exec web python manage.py shell -c "
from authenticate.models import ProfessionalUser
if not ProfessionalUser.objects.filter(email='admin@example.com').exists():
    ProfessionalUser.objects.create_superuser(
        email='admin@example.com',
        first_name='Admin',
        last_name='System',
        password='admin123'
    )
    print('Superuser criado!')
"

echo "Ambiente pronto! Acesse http://localhost:8000"
```

**scripts/backup-db.sh:**
```bash
#!/bin/bash

# Backup do banco de dados
BACKUP_FILE="backup/backup_$(date +%d%m%Y_%H%M%S).sql"

docker-compose exec -T db pg_dump -U postgres sisinfo_db > "$BACKUP_FILE"

echo "Backup salvo em: $BACKUP_FILE"
```

**scripts/restore-db.sh:**
```bash
#!/bin/bash

if [ -z "$1" ]; then
    echo "Uso: ./restore-db.sh <arquivo_backup.sql>"
    exit 1
fi

BACKUP_FILE=$1

# Restaurar backup
docker-compose exec -T db psql -U postgres sisinfo_db < "$BACKUP_FILE"

echo "Backup restaurado!"
```

### Uso do Backup Atualizado

**Restaurar backup JSON:**
```bash
# Copiar backup para container
docker cp backup/backup_atualizado_02122025.json sisinfo_web:/app/

# Restaurar dados
docker-compose exec web python manage.py loaddata backup_atualizado_02122025.json

echo "Dados restaurados!"
```

---

## 🏆 Melhores Práticas Django 2025

### 1. Estrutura de Projeto

```
sisinfo-v2/
├── core/                    # Configurações
│   ├── settings/
│   │   ├── base.py         # Configurações base
│   │   ├── development.py  # Desenvolvimento
│   │   └── production.py   # Produção
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── apps/                    # Apps do projeto
│   ├── authenticate/
│   ├── reports/
│   └── ...
├── static/                  # Arquivos estáticos
│   ├── css/
│   ├── js/
│   └── img/
├── templates/               # Templates globais
├── tests/                   # Testes
├── docs/                    # Documentação
├── scripts/                 # Scripts úteis
└── docker-compose.yaml
```

### 2. Performance

**Usar select_related e prefetch_related:**
```python
# Ruim
reports = Report.objects.all()
for report in reports:
    print(report.sector.name)  # N+1 queries

# Bom
reports = Report.objects.select_related('sector').all()
for report in reports:
    print(report.sector.name)  # 1 query
```

**Cache com Redis:**
```python
from django.core.cache import cache

def get_dashboard_stats():
    stats = cache.get('dashboard_stats')
    
    if stats is None:
        stats = {
            'total_reports': Report.objects.count(),
            'total_materials': Material.objects.count(),
            # ...
        }
        cache.set('dashboard_stats', stats, 300)  # 5 minutos
    
    return stats
```

### 3. Segurança

**settings.py (Produção):**
```python
# HTTPS
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# HSTS
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Outros
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
```

### 4. Testes

**Estrutura de Testes:**
```python
# tests/test_reports.py
from django.test import TestCase, Client
from django.urls import reverse
from authenticate.models import ProfessionalUser
from reports.models import Report

class ReportTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = ProfessionalUser.objects.create_user(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='testpass123'
        )
        self.client.login(email='test@example.com', password='testpass123')
    
    def test_create_report(self):
        response = self.client.post(reverse('reports:register_report'), {
            'sector': 1,
            'employee': 'João Silva',
            'justification': 'Teste',
            # ...
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Report.objects.count(), 1)
    
    def test_report_list_view(self):
        response = self.client.get(reverse('reports:reports'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Laudos')
```

**Executar testes:**
```bash
# Todos os testes
python manage.py test

# App específico
python manage.py test reports

# Com coverage
coverage run --source='.' manage.py test
coverage report
```

---

## ✅ Checklist de Implementação

### Fase 1: Remoção de Flowbite (2-3 dias)

- [ ] Instalar Alpine.js
- [ ] Remover Flowbite do package.json
- [ ] Remover Flowbite do tailwind.config.js
- [ ] Atualizar _nav.html com novo sidebar
- [ ] Atualizar _css.html e _js.html
- [ ] Substituir datepicker por Flatpickr
- [ ] Testar todos os componentes interativos
- [ ] Verificar responsividade

### Fase 2: Menu Retrátil (1-2 dias)

- [ ] Implementar sidebar colapsável
- [ ] Adicionar animações suaves
- [ ] Configurar comportamento mobile/desktop
- [ ] Adicionar persistência de estado
- [ ] Testar em diferentes resoluções

### Fase 3: Gráficos (2-3 dias)

- [ ] Instalar ApexCharts
- [ ] Criar gráfico de laudos por mês
- [ ] Criar gráfico de status
- [ ] Criar gráfico de materiais
- [ ] Integrar com tema claro/escuro
- [ ] Adicionar dados reais das views
- [ ] Otimizar queries

### Fase 4: WebSockets (3-4 dias)

- [ ] Instalar Django Channels
- [ ] Configurar Redis
- [ ] Criar consumers
- [ ] Implementar signals
- [ ] Adicionar notificações frontend
- [ ] Testar conexões
- [ ] Implementar reconexão automática

### Fase 5: Docker (1-2 dias)

- [ ] Expandir docker-compose.yaml
- [ ] Criar Dockerfile
- [ ] Criar scripts de gerenciamento
- [ ] Testar backup/restore
- [ ] Documentar uso

### Fase 6: Testes e Otimização (2-3 dias)

- [ ] Escrever testes unitários
- [ ] Escrever testes de integração
- [ ] Otimizar queries (select_related, prefetch_related)
- [ ] Implementar cache
- [ ] Verificar segurança
- [ ] Documentar código

---

## 📚 Referências e Recursos

### Documentação Oficial

- [Django 5.2](https://docs.djangoproject.com/en/5.2/)
- [Tailwind CSS 3.3](https://tailwindcss.com/docs)
- [Alpine.js 3.x](https://alpinejs.dev/)
- [ApexCharts](https://apexcharts.com/docs/)
- [Django Channels](https://channels.readthedocs.io/)

### Exemplos de Dashboards Modernos

1. **Vercel Dashboard** - Menu lateral minimalista
2. **GitHub** - Navegação responsiva
3. **Linear** - Animações suaves
4. **Notion** - Sidebar colapsável
5. **Tailwind UI** - Componentes prontos

### Paleta Catppuccin

- [Catppuccin](https://github.com/catppuccin/catppuccin)
- [Tailwind Plugin](https://github.com/catppuccin/tailwindcss)

---

## 🎯 Próximos Passos

1. **Revisar este documento** com a equipe
2. **Priorizar funcionalidades** (gráficos vs WebSockets)
3. **Definir cronograma** de implementação
4. **Configurar ambiente** de desenvolvimento
5. **Iniciar Fase 1** (Remoção de Flowbite)

---

**Documento criado em:** 02/12/2025  
**Última atualização:** 02/12/2025  
**Versão:** 2.0 - Expandida  
**Status:** ✅ Completo - Pronto para implementação
