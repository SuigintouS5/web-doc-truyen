document.addEventListener('DOMContentLoaded', function() {
    // 1. KHAI BÁO BIẾN
    const contactModal = document.getElementById('contactModal');
    const openContactBtn = document.getElementById('openContactModal');
    const closeContactBtn = document.getElementById('closeContactModal');
    const detailsContainer = document.getElementById('contactDetails');

    const extraModal = document.getElementById('extraModal');
    const openExtraBtn = document.getElementById('openExtraModal');
    const closeExtraBtn = document.getElementById('closeExtraModal');
    const cancelExtraBtn = document.getElementById('cancelExtraBtn');
    
    const avatarInput = document.getElementById('avatar-upload');
    const bannerInput = document.getElementById('banner-upload');
    const csrfToken = document.getElementById('csrf_token').value;

    // 2. XỬ LÝ MODAL LIÊN HỆ (VIEW)
    if (openContactBtn) {
        openContactBtn.onclick = function() {
            contactModal.style.display = 'flex';
            document.body.classList.add('modal-open');
            
            let htmlContent = '';
            const phone = document.getElementById('raw-phone').value;
            const gmail = document.getElementById('raw-gmail').value;
            const isHidePhone = document.getElementById('raw-hide-phone').value === 'True';
            const isHideGmail = document.getElementById('raw-hide-gmail').value === 'True';
            const socials = document.querySelectorAll('.social-data-source');

            if (phone && phone !== "None" && phone.trim() !== "") {
                htmlContent += `
                    <div class="contact-item">
                        <i class="fa-solid fa-phone" style="color: #28a745;"></i>
                        <span>${isHidePhone ? '<i style="color:#999">[Đã ẩn]</i>' : phone}</span>
                    </div>`;
            }

            if (gmail && gmail !== "None" && gmail.trim() !== "") {
                htmlContent += `
                    <div class="contact-item">
                        <i class="fa-solid fa-envelope" style="color: #ea4335;"></i>
                        <span>${isHideGmail ? '<i style="color:#999">[Đã ẩn]</i>' : gmail}</span>
                    </div>`;
            }

            socials.forEach(s => {
                const name = s.getAttribute('data-name');
                const link = s.getAttribute('data-link');
                let icon = 'fa-solid fa-link';
                let color = '#666';
                if (name === 'Facebook') { icon = 'fa-brands fa-facebook'; color = '#1877F2'; }
                else if (name === 'Zalo') { icon = 'fa-solid fa-comment-dots'; color = '#0068FF'; }
                else if (name === 'TikTok') { icon = 'fa-brands fa-tiktok'; color = '#000000'; }

                htmlContent += `
                    <div class="contact-item">
                        <i class="${icon}" style="color: ${color};"></i>
                        <a href="${link}" target="_blank">Ghé thăm ${name}</a>
                    </div>`;
            });

            detailsContainer.innerHTML = htmlContent || '<p class="status-msg">Thông tin liên hệ hiện chưa được thiết lập.</p>';
        };
    }

    // 3. XỬ LÝ UPLOAD ẢNH (AVATAR & BANNER)
    function uploadImage(file, type) {
        let formData = new FormData();
        formData.append(type, file);
        formData.append('csrfmiddlewaretoken', csrfToken);

        fetch(uploadUrl, { // uploadUrl lấy từ biến trong template HTML
            method: 'POST',
            body: formData,
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                if (type === 'avatar') {
                    document.getElementById('avatar-preview').src = data.avatar_url;
                } else {
                    document.getElementById('banner-preview').src = data.banner_url;
                }
                alert('Cập nhật ảnh thành công!');
            } else {
                alert('Lỗi: ' + (data.message || 'Không thể cập nhật.'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Lỗi kết nối server.');
        });
    }

    if (avatarInput) {
        avatarInput.addEventListener('change', function() {
            if (this.files && this.files[0]) uploadImage(this.files[0], 'avatar');
        });
    }

    if (bannerInput) {
        bannerInput.addEventListener('change', function() {
            if (this.files && this.files[0]) uploadImage(this.files[0], 'banner');
        });
    }

    // 4. XỬ LÝ MODAL THÊM MXH (EXTRA MODAL)
    if (openExtraBtn) {
        openExtraBtn.onclick = () => extraModal.style.display = 'flex';
    }

    const closeButtons = [closeContactBtn, closeExtraBtn, cancelExtraBtn];
    closeButtons.forEach(btn => {
        if (btn) {
            btn.onclick = () => {
                contactModal.style.display = 'none';
                if (extraModal) extraModal.style.display = 'none';
                document.body.classList.remove('modal-open');
            };
        }
    });

    window.onclick = (e) => {
        if (e.target == contactModal) {
            contactModal.style.display = 'none';
            document.body.classList.remove('modal-open');
        }
        if (extraModal && e.target == extraModal) {
            extraModal.style.display = 'none';
        }
    };

    // Thêm/Xóa hàng mạng xã hội
    const addSocialBtn = document.getElementById('addSocialRow');
    const socialContainer = document.getElementById('socialInputsContainer');

    if (addSocialBtn && socialContainer) {
        addSocialBtn.onclick = () => {
            const row = document.createElement('div');
            row.className = 'social-row';
            row.innerHTML = `
                <input type="text" name="social_name[]" placeholder="Tên" class="input-social-name">
                <input type="text" name="social_link[]" placeholder="Link..." class="input-social-link">
                <button type="button" class="btn-remove-row">×</button>
            `;
            socialContainer.appendChild(row);
        };

        socialContainer.addEventListener('click', (e) => {
            if (e.target.classList.contains('btn-remove-row')) {
                e.target.closest('.social-row').remove();
            }
        });
    }
});