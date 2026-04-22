import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages  
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib.auth import get_user_model  # Sửa lỗi Manager
from django.db.models import Count, Q
from django.db.models.functions import TruncDay
from datetime import timedelta
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth.decorators import user_passes_test
from doctruyen.models import Truyen, Chuong, Notification, Report , Genre

# Khởi tạo model User đúng (trỏ về doctruyen.User)
User = get_user_model()

def superuser_required(view_func):
    return user_passes_test(lambda u: u.is_superuser)(view_func)

@superuser_required
def dashboard(request):
    """Trang chủ Admin với biểu đồ và thống kê"""
    # --- 1. Thống kê tổng quan ---
    tong_so_truyen = Truyen.objects.count()
    tong_so_chuong = Chuong.objects.count()
    tong_so_user = User.objects.count()
    
    # Đếm số yêu cầu xóa và báo cáo chưa xử lý
    so_yeu_cau_cho = Notification.objects.filter(loai='delete_request').count()
    so_bao_cao_cho = Report.objects.filter(trang_thai='pending').count()

    # --- 2. Dữ liệu Biểu đồ (7 ngày qua) ---
    today = timezone.now().date()
    seven_days_ago = today - timedelta(days=6)
    stats = Chuong.objects.filter(ngay_dang__date__gte=seven_days_ago) \
        .annotate(day=TruncDay('ngay_dang')) \
        .values('day') \
        .annotate(count=Count('id')) \
        .order_by('day')

    labels = []
    data_points = []
    for i in range(7):
        current_day = seven_days_ago + timedelta(days=i)
        labels.append(current_day.strftime('%d/%m'))
        count = next((entry['count'] for entry in stats if entry['day'].date() == current_day), 0)
        data_points.append(count)

    # --- 3. Hoạt động gần đây ---
    recent_actions = Notification.objects.select_related('user_from', 'truyen').all().order_by('-ngay_tao')[:6]

    context = {
        'tong_so_truyen': tong_so_truyen,
        'tong_so_chuong': tong_so_chuong,
        'tong_so_user': tong_so_user,
        'so_yeu_cau_cho': so_yeu_cau_cho,
        'so_bao_cao_cho': so_bao_cao_cho,
        'chart_labels': json.dumps(labels),
        'chart_data': json.dumps(data_points),
        'recent_actions': recent_actions,
    }
    return render(request, 'admin_all/base_admin.html', context)

@superuser_required
def removal_requests(request):
    """Trang danh sách các yêu cầu xóa truyện với phân trang"""
    status_filter = request.GET.get('status')
    search_query = request.GET.get('search')
    
    yeu_cau_list = Notification.objects.filter(loai='delete_request')\
        .select_related('user_from', 'truyen')\
        .order_by('-ngay_tao')

    # Lọc theo trạng thái (Nếu có)
    if status_filter:
        yeu_cau_list = yeu_cau_list.filter(status=status_filter)
    
    # Tìm kiếm theo tên truyện (Nếu có)
    if search_query:
        yeu_cau_list = yeu_cau_list.filter(truyen__ten__icontains=search_query)

    # Phân trang (mỗi trang 10 yêu cầu)
    paginator = Paginator(yeu_cau_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj, # HTML dùng biến này để lặp và phân trang
        'status_filter': status_filter,
        'search_query': search_query,
    }
    return render(request, 'admin_all/yeu_cau_xoa.html', context)

@superuser_required
def danh_sach_bao_cao(request):
    """Trang hiển thị danh sách báo cáo vi phạm cho Admin"""
    reports_list = Report.objects.select_related('user_report', 'truyen', 'chuong').all().order_by('-ngay_tao')

    # Bộ lọc trạng thái
    status_filter = request.GET.get('status')
    if status_filter:
        reports_list = reports_list.filter(trang_thai=status_filter)

    # Tìm kiếm
    search_query = request.GET.get('search')
    if search_query:
        reports_list = reports_list.filter(
            Q(truyen__ten__icontains=search_query) | 
            Q(user_report__username__icontains=search_query)
        )

    # Phân trang
    paginator = Paginator(reports_list, 10)
    page_number = request.GET.get('page')
    reports = paginator.get_page(page_number)

    context = {
        'reports': reports,
        'status_filter': status_filter,
        'search_query': search_query,
    }
    return render(request, 'admin_all/bao_cao_vi_pham.html', context)

@login_required
def api_gui_bao_cao(request, truyen_id):
    """Xử lý API nhận báo cáo từ người dùng"""
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"status": "error", "message": "Bạn cần đăng nhập!"}, status=403)
        
        try:
            data = json.loads(request.body)
            noi_dung = data.get('noi_dung', '').strip()
            
            if not noi_dung:
                return JsonResponse({"status": "error", "message": "Nội dung trống!"}, status=400)

            truyen = get_object_or_404(Truyen, id=truyen_id)
            
            Report.objects.create(
                user_report=request.user,
                truyen=truyen,
                ly_do=noi_dung,
                trang_thai='pending'
            )
            
            return JsonResponse({"status": "success", "message": "Gửi báo cáo thành công!"})
            
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
            
    return JsonResponse({"status": "error", "message": "Yêu cầu không hợp lệ"}, status=405)

@superuser_required
def quan_ly_thanh_vien(request):
    """Trang danh sách thành viên"""
    search_query = request.GET.get('search', '')
    users_list = User.objects.all().order_by('-date_joined')

    if search_query:
        users_list = users_list.filter(
            Q(username__icontains=search_query) | 
            Q(email__icontains=search_query)
        )

    paginator = Paginator(users_list, 15)
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)

    return render(request, 'admin_all/quan_ly_thanh_vien.html', {'users': users, 'search_query': search_query})

