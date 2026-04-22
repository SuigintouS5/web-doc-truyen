from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.conf import settings
from unidecode import unidecode
from django.templatetags.static import static
from django.contrib.auth.models import AbstractUser

# =================================================
# 1. CUSTOM USER MODEL (Đăng nhập bằng Email)
# =================================================
class User(AbstractUser):
    # Biến Email thành định danh duy nhất
    email = models.EmailField(unique=True, verbose_name="Địa chỉ Email")
    
    # Username lúc này là "Biệt danh", có thể thay đổi và không cần duy nhất
    username = models.CharField(max_length=150, unique=False, blank=True, null=True)

    USERNAME_FIELD = 'email'  # Chỉ định dùng email để đăng nhập
    REQUIRED_FIELDS = ['username'] # Các trường bắt buộc khi tạo superuser

    def __str__(self):
        return self.email

# =================================================
# 2. USER PROFILE (Mở rộng thông tin người dùng)
# =================================================
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    banner = models.ImageField(upload_to='banners/', blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    hide_phone = models.BooleanField(default=False)

    def __str__(self):
        display_name = self.user.username if self.user.username else self.user.email
        return f"Profile của {display_name}"

class SocialLink(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='social_links')
    name = models.CharField(max_length=50) 
    link = models.URLField(max_length=500)

    class Meta:
        verbose_name = "Liên kết mạng xã hội"
        verbose_name_plural = "Các liên kết mạng xã hội"

    def __str__(self):
        return f"{self.name} - {self.profile.user.email}"

# =================================================
# 3. GENRE & TRUYỆN
# =================================================
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

class Truyen(models.Model):
    STATUS_CHOICES = [
        ('ongoing', 'Đang cập nhật'),
        ('hoan_thanh', 'Hoàn thành'),
        ('tam_ngung', 'Tạm ngưng'),
    ]
    STORY_TYPE_CHOICES = [
        ('translated', 'Truyện dịch'),
        ('original', 'Truyện sáng tác'),
        ('ai', 'Truyện AI dịch'),
    ]

    story_type = models.CharField(max_length=20, choices=STORY_TYPE_CHOICES, default='translated', blank=True, null=True)
    ten = models.CharField(max_length=200)
    tac_gia = models.CharField(max_length=100)
    mo_ta = models.TextField(blank=True)
    anh = models.ImageField(upload_to="truyen/", blank=True, null=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    ngay_dang = models.DateField(auto_now_add=True)
    trang_thai = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ongoing')
    genres = models.ManyToManyField(Genre, blank=True, related_name="truyens")
    
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="truyen_da_dang")
    collaborators = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="truyen_hop_tac")

    class Meta:
        ordering = ["-ngay_dang"]

    def __str__(self):
        return self.ten

    @property
    def get_anh_url(self):
        if self.anh and hasattr(self.anh, 'url'):
            return self.anh.url
        return static('img/cover_default.jpg')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.ten))
        super().save(*args, **kwargs)

    @property
    def chuong_moi_nhat(self):
        last_chuong = Chuong.objects.filter(volume__truyen=self).order_by('-volume__so_volume', '-so_chuong').first()
        return last_chuong.so_chuong if last_chuong else None

    @property
    def diem_trung_binh(self):
        ratings = self.ratings.all()
        if not ratings: return 0
        return sum([r.diem for r in ratings]) / len(ratings)

    @property
    def trang_thai_display(self):
        return dict(self.STATUS_CHOICES).get(self.trang_thai, 'Không xác định')

    def get_absolute_url(self):
        return reverse('truyen-detail', kwargs={'slug': self.slug})

# =================================================
# 4. VOLUME & CHƯƠNG
# =================================================
class Volume(models.Model):
    truyen = models.ForeignKey(Truyen, on_delete=models.CASCADE, related_name="volumes")
    so_volume = models.PositiveIntegerField()
    ten = models.CharField(max_length=200, blank=True)
    mo_ta = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["so_volume"]
        unique_together = ("truyen", "so_volume")

    def __str__(self):
        return f"Volume {self.so_volume} - {self.truyen.ten}"

