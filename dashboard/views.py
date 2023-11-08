from django.http import HttpResponse
from django.shortcuts import render

from .models import Direction


# Create your views here.
def index(request):
    context = {}
    return render(request, 'index.html', context)

##############################################
########## DIRETORIAS DASHBOARD ##############
##############################################

def list_all_diretorias(request):
    context = {
        'diretorias': Direction.objects.all(),
        }
    return render(request, 'setores/list_all_diretorias.html', context)