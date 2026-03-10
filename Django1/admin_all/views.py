import json
from django.shortcuts import render
from doctruyen.models import Truyen, Chuong, Notification, Report # Nhớ đúng tên Model Report
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.db.models.functions import TruncDay
from datetime import timedelta
from django.utils import timezone
from django.core.paginator import Paginator

def dashboard(request):
    # --- 1. Thống kê tổng quan ---
    tong_so_truyen = Truyen.objects.count()
    tong_so_chuong = Chuong.objects.count()
    tong_so_user = User.objects.count()
    # Lấy yêu cầu xóa từ Notification
    so_yeu_cau_cho = 0

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
        'chart_labels': json.dumps(labels),
        'chart_data': json.dumps(data_points),
        'recent_actions': recent_actions,
    }
    return render(request, 'admin_all/base_admin.html', context)

def removal_requests(request):
    """Trang danh sách các yêu cầu xóa truyện (lấy từ Notification)"""
    yeu_cau_xoa = Notification.objects.filter(loai='delete_request')\
        .select_related('user_from', 'truyen')\
        .order_by('-ngay_tao')
    
    context = {
        'yeu_cau_xoa': yeu_cau_xoa,
    }
    return render(request, 'admin_all/yeu_cau_xoa.html', context)

def danh_sach_bao_cao(request):
    """Trang quản lý báo cáo vi phạm (lấy từ model Report)"""
    # 1. Lấy tất cả báo cáo, dùng select_related để tối ưu hóa truy vấn SQL
    reports_list = Report.objects.select_related('user_report', 'truyen', 'chuong').all().order_by('-ngay_tao')

    # 2. Xử lý bộ lọc trạng thái (nếu có)
    status_filter = request.GET.get('status')
    if status_filter:
        reports_list = reports_list.filter(trang_thai=status_filter)

    # 3. Xử lý tìm kiếm nâng cao dùng Q (Search theo tên truyện hoặc tên người báo cáo)
    search_query = request.GET.get('search')
    if search_query:
        reports_list = reports_list.filter(
            Q(truyen__ten__icontains=search_query) | 
            Q(user_report__username__icontains=search_query)
        )

    # 4. Phân trang (Pagination) - Mỗi trang 10 báo cáo
    paginator = Paginator(reports_list, 10)
    page_number = request.GET.get('page')
    reports = paginator.get_page(page_number)

    context = {
        'reports': reports,
        'status_filter': status_filter,
        'search_query': search_query,
    }
    
    return render(request, 'admin_all/bao_cao_vi_pham.html', context)