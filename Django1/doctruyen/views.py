from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.text import slugify
from django.db import models, transaction, IntegrityError
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import (
    Truyen, Genre, Comment, Chuong, LichSuDoc, Volume,
    Follow, Rating, CommentLike, CommentReply, Notification, Bookmark,Profile ,SocialLink
)

# =========================
# 1. DANH SÁCH & CHI TIẾT TRUYỆN
# =========================

def truyen_list(request):
    ds = Truyen.objects.all().order_by('-ngay_dang')
    return render(request, 'doctruyen/truyen_list.html', {'ds': ds})

def truyen_detail(request, slug):
    truyen = get_object_or_404(Truyen, slug=slug)
    genres = truyen.genres.all()
    volumes = truyen.volumes.all().prefetch_related('chuongs')
    comments = Comment.objects.filter(truyen=truyen).select_related("user")
    
    can_edit = False
    if request.user.is_authenticated:
        can_edit = (request.user == truyen.author or 
                    request.user in truyen.editors.all() or 
                    request.user.is_staff)

    return render(request, 'doctruyen/truyen_detail.html', {
        'truyen': truyen,
        'genres': genres,
        'volumes': volumes,
        'comments': comments,
        'can_edit': can_edit
    })

def genre_detail(request, slug):
    genre = get_object_or_404(Genre, slug=slug)
    truyens = genre.truyens.all()
    return render(request, 'doctruyen/truyen_list.html', {
        'ds': truyens, 
        'current_genre': genre
    })

# =========================
# 2. XỬ LÝ CHƯƠNG (READER UI)
# =========================

def chuong_detail(request, truyen_slug, chuong_slug):
    chuong = get_object_or_404(Chuong, volume__truyen__slug=truyen_slug, slug=chuong_slug)
    truyen = chuong.volume.truyen
    
    if request.user.is_authenticated:
        LichSuDoc.objects.update_or_create(
            user=request.user,
            truyen=truyen,
            defaults={'chuong_vua_doc': chuong}
        )
    
    volumes_list = truyen.volumes.all().prefetch_related('chuongs')

    # Tìm chương TRƯỚC và SAU
    prev_chuong = Chuong.objects.filter(
        volume__truyen=truyen
    ).filter(
        models.Q(volume__so_volume__lt=chuong.volume.so_volume) | 
        models.Q(volume__so_volume=chuong.volume.so_volume, so_chuong__lt=chuong.so_chuong)
    ).order_by('-volume__so_volume', '-so_chuong').first()

    next_chuong = Chuong.objects.filter(
        volume__truyen=truyen
    ).filter(
        models.Q(volume__so_volume__gt=chuong.volume.so_volume) | 
        models.Q(volume__so_volume=chuong.volume.so_volume, so_chuong__gt=chuong.so_chuong)
    ).order_by('volume__so_volume', 'so_chuong').first()

    return render(request, 'doctruyen/chuong_detail.html', {
        'chuong': chuong,
        'truyen': truyen,
        'volumes_list': volumes_list,
        'prev_chuong': prev_chuong,
        'next_chuong': next_chuong,
    })

# =========================
# 3. AJAX VOLUME & CHƯƠNG
# =========================

