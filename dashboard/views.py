from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from organizational_structure.models import Direction, Sector
from reports.models import Report


# Create your views here.
@login_required
def index(request):
    total_reports_user = Report.objects.filter(
        professional=request.user).count()
    total_reports = Report.objects.all().count()
    total_sectors = Sector.objects.all().count()
    total_directions = Direction.objects.all().count()
    total_reports_accountable = Report.objects.all().filter(
        pro_accountable=request.user).count()
    context = {
        'total_reports': total_reports,
        'total_reports_user': total_reports_user,
        'total_sectors': total_sectors,
        'total_directions': total_directions,
        'total_reports_accountable': total_reports_accountable,
    }
    return render(request, "index.html", context)
