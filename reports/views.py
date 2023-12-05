from django.forms import inlineformset_factory
from django.http import HttpResponse
from django.shortcuts import render

from dashboard.models import Material
from reports.forms import MaterialReportForm, ReportForm
from reports.models import MaterialReport, Report


# Create your views here.
def reports(request):
    context = {}
    return render(request, 'reports.html', context)


def report_register(request):
    if request.method == 'POST':
        form = ReportForm(request.POST, request=request)
        form_material_factory = inlineformset_factory(
            Report, MaterialReport, form=MaterialReportForm)
        form_material = form_material_factory(request.POST)
        # TODO: ajustar message e redirect
        if form.is_valid() and form_material.is_valid():
            report = form.save()
            form_material.instance = report
            form_material.save()
            return HttpResponse('Sucessfully registered')
        else:
            return HttpResponse('Failed to register')
    form = ReportForm(request=request)
    form_material = inlineformset_factory(
        Report, MaterialReport, form=MaterialReportForm, extra=2)
    context = {
        'form': form,
        'form_material': form_material
    }
    return render(request, 'register_reports.html', context)
