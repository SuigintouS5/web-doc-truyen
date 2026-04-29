document.addEventListener('DOMContentLoaded', function() {
    // --- KHỞI TẠO BIẾN ---
    const sortModal = document.getElementById('sortModal');
    const sortableList = document.getElementById('sortableList'); // list container
    const saveSortBtn = document.getElementById('saveSortBtn');
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

    // --- RENDER DANH SÁCH SẮP XẾP (KIỂU CHỌN) ---
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
                li.className = 'select-move-item'; // Class để CSS nhận diện chọn
                li.dataset.id = item.id;
                li.innerText = item.name;
                sortableList.appendChild(li);
            });
        }
        openModal('sortModal');
    }

    // --- LOGIC CHỌN MỤC ---
    sortableList.addEventListener('click', function(e) {
        const target = e.target.closest('.select-move-item');
        if (!target) return;

        sortableList.querySelectorAll('.select-move-item').forEach(el => el.classList.remove('is-active'));
        target.classList.add('is-active');
    });

    // --- LOGIC ĐIỀU HƯỚNG DI CHUYỂN ---
    const navPanel = document.querySelector('.sort-navigation-panel');
    if (navPanel) {
        navPanel.addEventListener('click', function(e) {
            const btn = e.target.closest('.nav-btn');
            if (!btn) return;

            const activeItem = sortableList.querySelector('.select-move-item.is-active');
            if (!activeItem) {
                alert("Vui lòng nhấp chọn một mục trước khi di chuyển!");
                return;
            }

            if (btn.classList.contains('move-top')) {
                sortableList.prepend(activeItem);
            } 
            else if (btn.classList.contains('move-up')) {
                const prev = activeItem.previousElementSibling;
                if (prev) prev.before(activeItem);
            } 
            else if (btn.classList.contains('move-down')) {
                const next = activeItem.nextElementSibling;
                if (next) next.after(activeItem);
            } 
            else if (btn.classList.contains('move-bottom')) {
                sortableList.append(activeItem);
            }

            activeItem.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        });
    }

    // --- LƯU THỨ TỰ (FETCH API) ---
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
            const items = Array.from(sortableList.querySelectorAll('li.select-move-item'));
            const newOrder = items.map(li => li.dataset.id);
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || getCookie('csrftoken');

            const targetUrl = currentSortType === 'volume' 
                ? '/truyen/reorder-volumes/' 
                : '/truyen/reorder-chapters/';

            saveSortBtn.disabled = true;
            saveSortBtn.innerText = "Đang lưu...";

            const formData = new FormData();
            newOrder.forEach(id => formData.append('order[]', id));
            formData.append('csrfmiddlewaretoken', csrfToken);

            fetch(targetUrl, {
                method: 'POST',
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(res => res.json().then(data => {
                if (!res.ok) throw new Error(data.message || 'Lỗi server ' + res.status);
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
                modal.classList.add('hidden');
            }
        };
    });

    window.onclick = function(event) {
        if (event.target.classList.contains('modal-overlay')) {
            document.querySelectorAll('.volume-modal, #sortModal').forEach(m => m.classList.add('hidden'));
        }
    };
});