@login_required
def add_volume_ajax(request, truyen_id):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Phương thức không hỗ trợ"}, status=405)
    
    truyen = get_object_or_404(Truyen, id=truyen_id)
    if not (request.user == truyen.author or request.user in truyen.editors.all() or request.user.is_staff):
        return JsonResponse({"status": "error", "message": "Không có quyền"}, status=403)
    
    try:
        ten = request.POST.get('ten', '').strip()
        mo_ta = request.POST.get('mo_ta', '').strip()
        last_vol = truyen.volumes.order_by('so_volume').last()
        next_no = (last_vol.so_volume + 1) if last_vol else 1
        Volume.objects.create(truyen=truyen, ten=ten, mo_ta=mo_ta, so_volume=next_no)
        return JsonResponse({"status": "success"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)

@login_required
@login_required
def edit_volume_ajax(request, volume_id):
    vol = get_object_or_404(Volume, id=volume_id)
    # quyền: tác giả, editor hoặc staff
    if not (request.user == vol.truyen.author or
            request.user in vol.truyen.editors.all() or
            request.user.is_staff):
        return JsonResponse({"status": "error", "message": "Không có quyền"}, status=403)

    if request.method == "POST":
        vol.ten = request.POST.get('ten', '').strip()
        vol.mo_ta = request.POST.get('mo_ta', '').strip()
        vol.save()
        return JsonResponse({"status": "success"})
    elif request.method == "GET":
        # GET trả về dữ liệu hiện tại
        return JsonResponse({"status": "success", "ten": vol.ten, "mo_ta": vol.mo_ta})
    else:
        return JsonResponse({"status": "error", "message": "Phương thức không hỗ trợ"}, status=405)


@login_required
def reorder_volumes(request):
    """Ajax: cập nhật thứ tự volume theo danh sách order[]."""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Phương thức không hỗ trợ'}, status=405)

    order = request.POST.getlist('order[]')
    try:
        with transaction.atomic():
            for idx, vol_id in enumerate(order, start=1):
                vol = get_object_or_404(Volume, id=vol_id)
                if not (request.user == vol.truyen.author or
                        request.user in vol.truyen.editors.all() or
                        request.user.is_staff):
                    return JsonResponse({'status': 'error', 'message': 'Không có quyền'}, status=403)
                vol.so_volume = idx
                vol.save()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
def delete_volume_ajax(request, volume_id):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Phương thức không hỗ trợ"}, status=405)
    
    vol = get_object_or_404(Volume, id=volume_id)
    # quyền: tác giả, editor hoặc staff
    if not (request.user == vol.truyen.author or
            request.user in vol.truyen.editors.all() or
            request.user.is_staff):
        return JsonResponse({"status": "error", "message": "Không có quyền"}, status=403)
    
    vol.delete()
    return JsonResponse({"status": "success"})

@login_required
def add_chapter_ajax(request, volume_id):
    # volume_id comes from URL; use consistent name
    vol = get_object_or_404(Volume, id=volume_id)
    # chỉ tác giả, editor hoặc staff có quyền thêm chương
    if not (request.user == vol.truyen.author or
            request.user in vol.truyen.editors.all() or
            request.user.is_staff):
        return JsonResponse({"status": "error", "message": "Không có quyền"}, status=403)

    if request.method != "POST":
        return JsonResponse({"status": "error", "message": 'Phương thức không hỗ trợ'}, status=405)

    try:
        ten = request.POST.get('ten', '').strip()
        so_chuong_raw = request.POST.get('so_chuong', '').strip()
        noi_dung = request.POST.get('noi_dung', '').strip()
        
        # Nếu người dùng không nhập so_chuong, tính tự động
        if so_chuong_raw:
            so_chuong = int(so_chuong_raw)
        else:
            last_c = vol.chuongs.order_by('so_chuong').last()
            so_chuong = (last_c.so_chuong + 1) if last_c else 1
        
        chuong = Chuong.objects.create(volume=vol, ten=ten, so_chuong=so_chuong, noi_dung=noi_dung, slug=slugify(ten))
        
        # Create notifications for all followers of this story
        truyen = vol.truyen
        followers = Follow.objects.filter(truyen=truyen).select_related('user')
        for follow in followers:
            Notification.objects.create(
                user=follow.user,
                noi_dung=f"Truyện '{truyen.ten}' vừa cập nhật chương {so_chuong}: {ten}",
                loai='new_chapter',
                truyen=truyen,
                chuong=chuong,
                user_from=request.user
            )
        
        return JsonResponse({"status": "success"})
    except IntegrityError:
        return JsonResponse({"status": "error", "message": "Chương này đã tồn tại trong tập"}, status=400)
    except ValueError:
        return JsonResponse({"status": "error", "message": "Số chương không hợp lệ"}, status=400)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)

@login_required
def get_chapter_ajax(request, chapter_id):
    c = get_object_or_404(Chuong, id=chapter_id)
    return JsonResponse({
        "status": "success",
        "ten": c.ten,
        "so_chuong": c.so_chuong,
        "noi_dung": c.noi_dung
    })

@login_required
def edit_chapter_ajax(request, chapter_id):
    c = get_object_or_404(Chuong, id=chapter_id)
    # quyền: tác giả, editor hoặc staff
    if not (request.user == c.volume.truyen.author or
            request.user in c.volume.truyen.editors.all() or
            request.user.is_staff):
        return JsonResponse({"status": "error", "message": "Không có quyền"}, status=403)

    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Phương thức không hỗ trợ"}, status=405)
    
    try:
        c.ten = request.POST.get('ten', '').strip()
        c.so_chuong = request.POST.get('so_chuong')
        c.noi_dung = request.POST.get('noi_dung', '').strip()
        c.slug = slugify(c.ten)
        c.save()
        return JsonResponse({"status": "success"})
    except IntegrityError:
        return JsonResponse({"status": "error", "message": "Chương này đã tồn tại trong tập"}, status=400)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)


@login_required
def reorder_chapters(request):
    """Ajax: cập nhật thứ tự chương trong cùng volume."""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Phương thức không hỗ trợ'}, status=405)

    order = request.POST.getlist('order[]')
    try:
        total = len(order)
        with transaction.atomic():
            # gán tạm làm chỉ số lớn để tránh xung đột unique
            for idx, chuong_id in enumerate(order, start=1):
                ch = get_object_or_404(Chuong, id=chuong_id)
                if not (request.user == ch.volume.truyen.author or
                        request.user in ch.volume.truyen.editors.all() or
                        request.user.is_staff):
                    return JsonResponse({'status': 'error', 'message': 'Không có quyền'}, status=403)
                ch.so_chuong = idx + total
                ch.save()
            # sau khi mọi bản ghi đều lớn hơn giá trị cũ, đặt lại số chính xác
            for idx, chuong_id in enumerate(order, start=1):
                ch = get_object_or_404(Chuong, id=chuong_id)
                ch.so_chuong = idx
                ch.save()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
