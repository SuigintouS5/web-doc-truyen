document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('contactModal');
    const openBtn = document.getElementById('openContactModal');
    const closeBtn = document.getElementById('closeContactModal');
    const detailsContainer = document.getElementById('contactDetails');

    // 1. Hàm mở Modal và xử lý dữ liệu
    if (openBtn) {
        openBtn.onclick = function() {
            modal.style.display = 'flex';
            document.body.classList.add('modal-open');
            
            let htmlContent = '';
            
            // Lấy dữ liệu từ Data Store
            const phone = document.getElementById('raw-phone').value;
            const gmail = document.getElementById('raw-gmail').value;
            const isHidePhone = document.getElementById('raw-hide-phone').value === 'True';
            const isHideGmail = document.getElementById('raw-hide-gmail').value === 'True';
            const socials = document.querySelectorAll('.social-data-source');

            // Xử lý Số điện thoại
            if (phone && phone !== "None" && phone.trim() !== "") {
                htmlContent += `
                    <div class="contact-item">
                        <i class="fa-solid fa-phone" style="color: #28a745;"></i>
                        <span>${isHidePhone ? '<i style="color:#999">[Đã ẩn]</i>' : phone}</span>
                    </div>`;
            }

            // Xử lý Gmail
            if (gmail && gmail !== "None" && gmail.trim() !== "") {
                htmlContent += `
                    <div class="contact-item">
                        <i class="fa-solid fa-envelope" style="color: #ea4335;"></i>
                        <span>${isHideGmail ? '<i style="color:#999">[Đã ẩn]</i>' : gmail}</span>
                    </div>`;
            }

            // Xử lý Mạng xã hội
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

            // Kiểm tra nếu hoàn toàn không có thông tin
            if (htmlContent === '') {
                htmlContent = '<p class="status-msg">Thông tin liên hệ hiện chưa được thiết lập.</p>';
            }

            detailsContainer.innerHTML = htmlContent;
        };
    }

    // 2. Đóng Modal
    if (closeBtn) {
        closeBtn.onclick = () => {
            modal.style.display = 'none';
            document.body.classList.remove('modal-open');
        };
    }

    window.onclick = (e) => {
        if (e.target == modal) {
            modal.style.display = 'none';
            document.body.classList.remove('modal-open');
        }
    };
});