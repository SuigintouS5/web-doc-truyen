document.addEventListener("DOMContentLoaded", () => {
    const dropdown = document.getElementById("genreDropdown");
    const selectedBox = document.getElementById("selectedGenres");

    // Nếu không tìm thấy các phần tử quan trọng thì dừng lại để tránh lỗi console
    if (!dropdown || !selectedBox) return;

    const form = dropdown.closest("form");
    const selectedIds = new Set();

    /**
     * HÀM DÙNG CHUNG: Xóa thể loại
     * @param {string} id - ID của thể loại
     * @param {HTMLElement} tagElement - Thẻ tag hiển thị trên giao diện
     * @param {HTMLElement} itemElement - Item tương ứng trong dropdown list
     */
    function removeGenre(id, tagElement, itemElement) {
        selectedIds.delete(id);
        tagElement.remove();
        
        // Xóa input hidden tương ứng để Django không nhận dữ liệu này nữa
        const input = form.querySelector(`input[name="genres"][value="${id}"]`);
        if (input) input.remove();
        
        // Hiện lại item trong danh sách chọn
        if (itemElement) itemElement.style.display = "block";
    }

    /**
     * BƯỚC 1: XỬ LÝ DỮ LIỆU CŨ (Dành cho trang Chỉnh sửa)
     * Quét các tag đã được Django render sẵn để gán sự kiện xóa
     */
    selectedBox.querySelectorAll(".genre-tag").forEach(tag => {
        const id = tag.dataset.id;
        if (id) {
            selectedIds.add(id);
            
            // Tìm item tương ứng trong dropdown để ẩn đi (vì đã chọn rồi)
            const item = dropdown.querySelector(`.dropdown-item[data-id="${id}"]`);
            if (item) item.style.display = "none";

            // Gán sự kiện xóa cho các tag có sẵn này
            tag.addEventListener("click", (e) => {
                e.stopPropagation(); // Ngăn việc click vào tag làm mở ngược lại dropdown
                removeGenre(id, tag, item);
            });
        }
    });

    /**
     * BƯỚC 2: ĐÓNG/MỞ DROPDOWN
     */
    selectedBox.addEventListener("click", (e) => {
        e.stopPropagation();
        const isHidden = dropdown.style.display === "none" || dropdown.style.display === "";
        dropdown.style.display = isHidden ? "block" : "none";
    });

    /**
     * BƯỚC 3: CHỌN THỂ LOẠI MỚI TỪ DANH SÁCH
     */
    dropdown.querySelectorAll(".dropdown-item").forEach(item => {
        item.addEventListener("click", (e) => {
            e.stopPropagation();
            const id = item.dataset.id;
            const name = item.dataset.name;

            // Nếu đã chọn rồi thì không làm gì cả
            if (selectedIds.has(id)) return;

            selectedIds.add(id);
            item.style.display = "none"; // Ẩn khỏi danh sách chọn

            // Tạo Tag hiển thị mới (thêm dấu × đỏ cho đẹp)
            const tag = document.createElement("span");
            tag.className = "genre-tag";
            tag.dataset.id = id;
            tag.innerHTML = `${name} <b style="color:#ef4444; margin-left:8px; cursor:pointer;">×</b>`;

            // Tạo Input hidden để gửi ID về server Django
            const input = document.createElement("input");
            input.type = "hidden";
            input.name = "genres";
            input.value = id;

            // Gán sự kiện xóa cho tag mới tạo
            tag.addEventListener("click", (e) => {
                e.stopPropagation();
                removeGenre(id, tag, item);
            });

            selectedBox.appendChild(tag);
            form.appendChild(input);
            
            // Đóng dropdown sau khi chọn xong cho gọn
            dropdown.style.display = "none";
        });
    });

    /**
     * BƯỚC 4: CLICK RA NGOÀI THÌ ĐÓNG DROPDOWN
     */
    document.addEventListener("click", (e) => {
        if (!e.target.closest(".genre-select")) {
            dropdown.style.display = "none";
        }
    });
});