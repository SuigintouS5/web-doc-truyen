from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Q
from .models import (
    User, Profile, SocialLink, Truyen, Genre, 
    Volume, Chuong, Comment, Rating, Follow, 
    Notification, LichSuDoc, Report
)

# 1. QUẢN LÝ USER & PROFILE
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Thông tin mở rộng (Profile)'

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('email', 'username', 'is_staff', 'is_active')
    ordering = ('email',)
    # Hiển thị các trường trong trang chỉnh sửa User
    fieldsets = UserAdmin.fieldsets + (
        ('Thông tin định danh mới', {'fields': ('email_field',)}), # Nếu bạn muốn tùy chỉnh thêm
    )

# 2. INLINES CHO TRUYỆN
class ChuongInline(admin.TabularInline):
    model = Chuong
    extra = 1
    fields = ('so_chuong', 'ten', 'slug')

class VolumeInline(admin.TabularInline):
    model = Volume
    extra = 1

# 3. QUẢN LÝ TRUYỆN
@admin.register(Truyen)
class TruyenAdmin(admin.ModelAdmin):
    list_display = ("ten", "tac_gia", "author", "trang_thai")
    list_filter = ("trang_thai", "story_type")
    search_fields = ("ten", "tac_gia")
    inlines = [VolumeInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # SỬA: Đổi 'editors' thành 'collaborators' cho khớp với Model mới
        return qs.filter(
            Q(author=request.user) |
            Q(collaborators=request.user)
        ).distinct()

# 4. QUẢN LÝ NỘI DUNG CHƯƠNG
@admin.register(Volume)
class VolumeAdmin(admin.ModelAdmin):
    list_display = ("so_volume", "ten", "truyen")
    inlines = [ChuongInline]

@admin.register(Chuong)
class ChuongAdmin(admin.ModelAdmin):
    list_display = ("ten", "so_chuong", "volume")
    list_filter = ("volume__truyen",) # Lọc chương theo truyện cho dễ nhìn
    search_fields = ("ten",)

# 5. CÁC HỆ THỐNG TƯƠNG TÁC & BÁO CÁO
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "truyen", "ngay_tao", "is_pinned")

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("user_report", "truyen", "trang_thai", "ngay_tao")
    list_filter = ("trang_thai",)

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")

# Đăng ký nhanh các model còn lại
admin.site.register(Rating)
admin.site.register(Follow)
admin.site.register(Notification)
admin.site.register(LichSuDoc)
admin.site.register(SocialLink)