/**
 * Chuyên gia Front-end: Xử lý Upload ảnh Profile & Banner bằng AJAX
 */
document.addEventListener('DOMContentLoaded', function() {
    
    // Hàm xử lý chung cho cả Avatar và Banner
    const setupImageUpload = (inputId, type) => {
        const input = document.getElementById(inputId);
        if (!input) return;

        input.addEventListener('change', function() {
            const file = this.files[0];
            if (!file) return;

            // 1. Hiển thị ảnh xem trước ngay lập tức (Preview)
            const reader = new FileReader();
            reader.onload = (e) => {
                const previewId = (type === 'avatar') ? 'avatar-preview' : 'banner-preview';
                const previewImg = document.getElementById(previewId);
                if (previewImg) previewImg.src = e.target.result;
            };
            reader.readAsDataURL(file);

            // 2. Gửi dữ liệu lên Server qua AJAX
            const formData = new FormData();
            formData.append(type, file); // 'avatar' hoặc 'banner' khớp với views.py

            // Lấy CSRF Token nếu có (Django bảo mật)
            const csrftoken = getCookie('csrftoken');

            fetch('/profile/update-image/', {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrftoken
                },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    console.log('Cập nhật thành công!');
                    // Bạn có thể thêm thông báo toast thành công ở đây
                } else {
                    alert('Lỗi: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Lỗi kết nối:', error);
            });
        });
    };

    // Hàm lấy Cookie (dùng cho CSRF Token của Django)
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Khởi chạy cho cả 2 nút
    setupImageUpload('avatar-upload', 'avatar');
    setupImageUpload('banner-upload', 'banner');
});