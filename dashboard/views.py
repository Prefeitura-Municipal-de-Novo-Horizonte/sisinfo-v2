from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.shortcuts import resolve_url as r

from dashboard.forms import DirectionForm
from dashboard.models import Direction


# Create your views here.
def index(request):
    context = {}
    return render(request, 'index.html', context)

##############################################
########## DIRETORIAS DASHBOARD ##############
##############################################

def directions(request):
    form_diretoria = DirectionForm()
    diretorias= Direction.objects.all()
    context = {'form': form_diretoria, 'diretorias': diretorias}
    return render(request, 'setores/diretorias.html', context)