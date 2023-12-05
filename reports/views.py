from django.shortcuts import render

from reports.forms import ReportForm


# Create your views here.
def reports(request):
    context = {}
    return render(request, 'reports.html', context)


def report_register(request):
    professional = request.user
    form = ReportForm(request=request)
    context = {
        'form': form,
    }
    return render(request, 'register_reports.html', context)
