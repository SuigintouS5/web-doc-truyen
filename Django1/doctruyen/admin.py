from django.contrib import admin
from .models import Truyen, Genre


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Truyen)
class TruyenAdmin(admin.ModelAdmin):
    list_display = ("ten", "tac_gia", "thumbnail", "slug", "ngay_dang")
    search_fields = ("ten", "tac_gia")
    ordering = ("-ngay_dang",)
    prepopulated_fields = {"slug": ("ten",)}
    filter_horizontal = ("genres",)

    def thumbnail(self, obj):
        if obj.anh:
            from django.utils.html import format_html
            return format_html('<img src="{}" style="height:60px;" />', obj.anh.url)
        return "-"
    thumbnail.short_description = "Ảnh"




