from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.text import slugify
from django.db import models
from django.views.decorators.csrf import csrf_exempt
from .models import (
    Truyen, Genre, Comment, Chuong, LichSuDoc, Volume,
    Follow, Rating, CommentLike, CommentReply, Notification, Bookmark
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
    truyen = get_object_or_404(Truyen, id=truyen_id)
    if not (request.user == truyen.author or request.user in truyen.editors.all() or request.user.is_staff):
        return JsonResponse({"status": "error", "message": "Không có quyền"}, status=403)
    if request.method == "POST":
        ten = request.POST.get('ten', '').strip()
        mo_ta = request.POST.get('mo_ta', '').strip()
        last_vol = truyen.volumes.order_by('so_volume').last()
        next_no = (last_vol.so_volume + 1) if last_vol else 1
        Volume.objects.create(truyen=truyen, ten=ten, mo_ta=mo_ta, so_volume=next_no)
        return JsonResponse({"status": "success"})

@login_required
def edit_volume_ajax(request, vol_id):
    vol = get_object_or_404(Volume, id=vol_id)
    if request.method == "POST":
        vol.ten = request.POST.get('ten', '').strip()
        vol.mo_ta = request.POST.get('mo_ta', '').strip()
        vol.save()
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "success", "ten": vol.ten, "mo_ta": vol.mo_ta})

@login_required
def delete_volume_ajax(request, vol_id):
    vol = get_object_or_404(Volume, id=vol_id)
    vol.delete()
    return JsonResponse({"status": "success"})

@login_required
def add_chapter_ajax(request, vol_id):
    vol = get_object_or_404(Volume, id=vol_id)
    if request.method == "POST":
        ten = request.POST.get('ten', '').strip()
        so_chuong = request.POST.get('so_chuong')
        noi_dung = request.POST.get('noi_dung', '').strip()
        if not so_chuong:
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

@login_required
def get_chapter(request, chuong_id):
    c = get_object_or_404(Chuong, id=chuong_id)
    return JsonResponse({"status": "success", "ten": c.ten, "so_chuong": c.so_chuong, "noi_dung": c.noi_dung})

@login_required
def edit_chapter_ajax(request, chuong_id):
    c = get_object_or_404(Chuong, id=chuong_id)
    if request.method == "POST":
        c.ten = request.POST.get('ten', '').strip()
        c.so_chuong = request.POST.get('so_chuong')
        c.noi_dung = request.POST.get('noi_dung', '').strip()
        c.slug = slugify(c.ten)
        c.save()
        return JsonResponse({"status": "success"})

@login_required
def delete_chapter_ajax(request, chuong_id):
    c = get_object_or_404(Chuong, id=chuong_id)
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

