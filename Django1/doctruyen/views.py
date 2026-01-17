from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

from .models import Truyen, Genre, Comment


# =========================
# TRUYỆN
# =========================

def truyen_list(request):
    ds = Truyen.objects.all()
    return render(request, 'doctruyen/truyen_list.html', {'ds': ds})


def truyen_detail(request, slug):
    truyen = get_object_or_404(Truyen, slug=slug)
    genres = truyen.genres.all()
    comments = Comment.objects.filter(truyen=truyen).select_related("user")
    
    # Kiểm tra quyền chỉnh sửa: author, editor, hoặc superuser
    can_edit = False
    if request.user.is_authenticated:
        can_edit = (request.user == truyen.author or 
                   request.user in truyen.editors.all() or 
                   request.user.is_staff)

    return render(request, 'doctruyen/truyen_detail.html', {
        'truyen': truyen,
        'genres': genres,
        'comments': comments,
        'can_edit': can_edit
    })


def genre_detail(request, slug):
    genre = get_object_or_404(Genre, slug=slug)
    truyens = genre.truyens.all()
    return render(
        request,
        'doctruyen/truyen_list.html',
        {'ds': truyens, 'current_genre': genre}
    )


# =========================
# AUTH
# =========================

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            messages.success(request, f"Xin chào {user.username}! Đăng nhập thành công.")
            return redirect("truyen-list")
        else:
            messages.error(request, "Sai tài khoản hoặc mật khẩu")
            return redirect("truyen-list")

    return redirect("truyen-list")


def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")

        if password != password_confirm:
            messages.error(request, "Mật khẩu không khớp")
            return redirect("truyen-list")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Tên đăng nhập đã tồn tại")
            return redirect("truyen-list")

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(request, "Đăng ký thành công! Hãy đăng nhập ngay.")
        return redirect("truyen-list")

    return redirect("truyen-list")

def truyen_edit(request, slug):
    """View để chỉnh sửa truyện - chỉ author/editor/staff được phép"""
    truyen = get_object_or_404(Truyen, slug=slug)
    
    # Kiểm tra quyền
    if not (request.user.is_authenticated and 
            (request.user == truyen.author or 
             request.user in truyen.editors.all() or 
             request.user.is_staff)):
        messages.error(request, "Bạn không có quyền chỉnh sửa truyện này!")
        return redirect('truyen-detail', slug=truyen.slug)
    
    if request.method == 'POST':
        truyen.ten = request.POST.get('ten', truyen.ten)
        truyen.tac_gia = request.POST.get('tac_gia', truyen.tac_gia)
        truyen.mo_ta = request.POST.get('mo_ta', truyen.mo_ta)
        
        if request.FILES.get('anh'):
            truyen.anh = request.FILES.get('anh')
        
        genres_ids = request.POST.getlist('genres')
        if genres_ids:
            truyen.genres.set(genres_ids)
        
        truyen.save()
        messages.success(request, 'Truyện được cập nhật thành công!')
        return redirect('truyen-detail', slug=truyen.slug)
    
    genres = Genre.objects.all()
    return render(request, 'doctruyen/truyen_edit.html', {
        'truyen': truyen,
        'genres': genres
    })

from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    messages.success(request, "Bạn đã đăng xuất")
    return redirect("truyen-list")