@superuser_required
def quan_ly_truyen(request):
    query = request.GET.get('search', '')
    
    # Lấy danh sách truyện, đếm số lượng volume kèm theo
    truyen_list = Truyen.objects.select_related('author').annotate(
        num_volumes=Count('volumes')
    ).all().order_by('-ngay_dang')

    if query:
        truyen_list = truyen_list.filter(
            Q(ten__icontains=query) | 
            Q(tac_gia__icontains=query) | 
            Q(author__username__icontains=query)
        )
    
    paginator = Paginator(truyen_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'admin_all/quan_ly_truyen.html', {
        'page_obj': page_obj,
        'search_query': query
    })

@superuser_required
def xu_ly_yeu_cau_xoa(request, notification_id):
    noti = get_object_or_404(Notification, id=notification_id, loai='delete_request')
    
    if request.method == "POST":
        action = request.POST.get('action')
        
        if action == 'accept':
            if noti.truyen:
                ten_truyen = noti.truyen.ten 
                truyen_to_delete = noti.truyen
                
                noti.status = 'ACCEPTED'
                noti.truyen = None 
                noti.save()
                
                truyen_to_delete.delete()
                messages.success(request, f"Đã xóa vĩnh viễn truyện '{ten_truyen}' thành công!")
            
        elif action == 'decline':
            noti.status = 'DECLINED'
            noti.save()
            messages.warning(request, "Đã từ chối yêu cầu xóa truyện.")

    return redirect('admin_yeu_cau_xoa')

@superuser_required
@require_POST
def xu_ly_bao_cao_admin(request, report_id):
    """Xử lý duyệt hoặc bác bỏ báo cáo từ giao diện Admin"""
    try:
        data = json.loads(request.body)
        action = data.get('action') # Nhận 'resolve' hoặc 'reject' từ JS fetch
        report = get_object_or_404(Report, id=report_id)

        if action == 'resolve':
            report.trang_thai = 'resolved'
        elif action == 'reject':
            report.trang_thai = 'rejected'
        
        report.save()
        return JsonResponse({'status': 'success', 'message': 'Cập nhật trạng thái thành công!'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    

@superuser_required
@require_POST
def admin_xoa_truyen(request, slug):
    """Xóa vĩnh viễn truyện dựa trên slug"""
    truyen = get_object_or_404(Truyen, slug=slug)
    ten_truyen = truyen.ten
    
    try:
        truyen.delete()
        return JsonResponse({
            'status': 'success', 
            'message': f'Đã xóa vĩnh viễn truyện "{ten_truyen}" thành công.'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error', 
            'message': 'Không thể xóa truyện này do lỗi hệ thống.'
        }, status=500)

@superuser_required
def xoa_thanh_vien(request, user_id):
    """Xóa vĩnh viễn tài khoản người dùng"""
    if request.method == "POST":
        target_user = get_object_or_404(User, id=user_id)
        
        # Không cho phép tự xóa chính mình
        if target_user == request.user:
            messages.error(request, "Bạn không thể tự xóa chính mình!")
        else:
            email_da_xoa = target_user.email
            target_user.delete() # Xóa vĩnh viễn
            messages.success(request, f"Đã xóa vĩnh viễn tài khoản: {email_da_xoa}")
            
    return redirect('quan_ly_thanh_vien')

@superuser_required
def thay_doi_quyen_admin(request, user_id):
    """Bật/Tắt quyền Superuser"""
    if request.method == "POST":
        target_user = get_object_or_404(User, id=user_id)
        
        if target_user == request.user:
            messages.error(request, "Bạn không thể tự hạ quyền của mình!")
        else:
            # Đảo ngược quyền: Nếu đang admin -> user, nếu user -> admin
            is_admin = not target_user.is_superuser
            target_user.is_superuser = is_admin
            target_user.is_staff = is_admin
            target_user.save()
            
            role = "Quản trị viên" if is_admin else "Người dùng"
            messages.success(request, f"Đã chuyển {target_user.email} sang quyền {role}")
            
    return redirect('quan_ly_thanh_vien')

def quan_ly_the_loai(request):
    # Lấy danh sách thể loại sắp xếp theo tên (theo ordering trong Meta của bạn)
    ds_the_loai = Genre.objects.all()
    
    if request.method == 'POST':
        ten_the_loai = request.POST.get('name')
        if ten_the_loai:
            # Kiểm tra xem tên đã tồn tại chưa để tránh lỗi unique
            if Genre.objects.filter(name=ten_the_loai).exists():
                messages.error(request, f"Thể loại '{ten_the_loai}' đã tồn tại!")
            else:
                # Hàm save() của bạn đã có tự động tạo slugify(unidecode(name))
                Genre.objects.create(name=ten_the_loai)
                messages.success(request, f"Đã thêm thể loại: {ten_the_loai}")
            return redirect('admin_the_loai')

    return render(request, 'admin_all/quan_ly_the_loai.html', {
        'ds_the_loai': ds_the_loai
    })

# Hàm xóa thể loại
def xoa_the_loai(request, genre_id):
    genre = get_object_or_404(Genre, id=genre_id)
    ten_xoa = genre.name
    genre.delete()
    messages.success(request, f"Đã xóa thành công thể loại: {ten_xoa}")
    return redirect('admin_the_loai')