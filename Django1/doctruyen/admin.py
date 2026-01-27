from django.contrib import admin
from django.db.models import Q
from .models import Truyen, Genre, Volume, Chuong, Comment


class ChuongInline(admin.TabularInline):
    model = Chuong
    extra = 1


class VolumeInline(admin.TabularInline):
    model = Volume
    extra = 1


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Truyen)
class TruyenAdmin(admin.ModelAdmin):
    list_display = ("ten", "tac_gia", "author")
    inlines = [VolumeInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(
            Q(author=request.user) |
            Q(editors=request.user)
        ).distinct()


@admin.register(Volume)
class VolumeAdmin(admin.ModelAdmin):
    list_display = ("so_volume", "ten", "truyen")
    inlines = [ChuongInline]


@admin.register(Chuong)
class ChuongAdmin(admin.ModelAdmin):
    list_display = ("ten", "so_chuong", "volume")
    list_filter = ("volume",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "truyen", "ngay_tao")
