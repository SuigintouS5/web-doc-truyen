from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.conf import settings # Cần thiết để liên kết Comment với User

# =========================
# 1. MODEL THỂ LOẠI
# =========================
class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    class Meta:
        verbose_name = "Thể loại"
        verbose_name_plural = "Thể loại"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("genre-detail", args=[str(self.slug)])

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            slug = base
            counter = 1
            while Genre.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

# =========================
# 2. MODEL TRUYỆN
# =========================
class Truyen(models.Model):
    ten = models.CharField(max_length=200)
    tac_gia = models.CharField(max_length=100)
    mo_ta = models.TextField(blank=True)
    anh = models.ImageField(upload_to="truyen/", blank=True, null=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    ngay_dang = models.DateField(auto_now_add=True)
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
        verbose_name = "Truyện"
        verbose_name_plural = "Truyện"

    def __str__(self):
        return f"{self.ten} — {self.tac_gia}"

    def get_absolute_url(self):
        return reverse("truyen-detail", args=[str(self.slug)])

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.ten)
            slug = base
            counter = 1
            while Truyen.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

# =========================
# 3. MODEL CHƯƠNG (BỔ SUNG)
# =========================
class Chuong(models.Model):
    truyen = models.ForeignKey(Truyen, on_delete=models.CASCADE, related_name="chuongs")
    so_chuong = models.PositiveIntegerField()
    ten = models.CharField(max_length=200)
    noi_dung = models.TextField()
    ngay_dang = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=250, unique=True, blank=True)

    class Meta:
        ordering = ['so_chuong']
        verbose_name = "Chương"
        verbose_name_plural = "Chương"

    def __str__(self):
        return f"Chương {self.so_chuong}: {self.ten}"

    def get_absolute_url(self):
        # Đảm bảo bạn đã cấu hình url 'chuong-detail' nhận 2 tham số: truyen_slug và chuong_slug
        return reverse("chuong-detail", args=[self.truyen.slug, self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            # Tạo slug dạng: chuong-1-ten-chuong
            self.slug = slugify(f"chuong-{self.so_chuong}-{self.ten}")
        super().save(*args, **kwargs)

# =========================
# 4. MODEL BÌNH LUẬN (BỔ SUNG)
# =========================
class Comment(models.Model):
    truyen = models.ForeignKey(Truyen, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    noi_dung = models.TextField()
    ngay_tao = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-ngay_tao']
        verbose_name = "Bình luận"
        verbose_name_plural = "Bình luận"

    def __str__(self):
        return f"{self.user.username} - {self.truyen.ten}"