document.addEventListener('DOMContentLoaded', function() {
    // --- KHAI BÁO BIẾN DÙNG CHUNG ---
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    // --- 0. LOGIC CHUYỂN TAB ---
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabPanels = document.querySelectorAll('.tab-panel');

    function switchEditTab(tabId) {
        tabPanels.forEach(p => p.classList.remove('active'));
        tabButtons.forEach(b => b.classList.remove('active'));

        const targetPanel = document.getElementById(tabId);
        if (targetPanel) {
            targetPanel.classList.add('active');
            const targetBtn = document.querySelector(`[onclick*="${tabId}"]`) || 
                             Array.from(tabButtons).find(b => b.innerText.includes(tabId === 'info-panel' ? 'Thông tin' : 'Chương'));
            if (targetBtn) targetBtn.classList.add('active');
            localStorage.setItem('activeEditTab', tabId);
        }
    }

    tabButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            const funcCall = this.getAttribute('onclick');
            const match = funcCall ? funcCall.match(/'([^']+)'/) : null;
            if (match) {
                switchEditTab(match[1]);
            }
        });
    });

    const savedTab = localStorage.getItem('activeEditTab');
    if (savedTab) switchEditTab(savedTab);

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
    const wordCountNumber = document.getElementById('wordCountNumber');
    let currentVolIdForChapter = null;
    let currentChapterEditId = null;

    // --- FUNCTION HỖ TRỢ ĐẾM CHỮ ---
    const updateWordCount = () => {
        if (!chapterContentInput || !wordCountNumber) return;
        const text = chapterContentInput.value.trim();
        const words = text ? text.split(/\s+/).length : 0;
        wordCountNumber.innerText = words.toLocaleString();
    };

    if (chapterContentInput) {
        chapterContentInput.addEventListener('input', updateWordCount);
    }

    // --- 1. LOGIC VOLUME (THÊM / SỬA / XÓA) ---
    const btnOpenVol = document.getElementById('openVolumeModal');
    if (btnOpenVol) {
        btnOpenVol.onclick = function() {
            currentVolEditId = null;
            volModal.querySelector('h3').innerText = "Thêm Volume mới";
            btnSaveVolume.innerText = "Lưu";
            volInput.value = "";
            volDescInput.value = "";
            volModal.classList.remove('hidden'); // Để CSS mặc định display: flex xử lý
        };
    }

    document.querySelectorAll('.btn-edit-volume').forEach(btn => {
        btn.onclick = function(e) {
            e.stopPropagation();
            currentVolEditId = this.dataset.id;
            
            fetch(`/truyen/edit-volume-ajax/${currentVolEditId}/`)
                .then(res => res.json().then(data => ({ok: res.ok, data})))
                .then(({ok, data}) => {
                    if (!ok) {
                        alert(data.message || 'Không thể tải dữ liệu');
                        return;
                    }
                    volModal.querySelector('h3').innerText = "Chỉnh sửa Volume";
                    btnSaveVolume.innerText = "Cập nhật";
                    volInput.value = data.ten;
                    volDescInput.value = data.mo_ta;
                    volModal.classList.remove('hidden');
                })
                .catch(err => alert('Lỗi: ' + err.message));
        };
    });

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
                .then(res => res.json().then(data => ({ok: res.ok, data})))
                .then(({ok, data}) => {
                    if (ok && data.status === 'success') location.reload();
                    else {
                        alert(data.message || 'Không thể lưu');
                        btnSaveVolume.disabled = false;
                        btnSaveVolume.innerText = currentVolEditId ? "Cập nhật" : "Lưu";
                    }
                })
                .catch(err => {
                    alert('Lỗi: ' + err.message);
                    btnSaveVolume.disabled = false;
                    btnSaveVolume.innerText = "Thử lại";
                });
        };
    }

    document.querySelectorAll('.btn-delete-volume').forEach(btn => {
        btn.onclick = function(e) {
            e.stopPropagation();
            const volId = this.dataset.id;
            const volName = this.dataset.name;

            if (confirm(`Bạn có chắc muốn xóa ${volName}? Tất cả chương bên trong sẽ mất!`)) {
                const formData = new FormData();
                formData.append('csrfmiddlewaretoken', csrfToken);
                fetch(`/truyen/delete-volume-ajax/${volId}/`, { method: 'POST', body: formData })
                    .then(res => res.json().then(data => ({ok: res.ok, data})))
                    .then(({ok, data}) => {
                        if (ok) location.reload();
                        else alert(data.message || 'Không thể xóa tập');
                    })
                    .catch(err => alert('Lỗi: ' + err.message));
            }
        };
    });

    // --- 2. LOGIC CHƯƠNG (THÊM / SỬA / XÓA) ---
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
            if (wordCountNumber) wordCountNumber.innerText = "0";

            chapterModal.classList.remove('hidden');
        };
    });

    document.querySelectorAll('.btn-edit-chapter').forEach(btn => {
        btn.onclick = function(e) {
            e.stopPropagation();
            currentChapterEditId = this.dataset.id;

            fetch(`/truyen/get-chapter/${currentChapterEditId}/`)
                .then(res => res.json().then(data => ({ok: res.ok, data})))
                .then(({ok, data}) => {
                    if (!ok) {
                        alert(data.message || 'Không thể tải dữ liệu');
                        return;
                    }
                    document.getElementById('chapterModalTitle').innerText = "Sửa chương";
                    btnSaveChapter.innerText = "Cập nhật";
                    btnSaveChapter.style.background = "#2563eb"; 

                    chapterNoInput.value = data.so_chuong;
                    chapterNameInput.value = data.ten;
                    chapterContentInput.value = data.noi_dung;
                    updateWordCount();

                    chapterModal.classList.remove('hidden');
                })
                .catch(err => alert('Lỗi: ' + err.message));
        };
    });

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
                .then(res => res.json().then(data => ({ok: res.ok, data})))
                .then(({ok, data}) => {
                    if (ok && data.status === 'success') location.reload();
                    else {
                        alert(data.message || 'Không thể lưu');
                        btnSaveChapter.disabled = false;
                        btnSaveChapter.innerText = currentChapterEditId ? "Cập nhật" : "Thêm chương";
                    }
                })
                .catch(err => {
                    alert("Lỗi: " + err.message);
                    btnSaveChapter.disabled = false;
                    btnSaveChapter.innerText = "Thử lại";
                });
        };
    }

    document.querySelectorAll('.btn-delete-chapter').forEach(btn => {
        btn.onclick = function(e) {
            e.stopPropagation();
            const id = this.dataset.id;
            const name = this.dataset.name;

            if (confirm(`Bạn có chắc chắn muốn xóa chương: ${name}?`)) {
                const formData = new FormData();
                formData.append('csrfmiddlewaretoken', csrfToken);
                fetch(`/truyen/delete-chapter-ajax/${id}/`, { method: 'POST', body: formData })
                    .then(res => res.json().then(data => ({ok: res.ok, data})))
                    .then(({ok, data}) => {
                        if (ok) location.reload();
                        else alert(data.message || 'Không thể xóa chương');
                    })
                    .catch(err => alert('Lỗi: ' + err.message));
            }
        };
    });

    // --- 3. LOGIC GIAO DIỆN (ĐÓNG MODAL & TOGGLE) ---
    const closeElements = ['#closeVolumeModal', '#closeChapterBtn', '#closeChapterX', '.modal-overlay'];
    closeElements.forEach(selector => {
        document.querySelectorAll(selector).forEach(el => {
            el.onclick = function() {
                volModal.classList.add('hidden');
                chapterModal.classList.add('hidden');
                document.body.style.overflow = '';
            };
        });
    });
});