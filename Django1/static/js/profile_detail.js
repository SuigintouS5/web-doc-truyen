document.addEventListener('DOMContentLoaded', function() {
    const extraModal = document.getElementById('extraModal');
    const openBtn = document.getElementById('openExtraModal');
    const closeBtn = document.getElementById('closeExtraModal');
    const cancelBtn = document.getElementById('cancelExtraBtn');
    const addSocialBtn = document.getElementById('addSocialRow');
    const socialContainer = document.getElementById('socialInputsContainer');

    // Mở Modal
    openBtn.onclick = () => extraModal.style.display = 'flex';

    // Đóng Modal
    [closeBtn, cancelBtn].forEach(btn => {
        btn.onclick = () => extraModal.style.display = 'none';
    });

    // Đóng khi click ra ngoài
    window.onclick = (e) => {
        if (e.target == extraModal) extraModal.style.display = 'none';
    };

    // Thêm hàng MXH mới
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

    // Xóa hàng MXH
    socialContainer.addEventListener('click', (e) => {
        if (e.target.classList.contains('btn-remove-row')) {
            e.target.closest('.social-row').remove();
        }
    });
});