from doctruyen.models import Notification

def notification_count(request):
    if request.user.is_authenticated:
        # 1. Nhóm thông báo Chương mới/Follow (Trái tim) - Giữ nguyên
        unread_follow = Notification.objects.filter(
            user=request.user,
            da_doc=False,
            loai__in=['new_chapter']
        ).count()

        # 2. Nhóm thông báo Hệ thống (Cái chuông) 
        # Cách này sẽ đếm TẤT CẢ thông báo chưa đọc TRỪ các loại đã đếm ở trên
        unread_bell = Notification.objects.filter(
            user=request.user,
            da_doc=False
        ).exclude(
            loai__in=['new_chapter']
        ).count()

        return {
            'unread_bell_count': unread_bell,
            'unread_follow_count': unread_follow
        }
    return {
        'unread_bell_count': 0, 
        'unread_follow_count': 0
    }