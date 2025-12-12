from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.messages import constants
from django.db.models import Sum
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    View,
)

from bidding_procurement.filters import BiddingFilter, MaterialFilter
from bidding_procurement.forms import (
    BiddingForm,
    MaterialBiddingForm,
    MaterialForm,
)
from bidding_procurement.mixins import (
    FilteredListMixin,
    PaginatedListMixin,
    MessageMixin,
)
from bidding_procurement.models import Bidding, Material, MaterialBidding
from bidding_procurement.services import BiddingService, MaterialService
from reports.models import MaterialReport


# ==================== BIDDING VIEWS ====================

class BiddingListView(
    LoginRequiredMixin,
    FilteredListMixin,
    PaginatedListMixin,
    ListView
):
    """
    View para listar licitações com filtros e paginação.
    """
    model = Bidding
    template_name = "bidding_procurement/biddings.html"
    context_object_name = "page_obj"
    filterset_class = BiddingFilter
    paginate_by = 15
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = BiddingForm()
        context['btn'] = "Adicionar nova Licitação"
        context['total_licitacoes'] = self.get_queryset().count()
        return context


class BiddingCreateView(LoginRequiredMixin, MessageMixin, CreateView):
    """
    View para criar uma nova licitação.
    """
    model = Bidding
    form_class = BiddingForm
    success_url = reverse_lazy("bidding_procurement:licitacoes")
    success_message = "Inserido com sucesso!"
    error_message = "Ocorreu um erro!"
    
    def form_valid(self, form):
        if BiddingService.create_bidding(form):
            messages.add_message(
                self.request,
                constants.SUCCESS,
                self.success_message
            )
        else:
            messages.add_message(
                self.request,
                constants.ERROR,
                self.error_message
            )
        return redirect(self.success_url)


class BiddingDetailView(LoginRequiredMixin, DetailView):
    """
    View para exibir detalhes de uma licitação e vincular materiais.
    """
    model = Bidding
    template_name = "bidding_procurement/bidding_detail.html"
    context_object_name = "licitacao"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        licitacao = self.object
        
        # Usa o novo método do modelo para pegar materiais ativos
        material_associations = licitacao.material_associations.all().select_related(
            'material', 'supplier'
        )
        
        context['form'] = MaterialBiddingForm()
        context['material_associations'] = material_associations
        context['myFilter'] = MaterialFilter(
            self.request.GET,
            queryset=MaterialService.get_all_materials()
        )
        context['total_materiais'] = material_associations.count()
        context['btn'] = "Vincular Material"
        return context
    
    def post(self, request, *args, **kwargs):
        """Processa vinculação de material à licitação."""
        self.object = self.get_object()
        form_material = MaterialBiddingForm(request.POST)
        
        success, msg = BiddingService.add_material_to_bidding(
            self.object,
            form_material
        )
        
        if success:
            messages.add_message(request, constants.SUCCESS, msg)
        else:
            messages.add_message(request, constants.ERROR, msg)
        
        return redirect("bidding_procurement:licitacao", slug=self.object.slug)


class BiddingUpdateView(LoginRequiredMixin, MessageMixin, UpdateView):
    """
    View para atualizar uma licitação existente.
    """
    model = Bidding
    form_class = BiddingForm
    template_name = "bidding_procurement/biddings.html"
    context_object_name = "licitacao"
    success_url = reverse_lazy("bidding_procurement:licitacoes")
    success_message = "Atualizado com Sucesso!"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        licitacoes = BiddingService.get_all_biddings()
        myFilter = BiddingFilter(self.request.GET, queryset=licitacoes)
        
        # Paginação para listagem
        from django.core.paginator import Paginator
        paginator = Paginator(myFilter.qs, 15)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        
        context['page_obj'] = page_obj
        context['myFilter'] = myFilter
        context['btn'] = "Atualizar Licitação"
        context['total_licitacoes'] = Bidding.objects.count()
        # Indica que estamos editando
        context['editing'] = True
        return context
    
    def form_valid(self, form):
        if BiddingService.update_bidding(self.object, form):
            messages.add_message(
                self.request,
                constants.SUCCESS,
                self.success_message
            )
            return redirect(self.success_url)
        return self.form_invalid(form)


class BiddingDeleteView(LoginRequiredMixin, View):
    """
    View para excluir uma licitação diretamente sem template de confirmação.
    """
    def get(self, request, slug):
        """Exclui a licitação e redireciona."""
        licitacao = BiddingService.get_bidding_by_slug(slug)
        name = licitacao.name
        BiddingService.delete_bidding(licitacao)
        
        messages.add_message(
            request,
            constants.ERROR,
            f"A licitação {name} foi excluída com sucesso!"
        )
        return redirect("bidding_procurement:licitacoes")


