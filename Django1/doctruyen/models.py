from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.conf import settings
from unidecode import unidecode
from django.templatetags.static import static  # Dùng để gọi ảnh mặc định từ static

# =========================
# 1. GENRE (Thể loại)
# =========================
class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.name))
        super().save(*args, **kwargs)


# =========================
# 2. TRUYỆN
# =========================
class Truyen(models.Model):
    STATUS_CHOICES = [
        ('dang_ra', 'Đang ra'),
        ('hoan_thanh', 'Hoàn thành'),
        ('tam_ngung', 'Tạm ngưng'),
    ]
    
    ten = models.CharField(max_length=200)
    tac_gia = models.CharField(max_length=100)
    mo_ta = models.TextField(blank=True)
    anh = models.ImageField(upload_to="truyen/", blank=True, null=True)

    slug = models.SlugField(max_length=200, unique=True, blank=True)
    ngay_dang = models.DateField(auto_now_add=True)
    
    # Trạng thái truyện
    trang_thai = models.CharField(max_length=20, choices=STATUS_CHOICES, default='dang_ra')

    genres = models.ManyToManyField(Genre, blank=True, related_name="truyens")

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="truyen_da_dang"
    )
    editors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="truyen_duoc_uy_quyen"
    )

    class Meta:
        ordering = ["-ngay_dang"]

    def __str__(self):
        return self.ten

    # --- LOGIC Senior: Gọi ảnh mặc định ---
    @property
    def get_anh_url(self):
        """Trả về URL ảnh upload, nếu không có trả về ảnh mặc định trong static/img/"""
        if self.anh and hasattr(self.anh, 'url'):
            return self.anh.url
        # Đảm bảo bạn đã có file này trong static/img/logo.svg hoặc cover_default.jpg
        return static('img/cover_default.jpg')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.ten))
        super().save(*args, **kwargs)

    @property
    def chuong_moi_nhat(self):
        """Lấy số chương mới nhất của truyện"""
        last_chuong = Chuong.objects.filter(
            volume__truyen=self
        ).order_by('-volume__so_volume', '-so_chuong').first()
        return last_chuong.so_chuong if last_chuong else None
    
    @property
    def diem_trung_binh(self):
        """Lấy điểm đánh giá trung bình"""
        ratings = self.ratings.all()
        if not ratings:
            return 0
        return sum([r.diem for r in ratings]) / len(ratings)
    
    @property
    def so_luong_danh_gia(self):
        """Lấy số lượng đánh giá"""
        return self.ratings.count()
    
    @property
    def trang_thai_display(self):
        """Hiển thị trạng thái dạng text"""
        return dict(self.STATUS_CHOICES).get(self.trang_thai, 'Không xác định')

    def get_absolute_url(self):
        return reverse('truyen-detail', kwargs={'slug': self.slug})


# =========================
# 3. VOLUME
# =========================
class Volume(models.Model):
    truyen = models.ForeignKey(
        Truyen,
        on_delete=models.CASCADE,
        related_name="volumes"
    )
    so_volume = models.PositiveIntegerField()
    ten = models.CharField(max_length=200, blank=True)
    mo_ta = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["so_volume"]
        unique_together = ("truyen", "so_volume")

    def __str__(self):
        return f"Volume {self.so_volume} - {self.truyen.ten}"


# =========================
# 4. CHƯƠNG (CHUẨN)
# =========================
class Chuong(models.Model):
    volume = models.ForeignKey(
        Volume,
        on_delete=models.CASCADE,
        related_name="chuongs",
        null=True
    )
    so_chuong = models.PositiveIntegerField()
    ten = models.CharField(max_length=200)
    noi_dung = models.TextField()
    ngay_dang = models.DateTimeField(auto_now_add=True)

    slug = models.SlugField(max_length=250, blank=True)

    class Meta:
        ordering = ["so_chuong"]
        unique_together = ("volume", "slug")

    def __str__(self):
        return f"Chương {self.so_chuong}: {self.ten}"

    def save(self, *args, **kwargs):
        if not self.slug:
            # Tạo slug bao gồm cả số chương để tránh trùng lặp
            self.slug = slugify(unidecode(f"chuong-{self.so_chuong}-{self.ten}"))
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('chuong-detail', kwargs={
            'truyen_slug': self.volume.truyen.slug,
            'chuong_slug': self.slug
        })


