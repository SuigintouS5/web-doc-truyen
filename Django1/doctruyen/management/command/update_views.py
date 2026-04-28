from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta
from doctruyen.models import Truyen, ViewStatistic

class Command(BaseCommand):
    help = 'Cập nhật chỉ số view_tuan và view_thang cho toàn bộ truyện'

    def handle(self, *args, **options):
        today = timezone.now().date()
        tuan_ago = today - timedelta(days=7)
        thang_ago = today - timedelta(days=30)

        truyens = Truyen.objects.all()
        for t in truyens:
            # Tính tổng view 7 ngày qua từ bảng thống kê chi tiết
            v_tuan = ViewStatistic.objects.filter(
                truyen=t, 
                date__gte=tuan_ago
            ).aggregate(total=Sum('count'))['total'] or 0
            
            # Tính tổng view 30 ngày qua
            v_thang = ViewStatistic.objects.filter(
                truyen=t, 
                date__gte=thang_ago
            ).aggregate(total=Sum('count'))['total'] or 0

            # Cập nhật vào model Truyen
            t.view_tuan = v_tuan
            t.view_thang = v_thang
            t.save(update_fields=['view_tuan', 'view_thang'])
            
        self.stdout.write(self.style.SUCCESS('Đã cập nhật chỉ số Ranking thành công!'))