from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages import constants
from django.forms import inlineformset_factory
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.text import slugify
from django.views.generic import DetailView, ListView, View
from django.core.paginator import Paginator

# Imports locais movidos para o topo
from reports.filters import ReportFilter
from reports.forms import MaterialReportForm, MaterialReportFormset, ReportForm, ReportUpdateForm
from reports.models import MaterialReport, Report
from reports.pdf_generator import PDFGenerator
from reports.services import ReportService
from organizational_structure.models import Sector
import json


# Create your views here.
class ReportListView(LoginRequiredMixin, ListView):
    """
    Lista todos os laudos com paginação e filtro.
    Substitui a FBV `reports`.
    """
    model = Report
    template_name = 'reports.html'
    context_object_name = 'page_obj'
    paginate_by = 15
    context_object_name = 'page_obj'
    paginate_by = 15
    login_url = 'authenticate:login'

    def get_queryset(self):
        queryset = ReportService.get_all_reports()
        self.filterset = ReportFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['myFilter'] = self.filterset
        return context


@login_required(login_url='authenticate:login')
def report_register(request):
    """
    View para registrar um novo laudo.
    Mantida como FBV devido à complexidade do inline formset.
    """
    if request.method == 'POST':
        form = ReportForm(request.POST, request=request)
        # Formset para materiais
        form_material_factory = inlineformset_factory(
            Report, MaterialReport, form=MaterialReportForm)
        form_material = form_material_factory(request.POST)
        
        report = ReportService.create_report(form, form_material)
        if report:
            messages.add_message(request, constants.SUCCESS,
                                 f'Laudo {report.slug} salvo com sucesso!')
            return redirect(reverse('reports:register_report'))
        else:
            messages.add_message(request, constants.ERROR,
                                 'Ocorreu um erro tente novamente!')
            return redirect(reverse('reports:reports'))
            
    form = ReportForm(request=request)
    form_material = inlineformset_factory(
        Report, MaterialReport, form=MaterialReportForm, extra=2)
    context = {
        'form': form,
        'form_material': form_material
    }
    return render(request, 'register_reports.html', context)


class ReportDetailView(LoginRequiredMixin, DetailView):
    """
    Visualiza detalhes de um laudo.
    Substitui a FBV `report_view`.
    """
    model = Report
    template_name = 'report.html'
    context_object_name = 'report'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    login_url = 'authenticate:login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Usa o service para pegar detalhes adicionais (como preço total)
        # O service retorna um dict com 'report' e 'total_price'
        details = ReportService.get_report_details(self.object.slug)
        context.update(details)
        return context


@login_required(login_url='authenticate:login')
def report_update(request, slug):
    """
    Atualiza um laudo existente.
    Mantida como FBV verificação de permissão customizada e formset.
    """
    report = ReportService.get_report_by_slug(slug)
    # Verifica permissão: apenas o profissional ou responsável podem editar
    if request.user in [report.professional, report.pro_accountable]:
        form = ReportUpdateForm(request.POST or None,
                                instance=report, request=request)
        form_material = MaterialReportFormset(
            request.POST or None, instance=report, prefix='materials')
        
        if request.method == 'POST':
            updated_report = ReportService.update_report(form, form_material)
            if updated_report:
                messages.add_message(
                    request, constants.SUCCESS, f'O Laudo {updated_report.number_report} foi atualizado com sucesso.')
                return redirect(reverse('reports:report_update', kwargs={'slug': slug}))
            messages.add_message(request, constants.ERROR,
                                 'Não foi possivel atualizar o laudo.')
            return redirect(reverse('reports:report_update', kwargs={'slug': slug}))
            
        context = {
            'report': report,
            'form': form,
            'form_material': form_material,
            'btn': 'Atualizar Laudo',
        }
        return render(request, 'update_report.html', context)
    else:
        messages.add_message(request, constants.WARNING,
                             'Você não tem permissão para alterar esse laudo!')
        return redirect('reports:reports')





@login_required(login_url='authenticate:login')
def material_report_delete(request, report_slug, pk):
    """
    Exclui um material de um laudo.
    """
    report, msg = ReportService.delete_material_report(pk)
    messages.add_message(request, constants.SUCCESS, msg)
    return redirect(reverse('reports:report_update', kwargs={'slug': report.slug}))


@login_required(login_url='authenticate:login')
def generate_pdf_report(request, slug):
    """
    Gera e retorna PDF do laudo usando Browserless.io/PDFGenerator.
    """
    report = ReportService.get_report_by_slug(slug)
    
    try:
        pdf_bytes = PDFGenerator.generate_report_pdf(report)
        
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        # nome do arquivo para download
        response['Content-Disposition'] = f'inline; filename="laudo_{report.number_report}.pdf"'
        return response
    except Exception as e:
        messages.add_message(request, constants.ERROR, f'Erro ao gerar PDF: {str(e)}')
        return redirect(reverse('reports:report_view', kwargs={'slug': slug}))


@login_required(login_url='authenticate:login')
def create_sector_api(request):
    """
    API para criar um novo setor via AJAX.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            
            if not name:
                return JsonResponse({'error': 'Nome do setor é obrigatório'}, status=400)
                
            # Verifica se já existe (independente de maiúsculas/minúsculas)
            if Sector.objects.filter(name__iexact=name).exists():
                return JsonResponse({'error': 'Setor já existe'}, status=400)
                
            # Cria o setor e gera slug
            slug = slugify(name)
            sector = Sector.objects.create(name=name, slug=slug)
            
            return JsonResponse({'id': sector.id, 'name': sector.name})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Método não permitido'}, status=405)