class BiddingToggleStatusView(LoginRequiredMixin, View):
    """
    View para alternar o status de uma licitação (Ativo/Inativo).
    """
    def get(self, request, slug):
        licitacao = BiddingService.get_bidding_by_slug(slug)
        msg = BiddingService.toggle_status(licitacao)
        messages.add_message(request, constants.SUCCESS, msg)
        return redirect("bidding_procurement:licitacoes")


class MaterialToggleStatusView(LoginRequiredMixin, View):
    """
    View para alternar o status de um material em uma licitação específica.
    """
    def get(self, request, id):
        material_bidding, msg = BiddingService.toggle_material_status(id)
        messages.add_message(request, constants.SUCCESS, msg)
        return redirect(
            "bidding_procurement:licitacao",
            slug=material_bidding.bidding.slug
        )


# ==================== MATERIAL VIEWS ====================

class MaterialListView(
    LoginRequiredMixin,
    FilteredListMixin,
    PaginatedListMixin,
    ListView
):
    """
    View para listar materiais com filtros e paginação.
    """
    model = Material
    template_name = "bidding_procurement/materials.html"
    context_object_name = "materiais"  # Corrigido: era page_obj, agora materiais
    filterset_class = MaterialFilter
    paginate_by = 15
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Adiciona page_obj para compatibilidade com template
        if 'page_obj' not in context and 'materiais' in context:
            context['page_obj'] = context['materiais']
        context['form'] = MaterialForm()
        context['btn'] = "Adicionar novo material"
        context['total_materiais'] = Material.objects.count()
        return context


class MaterialCreateView(LoginRequiredMixin, MessageMixin, CreateView):
    """
    View para criar um novo material.
    """
    model = Material
    form_class = MaterialForm
    success_url = reverse_lazy("bidding_procurement:materiais")
    success_message = "Inserido com sucesso!"
    error_message = "Ocorreu um erro!"
    
    def form_valid(self, form):
        if MaterialService.create_material(form):
            messages.add_message(
                self.request,
                constants.SUCCESS,
                self.success_message
            )
        else:
            messages.add_message(
                self.request,
                constants.ERROR,
                self.error_message
            )
        return redirect(self.success_url)


class MaterialDetailView(LoginRequiredMixin, DetailView):
    """
    View para exibir detalhes de um material e seu histórico de uso.
    """
    model = Material
    template_name = "bidding_procurement/material_detail.html"
    context_object_name = "material"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        material = self.object
        
        reports = MaterialReport.objects.filter(material=material.id)
        total_quantity = reports.aggregate(total_value=Sum("quantity"))
        
        context['reports'] = reports
        context['total_quantity'] = total_quantity.get("total_value")
        return context


class MaterialUpdateView(LoginRequiredMixin, MessageMixin, UpdateView):
    """
    View para atualizar um material existente.
    """
    model = Material
    form_class = MaterialForm
    template_name = "bidding_procurement/materials.html"
    context_object_name = "material"
    success_url = reverse_lazy("bidding_procurement:materiais")
    success_message = "Atualizado com Sucesso!"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        materiais = MaterialService.get_all_materials()
        myFilter = MaterialFilter(self.request.GET, queryset=materiais)
        
        # Paginação para listagem
        from django.core.paginator import Paginator
        paginator = Paginator(myFilter.qs, 15)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        
        context['page_obj'] = page_obj
        context['myFilter'] = myFilter
        context['btn'] = "Atualizar Material"
        context['total_materiais'] = Material.objects.count()
        # Indica que estamos editando
        context['editing'] = True
        return context
    
    def form_valid(self, form):
        if MaterialService.update_material(self.object, form):
            messages.add_message(
                self.request,
                constants.SUCCESS,
                self.success_message
            )
            return redirect(self.success_url)
        return self.form_invalid(form)


class MaterialDeleteView(LoginRequiredMixin, View):
    """
    View para excluir um material diretamente sem template de confirmação.
    """
    def get(self, request, slug):
        """Exclui o material e redireciona."""
        material = MaterialService.get_material_by_slug(slug)
        name = material.name
        MaterialService.delete_material(material)
        
        messages.add_message(
            request,
            constants.ERROR,
            f"O suprimento {name} foi excluído com sucesso!"
        )
        return redirect("bidding_procurement:materiais")
