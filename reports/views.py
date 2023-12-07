from django.contrib import messages
from django.contrib.messages import constants
from django.core.paginator import Paginator
from django.db.models import Sum
from django.forms import inlineformset_factory
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from reports.forms import MaterialReportForm, ReportForm
from reports.models import MaterialReport, Report


# Create your views here.
def reports(request):
    report_list = Report.objects.all()
    paginator = Paginator(report_list, 15)  # Show 15 reports per page.

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj,
    }
    return render(request, 'reports.html', context)


def report_register(request):
    if request.method == 'POST':
        form = ReportForm(request.POST, request=request)
        form_material_factory = inlineformset_factory(
            Report, MaterialReport, form=MaterialReportForm)
        form_material = form_material_factory(request.POST)
        if form.is_valid() and form_material.is_valid():
            report = form.save()
            form_material.instance = report
            form_material.save()
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


def report_view(request, slug):
    report = get_object_or_404(Report, slug=slug)
    materiais_report = MaterialReport.objects.filter(report=report)
    total_price = 0
    for material in materiais_report:
        total_price = total_price + material.total_price()
    context = {
        'report': report,
        'total_price': total_price,
    }
    return render(request, 'report.html', context)
