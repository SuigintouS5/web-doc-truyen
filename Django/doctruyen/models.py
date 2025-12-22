from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Truyen(models.Model):
    ten = models.CharField(max_length=200)
    tac_gia = models.CharField(max_length=100)
    mo_ta = models.TextField(blank=True)
    anh = models.ImageField(upload_to="truyen/", blank=True, null=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    ngay_dang = models.DateField(auto_now_add=True)

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
            # ensure uniqueness (exclude self when updating)
            while Truyen.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)