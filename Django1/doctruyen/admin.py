from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Q
from .models import Truyen, Genre, Chuong, Comment


# =========================
# INLINE CHƯƠNG
# =========================
class ChuongInline(admin.TabularInline):
    model = Chuong
    extra = 1
    fields = ("so_chuong", "ten", "ngay_dang")
    readonly_fields = ("ngay_dang",)


# =========================
# GENRE
# =========================
@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


# =========================
# TRUYỆN (PHÂN QUYỀN CHÍNH)
# =========================
@admin.register(Truyen)
class TruyenAdmin(admin.ModelAdmin):
    list_display = ("ten", "tac_gia", "author", "thumbnail", "slug", "ngay_dang")
    search_fields = ("ten", "tac_gia")
    list_filter = ("genres", "ngay_dang", "author")
    ordering = ("-ngay_dang",)
    prepopulated_fields = {"slug": ("ten",)}
    filter_horizontal = ("genres", "editors")
    inlines = [ChuongInline]

    fieldsets = (
        ("Thông tin truyện", {
            "fields": ("ten", "tac_gia", "mo_ta", "anh", "genres")
        }),
        ("Phân quyền", {
            "fields": ("author", "editors"),
            "description": "Author là người đăng chính, Editors là người được sửa"
        }),
        ("SEO", {
            "fields": ("slug",)
        }),
    )

    # -------------------------
    # HIỂN THỊ ẢNH
    # -------------------------
    def thumbnail(self, obj):
        if obj.anh:
            return format_html(
                '<img src="{}" style="height:60px; border-radius:4px;" />',
                obj.anh.url
            )
        return "-"
    thumbnail.short_description = "Ảnh"

    # -------------------------
    # TỰ GÁN AUTHOR = USER ĐĂNG NHẬP
    # -------------------------
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.author = request.user
        super().save_model(request, obj, form, change)

    # -------------------------
    # CHỈ THẤY TRUYỆN CÓ QUYỀN
    # -------------------------
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(
            Q(author=request.user) |
            Q(editors=request.user)
        ).distinct()

    # -------------------------
    # KHÓA FIELD AUTHOR
    # -------------------------
    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return ("author",)
        return ()


# =========================
# CHƯƠNG
# =========================
@admin.register(Chuong)
class ChuongAdmin(admin.ModelAdmin):
    list_display = ("ten", "truyen", "so_chuong", "ngay_dang")
    list_filter = ("truyen", "ngay_dang")
    search_fields = ("ten", "truyen__ten")
    prepopulated_fields = {"slug": ("ten",)}

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(
            Q(truyen__author=request.user) |
            Q(truyen__editors=request.user)
        )


# =========================
# COMMENT
# =========================
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "truyen", "ngay_tao")
    list_filter = ("ngay_tao",)
    search_fields = ("user__username", "truyen__ten", "noi_dung")