def delete_chapter_ajax(request, chapter_id):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Phương thức không hỗ trợ"}, status=405)
    
    # Đồng bộ tham số chapter_id với urls.py
    c = get_object_or_404(Chuong, id=chapter_id)
    
    # Kiểm tra quyền: tác giả, editor hoặc staff
    if not (c.volume.truyen.author == request.user or
            request.user in c.volume.truyen.editors.all() or
            request.user.is_staff):
        return JsonResponse({"status": "error", "message": "Không có quyền"}, status=403)
    
    c.delete()
    return JsonResponse({"status": "success"})

# =========================
# 4. TÀI KHOẢN & HỆ THỐNG
# =========================

def login_view(request):
    if request.method == "POST":
        user = authenticate(request, username=request.POST.get("username"), password=request.POST.get("password"))
        if user:
            login(request, user)
            return redirect("truyen-list")
    return redirect("truyen-list")

def register_view(request):
    if request.method == "POST":
        u_name = request.POST.get("username")
        if not User.objects.filter(username=u_name).exists():
            User.objects.create_user(username=u_name, password=request.POST.get("password"))
    return redirect("truyen-list")

def logout_view(request):
    logout(request)
    return redirect("truyen-list")


def profile_view(request , username=None):
    if username:
        display_user = get_object_or_404(User, username=username)
    else:
        if not request.user.is_authenticated:
            return redirect('user-login')
        display_user = request.user
    truyen_dang = display_user.truyen_da_dang.all()
    truyen_edit = display_user.truyen_duoc_uy_quyen.all()
    is_owner = (request.user == display_user)
    return render(request, 'doctruyen/profile.html', {
        'display_user': display_user,
        'truyen_dang': display_user.truyen_da_dang.all(),
        'truyen_edit': display_user.truyen_duoc_uy_quyen.all(),
        'is_owner': is_owner, 
    })

@csrf_exempt
@login_required
def update_profile_image_ajax(request):
    if request.method == 'POST':
        profile = getattr(request.user, 'profile', None)
        if not profile:
            return JsonResponse({"status": "error", "message": "Profile không tồn tại"}, status=404)

        changed = False
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
            changed = True
        if 'banner' in request.FILES:
            profile.banner = request.FILES['banner']
            changed = True

        if changed:
            profile.save()
            return JsonResponse({"status": "success", "avatar_url": profile.avatar.url if profile.avatar else ""})
    return JsonResponse({"status": "error"}, status=400)

from django.core.exceptions import PermissionDenied

@login_required
def truyen_create(request):
    if request.method == 'POST':
        # Dùng slugify để tạo đường dẫn từ tên truyện
        ten_truyen = request.POST.get('ten')
        new_truyen = Truyen.objects.create(
            ten=ten_truyen,
            tac_gia=request.POST.get('tac_gia'),
            mo_ta=request.POST.get('mo_ta'),
            anh=request.FILES.get('anh'),
            author=request.user,
            story_type=request.POST.get('story_type'),
            trang_thai=request.POST.get('trang_thai'),
            slug=slugify(ten_truyen) # Đảm bảo có slug để không lỗi URL
        )
        new_truyen.genres.set(request.POST.getlist('genres'))
        messages.success(request, f"Đã tạo truyện '{ten_truyen}' thành công!")
        return redirect('profile') 
    
    return render(request, 'doctruyen/themtruyen.html', {
        'genres': Genre.objects.all(), 
        'is_create': True
    })

@login_required
def truyen_edit(request, slug):
    truyen = get_object_or_404(Truyen, slug=slug)
    
    # KIỂM TRA QUYỀN: Chỉ tác giả, editor hoặc admin mới được sửa
    can_edit = (request.user == truyen.author or 
                request.user in truyen.editors.all() or 
                request.user.is_staff)
    
    if not can_edit:
        messages.error(request, "Bạn không có quyền chỉnh sửa truyện này!")
        return redirect('truyen-detail', slug=slug)

    if request.method == 'POST':
        truyen.ten = request.POST.get('ten')
        truyen.tac_gia = request.POST.get('tac_gia')
        truyen.mo_ta = request.POST.get('mo_ta') 
        # Cập nhật lại slug nếu đổi tên truyện (tùy bạn muốn hay không)
        truyen.slug = slugify(truyen.ten)
        
        # Dùng giá trị cũ nếu người dùng không chọn option mới
        truyen.story_type = request.POST.get('story_type') or truyen.story_type
        truyen.trang_thai = request.POST.get('trang_thai') or truyen.trang_thai 
        
        if request.FILES.get('anh'): 
            truyen.anh = request.FILES.get('anh')
            
        truyen.genres.set(request.POST.getlist('genres'))
        truyen.save()
        
        messages.success(request, "Đã lưu thay đổi thành công!")
        return redirect('truyen-edit', slug=truyen.slug)

    return render(request, 'doctruyen/truyen_edit.html', {
        'truyen': truyen, 
        'genres': Genre.objects.all(),
        'volumes': truyen.volumes.all().prefetch_related('chuongs')
    })
@login_required
def lich_su_view(request):
    ds_lich_su = LichSuDoc.objects.filter(user=request.user).select_related('truyen', 'chuong_vua_doc')
    return render(request, 'doctruyen/history.html', {'ds_lich_su': ds_lich_su})