class Chuong(models.Model):
    volume = models.ForeignKey(Volume, on_delete=models.CASCADE, related_name="chuongs", null=True)
    so_chuong = models.PositiveIntegerField()
    ten = models.CharField(max_length=200, blank=False , null=False)
    noi_dung = models.TextField()
    ngay_dang = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=250, blank=True)

    class Meta:
        ordering = ["so_chuong"]
        unique_together = ("volume", "so_chuong")

    def __str__(self):
        return f"Chương {self.so_chuong}: {self.ten}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(f"chuong-{self.so_chuong}-{self.ten}"))
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('chuong-detail', kwargs={'truyen_slug': self.volume.truyen.slug, 'chuong_slug': self.slug})

# =================================================
# 5. TƯƠNG TÁC (COMMENT, LIKE, FOLLOW, RATING)
# =================================================
class Comment(models.Model):
    truyen = models.ForeignKey(Truyen, on_delete=models.CASCADE, related_name="comments")
    chuong = models.ForeignKey(Chuong, on_delete=models.CASCADE, related_name="comments", null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    noi_dung = models.TextField()
    ngay_tao = models.DateTimeField(auto_now_add=True)
    is_pinned = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)
    
    @property
    def total_likes(self):
        """Đếm số lượng like của bình luận này"""
        return self.likes.count()

    class Meta:
        ordering = ["-is_pinned", "-ngay_tao"]

    def __str__(self):
        return self.noi_dung[:30]

class CommentReply(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="replies")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    noi_dung = models.TextField()
    ngay_tao = models.DateTimeField(auto_now_add=True)

class CommentLike(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ngay_tao = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("comment", "user")

class Follow(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="follows")
    truyen = models.ForeignKey(Truyen, on_delete=models.CASCADE, related_name="followers")
    ngay_theo_doi = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "truyen")

class Rating(models.Model):
    truyen = models.ForeignKey(Truyen, on_delete=models.CASCADE, related_name="ratings")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ratings")
    diem = models.PositiveIntegerField(choices=[(i, f'{i} ⭐') for i in range(1, 6)])
    ngay_tao = models.DateTimeField(auto_now_add=True)
    ngay_cap_nhat = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("truyen", "user")

# =================================================
# 6. HỆ THỐNG PHỤ (NOTIFICATION, HISTORY, REPORT)
# =================================================
class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('like_comment', 'Like bình luận'),
        ('reply_comment', 'Reply bình luận'),
        ('mention_comment', 'Mention trong bình luận'),
        ('new_chapter', 'Chương mới'),
        ('new_follow', 'Follow mới'),
        ('transfer', 'Yêu cầu chuyển quyền'),
        ('share', 'Yêu cầu chia sẻ quyền'),
        ('delete_request', 'Yêu cầu xóa truyện'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    noi_dung = models.CharField(max_length=255)
    loai = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    truyen = models.ForeignKey(Truyen, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    chuong = models.ForeignKey(Chuong, on_delete=models.CASCADE, null=True, blank=True)
    user_from = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications_sent", null=True, blank=True)
    da_doc = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=[('PENDING','Chờ xử lý'),('ACCEPTED','Đã chấp nhận'),('DECLINED','Đã từ chối')], default='PENDING')
    ngay_tao = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-ngay_tao"]

class LichSuDoc(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    truyen = models.ForeignKey(Truyen, on_delete=models.CASCADE)
    chuong_vua_doc = models.ForeignKey(Chuong, on_delete=models.CASCADE)
    ngay_cap_nhat = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "truyen")
        ordering = ["-ngay_cap_nhat"]

class Bookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookmarks")
    chuong = models.ForeignKey(Chuong, on_delete=models.CASCADE, related_name="bookmarks")
    ngay_tao = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "chuong")

class Report(models.Model):
    REPORT_STATUS = [('pending', 'Chờ xử lý'), ('resolved', 'Đã xử lý'), ('rejected', 'Đã bác bỏ')]
    user_report = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reports_sent")
    truyen = models.ForeignKey(Truyen, on_delete=models.CASCADE, related_name="reports")
    chuong = models.ForeignKey(Chuong, on_delete=models.CASCADE, null=True, blank=True)
    ly_do = models.TextField()
    trang_thai = models.CharField(max_length=20, choices=REPORT_STATUS, default='pending')
    ghi_chu_admin = models.TextField(blank=True, null=True)
    ngay_tao = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-ngay_tao"]