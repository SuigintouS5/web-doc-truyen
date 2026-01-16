from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from io import BytesIO

from .models import Truyen

class TruyenImageTests(TestCase):
    def _make_image_file(self, name='test.png', size=(10,10), color=(255,0,0)):
        img_io = BytesIO()
        image = Image.new('RGB', size, color)
        image.save(img_io, 'PNG')
        img_io.seek(0)
        return SimpleUploadedFile(name, img_io.read(), content_type='image/png')

    def test_image_field_save_and_url(self):
        img = self._make_image_file()
        t = Truyen(ten='Test with image', tac_gia='Author')
        t.anh = img
        t.save()
        self.assertTrue(hasattr(t.anh, 'url') and t.anh.url)
        t.delete()

