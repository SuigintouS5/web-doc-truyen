document.addEventListener('DOMContentLoaded', function() {
    const filterForm = document.getElementById('filterForm');
    const genreBtn = document.getElementById('genreBtn');
    const genreContent = document.getElementById('genreContent');
    const closeGenre = document.getElementById('closeGenre');
    const genreCheckboxes = document.querySelectorAll('.genre-checkbox');
    const genreCountLabel = document.getElementById('genreCount');
    const selectFilters = document.querySelectorAll('.filter-select');
    const authorInput = document.querySelector('input[name="tac_gia"]');

    // --- 1. LOGIC DROPDOWN THỂ LOẠI ---

    // Cập nhật số lượng thể loại đã chọn lên nút bấm
    const updateGenreCount = () => {
        const checkedCount = document.querySelectorAll('.genre-checkbox:checked').length;
        if (genreCountLabel) genreCountLabel.textContent = checkedCount;
    };

    // Mở/Đóng dropdown khi bấm nút
    if (genreBtn) {
        genreBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            genreContent.classList.toggle('show');
        });
    }

    // Đóng dropdown khi bấm nút "Áp dụng" và thực hiện Lọc
    if (closeGenre) {
        closeGenre.addEventListener('click', () => {
            genreContent.classList.remove('show');
            filterForm.submit(); // Chỉ lọc sau khi chọn xong nhiều cái
        });
    }

    // Đóng khi nhấn ra ngoài vùng dropdown
    document.addEventListener('click', (e) => {
        if (genreContent && !genreContent.contains(e.target) && e.target !== genreBtn) {
            if (genreContent.classList.contains('show')) {
                genreContent.classList.remove('show');
                filterForm.submit(); // Tự động lọc khi người dùng thoát menu
            }
        }
    });

    // Cập nhật số lượng mỗi khi tích (nhưng chưa load lại trang ngay)
    genreCheckboxes.forEach(cb => {
        cb.addEventListener('change', updateGenreCount);
    });


    // --- 2. LOGIC AUTO-SUBMIT CHO CÁC BỘ LỌC KHÁC ---

    const autoSubmit = () => {
        // Reset về trang 1 khi lọc mới
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.has('page')) {
            const pageInput = document.createElement('input');
            pageInput.type = 'hidden';
            pageInput.name = 'page';
            pageInput.value = '1';
            filterForm.appendChild(pageInput);
        }
        filterForm.submit();
    };

    // Tự động lọc khi đổi Trạng thái hoặc Loại truyện
    selectFilters.forEach(select => {
        select.addEventListener('change', autoSubmit);
    });

    // Xử lý nhập tên tác giả (Debounce 0.8s)
    let typingTimer;
    if (authorInput) {
        authorInput.addEventListener('input', () => {
            clearTimeout(typingTimer);
            typingTimer = setTimeout(autoSubmit, 800);
        });
    }


    // --- 3. XỬ LÝ NÚT RESET (XÓA BỘ LỌC) ---
    const resetBtn = document.querySelector('.btn-filter.reset');
    if (resetBtn) {
        resetBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const urlParams = new URLSearchParams(window.location.search);
            const query = urlParams.get('q') || '';
            window.location.href = `${window.location.pathname}?q=${query}`;
        });
    }

    // Khởi tạo số lượng thể loại khi mới load trang
    updateGenreCount();
    console.log('Search Engine Optimized Ready');
});