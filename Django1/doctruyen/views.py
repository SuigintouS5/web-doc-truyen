from django.shortcuts import render, get_object_or_404
from .models import Truyen, Genre

def truyen_list(request):
    ds = Truyen.objects.all()
    return render(request, 'doctruyen/truyen_list.html', {'ds': ds})

def truyen_detail(request, slug):
    truyen = get_object_or_404(Truyen, slug=slug)
    genres = truyen.genres.all()
    return render(request, 'doctruyen/truyen_detail.html', {'truyen': truyen, 'genres': genres})

def genre_detail(request, slug):
    genre = get_object_or_404(Genre, slug=slug)
    truyens = genre.truyens.all()
    return render(request, 'doctruyen/truyen_list.html', {'ds': truyens, 'current_genre': genre})

