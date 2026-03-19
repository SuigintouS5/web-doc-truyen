import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.db.models.functions import TruncDay
from datetime import timedelta
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

# Nhớ kiểm tra lại đường dẫn import đúng với cấu trúc thư mục của bạn
from doctruyen.models import Truyen, Chuong, Notification, Report 

def dashboard(request):
    """Trang chủ Admin với biểu đồ và thống kê"""
    # --- 1. Thống kê tổng quan ---
    tong_so_truyen = Truyen.objects.count()
    tong_so_chuong = Chuong.objects.count()
    tong_so_user = User.objects.count()
    
    # Đếm số yêu cầu xóa và báo cáo chưa xử lý (để hiện badge thông báo)
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

def removal_requests(request):
    """Trang danh sách các yêu cầu xóa truyện"""
    yeu_cau_xoa = Notification.objects.filter(loai='delete_request')\
        .select_related('user_from', 'truyen')\
        .order_by('-ngay_tao')
    
    context = {'yeu_cau_xoa': yeu_cau_xoa}
    return render(request, 'admin_all/yeu_cau_xoa.html', context)

def danh_sach_bao_cao(request):
    """Trang hiển thị danh sách báo cáo vi phạm cho Admin"""
    reports_list = Report.objects.select_related('user_report', 'truyen', 'chuong').all().order_by('-ngay_tao')

    # Bộ lọc trạng thái (Chờ xử lý, Đã xử lý...)
    status_filter = request.GET.get('status')
    if status_filter:
        reports_list = reports_list.filter(trang_thai=status_filter)

    # Tìm kiếm theo tên truyện hoặc người báo cáo
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

# --- PHẦN QUAN TRỌNG: API NHẬN DỮ LIỆU TỪ NÚT BẤM BÁO CÁO ---

def gui_bao_cao_api(request, truyen_id):
    """Hàm xử lý khi người dùng nhấn 'Gửi báo cáo' ở trang chi tiết truyện"""
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"status": "error", "message": "Bạn cần đăng nhập để báo cáo!"}, status=403)
        
        try:
            data = json.loads(request.body)
            noi_dung = data.get('noi_dung', '').strip()
            
            if not noi_dung:
                return JsonResponse({"status": "error", "message": "Nội dung không được để trống!"}, status=400)

            truyen = get_object_or_404(Truyen, id=truyen_id)
            
            # Tạo bản ghi báo cáo mới
            Report.objects.create(
                user_report=request.user,
                truyen=truyen,
                noi_dung=noi_dung,
                trang_thai='pending'  # Đảm bảo model Report có field trang_thai
            )
            
            return JsonResponse({"status": "success", "message": "Gửi báo cáo thành công!"})
            
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
            
    return JsonResponse({"status": "error", "message": "Yêu cầu không hợp lệ"}, status=405)