# =========================
# 5. COMMENT (Bình luận)
# =========================
class Comment(models.Model):
    truyen = models.ForeignKey(
        Truyen,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    chuong = models.ForeignKey(
        Chuong,
        on_delete=models.CASCADE,
        related_name="comments",
        null=True,
        blank=True
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    noi_dung = models.TextField()
    ngay_tao = models.DateTimeField(auto_now_add=True)
    ngay_chinh_sua = models.DateTimeField(auto_now=True)
    is_pinned = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)

    class Meta:
        ordering = ["-is_pinned", "-ngay_tao"]

    def __str__(self):
        return self.noi_dung[:30]
    
    @property
    def total_likes(self):
        return self.likes.count()


# =========================
# 6. LỊCH SỬ ĐỌC
# =========================
class LichSuDoc(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    truyen = models.ForeignKey(Truyen, on_delete=models.CASCADE)
    chuong_vua_doc = models.ForeignKey(Chuong, on_delete=models.CASCADE)
    ngay_cap_nhat = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "truyen")
        ordering = ["-ngay_cap_nhat"]


# =========================
# 7. USER PROFILE (ĐỠ AVATAR, BANNER)
# =========================
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    banner = models.ImageField(upload_to='banners/', blank=True, null=True)

    def __str__(self):
        return f"Profile của {self.user.username}"


# =========================
# 8. THEO DÕI TRUYỆN (FOLLOW)
# =========================
class Follow(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="follows")
    truyen = models.ForeignKey(Truyen, on_delete=models.CASCADE, related_name="followers")
    ngay_theo_doi = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "truyen")
        ordering = ["-ngay_theo_doi"]

    def __str__(self):
        return f"{self.user.username} follow {self.truyen.ten}"


# =========================
# 9. ĐÁNH GIÁ TRUYỆN (RATING)
# =========================
class Rating(models.Model):
    RATING_CHOICES = [
        (1, '1 ⭐'),
        (2, '2 ⭐'),
        (3, '3 ⭐'),
        (4, '4 ⭐'),
        (5, '5 ⭐'),
    ]
    
    truyen = models.ForeignKey(Truyen, on_delete=models.CASCADE, related_name="ratings")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ratings")
    diem = models.PositiveIntegerField(choices=RATING_CHOICES)
    ngay_tao = models.DateTimeField(auto_now_add=True)
    ngay_cap_nhat = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("truyen", "user")
        ordering = ["-ngay_cap_nhat"]

    def __str__(self):
        return f"{self.user.username} rated {self.truyen.ten} {self.diem}⭐"

    @property
    def get_star_display(self):
        return "⭐" * self.diem


# =========================
# 10. LIKE BÌNH LUẬN (COMMENT LIKE)
# =========================
class CommentLike(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ngay_tao = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("comment", "user")
        ordering = ["-ngay_tao"]

    def __str__(self):
        return f"{self.user.username} like comment"


# =========================
# 11. REPLY BÌNH LUẬN (COMMENT REPLY)
# =========================
class CommentReply(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="replies")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    noi_dung = models.TextField()
    ngay_tao = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-ngay_tao"]

    def __str__(self):
        return f"Reply từ {self.user.username}"


# =========================
# 12. THÔNG BÁO (NOTIFICATION)
# =========================
class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('like_comment', 'Like bình luận'),
        ('reply_comment', 'Reply bình luận'),
        ('mention_comment', 'Mention trong bình luận'),
        ('new_chapter', 'Chương mới'),
        ('new_follow', 'Follow mới'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    noi_dung = models.CharField(max_length=255)
    loai = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    truyen = models.ForeignKey(Truyen, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    chuong = models.ForeignKey(Chuong, on_delete=models.CASCADE, null=True, blank=True)
    user_from = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications_sent", null=True, blank=True)
    da_doc = models.BooleanField(default=False)
    ngay_tao = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-ngay_tao"]

    def __str__(self):
        return f"Notification for {self.user.username}: {self.loai}"


# =========================
# 13. BOOKMARK CHƯƠNG (BOOKMARK)
# =========================
class Bookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookmarks")
    chuong = models.ForeignKey(Chuong, on_delete=models.CASCADE, related_name="bookmarks")
    ngay_tao = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "chuong")
        ordering = ["-ngay_tao"]

    def __str__(self):
        return f"{self.user.username} bookmark {self.chuong}"