@login_required
def profile_view(request):
    return render(request, 'doctruyen/profile.html', {
        'truyen_dang': request.user.truyen_da_dang.all(),
        'truyen_edit': request.user.truyen_duoc_uy_quyen.all(),
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

@login_required
def truyen_create(request):
    if request.method == 'POST':
        new_truyen = Truyen.objects.create(
            ten=request.POST.get('ten'), tac_gia=request.POST.get('tac_gia'),
            mo_ta=request.POST.get('mo_ta'), anh=request.FILES.get('anh'), author=request.user 
        )
        new_truyen.genres.set(request.POST.getlist('genres'))
        return redirect('profile') 
    return render(request, 'doctruyen/themtruyen.html', {'genres': Genre.objects.all(), 'is_create': True})

@login_required
def truyen_edit(request, slug):
    truyen = get_object_or_404(Truyen, slug=slug)
    if request.method == 'POST':
        truyen.ten = request.POST.get('ten')
        truyen.tac_gia = request.POST.get('tac_gia')
        if request.FILES.get('anh'): truyen.anh = request.FILES.get('anh')
        truyen.genres.set(request.POST.getlist('genres'))
        truyen.save()
    return render(request, 'doctruyen/truyen_edit.html', {
        'truyen': truyen, 'genres': Genre.objects.all(),
        'volumes': truyen.volumes.all().prefetch_related('chuongs')
    })

@login_required
def lich_su_view(request):
    ds_lich_su = LichSuDoc.objects.filter(user=request.user).select_related('truyen', 'chuong_vua_doc')
    return render(request, 'doctruyen/history.html', {'ds_lich_su': ds_lich_su})

# =========================
# 5. PROFILE - SỬA THÔNG TIN & ĐỔI MẬT KHẨU
# =========================

@login_required
def profile_detail_view(request):
    """Hiển thị trang chi tiết hồ sơ cá nhân"""
    return render(request, 'doctruyen/profile_detail.html', {
        'user': request.user
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
            
            # Validation
            errors = {}
            if not username:
                errors['username'] = 'Tên đăng nhập không được rỗng'
            elif username != request.user.username and User.objects.filter(username=username).exists():
                errors['username'] = 'Tên đăng nhập đã tồn tại'
            
            if not email:
                errors['email'] = 'Email không được rỗng'
            elif email != request.user.email and User.objects.filter(email=email).exists():
                errors['email'] = 'Email đã tồn tại'
            elif '@' not in email:
                errors['email'] = 'Email không hợp lệ'
            
            if errors:
                return JsonResponse({'status': 'error', 'errors': errors}, status=400)
            
            # Update
            request.user.username = username
            request.user.email = email
            request.user.save()
            
            return JsonResponse({'status': 'success', 'message': 'Cập nhật thông tin thành công'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Phương thức không hỗ trợ'}, status=405)

@login_required
def change_password_ajax(request):
    """AJAX: Đổi mật khẩu"""
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            old_password = data.get('old_password', '')
            new_password = data.get('new_password', '')
            confirm_password = data.get('confirm_password', '')
            
            # Validation
            errors = {}
            if not request.user.check_password(old_password):
                errors['old_password'] = 'Mật khẩu cũ không chính xác'
            
            if len(new_password) < 6:
                errors['new_password'] = 'Mật khẩu mới phải có ít nhất 6 ký tự'
            
            if new_password != confirm_password:
                errors['confirm_password'] = 'Mật khẩu mới không trùng khớp'
            
            if errors:
                return JsonResponse({'status': 'error', 'errors': errors}, status=400)
            
            # Update password
            request.user.set_password(new_password)
            request.user.save()
            
            return JsonResponse({'status': 'success', 'message': 'Đổi mật khẩu thành công'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Phương thức không hỗ trợ'}, status=405)


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
    """Trang tìm kiếm truyện"""
    query = request.GET.get('q', '').strip()
    
    # Filters
    tac_gia = request.GET.get('tac_gia', '').strip()
    trang_thai = request.GET.get('trang_thai', '')
    genres = request.GET.getlist('genres')
    
    # Base queryset
    truyens = Truyen.objects.all()
    
    # Text search
    if query:
        truyens = truyens.filter(
            models.Q(ten__icontains=query) | 
            models.Q(tac_gia__icontains=query) |
            models.Q(mo_ta__icontains=query)
        )
    
    # Filter by tác giả
    if tac_gia:
        truyens = truyens.filter(tac_gia__icontains=tac_gia)
    
    # Filter by trang thái
    if trang_thai:
        truyens = truyens.filter(trang_thai=trang_thai)
    
    # Filter by genres
    if genres:
        truyens = truyens.filter(genres__slug__in=genres).distinct()
    
    # Get all genres for filter
    all_genres = Genre.objects.all()
    
    context = {
        'query': query,
        'truyens': truyens,
        'all_genres': all_genres,
        'tac_gia_filter': tac_gia,
        'trang_thai_filter': trang_thai,
        'genres_filter': genres,
        'count': truyens.count()
    }
    
    return render(request, 'doctruyen/search.html', context)