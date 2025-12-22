from django.shortcuts import render, get_object_or_404
from .models import Truyen

def truyen_list(request):
    ds = Truyen.objects.all()
    return render(request, 'doctruyen/truyen_list.html', {'ds': ds})

def truyen_detail(request, slug):
    truyen = get_object_or_404(Truyen, slug=slug)
    return render(request, 'doctruyen/truyen_detail.html', {'truyen': truyen})
