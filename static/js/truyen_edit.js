document.addEventListener('DOMContentLoaded', function() {
    // --- KHAI BÁO BIẾN DÙNG CHUNG ---
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    // Modal Volume
    const volModal = document.getElementById('volumeModal');
    const volInput = document.getElementById('volumeNameInput');
    const volDescInput = document.getElementById('volumeDescInput');
    const btnSaveVolume = document.getElementById('saveVolumeBtn');
    let currentVolEditId = null;

    // Modal Chương
    const chapterModal = document.getElementById('chapterModal');
    const chapterNoInput = document.getElementById('chapterNoInput');
    const chapterNameInput = document.getElementById('chapterNameInput');
    const chapterContentInput = document.getElementById('chapterContentInput');
    const btnSaveChapter = document.getElementById('saveChapterBtn');
    const wordCountNumber = document.getElementById('wordCountNumber'); // Biến cho đếm chữ
    let currentVolIdForChapter = null;
    let currentChapterEditId = null;

    // --- FUNCTION HỖ TRỢ ĐẾM CHỮ ---
    const updateWordCount = () => {
        if (!chapterContentInput || !wordCountNumber) return;
        const text = chapterContentInput.value.trim();
        // Đếm theo khoảng trắng, xuống dòng
        const words = text ? text.split(/\s+/).length : 0;
        wordCountNumber.innerText = words.toLocaleString();
    };

    // Lắng nghe sự kiện gõ phím để đếm chữ thời gian thực
    if (chapterContentInput) {
        chapterContentInput.addEventListener('input', updateWordCount);
    }

    // --- 1. LOGIC VOLUME (THÊM / SỬA / XÓA) ---

    // Mở modal Thêm Volume
    const btnOpenVol = document.getElementById('openVolumeModal');
    if (btnOpenVol) {
        btnOpenVol.onclick = function() {
            currentVolEditId = null;
            volModal.querySelector('h3').innerText = "Thêm Volume mới";
            btnSaveVolume.innerText = "Lưu";
            volInput.value = "";
            volDescInput.value = "";
            volModal.classList.remove('hidden');
            volModal.style.display = 'flex';
        };
    }

    // Mở modal Sửa Volume
    document.querySelectorAll('.btn-edit-volume').forEach(btn => {
        btn.onclick = function(e) {
            e.stopPropagation();
            currentVolEditId = this.dataset.id;
            
            fetch(`/truyen/edit-volume-ajax/${currentVolEditId}/`)
                .then(res => res.json())
                .then(data => {
                    volModal.querySelector('h3').innerText = "Chỉnh sửa Volume";
                    btnSaveVolume.innerText = "Cập nhật";
                    volInput.value = data.ten;
                    volDescInput.value = data.mo_ta;
                    volModal.classList.remove('hidden');
                    volModal.style.display = 'flex';
                });
        };
    });

    // Lưu Volume (Thêm hoặc Sửa)
    if (btnSaveVolume) {
        btnSaveVolume.onclick = function() {
            const truyenId = document.getElementById('currentTruyenId').value;
            const url = currentVolEditId 
                ? `/truyen/edit-volume-ajax/${currentVolEditId}/` 
                : `/truyen/add-volume/${truyenId}/`;

            const formData = new FormData();
            formData.append('ten', volInput.value.trim());
            formData.append('mo_ta', volDescInput.value.trim());
            formData.append('csrfmiddlewaretoken', csrfToken);

            btnSaveVolume.disabled = true;
            btnSaveVolume.innerText = "Đang lưu...";

            fetch(url, { method: 'POST', body: formData })
                .then(res => res.json())
                .then(data => {
                    if (data.status === 'success') location.reload();
                    else {
                        alert(data.message);
                        btnSaveVolume.disabled = false;
                        btnSaveVolume.innerText = currentVolEditId ? "Cập nhật" : "Lưu";
                    }
                });
        };
    }

    // Xóa Volume
    document.querySelectorAll('.btn-delete-volume').forEach(btn => {
        btn.onclick = function(e) {
            e.stopPropagation();
            const volId = this.dataset.id;
            const volName = this.dataset.name;

            if (confirm(`Bạn có chắc muốn xóa ${volName}? Tất cả chương bên trong sẽ mất!`)) {
                const formData = new FormData();
                formData.append('csrfmiddlewaretoken', csrfToken);
                fetch(`/truyen/delete-volume-ajax/${volId}/`, { method: 'POST', body: formData })
                    .then(res => res.json()).then(() => location.reload());
            }
        };
    });

    // --- 2. LOGIC CHƯƠNG (THÊM / SỬA / XÓA) ---

    // Mở modal Thêm Chương
    document.querySelectorAll('.btn-add-chapter').forEach(btn => {
        btn.onclick = function() {
            currentVolIdForChapter = this.dataset.volid;
            currentChapterEditId = null;
            
            document.getElementById('chapterModalTitle').innerText = "Thêm chương";
            btnSaveChapter.innerText = "Thêm chương";
            btnSaveChapter.style.background = "#a855f7"; 

            chapterNoInput.value = "";
            chapterNameInput.value = "";
            chapterContentInput.value = "";
            
            // Reset số chữ về 0
            if (wordCountNumber) wordCountNumber.innerText = "0";

            chapterModal.classList.remove('hidden');
            chapterModal.style.display = 'flex';
        };
    });

    // Mở modal Sửa Chương
    document.querySelectorAll('.btn-edit-chapter').forEach(btn => {
        btn.onclick = function(e) {
            e.stopPropagation();
            currentChapterEditId = this.dataset.id;

            fetch(`/truyen/get-chapter/${currentChapterEditId}/`)
                .then(res => res.json())
                .then(data => {
                    document.getElementById('chapterModalTitle').innerText = "Sửa chương";
                    btnSaveChapter.innerText = "Cập nhật";
                    btnSaveChapter.style.background = "#2563eb"; 

                    chapterNoInput.value = data.so_chuong;
                    chapterNameInput.value = data.ten;
                    chapterContentInput.value = data.noi_dung;
                    
                    // Cập nhật số chữ sau khi load nội dung cũ
                    updateWordCount();

                    chapterModal.classList.remove('hidden');
                    chapterModal.style.display = 'flex';
                });
        };
    });

    // Lưu Chương (Thêm hoặc Sửa)
    if (btnSaveChapter) {
        btnSaveChapter.onclick = function() {
            const url = currentChapterEditId 
                ? `/truyen/edit-chapter-ajax/${currentChapterEditId}/` 
                : `/truyen/add-chapter-ajax/${currentVolIdForChapter}/`;

            const formData = new FormData();
            formData.append('ten', chapterNameInput.value.trim());
            formData.append('so_chuong', chapterNoInput.value);
            formData.append('noi_dung', chapterContentInput.value.trim());
            formData.append('csrfmiddlewaretoken', csrfToken);

            btnSaveChapter.disabled = true;
            btnSaveChapter.innerText = "Đang xử lý...";

            fetch(url, { method: 'POST', body: formData })
                .then(res => res.json())
                .then(data => {
                    if (data.status === 'success') location.reload();
                    else {
                        alert(data.message);
                        btnSaveChapter.disabled = false;
                        btnSaveChapter.innerText = currentChapterEditId ? "Cập nhật" : "Thêm chương";
                    }
                })
                .catch(err => {
                    alert("Có lỗi xảy ra kết nối Server.");
                    btnSaveChapter.disabled = false;
                    btnSaveChapter.innerText = "Thử lại";
                });
        };
    }

    // Xóa Chương
    document.querySelectorAll('.btn-delete-chapter').forEach(btn => {
        btn.onclick = function(e) {
            e.stopPropagation();
            const id = this.dataset.id;
            const name = this.dataset.name;

            if (confirm(`Bạn có chắc chắn muốn xóa chương: ${name}?`)) {
                const formData = new FormData();
                formData.append('csrfmiddlewaretoken', csrfToken);
                fetch(`/truyen/delete-chapter-ajax/${id}/`, { method: 'POST', body: formData })
                    .then(res => res.json()).then(() => location.reload());
            }
        };
    });

    // --- 3. LOGIC GIAO DIỆN (ĐÓNG MODAL & TOGGLE) ---

    // Đóng tất cả modal
    const closeElements = ['#closeVolumeModal', '#closeChapterBtn', '#closeChapterX', '.modal-overlay'];
    closeElements.forEach(selector => {
        document.querySelectorAll(selector).forEach(el => {
            el.onclick = function() {
                volModal.style.display = 'none';
                chapterModal.style.display = 'none';
                document.body.style.overflow = '';
            };
        });
    });

    // Toggle Ẩn/Hiện chương trong Volume
    document.querySelectorAll('.volume-card-header').forEach(header => {
        header.addEventListener('click', function(e) {
            if (e.target.closest('.volume-actions')) return;

            const card = this.closest('.volume-card');
            const content = card.querySelector('.chapter-content-area');
            const icon = this.querySelector('.toggle-icon');

            if (!content) return;

            if (content.classList.contains('hidden') || content.style.display === 'none') {
                content.classList.remove('hidden');
                content.style.display = 'block';
                if (icon) icon.style.transform = 'rotate(90deg)';
            } else {
                content.classList.add('hidden');
                content.style.display = 'none';
                if (icon) icon.style.transform = 'rotate(0deg)';
            }
        });
    });
});