# =========================
# 5. PROFILE - SỬA THÔNG TIN & ĐỔI MẬT KHẨU
# =========================
from django.contrib.auth import update_session_auth_hash

@login_required
def profile_detail_view(request):
    """Hiển thị trang chi tiết hồ sơ cá nhân"""
    # Đảm bảo Profile luôn tồn tại để tránh lỗi template
    profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, 'doctruyen/profile_detail.html', {
        'user': request.user,
        'profile': profile
    })

@login_required
def update_profile_ajax(request):
    """AJAX: Cập nhật username và email"""
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            username = data.get('username', '').strip()
            email = data.get('email', '').strip()
            
            user = request.user
            errors = {}

            if username != user.username and User.objects.filter(username=username).exists():
                errors['username'] = 'Tên đăng nhập đã tồn tại'
            
            if email != user.email and User.objects.filter(email=email).exists():
                errors['email'] = 'Email đã tồn tại'

            if errors:
                return JsonResponse({'status': 'error', 'errors': errors}, status=400)
            
            user.username = username
            user.email = email
            user.save()
            
            # Giữ trạng thái đăng nhập sau khi đổi username
            update_session_auth_hash(request, user)
            
            return JsonResponse({'status': 'success', 'message': 'Cập nhật thành công'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error'}, status=405)

@login_required
def change_password_ajax(request):
    """AJAX: Đổi mật khẩu"""
    if request.method == 'POST':
        try:
            if request.content_type == 'application/json':
                import json
                data = json.loads(request.body)
            else:
                data = request.POST

            old_password = data.get('old_password', '')
            new_password = data.get('new_password', '')
            
            user = request.user
            if not user.check_password(old_password):
                return JsonResponse({'status': 'error', 'message': 'Mật khẩu cũ không chính xác'}, status=400)
            
            if len(new_password) < 6:
                return JsonResponse({'status': 'error', 'message': 'Mật khẩu mới phải từ 6 ký tự'}, status=400)
            
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error'}, status=405)

@login_required
def update_privacy_ajax(request):
    """AJAX: Cài đặt ẩn/hiện SĐT và Gmail (Khớp với name='update_privacy' trong urls)"""
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            profile = request.user.profile
            profile.hide_phone = data.get('hide_phone', False)
            profile.hide_gmail = data.get('hide_gmail', False)
            profile.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error'}, status=405)

@login_required
def update_profile_extra_ajax(request):
    """AJAX: Cập nhật SĐT, Gmail và MXH (Khớp với name='update_extra' trong urls)"""
    if request.method == 'POST':
        profile = request.user.profile
        profile.phone = request.POST.get('phone', '').strip()
        profile.gmail = request.POST.get('gmail', '').strip()
        profile.save()

        # Cập nhật danh sách mạng xã hội động
        names = request.POST.getlist('social_name[]')
        links = request.POST.getlist('social_link[]')
        
        # Xóa cũ thêm mới để đồng bộ dữ liệu
        profile.social_links.all().delete()
        for name, link in zip(names, links):
            if name and link.strip():
                from .models import SocialLink # Đảm bảo đã import model này
                SocialLink.objects.create(profile=profile, name=name, link=link.strip())

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=405)
# =========================
# 6. PHẦN MỞ RỘNG TRUYỆN DETAIL
# =========================

def read_now_view(request, slug):
    """Redirect tới chương đầu tiên của volume đầu tiên"""
    truyen = get_object_or_404(Truyen, slug=slug)
    
    # Lấy volume đầu tiên
    first_volume = truyen.volumes.order_by('so_volume').first()
    if not first_volume:
        messages.warning(request, 'Truyện này chưa có volume')
        return redirect('truyen-detail', slug=slug)
    
    # Lấy chương đầu tiên trong volume
    first_chuong = first_volume.chuongs.order_by('so_chuong').first()
    if not first_chuong:
        messages.warning(request, 'Volume này chưa có chương')
        return redirect('truyen-detail', slug=slug)
    
    # Cập nhật lịch sử đọc nếu đã đăng nhập
    if request.user.is_authenticated:
        LichSuDoc.objects.update_or_create(
            user=request.user,
            truyen=truyen,
            defaults={'chuong_vua_doc': first_chuong}
        )
    
    return redirect('chuong-detail', truyen_slug=truyen.slug, chuong_slug=first_chuong.slug)


# =========================
# 7. THEO DÕI TRUYỆN (AJAX)
# =========================

@login_required
def toggle_follow_ajax(request, truyen_id):
    """AJAX: Toggle theo dõi truyện"""
    truyen = get_object_or_404(Truyen, id=truyen_id)
    
    follow = Follow.objects.filter(user=request.user, truyen=truyen).first()
    
    if follow:
        follow.delete()
        return JsonResponse({'status': 'success', 'action': 'unfollowed'})
    else:
        Follow.objects.create(user=request.user, truyen=truyen)
        # Create notification for the story author when someone follows
        if request.user != truyen.author:
            Notification.objects.create(
                user=truyen.author,
                noi_dung=f"{request.user.username} đã theo dõi truyện '{truyen.ten}'",
                loai='new_follow',
                truyen=truyen,
                user_from=request.user
            )
        return JsonResponse({'status': 'success', 'action': 'followed'})


@login_required
def is_following_ajax(request, truyen_id):
    """AJAX: Kiểm tra có đang theo dõi không"""
    is_following = Follow.objects.filter(user=request.user, truyen_id=truyen_id).exists()
    return JsonResponse({'is_following': is_following})


# =========================
# 8. ĐÁNH GIÁ TRUYỆN (AJAX)
# =========================

@login_required
def add_rating_ajax(request, truyen_id):
    """AJAX: Thêm hoặc cập nhật đánh giá"""
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            diem = int(data.get('diem'))
            
            if diem < 1 or diem > 5:
                return JsonResponse({'status': 'error', 'message': 'Điểm phải từ 1-5'}, status=400)
            
            truyen = get_object_or_404(Truyen, id=truyen_id)
            
            rating, created = Rating.objects.update_or_create(
                user=request.user,
                truyen=truyen,
                defaults={'diem': diem}
            )
            
            # Lấy điểm trung bình và số lượng đánh giá
            diem_trung_binh = truyen.diem_trung_binh
            so_luong = truyen.so_luong_danh_gia
            
            action = 'created' if created else 'updated'
            return JsonResponse({
                'status': 'success',
                'action': action,
                'diem_trung_binh': round(diem_trung_binh, 1),
                'so_luong': so_luong
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Phương thức không hỗ trợ'}, status=405)


@login_required
def get_user_rating_ajax(request, truyen_id):
    """AJAX: Lấy đánh giá của user"""
    rating = Rating.objects.filter(user=request.user, truyen_id=truyen_id).first()
    if rating:
        return JsonResponse({'diem': rating.diem})
    return JsonResponse({'diem': 0})


# =========================
# 9. BÌNH LUẬN & REPLY (AJAX)
# =========================

@login_required
def add_comment_ajax(request, truyen_id):
    """AJAX: Thêm bình luận mới"""
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            noi_dung = data.get('noi_dung', '').strip()
            chuong_id = data.get('chuong_id', None)
            
            if not noi_dung:
                return JsonResponse({'status': 'error', 'message': 'Bình luận không được rỗng'}, status=400)
            
            truyen = get_object_or_404(Truyen, id=truyen_id)
            chuong = None
            if chuong_id:
                chuong = get_object_or_404(Chuong, id=chuong_id)
            
            comment = Comment.objects.create(
                truyen=truyen,
                chuong=chuong,
                user=request.user,
                noi_dung=noi_dung
            )
            
            return JsonResponse({
                'status': 'success',
                'comment_id': comment.id,
                'username': request.user.username,
                'avatar': comment.user.profile.avatar.url if hasattr(comment.user, 'profile') and comment.user.profile.avatar else '/static/img/avatar.jpg',
                'noi_dung': comment.noi_dung,
                'ngay_tao': comment.ngay_tao.strftime('%Y-%m-%d %H:%M'),
                'chuong_ten': f"Chương {chuong.so_chuong}: {chuong.ten}" if chuong else "Tổng quan",
                'total_likes': 0
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Phương thức không hỗ trợ'}, status=405)


@login_required
@login_required
def like_comment_ajax(request, comment_id):
    """AJAX: Like/Unlike bình luận"""
    comment = get_object_or_404(Comment, id=comment_id)
    
    like = CommentLike.objects.filter(comment=comment, user=request.user).first()
    
    if like:
        like.delete()
        action = 'unliked'
    else:
        CommentLike.objects.create(comment=comment, user=request.user)
        action = 'liked'
        
        # Tạo thông báo nếu không phải author của comment
        if comment.user != request.user:
            Notification.objects.create(
                user=comment.user,
                noi_dung=f"{request.user.username} đã like bình luận của bạn",
                loai='like_comment',
                truyen=comment.truyen,
                comment=comment,
                user_from=request.user
            )
    
    total_likes = comment.total_likes
    return JsonResponse({
        'status': 'success',
        'action': action,
        'total_likes': total_likes
    })


@login_required
def reply_comment_ajax(request, comment_id):
    """AJAX: Reply bình luận"""
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            noi_dung = data.get('noi_dung', '').strip()
            
            if not noi_dung:
                return JsonResponse({'status': 'error', 'message': 'Reply không được rỗng'}, status=400)
            
            comment = get_object_or_404(Comment, id=comment_id)
            
            reply = CommentReply.objects.create(
                comment=comment,
                user=request.user,
                noi_dung=noi_dung
            )
            
            # Tạo thông báo
            if comment.user != request.user:
                Notification.objects.create(
                    user=comment.user,
                    noi_dung=f"{request.user.username} đã reply bình luận của bạn",
                    loai='reply_comment',
                    truyen=comment.truyen,
                    comment=comment,
                    user_from=request.user
                )
            
            return JsonResponse({
                'status': 'success',
                'reply_id': reply.id,
                'username': request.user.username,
                'noi_dung': reply.noi_dung,
                'ngay_tao': reply.ngay_tao.strftime('%Y-%m-%d %H:%M')
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Phương thức không hỗ trợ'}, status=405)


@login_required
def get_comments_ajax(request, truyen_id):
    """AJAX: Lấy danh sách bình luận"""
    truyen = get_object_or_404(Truyen, id=truyen_id)
    comments = Comment.objects.filter(truyen=truyen).select_related('user', 'chuong').prefetch_related('likes', 'replies')
    
    comments_data = []
    for comment in comments:
        replies_data = [
            {
                'id': reply.id,
                'username': reply.user.username,
                'avatar': reply.user.profile.avatar.url if hasattr(reply.user, 'profile') and reply.user.profile.avatar else '/static/img/avatar.jpg',
                'noi_dung': reply.noi_dung,
                'ngay_tao': reply.ngay_tao.strftime('%Y-%m-%d %H:%M')
            }
            for reply in comment.replies.all()
        ]
        
        user_liked = request.user in [like.user for like in comment.likes.all()]
        can_edit = request.user == comment.user or request.user.is_staff
        can_delete = request.user == comment.user or request.user.is_staff
        can_pin = request.user == truyen.author or request.user.is_staff
        
        comments_data.append({
            'id': comment.id,
            'username': comment.user.username,
            'avatar': comment.user.profile.avatar.url if hasattr(comment.user, 'profile') and comment.user.profile.avatar else '/static/img/avatar.jpg',
            'noi_dung': comment.noi_dung,
            'ngay_tao': comment.ngay_tao.strftime('%Y-%m-%d %H:%M'),
            'ngay_chinh_sua': comment.ngay_chinh_sua.strftime('%Y-%m-%d %H:%M') if comment.is_edited else None,
            'total_likes': comment.total_likes,
            'user_liked': user_liked,
            'is_pinned': comment.is_pinned,
            'is_edited': comment.is_edited,
            'chuong_ten': f"Chương {comment.chuong.so_chuong}: {comment.chuong.ten}" if comment.chuong else "Tổng quan",
            'replies': replies_data,
            'can_edit': can_edit,
            'can_delete': can_delete,
            'can_pin': can_pin
        })
    
    return JsonResponse({'comments': comments_data})


# =========================
# 10. BOOKMARK CHƯƠNG (AJAX)
# =========================

@login_required
def toggle_bookmark_ajax(request, chuong_id):
    """AJAX: Toggle bookmark chương"""
    chuong = get_object_or_404(Chuong, id=chuong_id)
    
    bookmark = Bookmark.objects.filter(user=request.user, chuong=chuong).first()
    
    if bookmark:
        bookmark.delete()
        return JsonResponse({'status': 'success', 'action': 'removed'})
    else:
        Bookmark.objects.create(user=request.user, chuong=chuong)
        return JsonResponse({'status': 'success', 'action': 'added'})


@login_required
def is_bookmarked_ajax(request, chuong_id):
    """AJAX: Kiểm tra đã bookmark chưa"""
    is_bookmarked = Bookmark.objects.filter(user=request.user, chuong_id=chuong_id).exists()
    return JsonResponse({'is_bookmarked': is_bookmarked})


# =========================
# 11. THÔNG BÁO (NOTIFICATIONS)
# =========================

@login_required
def get_notifications_ajax(request):
    """AJAX: Lấy thông báo bình luận (bell icon)"""
    notification_types = ['like_comment', 'reply_comment', 'mention_comment']
    notifications = Notification.objects.filter(user=request.user, loai__in=notification_types).select_related('user_from', 'truyen', 'comment')
    
    notifications_data = []
    for notif in notifications:
        link = ''
        if notif.comment and notif.truyen:
            link = f"/truyen/{notif.truyen.slug}/"
        elif notif.truyen:
            link = f"/truyen/{notif.truyen.slug}/"
        
        notifications_data.append({
            'id': notif.id,
            'noi_dung': notif.noi_dung,
            'loai': notif.loai,
            'da_doc': notif.da_doc,
            'ngay_tao': notif.ngay_tao.strftime('%Y-%m-%d %H:%M'),
            'link': link
        })
    
    return JsonResponse({'notifications': notifications_data})


@login_required
def get_follow_notifications_ajax(request):
    """AJAX: Lấy thông báo follow (heart icon)"""
    notification_types = ['new_chapter', 'new_follow']
    notifications = Notification.objects.filter(user=request.user, loai__in=notification_types).select_related('user_from', 'truyen', 'chuong')
    
    notifications_data = []
    for notif in notifications:
        link = ''
        if notif.chuong and notif.truyen:
            link = f"/truyen/{notif.truyen.slug}/{notif.chuong.slug}/"
        elif notif.truyen:
            link = f"/truyen/{notif.truyen.slug}/"
        
        notifications_data.append({
            'id': notif.id,
            'noi_dung': notif.noi_dung,
            'loai': notif.loai,
            'da_doc': notif.da_doc,
            'ngay_tao': notif.ngay_tao.strftime('%Y-%m-%d %H:%M'),
            'link': link
        })
    
    return JsonResponse({'notifications': notifications_data})


@login_required
def count_unread_notifications_ajax(request):
    """AJAX: Đếm thông báo chưa đọc (bell)"""
    notification_types = ['like_comment', 'reply_comment', 'mention_comment']
    count = Notification.objects.filter(user=request.user, loai__in=notification_types, da_doc=False).count()
    return JsonResponse({'count': count})


@login_required
def count_follow_notifications_ajax(request):
    """AJAX: Đếm thông báo follow chưa đọc (heart)"""
    notification_types = ['new_chapter', 'new_follow']
    count = Notification.objects.filter(user=request.user, loai__in=notification_types, da_doc=False).count()
    return JsonResponse({'count': count})


@login_required
def mark_notification_read_ajax(request, notification_id):
    """AJAX: Đánh dấu thông báo là đã đọc"""
    notif = get_object_or_404(Notification, id=notification_id, user=request.user)
    notif.da_doc = True
    notif.save()
    return JsonResponse({'status': 'success'})


@login_required
def create_notification_ajax(request):
    """AJAX: Tạo thông báo (transfer/share/delete_request)
    POST expected: receiver_id, loai, truyen_id (optional), message
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Phương thức không hỗ trợ'}, status=405)

    loai = request.POST.get('loai')
    receiver_id = request.POST.get('receiver_id')
    receiver_username = request.POST.get('receiver_username')
    truyen_id = request.POST.get('truyen_id')
    message = request.POST.get('message', '')

    # For delete_request we don't require a specific receiver.
    if loai != 'delete_request' and not (receiver_id or receiver_username):
        return JsonResponse({'status': 'error', 'message': 'Dữ liệu không hợp lệ'}, status=400)

    from django.contrib.auth import get_user_model
    User = get_user_model()
    receiver = None
    try:
        if receiver_id:
            receiver = User.objects.get(id=receiver_id)
        elif receiver_username:
            receiver = User.objects.get(username=receiver_username)
        else:
            return JsonResponse({'status': 'error', 'message': 'Người nhận không được cung cấp'}, status=400)
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Người nhận không tồn tại'}, status=404)

    truyen = None
    if truyen_id:
        truyen = get_object_or_404(Truyen, id=truyen_id)

    # nếu là delete_request, gửi tới tất cả superusers
    if loai == 'delete_request':
        admins = User.objects.filter(is_superuser=True)
        for admin in admins:
            Notification.objects.create(user=admin, noi_dung=message or f"Yêu cầu xóa truyện: {truyen.ten if truyen else ''}", loai=loai, truyen=truyen, user_from=request.user)
        return JsonResponse({'status': 'success'})

    Notification.objects.create(user=receiver, noi_dung=message or '', loai=loai, truyen=truyen, user_from=request.user)
    return JsonResponse({'status': 'success'})


@login_required
def accept_notification_ajax(request, notification_id):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Phương thức không hỗ trợ'}, status=405)
    notif = get_object_or_404(Notification, id=notification_id)
    if notif.user != request.user and not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': 'Không có quyền'}, status=403)
    if notif.status != 'PENDING':
        return JsonResponse({'status': 'error', 'message': 'Đã xử lý trước đó'}, status=400)

    # Xử lý theo loại
    if notif.loai == 'transfer':
        tr = notif.truyen
        if not tr:
            return JsonResponse({'status': 'error', 'message': 'Truyện không tồn tại'}, status=404)
        old_owner = tr.author
        tr.author = notif.user
        # Add old owner to editors so they can still edit
        tr.editors.add(old_owner)
        tr.save()
        notif.status = 'ACCEPTED'
        notif.save()
        return JsonResponse({'status': 'success'})

    if notif.loai == 'share':
        tr = notif.truyen
        if not tr:
            return JsonResponse({'status': 'error', 'message': 'Truyện không tồn tại'}, status=404)
        tr.collaborators.add(notif.user)
        notif.status = 'ACCEPTED'
        notif.save()
        return JsonResponse({'status': 'success'})

    if notif.loai == 'delete_request':
        if not request.user.is_superuser:
            return JsonResponse({'status': 'error', 'message': 'Chỉ admin mới có quyền'}, status=403)
        tr = notif.truyen
        if tr:
            tr.delete()
        notif.status = 'ACCEPTED'
        notif.save()
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error', 'message': 'Loại thông báo không hỗ trợ'}, status=400)


@login_required
def decline_notification_ajax(request, notification_id):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Phương thức không hỗ trợ'}, status=405)
    notif = get_object_or_404(Notification, id=notification_id)
    if notif.user != request.user and not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': 'Không có quyền'}, status=403)
    if notif.status != 'PENDING':
        return JsonResponse({'status': 'error', 'message': 'Đã xử lý trước đó'}, status=400)
    notif.status = 'DECLINED'
    notif.save()
    return JsonResponse({'status': 'success'})


@login_required
def notifications_view(request):
    # Trang hiển thị thông báo (dành cho người dùng)
    notifs = Notification.objects.filter(user=request.user).select_related('user_from', 'truyen')
    return render(request, 'doctruyen/notifications.html', {'notifications': notifs})



# =========================
# 12. TRANG BOOKMARKS/FOLLOW
# =========================

@login_required
def bookmarks_view(request):
    """Trang đánh dấu với 3 tab: Follow, Bookmark, Thông báo"""
    # Tab 1: Truyện đang theo dõi
    follows = Follow.objects.filter(user=request.user).select_related('truyen')
    truyen_follows = [f.truyen for f in follows]
    
    # Tab 2: Chương đã bookmark
    bookmarks = Bookmark.objects.filter(user=request.user).select_related('chuong', 'chuong__volume', 'chuong__volume__truyen')
    
    # Tab 3: Thông báo
    notifications = Notification.objects.filter(user=request.user).select_related('user_from', 'truyen')
    
    context = {
        'truyen_follows': truyen_follows,
        'bookmarks': bookmarks,
        'notifications': notifications,
    }
    
    return render(request, 'doctruyen/bookmarks.html', context)


# =========================
# 13. EDIT/DELETE/PIN COMMENT
# =========================

@login_required
def edit_comment_ajax(request, comment_id):
    """AJAX: Sửa bình luận"""
    comment = get_object_or_404(Comment, id=comment_id)
    
    if request.user != comment.user and not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': 'Không có quyền'}, status=403)
    
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            noi_dung = data.get('noi_dung', '').strip()
            
            if not noi_dung:
                return JsonResponse({'status': 'error', 'message': 'Nội dung không được rỗng'}, status=400)
            
            comment.noi_dung = noi_dung
            comment.is_edited = True
            comment.save()
            
            return JsonResponse({
                'status': 'success',
                'noi_dung': comment.noi_dung,
                'ngay_chinh_sua': comment.ngay_chinh_sua.strftime('%Y-%m-%d %H:%M')
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Phương thức không hỗ trợ'}, status=405)


@login_required
def delete_comment_ajax(request, comment_id):
    """AJAX: Xóa bình luận"""
    comment = get_object_or_404(Comment, id=comment_id)
    
    if request.user != comment.user and not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': 'Không có quyền'}, status=403)
    
    comment.delete()
    return JsonResponse({'status': 'success', 'message': 'Bình luận đã được xóa'})


@login_required
def pin_comment_ajax(request, comment_id):
    """AJAX: Ghim/bỏ ghim bình luận (dành cho tác giả)"""
    comment = get_object_or_404(Comment, id=comment_id)
    
    # Chỉ tác giả truyện hoặc staff mới được ghim
    if request.user != comment.truyen.author and not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': 'Chỉ tác giả mới được ghim'}, status=403)
    
    comment.is_pinned = not comment.is_pinned
    comment.save()
    
    return JsonResponse({
        'status': 'success',
        'is_pinned': comment.is_pinned
    })


# =========================
# 14. TÌM KIẾM TRUYỆN
# =========================


def search_view(request):
    """Trang tìm kiếm truyện - Chuyên gia tối ưu"""
    query = request.GET.get('q', '').strip()
    tac_gia = request.GET.get('tac_gia', '').strip()
    trang_thai = request.GET.get('trang_thai', '')
    story_type = request.GET.get('story_type', '')
    genres = request.GET.getlist('genres')
    page = request.GET.get('page', 1) # Lấy số trang hiện tại
    
    # Base queryset: Sắp xếp theo ID giảm dần để kết quả phân trang không bị đảo lộn
    truyens = Truyen.objects.all().order_by('-id')
    
    # 1. Tìm kiếm theo văn bản (Đã bỏ mô tả để tránh nhiễu)
    if query:
        truyens = truyens.filter(
            models.Q(ten__icontains=query) | 
            models.Q(tac_gia__icontains=query)
        )
    
    # 2. Lọc theo tác giả (nếu người dùng nhập ô filter riêng)
    if tac_gia:
        truyens = truyens.filter(tac_gia__icontains=tac_gia)
    
    # 3. Lọc theo trạng thái (ongoing, hoan-thanh, tam-dung)
    if trang_thai:
        truyens = truyens.filter(trang_thai=trang_thai)
    
    # 4. Lọc theo thể loại (ManyToMany)
    if genres:
        for genre_slug in genres:
            truyens = truyens.filter(genres__slug=genre_slug)       
        truyens = truyens.distinct()
    
    # --- PHẦN PHÂN TRANG (PAGINATION) ---
    items_per_page = 20 # Số truyện mỗi trang
    paginator = Paginator(truyens, items_per_page)
    
    try:
        truyens_paginated = paginator.page(page)
    except PageNotAnInteger:
        # Nếu ?page=abc không phải số, về trang 1
        truyens_paginated = paginator.page(1)
    except EmptyPage:
        # Nếu ?page=999 vượt quá giới hạn, về trang cuối
        truyens_paginated = paginator.page(paginator.num_pages)
    
    # Lấy danh sách thể loại (chỉ lấy field cần thiết để tiết kiệm RAM)
    all_genres = Genre.objects.only('id', 'name', 'slug')
    
    context = {
        'query': query,
        'truyens': truyens_paginated, # Trả về đối tượng đã phân trang
        'all_genres': all_genres,
        'tac_gia_filter': tac_gia,
        'trang_thai_filter': trang_thai,
        'genres_filter': genres,
        'total_count': paginator.count # Tổng số kết quả tìm thấy
    }
    
    return render(request, 'doctruyen/search.html', context)

