from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages import constants
from django.core.paginator import Paginator
from django.forms import inlineformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from reports.filters import ReportFilter
from reports.forms import MaterialReportForm, MaterialReportFormset, ReportForm, ReportUpdateForm
from reports.models import MaterialReport, Report
from reports.services import ReportService


# Create your views here.
@login_required(login_url='login')
def reports(request):
    """
    View para listar laudos.
    
    GET: Lista todos os laudos com paginação e filtro.
    """
    reports_list = ReportService.get_all_reports()
    myFilter = ReportFilter(request.GET, queryset=reports_list)
    reports_list = myFilter.qs
    paginator = Paginator(reports_list, 15)  # Show 15 reports per page.

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj,
        "myFilter": myFilter,
    }
    return render(request, 'reports.html', context)


@login_required(login_url='login')
def report_register(request):
    """
    View para registrar um novo laudo.
    """
    if request.method == 'POST':
        form = ReportForm(request.POST, request=request)
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


@login_required(login_url='login')
def report_view(request, slug):
    """
    View para visualizar detalhes de um laudo.
    """
    context = ReportService.get_report_details(slug)
    return render(request, 'report.html', context)


@login_required(login_url='login')
def report_update(request, slug):
    """
    View para atualizar um laudo existente.
    Apenas o profissional responsável ou o criador podem editar.
    """
    report = ReportService.get_report_by_slug(slug)
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


def pdf_report(request, slug):
    """
    View para gerar visualização de impressão (PDF) do laudo.
    """
    report = ReportService.get_report_by_slug(slug)
    context = {
        'report': report,
    }
    return render(request, 'pdf_template.html', context)


@login_required(login_url='login')
def material_report_delete(request, report_slug, pk):
    """
    View para excluir um material de um laudo.
    """
    report, msg = ReportService.delete_material_report(pk)
    messages.add_message(request, constants.SUCCESS, msg)
    return redirect(reverse('reports:report_update', kwargs={'slug': report.slug}))


@login_required(login_url='login')
def generate_pdf_report(request, slug):
    """
    Gera e retorna PDF do laudo usando Browserless.io.
    
    Args:
        request: HttpRequest
        slug: Slug do laudo
        
    Returns:
        HttpResponse com PDF gerado
    """
    from reports.pdf_generator import PDFGenerator
    from django.http import HttpResponse
    
    report = ReportService.get_report_by_slug(slug)
    
    try:
        pdf_bytes = PDFGenerator.generate_report_pdf(report)
        
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="laudo_{report.number_report}.pdf"'
        return response
    except Exception as e:
        messages.add_message(request, constants.ERROR, f'Erro ao gerar PDF: {str(e)}')
        return redirect(reverse('reports:report_view', kwargs={'slug': slug}))
