document.addEventListener('DOMContentLoaded', function() {
    // --- KHỞI TẠO BIẾN ---
    const sortModal = document.getElementById('sortModal');
    const sortableList = document.getElementById('sortableList');
    const saveSortBtn = document.getElementById('saveSortBtn');
    let sortableInstance = null;
    let currentSortType = ''; // 'volume' hoặc 'chapter'

    // --- HÀM TIỆN ÍCH ---
    function openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) modal.classList.remove('hidden');
    }

    function closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) modal.classList.add('hidden');
    }

    // --- XỬ LÝ ĐÓNG/MỞ DANH SÁCH CHƯƠNG (ACCORDION) ---
    document.querySelectorAll('.volume-card-header').forEach(header => {
        header.onclick = function(e) {
            if (e.target.closest('.volume-actions')) return;
            const card = this.closest('.volume-card');
            const content = card.querySelector('.chapter-content-area');
            const icon = this.querySelector('.toggle-icon');
            if (!content) return;

            const isClosing = content.classList.toggle('hidden');
            if (icon) {
                icon.style.transform = isClosing ? 'rotate(0deg)' : 'rotate(90deg)';
            }
        };
    });

    // --- CHUẨN BỊ DỮ LIỆU SẮP XẾP ---
    const sortVolBtn = document.getElementById('sortVolumeBtn');
    if (sortVolBtn) {
        sortVolBtn.onclick = () => {
            currentSortType = 'volume';
            const volumes = Array.from(document.querySelectorAll('.volume-card')).map(card => ({
                id: card.querySelector('.btn-edit-volume').dataset.id,
                name: card.querySelector('.vol-name').innerText.trim()
            }));
            renderSortList('Sắp xếp thứ tự các Tập', volumes);
        };
    }

    document.querySelectorAll('.btn-sort-chapter').forEach(btn => {
        btn.onclick = function(e) {
            e.stopPropagation();
            currentSortType = 'chapter';
            const volCard = this.closest('.volume-card');
            const chapters = Array.from(volCard.querySelectorAll('tbody tr:not(.empty-state)')).map(tr => {
                const nameEl = tr.querySelector('.chuong-name') || tr.querySelector('td:nth-child(2)');
                return {
                    id: tr.querySelector('.btn-edit-chapter').dataset.id,
                    name: nameEl ? nameEl.innerText.trim() : 'Chương không tên'
                };
            });
            const volName = volCard.querySelector('.vol-name').innerText.trim();
            renderSortList(`Sắp xếp chương - ${volName}`, chapters);
        };
    });

    function renderSortList(title, items) {
        const titleEl = document.getElementById('sortModalTitle');
        if (titleEl) titleEl.innerText = title;
        sortableList.innerHTML = '';
        
        if (items.length === 0) {
            sortableList.innerHTML = '<li style="justify-content:center; color:#9ca3af; padding:20px;">Trống...</li>';
            if (saveSortBtn) saveSortBtn.classList.add('hidden');
        } else {
            if (saveSortBtn) saveSortBtn.classList.remove('hidden');
            items.forEach(item => {
                const li = document.createElement('li');
                li.dataset.id = item.id; // Quan trọng để Backend nhận ID
                li.innerHTML = `<i class="fas fa-bars sort-handle"></i> <span>${item.name}</span>`;
                sortableList.appendChild(li);
            });
        }
        openModal('sortModal');

        if (sortableInstance) sortableInstance.destroy();
        sortableInstance = new Sortable(sortableList, {
            animation: 150,
            ghostClass: 'sortable-ghost',
            handle: '.sort-handle',
            forceFallback: true
        });
    }

    // --- LƯU THỨ TỰ (FETCH API - chỉ sửa phần này) ---
    // *** đoạn mã dưới đây đã được chỉnh sửa trực tiếp theo yêu cầu của bạn ***
    // thêm hàm lấy cookie để dùng khi không có input csrf trên page
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                cookie = cookie.trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    if (saveSortBtn) {
        saveSortBtn.onclick = function() {
            const items = Array.from(sortableList.querySelectorAll('li'));
            const newOrder = items.map(li => li.dataset.id);
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || getCookie('csrftoken');

            // URL tuyệt đối khớp với urlpatterns trong urls.py
            const targetUrl = currentSortType === 'volume' 
                ? '/truyen/reorder-volumes/' 
                : '/truyen/reorder-chapters/';

            saveSortBtn.disabled = true;
            saveSortBtn.innerText = "Đang lưu...";

            // FormData để Django nhận order[] dưới dạng list
            const formData = new FormData();
            newOrder.forEach(id => formData.append('order[]', id));
            formData.append('csrfmiddlewaretoken', csrfToken);

            fetch(targetUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(res => res.json().then(data => {
                if (!res.ok) {
                    // nếu server trả lỗi, dùng thông điệp từ JSON nếu có
                    throw new Error(data.message || 'Lỗi server ' + res.status);
                }
                return data;
            }))
            .then(data => {
                if (data.status === 'success') {
                    location.reload();
                } else {
                    alert("Lỗi: " + (data.message || "Không thể lưu thứ tự"));
                    resetSaveBtn();
                }
            })
            .catch(err => {
                console.error("Fetch error:", err);
                alert("Lỗi: " + err.message);
                resetSaveBtn();
            });
        };
    }

    function resetSaveBtn() {
        saveSortBtn.disabled = false;
        saveSortBtn.innerText = "Lưu thứ tự";
    }

    // --- ĐÓNG MODAL ---
    const closeIds = ['closeVolumeModal', 'closeChapterBtn', 'closeChapterX', 'closeSortModal'];
    closeIds.forEach(id => {
        const btn = document.getElementById(id);
        if (btn) btn.onclick = () => {
            const modal = btn.closest('.volume-modal') || btn.closest('#sortModal');
            if (modal) {
                modal.id === 'sortModal' ? closeModal('sortModal') : modal.classList.add('hidden');
            }
        };
    });

    window.onclick = function(event) {
        if (event.target.classList.contains('modal-overlay')) {
            document.querySelectorAll('.volume-modal, #sortModal').forEach(m => m.classList.add('hidden'));
        }
    };
});