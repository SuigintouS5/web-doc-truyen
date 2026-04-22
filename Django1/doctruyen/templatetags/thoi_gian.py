from django import template
from django.utils.timesince import timesince
from django.utils import timezone

register = template.Library()

@register.filter(name='time_vi')
def time_vi(value):
    if not value:
        return ""
    
    # Lấy khoảng cách thời gian từ lúc đăng đến hiện tại
    now = timezone.now()
    try:
        diff = timesince(value, now)
    except:
        return ""

    # Bảng tra cứu để thay thế từ tiếng Anh sang tiếng Việt
    dic = {
        'minute': 'phút',
        'hour': 'giờ',
        'day': 'ngày',
        'week': 'tuần',
        'month': 'tháng',
        'year': 'năm',
        's': '',      # Xóa chữ 's' ở số nhiều (ví dụ: hours -> hour)
        ',': '',     # Xóa dấu phẩy cho gọn
    }

    # Tiến hành thay thế
    result = diff
    for en, vi in dic.items():
        result = result.replace(en, vi)

    # Cắt bỏ khoảng trắng thừa và trả về
    return result.strip()