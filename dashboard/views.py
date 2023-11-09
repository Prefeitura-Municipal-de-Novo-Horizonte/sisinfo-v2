from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.shortcuts import resolve_url as r
from django.urls import reverse

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
    diretorias = Direction.objects.all()
    if request.method == 'POST':
        form = DirectionForm(request.POST)
        if form.is_valid():
            form.save()
            # TODO: Add message success
        return HttpResponse('Cadastro OK')
    form = DirectionForm()
    context = {
        'form': form, 
        'diretorias': diretorias,
        }
    return render(request, 'setores/diretorias.html', context)