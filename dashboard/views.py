from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from dashboard.services import DashboardService


# Create your views here.
@login_required
def index(request):
    """
    View principal do Dashboard.
    Exibe contadores e resumos para o usuário logado.
    """
    context = DashboardService.get_dashboard_data(request.user)
    return render(request, "index.html", context)
