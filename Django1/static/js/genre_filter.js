document.addEventListener('DOMContentLoaded', function() {
    const filterForm = document.getElementById('filter-form');
    const storyContainer = document.querySelector('.story-grid');
    const sortSelect = document.getElementById('sort-select');

    if (!filterForm || !storyContainer) return;

    /**
     * Hàm xử lý lấy dữ liệu và cập nhật giao diện không reload trang
     */
    function updateFilters() {
        // Tạo query string từ dữ liệu hiện tại của Form
        const formData = new URLSearchParams(new FormData(filterForm)).toString();
        const fetchUrl = `${window.location.pathname}?${formData}`;

        // Cập nhật thanh địa chỉ trình duyệt để có thể copy link hoặc dùng nút Back
        window.history.pushState({ path: fetchUrl }, '', fetchUrl);

        // Hiệu ứng phản hồi thị giác: Làm mờ danh sách cũ trong khi tải
        storyContainer.style.opacity = '0.5';
        storyContainer.style.transition = 'opacity 0.2s ease';

        fetch(fetchUrl, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(response => {
            if (!response.ok) throw new Error('Mạng không ổn định');
            return response.text();
        })
        .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            
            // 1. Cập nhật danh sách truyện mới
            const newStoryGrid = doc.querySelector('.story-grid');
            if (newStoryGrid) {
                storyContainer.innerHTML = newStoryGrid.innerHTML;
            }

            // 2. Cập nhật lại số chương/tập hiển thị (nếu có thay đổi logic từ server)
            // Lưu ý: Logic "Chưa có tập" đã được server render sẵn trong HTML mới

            // Trả lại độ hiển thị bình thường
            storyContainer.style.opacity = '1';
        })
        .catch(err => {
            console.error("Lỗi khi lọc danh sách:", err);
            storyContainer.style.opacity = '1';
        });
    }

    /**
     * TỰ ĐỘNG LỌC: Lắng nghe sự kiện thay đổi của các checkbox Phân loại & Tình trạng
     */
    filterForm.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            // Khi người dùng tích hoặc bỏ tích, tự động gọi hàm cập nhật
            updateFilters();
        });
    });

    /**
     * TỰ ĐỘNG LỌC: Lắng nghe sự kiện thay đổi của thanh Sắp xếp
     */
    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            updateFilters();
        });
    }

    /**
     * Chặn sự kiện submit mặc định (nếu người dùng bấm Enter hoặc nút Áp dụng)
     */
    filterForm.addEventListener('submit', function(e) {
        e.preventDefault(); 
        updateFilters();
    });

    /**
     * Xử lý nút Back/Forward của trình duyệt để đồng bộ lại dữ liệu
     */
    window.addEventListener('popstate', function() {
        window.location.reload();
    });
});