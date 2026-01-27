document.addEventListener('DOMContentLoaded', () => {
    // Sửa 1: Chỉ dùng một bộ chọn duy nhất và chính xác theo ID trong HTML
    const trigger = document.getElementById('accountTrigger');
    const menu = document.getElementById('dropdownMenu');
    const darkToggle = document.getElementById('darkModeToggle');

    // Kiểm tra sự tồn tại của phần tử trước khi gán sự kiện
    if (!trigger || !menu) return;

    // Sửa 2: Gộp logic xử lý click vào một hàm duy nhất
    trigger.addEventListener('click', (e) => {
        e.stopPropagation(); // Ngăn sự kiện lan ra ngoài gây tự đóng menu
        menu.classList.toggle('active');
    });

    // Sửa 3: Cải thiện logic đóng menu khi click ra ngoài (dùng .contains để chính xác hơn)
    document.addEventListener('click', (e) => {
        if (!menu.contains(e.target) && !trigger.contains(e.target)) {
            menu.classList.remove('active');
        }
    });

    // Dark mode
    if (darkToggle) {
        darkToggle.addEventListener('change', () => {
            document.body.classList.toggle('dark-mode', darkToggle.checked);
        });
    }
});