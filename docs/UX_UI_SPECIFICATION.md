# 📐 Especificação Detalhada de UX/UI - SISInfo V2

**Data:** 03/12/2025  
**Objetivo:** Detalhar melhorias de UX/UI para cada página do sistema  
**Status:** 📋 Planejamento - Aguardando aprovação

---

## 📋 Índice

1. [Dashboard (Página Principal)](#dashboard-página-principal)
2. [Laudos (Reports)](#laudos-reports)
3. [Licitações (Bidding)](#licitações-bidding)
4. [Fornecedores (Suppliers)](#fornecedores-suppliers)
5. [Materiais](#materiais)
6. [Setores e Diretorias](#setores-e-diretorias)
7. [Usuários (Admin)](#usuários-admin)
8. [Componentes Globais](#componentes-globais)

---

## 🏠 Dashboard (Página Principal)

### 📊 Estado Atual
- 7 cards simples com contadores
- Sem gráficos
- Sem calendário
- Layout poluído com informações pouco úteis

### ✨ Novo Design

#### Layout Proposto
```
┌─────────────────────────────────────────────────────────┐
│  📊 Dashboard                              [Filtro: ▼]  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │
│  │ 📝 Laudos    │ │ 📦 Materiais │ │ 🏢 Setores   │   │
│  │    125       │ │     450      │ │     12       │   │
│  │  ↑ +15%     │ │  ↑ +8%      │ │  →  0%      │   │
│  └──────────────┘ └──────────────┘ └──────────────┘   │
│                                                         │
│  ┌────────────────────────────────┐ ┌────────────────┐ │
│  │ 📈 Laudos por Setor            │ │ 📅 Calendário  │ │
│  │                                │ │                │ │
│  │ [Filtro: 1 ano ▼]             │ │  Dez 2025      │ │
│  │                                │ │                │ │
│  │  [Gráfico de Barras]          │ │  D S T Q Q S S │ │
│  │                                │ │  1 2 3 4 5 6 7 │ │
│  │                                │ │  8 9...        │ │
│  └────────────────────────────────┘ └────────────────┘ │
│                                                         │
│  ┌────────────────────────────────────────────────────┐ │
│  │ 🏆 Top 10 Materiais Mais Pedidos                   │ │
│  │                                                     │ │
│  │ [Filtro: 1 ano ▼]                                  │ │
│  │                                                     │ │
│  │  [Gráfico de Barras Horizontal]                    │ │
│  │                                                     │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

#### 1. Cards de Métricas (Top)
**Manter apenas 3 cards essenciais:**

```html
<div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
  <!-- Card 1: Laudos -->
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
    <div class="flex items-center justify-between">
      <div>
        <p class="text-sm text-gray-500 dark:text-gray-400">Laudos Emitidos</p>
        <h3 class="text-3xl font-bold text-gray-900 dark:text-white mt-1">
          {{ total_reports }}
        </h3>
        <p class="text-sm text-green-600 mt-2">
          <span class="inline-flex items-center">
            <svg class="w-4 h-4 mr-1">↑</svg>
            +15% este mês
          </span>
        </p>
      </div>
      <div class="p-3 bg-blue-100 dark:bg-blue-900 rounded-full">
        <svg class="w-8 h-8 text-blue-600 dark:text-blue-300">📝</svg>
      </div>
    </div>
  </div>

  <!-- Card 2: Materiais -->
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
    <!-- Similar structure -->
  </div>

  <!-- Card 3: Setores -->
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
    <!-- Similar structure -->
  </div>
</div>
```

**Remover:**
- ❌ "Meus Atendimentos" (sempre 0)
- ❌ "Laudos Responsável" (redundante)
- ❌ "Meus Laudos" (redundante)
- ❌ "Ordem de Serviços" (sempre 0)
- ❌ "Diretorias" (pouco relevante)

#### 2. Gráfico: Laudos por Setor

```html
<div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-8">
  <div class="flex items-center justify-between mb-6">
    <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
      Laudos Emitidos por Setor
    </h3>
    
    <!-- Filtro Temporal -->
    <select id="periodo-laudos" class="rounded-lg border-gray-300 dark:border-gray-600">
      <option value="1m">Último mês</option>
      <option value="3m">Trimestral</option>
      <option value="6m">Semestral</option>
      <option value="1y" selected>1 ano</option>
      <option value="2y">2 anos</option>
      <option value="3y">3 anos</option>
    </select>
  </div>
  
  <div id="chart-laudos-setor" class="h-80"></div>
</div>
```

**JavaScript (ApexCharts):**
```javascript
const chartLaudosSetor = {
  series: [{
    name: 'Laudos',
    data: {{ laudos_por_setor|safe }}  // Do Django
  }],
  chart: {
    type: 'bar',
    height: 320,
    toolbar: { show: false }
  },
  plotOptions: {
    bar: {
      borderRadius: 8,
      horizontal: false,
      columnWidth: '60%',
      distributed: true
    }
  },
  colors: ['#89b4fa', '#cba6f7', '#f5c2e7', '#f38ba8', '#fab387', 
           '#f9e2af', '#a6e3a1', '#94e2d5', '#89dceb', '#74c7ec'],
  xaxis: {
    categories: {{ setores_nomes|safe }},
    labels: {
      rotate: -45,
      style: { colors: '#a6adc8' }
    }
  },
  yaxis: {
    title: { text: 'Quantidade de Laudos' },
    labels: { style: { colors: '#a6adc8' } }
  },
  theme: {
    mode: localStorage.getItem('theme') || 'dark'
  },
  legend: { show: false }
};

const chart = new ApexCharts(document.querySelector("#chart-laudos-setor"), chartLaudosSetor);
chart.render();

// Atualizar ao mudar período
document.getElementById('periodo-laudos').addEventListener('change', function() {
  fetch(`/dashboard/laudos-setor/?periodo=${this.value}`)
    .then(res => res.json())
    .then(data => {
      chart.updateSeries([{
        name: 'Laudos',
        data: data.valores
      }]);
      chart.updateOptions({
        xaxis: { categories: data.setores }
      });
    });
});
```

**View (dashboard/views.py):**
```python
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from datetime import datetime, timedelta
import json

def index(request):
    # Laudos por setor (último ano por padrão)
    periodo = request.GET.get('periodo', '1y')
    
    # Calcular data inicial
    hoje = datetime.now()
    if periodo == '1m':
        data_inicial = hoje - timedelta(days=30)
    elif periodo == '3m':
        data_inicial = hoje - timedelta(days=90)
    elif periodo == '6m':
        data_inicial = hoje - timedelta(days=180)
    elif periodo == '1y':
        data_inicial = hoje - timedelta(days=365)
    elif periodo == '2y':
        data_inicial = hoje - timedelta(days=730)
    else:  # 3y
        data_inicial = hoje - timedelta(days=1095)
    
    # Query
    laudos_stats = Report.objects.filter(
        created_at__gte=data_inicial
    ).values('sector__name').annotate(
        count=Count('id')
    ).order_by('-count')[:10]  # Top 10 setores
    
    setores_nomes = [stat['sector__name'] or 'Sem setor' for stat in laudos_stats]
    laudos_valores = [stat['count'] for stat in laudos_stats]
    
    context = {
        'setores_nomes': json.dumps(setores_nomes),
        'laudos_por_setor': json.dumps(laudos_valores),
        # ... outros dados
    }
    
    return render(request, 'index.html', context)

# API para AJAX
def laudos_setor_api(request):
    periodo = request.GET.get('periodo', '1y')
    # ... mesma lógica acima
    return JsonResponse({
        'setores': setores_nomes,
        'valores': laudos_valores
    })
```

#### 3. Gráfico: Top 10 Materiais Mais Pedidos

```html
<div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-8">
  <div class="flex items-center justify-between mb-6">
    <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
      🏆 Top 10 Materiais Mais Pedidos
    </h3>
    
    <select id="periodo-materiais" class="rounded-lg border-gray-300">
      <option value="1m">Último mês</option>
      <option value="3m">Trimestral</option>
      <option value="6m">Semestral</option>
      <option value="1y" selected>1 ano</option>
      <option value="2y">2 anos</option>
      <option value="3y">3 anos</option>
    </select>
  </div>
  
  <div id="chart-top-materiais" class="h-96"></div>
</div>
```

**JavaScript:**
```javascript
const chartTopMateriais = {
  series: [{
    name: 'Quantidade Pedida',
    data: {{ materiais_qtd|safe }}
  }],
  chart: {
    type: 'bar',
    height: 384,
    toolbar: { show: false }
  },
  plotOptions: {
    bar: {
      borderRadius: 8,
      horizontal: true,  // Barras horizontais
      distributed: true,
      barHeight: '70%'
    }
  },
  colors: ['#89b4fa', '#cba6f7', '#f5c2e7', '#f38ba8', '#fab387', 
           '#f9e2af', '#a6e3a1', '#94e2d5', '#89dceb', '#74c7ec'],
  xaxis: {
    title: { text: 'Quantidade' },
    labels: { style: { colors: '#a6adc8' } }
  },
  yaxis: {
    labels: {
      style: { colors: '#a6adc8' },
      maxWidth: 200
    }
  },
  dataLabels: {
    enabled: true,
    style: { colors: ['#1e1e2e'] }
  },
  theme: {
    mode: localStorage.getItem('theme') || 'dark'
  },
  legend: { show: false }
};
```

**View:**
```python
def index(request):
    # Top 10 materiais
    periodo = request.GET.get('periodo', '1y')
    data_inicial = calcular_data_inicial(periodo)
    
    materiais_stats = MaterialReport.objects.filter(
        report__created_at__gte=data_inicial
    ).values('material_bidding__material__name').annotate(
        total=Sum('quantity')
    ).order_by('-total')[:10]
    
    materiais_nomes = [stat['material_bidding__material__name'] for stat in materiais_stats]
    materiais_qtd = [stat['total'] for stat in materiais_stats]
    
    context = {
        'materiais_nomes': json.dumps(materiais_nomes),
        'materiais_qtd': json.dumps(materiais_qtd),
    }
```

#### 4. Calendário

```html
<div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
  <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
    📅 Calendário de Eventos
  </h3>
  
  <div id="calendar"></div>
</div>
```

**Usar FullCalendar:**
```javascript
// npm install @fullcalendar/core @fullcalendar/daygrid @fullcalendar/interaction

import { Calendar } from '@fullcalendar/core';
import dayGridPlugin from '@fullcalendar/daygrid';
import interactionPlugin from '@fullcalendar/interaction';

const calendar = new Calendar(document.getElementById('calendar'), {
  plugins: [dayGridPlugin, interactionPlugin],
  initialView: 'dayGridMonth',
  locale: 'pt-br',
  headerToolbar: {
    left: 'prev,next today',
    center: 'title',
    right: 'dayGridMonth,dayGridWeek'
  },
  events: '/dashboard/eventos/',  // API endpoint
  eventClick: function(info) {
    // Abrir modal com detalhes
    showEventModal(info.event);
  },
  dateClick: function(info) {
    // Criar novo evento
    showCreateEventModal(info.date);
  }
});

calendar.render();
```

**API de Eventos:**
```python
def eventos_api(request):
    # Retornar laudos como eventos
    laudos = Report.objects.filter(
        created_at__gte=datetime.now() - timedelta(days=90)
    ).values('id', 'number_report', 'created_at', 'status')
    
    events = []
    for laudo in laudos:
        events.append({
            'id': laudo['id'],
            'title': f"Laudo {laudo['number_report']}",
            'start': laudo['created_at'].isoformat(),
            'color': get_status_color(laudo['status']),
            'url': f"/reports/{laudo['id']}/"
        })
    
    return JsonResponse(events, safe=False)
```

---

## 📝 Laudos (Reports)

### 📊 Estado Atual
- Listagem e formulário na mesma página
- Sem modal de cadastro rápido de setor
- Formset de materiais funcional

### ✨ Melhorias

#### 1. Separar Visualização de Formulário

**Listagem (`reports/templates/reports.html`):**
```html
<div class="bg-white dark:bg-gray-800 rounded-lg shadow">
  <!-- Header -->
  <div class="p-6 border-b border-gray-200 dark:border-gray-700">
    <div class="flex items-center justify-between">
      <h2 class="text-2xl font-bold">Laudos Técnicos</h2>
      <a href="{% url 'reports:register_report' %}" 
         class="btn btn-primary">
        + Novo Laudo
      </a>
    </div>
  </div>
  
  <!-- Filtros -->
  <div class="p-6 border-b border-gray-200 dark:border-gray-700">
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <input type="text" placeholder="Buscar..." class="form-input">
      <select class="form-select">
        <option>Todos os setores</option>
        {% for setor in setores %}
        <option>{{ setor.name }}</option>
        {% endfor %}
      </select>
      <select class="form-select">
        <option>Todos os status</option>
        <option>Pendente</option>
        <option>Aprovado</option>
        <option>Rejeitado</option>
      </select>
      <input type="date" class="form-input">
    </div>
  </div>
  
  <!-- Tabela -->
  <div class="overflow-x-auto">
    <table class="w-full">
      <thead class="bg-gray-50 dark:bg-gray-700">
        <tr>
          <th class="px-6 py-3 text-left">Número</th>
          <th class="px-6 py-3 text-left">Setor</th>
          <th class="px-6 py-3 text-left">Data</th>
          <th class="px-6 py-3 text-left">Status</th>
          <th class="px-6 py-3 text-left">Ações</th>
        </tr>
      </thead>
      <tbody>
        {% for report in reports %}
        <tr class="border-b hover:bg-gray-50 dark:hover:bg-gray-700">
          <td class="px-6 py-4">{{ report.number_report }}</td>
          <td class="px-6 py-4">{{ report.sector.name }}</td>
          <td class="px-6 py-4">{{ report.created_at|date:"d/m/Y" }}</td>
          <td class="px-6 py-4">
            <span class="badge badge-{{ report.status }}">
              {{ report.get_status_display }}
            </span>
          </td>
          <td class="px-6 py-4">
            <a href="{% url 'reports:report' report.slug %}" 
               class="text-blue-600 hover:underline">Ver</a>
            <a href="{% url 'reports:update_report' report.slug %}" 
               class="text-green-600 hover:underline ml-3">Editar</a>
          </td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
  
  <!-- Paginação -->
  {% include "include/_pagination.html" %}
</div>
```

**Formulário (`reports/templates/register_reports.html`):**
```html
<div class="max-w-4xl mx-auto">
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
    <h2 class="text-2xl font-bold mb-6">Novo Laudo Técnico</h2>
    
    <form method="post">
      {% csrf_token %}
      
      <!-- Setor com botão de cadastro rápido -->
      <div class="mb-6">
        <label class="block text-sm font-medium mb-2">Setor</label>
        <div class="flex gap-2">
          {{ form.sector }}
          <button type="button" 
                  @click="openSetorModal()" 
                  class="btn btn-secondary whitespace-nowrap">
            + Novo Setor
          </button>
        </div>
      </div>
      
      <!-- Outros campos -->
      <div class="mb-6">
        <label class="block text-sm font-medium mb-2">Funcionário</label>
        {{ form.employee }}
      </div>
      
      <div class="mb-6">
        <label class="block text-sm font-medium mb-2">Justificativa</label>
        {{ form.justification }}
      </div>
      
      <!-- Formset de Materiais -->
      <div class="mb-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold">Materiais</h3>
          <button type="button" 
                  @click="addMaterial()" 
                  class="btn btn-sm btn-secondary">
            + Adicionar Material
          </button>
        </div>
        
        <div id="materiais-formset">
          {{ formset.management_form }}
          {% for form in formset %}
          <div class="material-form border rounded p-4 mb-4">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label class="block text-sm font-medium mb-2">Material</label>
                {{ form.material_bidding }}
              </div>
              <div>
                <label class="block text-sm font-medium mb-2">Quantidade</label>
                {{ form.quantity }}
              </div>
              <div class="flex items-end">
                <button type="button" 
                        @click="removeMaterial(this)" 
                        class="btn btn-danger w-full">
                  Remover
                </button>
              </div>
            </div>
          </div>
          {% endfor %}
        </div>
      </div>
      
      <!-- Botões -->
      <div class="flex gap-4">
        <button type="submit" class="btn btn-primary">Salvar Laudo</button>
        <a href="{% url 'reports:reports' %}" class="btn btn-secondary">Cancelar</a>
      </div>
    </form>
  </div>
</div>
```

#### 2. Modal de Cadastro Rápido de Setor

```html
<!-- Modal -->
<div x-show="setorModalOpen" 
     x-cloak
     class="fixed inset-0 z-50 overflow-y-auto">
  <!-- Overlay -->
  <div class="fixed inset-0 bg-black bg-opacity-50" 
       @click="setorModalOpen = false"></div>
  
  <!-- Modal Content -->
  <div class="relative min-h-screen flex items-center justify-center p-4">
    <div class="relative bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full p-6">
      <h3 class="text-xl font-bold mb-4">Cadastrar Novo Setor</h3>
      
      <form @submit.prevent="saveSetor()">
        <div class="mb-4">
          <label class="block text-sm font-medium mb-2">Nome do Setor</label>
          <input type="text" 
                 x-model="newSetor.name" 
                 class="form-input w-full" 
                 required>
        </div>
        
        <div class="mb-4">
          <label class="block text-sm font-medium mb-2">Diretoria</label>
          <select x-model="newSetor.direction" class="form-select w-full">
            <option value="">Selecione...</option>
            {% for direction in directions %}
            <option value="{{ direction.id }}">{{ direction.name }}</option>
            {% endfor %}
          </select>
        </div>
        
        <div class="mb-4">
          <label class="block text-sm font-medium mb-2">Responsável</label>
          <input type="text" 
                 x-model="newSetor.accountable" 
                 class="form-input w-full">
        </div>
        
        <div class="flex gap-4">
          <button type="submit" class="btn btn-primary flex-1">Salvar</button>
          <button type="button" 
                  @click="setorModalOpen = false" 
                  class="btn btn-secondary flex-1">
            Cancelar
          </button>
        </div>
      </form>
    </div>
  </div>
</div>
```

**JavaScript (Alpine.js):**
```javascript
<script>
document.addEventListener('alpine:init', () => {
  Alpine.data('reportForm', () => ({
    setorModalOpen: false,
    newSetor: {
      name: '',
      direction: '',
      accountable: ''
    },
    
    openSetorModal() {
      this.setorModalOpen = true;
    },
    
    async saveSetor() {
      try {
        const response = await fetch('/structure/setores/quick-create/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
          },
          body: JSON.stringify(this.newSetor)
        });
        
        const data = await response.json();
        
        if (data.success) {
          // Adicionar novo setor ao select
          const select = document.querySelector('#id_sector');
          const option = new Option(data.setor.name, data.setor.id, true, true);
          select.add(option);
          
          // Fechar modal
          this.setorModalOpen = false;
          
          // Resetar form
          this.newSetor = { name: '', direction: '', accountable: '' };
          
          // Mostrar notificação
          showToast('Setor cadastrado com sucesso!', 'success');
        }
      } catch (error) {
        showToast('Erro ao cadastrar setor', 'error');
      }
    }
  }));
});
</script>
```

**View (organizational_structure/views.py):**
```python
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json

@require_POST
def quick_create_setor(request):
    try:
        data = json.loads(request.body)
        
        setor = Sector.objects.create(
            name=data['name'],
            direction_id=data.get('direction'),
            accountable=data.get('accountable', '')
        )
        
        return JsonResponse({
            'success': True,
            'setor': {
                'id': setor.id,
                'name': setor.name
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
```

---

## 🏢 Licitações (Bidding)

### ✨ Melhorias

#### 1. Modal de Cadastro Rápido de Fornecedor

Similar ao modal de setor, mas para fornecedores:

```html
<!-- No formulário de licitação -->
<div class="mb-6">
  <label class="block text-sm font-medium mb-2">Fornecedor</label>
  <div class="flex gap-2">
    {{ form.supplier }}
    <button type="button" 
            @click="openSupplierModal()" 
            class="btn btn-secondary whitespace-nowrap">
      + Novo Fornecedor
    </button>
  </div>
</div>

<!-- Modal -->
<div x-show="supplierModalOpen" x-cloak class="fixed inset-0 z-50">
  <div class="fixed inset-0 bg-black bg-opacity-50" 
       @click="supplierModalOpen = false"></div>
  
  <div class="relative min-h-screen flex items-center justify-center p-4">
    <div class="relative bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full p-6">
      <h3 class="text-xl font-bold mb-4">Cadastrar Novo Fornecedor</h3>
      
      <form @submit.prevent="saveSupplier()">
        <div class="mb-4">
          <label class="block text-sm font-medium mb-2">Razão Social</label>
          <input type="text" x-model="newSupplier.company" class="form-input w-full" required>
        </div>
        
        <div class="mb-4">
          <label class="block text-sm font-medium mb-2">Nome Fantasia</label>
          <input type="text" x-model="newSupplier.trade" class="form-input w-full">
        </div>
        
        <div class="mb-4">
          <label class="block text-sm font-medium mb-2">CNPJ</label>
          <input type="text" 
                 x-model="newSupplier.cnpj" 
                 x-mask="99.999.999/9999-99"
                 class="form-input w-full" 
                 required>
        </div>
        
        <div class="flex gap-4">
          <button type="submit" class="btn btn-primary flex-1">Salvar</button>
          <button type="button" 
                  @click="supplierModalOpen = false" 
                  class="btn btn-secondary flex-1">
            Cancelar
          </button>
        </div>
      </form>
    </div>
  </div>
</div>
```

---

## 📦 Fornecedores (Suppliers)

### ✨ Melhorias

#### 1. Manter Formset de Contatos

O formset de contatos já está implementado e funcionando bem. **Manter como está.**

#### 2. Melhorar Listagem

```html
<div class="bg-white dark:bg-gray-800 rounded-lg shadow">
  <!-- Header com busca -->
  <div class="p-6 border-b">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-2xl font-bold">Fornecedores</h2>
      <a href="{% url 'suppliers:create' %}" class="btn btn-primary">
        + Novo Fornecedor
      </a>
    </div>
    
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <input type="text" placeholder="Buscar por nome ou CNPJ..." class="form-input">
      <select class="form-select">
        <option>Todos os fornecedores</option>
        <option>Ativos</option>
        <option>Inativos</option>
      </select>
    </div>
  </div>
  
  <!-- Grid de Cards -->
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-6">
    {% for supplier in suppliers %}
    <div class="border rounded-lg p-4 hover:shadow-lg transition">
      <h3 class="font-bold text-lg mb-2">{{ supplier.company }}</h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
        {{ supplier.trade }}
      </p>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
        CNPJ: {{ supplier.cnpj|format_cnpj }}
      </p>
      
      <!-- Contatos -->
      <div class="mb-4">
        {% for contact in supplier.suppliers.all %}
        <div class="text-sm flex items-center gap-2 mb-1">
          {% if contact.kind == 'E' %}
            <svg class="w-4 h-4">📧</svg>
          {% else %}
            <svg class="w-4 h-4">📱</svg>
          {% endif %}
          {{ contact.value }}
        </div>
        {% endfor %}
      </div>
      
      <div class="flex gap-2">
        <a href="{% url 'suppliers:detail' supplier.slug %}" 
           class="btn btn-sm btn-primary flex-1">Ver</a>
        <a href="{% url 'suppliers:update' supplier.slug %}" 
           class="btn btn-sm btn-secondary flex-1">Editar</a>
      </div>
    </div>
    {% endfor %}
  </div>
</div>
```

---

## 🎯 Componentes Globais

### 1. Sistema de Notificações (Toasts)

```html
<!-- templates/include/_toasts.html -->
<div x-data="toastManager()" 
     @toast.window="addToast($event.detail)"
     class="fixed top-20 right-4 z-50 space-y-2">
  
  <template x-for="toast in toasts" :key="toast.id">
    <div x-show="toast.show"
         x-transition:enter="transition ease-out duration-300"
         x-transition:enter-start="opacity-0 transform translate-x-full"
         x-transition:enter-end="opacity-100 transform translate-x-0"
         x-transition:leave="transition ease-in duration-200"
         x-transition:leave-start="opacity-100"
         x-transition:leave-end="opacity-0"
         :class="{
           'bg-green-500': toast.type === 'success',
           'bg-red-500': toast.type === 'error',
           'bg-blue-500': toast.type === 'info',
           'bg-yellow-500': toast.type === 'warning'
         }"
         class="rounded-lg shadow-lg p-4 text-white min-w-[300px] max-w-md">
      
      <div class="flex items-start gap-3">
        <div class="flex-shrink-0">
          <template x-if="toast.type === 'success'">
            <svg class="w-6 h-6">✓</svg>
          </template>
          <template x-if="toast.type === 'error'">
            <svg class="w-6 h-6">✕</svg>
          </template>
        </div>
        
        <div class="flex-1">
          <p class="font-semibold" x-text="toast.title"></p>
          <p class="text-sm" x-text="toast.message"></p>
        </div>
        
        <button @click="removeToast(toast.id)" class="flex-shrink-0">
          <svg class="w-5 h-5">×</svg>
        </button>
      </div>
    </div>
  </template>
</div>

<script>
function toastManager() {
  return {
    toasts: [],
    nextId: 1,
    
    addToast(data) {
      const id = this.nextId++;
      const toast = {
        id,
        show: true,
        ...data
      };
      
      this.toasts.push(toast);
      
      setTimeout(() => {
        this.removeToast(id);
      }, data.duration || 5000);
    },
    
    removeToast(id) {
      const index = this.toasts.findIndex(t => t.id === id);
      if (index > -1) {
        this.toasts[index].show = false;
        setTimeout(() => {
          this.toasts.splice(index, 1);
        }, 300);
      }
    }
  };
}

// Helper function
function showToast(message, type = 'info', title = '') {
  window.dispatchEvent(new CustomEvent('toast', {
    detail: { message, type, title }
  }));
}
</script>
```

### 2. Confirmação de Ações

```html
<!-- Modal de Confirmação -->
<div x-data="{ confirmOpen: false, confirmData: {} }"
     @confirm.window="confirmOpen = true; confirmData = $event.detail">
  
  <div x-show="confirmOpen" x-cloak class="fixed inset-0 z-50">
    <div class="fixed inset-0 bg-black bg-opacity-50" 
         @click="confirmOpen = false"></div>
    
    <div class="relative min-h-screen flex items-center justify-center p-4">
      <div class="relative bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full p-6">
        <h3 class="text-xl font-bold mb-4" x-text="confirmData.title || 'Confirmar'"></h3>
        <p class="text-gray-600 dark:text-gray-400 mb-6" x-text="confirmData.message"></p>
        
        <div class="flex gap-4">
          <button @click="confirmData.onConfirm(); confirmOpen = false" 
                  class="btn btn-danger flex-1">
            Confirmar
          </button>
          <button @click="confirmOpen = false" 
                  class="btn btn-secondary flex-1">
            Cancelar
          </button>
        </div>
      </div>
    </div>
  </div>
</div>

<script>
function showConfirm(message, onConfirm, title = 'Confirmar') {
  window.dispatchEvent(new CustomEvent('confirm', {
    detail: { message, onConfirm, title }
  }));
}
</script>
```

---

## ✅ Checklist de Implementação

### Dashboard
- [ ] Remover cards desnecessários (5 → 3)
- [ ] Implementar gráfico de laudos por setor
- [ ] Implementar filtro temporal (1m, 3m, 6m, 1y, 2y, 3y)
- [ ] Implementar gráfico de top 10 materiais
- [ ] Integrar FullCalendar
- [ ] Criar API de eventos
- [ ] Atualizar views com queries otimizadas

### Laudos
- [ ] Separar listagem de formulário
- [ ] Criar modal de cadastro rápido de setor
- [ ] Implementar API de criação rápida
- [ ] Atualizar select dinamicamente
- [ ] Manter formset de materiais

### Licitações
- [ ] Criar modal de cadastro rápido de fornecedor
- [ ] Implementar API de criação rápida

### Fornecedores
- [ ] Melhorar listagem (grid de cards)
- [ ] Manter formset de contatos

### Componentes Globais
- [ ] Implementar sistema de toasts
- [ ] Implementar modal de confirmação
- [ ] Criar helpers JavaScript

---

## 📊 Estimativa de Tempo

- **Dashboard:** 3-4 dias
- **Laudos:** 2-3 dias
- **Licitações:** 1-2 dias
- **Fornecedores:** 1 dia
- **Componentes Globais:** 1-2 dias

**Total:** 8-12 dias úteis

---

**Documento criado em:** 03/12/2025  
**Status:** 📋 Aguardando aprovação  
**Próximo passo:** Revisar e aprovar especificações
