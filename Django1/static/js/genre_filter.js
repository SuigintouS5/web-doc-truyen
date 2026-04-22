document.addEventListener('DOMContentLoaded', function() {
    // 1. Dùng ID cho chính xác vì bạn đã đặt id="filter-form"
    const filterForm = document.getElementById('filter-form');
    const storyContainer = document.querySelector('.story-grid');
    const sortSelect = document.getElementById('sort-select');

    if (!filterForm) return;

    // Hàm xử lý lấy dữ liệu không reload trang
    function updateFilters() {
        const formData = new URLSearchParams(new FormData(filterForm)).toString();
        const fetchUrl = `${window.location.pathname}?${formData}`;

        // Cập nhật thanh địa chỉ
        window.history.pushState({}, '', fetchUrl);

        // Hiệu ứng mờ để người dùng biết đang load (tùy chọn)
        storyContainer.style.opacity = '0.5';

        fetch(fetchUrl, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(response => response.text())
        .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            
            // Cập nhật danh sách truyện
            const newStoryContent = doc.querySelector('.story-grid').innerHTML;
            storyContainer.innerHTML = newStoryContent;
            storyContainer.style.opacity = '1';

            // QUAN TRỌNG: Cập nhật lại các checkbox và select để "lưu" trạng thái
            // vì form hiện tại đang bao quanh cả trang
            const newForm = doc.getElementById('filter-form');
            // Cập nhật lại các checkbox (nếu cần đồng bộ thủ công)
        })
        .catch(err => console.error("Lỗi load filter:", err));
    }

    // 2. Chặn sự kiện submit của nút "Áp dụng"
    filterForm.addEventListener('submit', function(e) {
        e.preventDefault(); 
        updateFilters();
    });

    // 3. Xử lý thanh sắp xếp (Thay thế cho cái onchange trong HTML)
    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            updateFilters();
        });
    }
});