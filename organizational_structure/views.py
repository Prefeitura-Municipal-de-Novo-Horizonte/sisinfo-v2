from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages import constants
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, DetailView, UpdateView, TemplateView

from core.mixins import TechOnlyMixin
from organizational_structure.filters import DirectionFilter, SectorFilter
from organizational_structure.forms import DirectionForm, SectorForm
from organizational_structure.models import Direction, Sector
from organizational_structure.services import StructureService
from reports.models import Report


##############################################
# PÁGINA UNIFICADA (ESTRUTURA)
##############################################

class StructureView(LoginRequiredMixin, TemplateView):
    """View para página unificada de Estrutura (Setores + Diretorias)."""
    template_name = "organizational_structure/estrutura.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Aba ativa (setores ou diretorias)
        tab = self.request.GET.get('tab', 'setores')
        context['active_tab'] = tab
        
        # Setores
        setores = StructureService.get_all_sectors()
        setores_filter = SectorFilter(self.request.GET, queryset=setores)
        context['setores'] = setores_filter.qs[:20]  # Limitar para performance
        context['setores_filter'] = setores_filter
        context['total_setores'] = setores.count()
        
        # Diretorias
        diretorias = StructureService.get_all_directions()
        diretorias_filter = DirectionFilter(self.request.GET, queryset=diretorias)
        context['diretorias'] = diretorias_filter.qs[:20]
        context['diretorias_filter'] = diretorias_filter
        context['total_diretorias'] = diretorias.count()
        
        return context


##############################################
# DIRETORIAS
##############################################

class DirectionListView(LoginRequiredMixin, ListView):
    """View para listar diretorias com filtros e paginação."""
    model = Direction
    template_name = "organizational_structure/diretorias.html"
    context_object_name = "diretorias"
    paginate_by = 12
    
    def get_queryset(self):
        queryset = StructureService.get_all_directions()
        self.filterset = DirectionFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['myFilter'] = self.filterset
        return context


class DirectionCreateView(LoginRequiredMixin, CreateView):
    """View para criar uma nova diretoria."""
    model = Direction
    form_class = DirectionForm
    template_name = "organizational_structure/direction_form.html"
    success_url = reverse_lazy("organizational_structure:diretorias")
    
    def form_valid(self, form):
        messages.add_message(self.request, constants.SUCCESS, "Diretoria criada com sucesso!")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.add_message(self.request, constants.ERROR, "Erro ao criar diretoria. Verifique os dados.")
        return super().form_invalid(form)


class DirectionDetailView(LoginRequiredMixin, DetailView):
    """View para visualizar detalhes de uma diretoria e seus setores."""
    model = Direction
    template_name = "organizational_structure/diretoria_detail.html"
    context_object_name = "diretoria"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        setores = self.object.setores.all()
        
        self.filterset = SectorFilter(self.request.GET, queryset=setores)
        setores = self.filterset.qs
        
        # Paginação manual
        from django.core.paginator import Paginator
        paginator = Paginator(setores, 12)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        
        context['page_obj'] = page_obj
        context['myFilter'] = self.filterset
        context['total_setores'] = self.object.setores.count()
        return context


class DirectionUpdateView(LoginRequiredMixin, UpdateView):
    """View para atualizar uma diretoria existente."""
    model = Direction
    form_class = DirectionForm
    template_name = "organizational_structure/direction_form.html"
    context_object_name = "diretoria"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    
    def get_success_url(self):
        return reverse_lazy("organizational_structure:diretorias")
    
    def form_valid(self, form):
        messages.add_message(self.request, constants.SUCCESS, "Diretoria atualizada com sucesso!")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.add_message(self.request, constants.ERROR, "Erro ao atualizar diretoria.")
        return super().form_invalid(form)


class DirectionDeleteView(LoginRequiredMixin, TechOnlyMixin, View):
    """View para excluir uma diretoria."""
    def get(self, request, slug):
        diretoria = get_object_or_404(Direction, slug=slug)
        name = diretoria.name
        StructureService.delete_direction(diretoria)
        messages.add_message(request, constants.ERROR, f"Diretoria {name} foi excluída com sucesso!")
        return redirect("organizational_structure:diretorias")


##############################################
# SETORES
##############################################

class SectorListView(LoginRequiredMixin, ListView):
    """View para listar setores com filtros e paginação."""
    model = Sector
    template_name = "organizational_structure/setores.html"
    context_object_name = "setores"
    paginate_by = 15
    
    def get_queryset(self):
        queryset = StructureService.get_all_sectors()
        self.filterset = SectorFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['myFilter'] = self.filterset
        return context


class SectorCreateView(LoginRequiredMixin, CreateView):
    """View para criar um novo setor."""
    model = Sector
    form_class = SectorForm
    template_name = "organizational_structure/sector_form.html"
    success_url = reverse_lazy("organizational_structure:setores")
    
    def form_valid(self, form):
        messages.add_message(self.request, constants.SUCCESS, "Setor criado com sucesso!")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.add_message(self.request, constants.ERROR, "Erro ao criar setor. Verifique os dados.")
        return super().form_invalid(form)


class SectorDetailView(LoginRequiredMixin, DetailView):
    """View para visualizar detalhes de um setor e seus relatórios."""
    model = Sector
    template_name = "organizational_structure/setor_detail.html"
    context_object_name = "setor"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reports'] = Report.objects.filter(sector=self.object)
        return context


class SectorUpdateView(LoginRequiredMixin, UpdateView):
    """View para atualizar um setor existente."""
    model = Sector
    form_class = SectorForm
    template_name = "organizational_structure/sector_form.html"
    context_object_name = "setor"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    
    def get_success_url(self):
        return reverse_lazy("organizational_structure:setores")
    
    def form_valid(self, form):
        messages.add_message(self.request, constants.SUCCESS, "Setor atualizado com sucesso!")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.add_message(self.request, constants.ERROR, "Erro ao atualizar setor.")
        return super().form_invalid(form)


class SectorDeleteView(LoginRequiredMixin, View):
    """View para excluir um setor."""
    def get(self, request, slug):
        setor = get_object_or_404(Sector, slug=slug)
        name = setor.name
        StructureService.delete_sector(setor)
        messages.add_message(request, constants.ERROR, f"O Setor {name} foi excluído com sucesso!")
        return redirect("organizational_structure:setores")
