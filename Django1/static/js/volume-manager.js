document.addEventListener('DOMContentLoaded', function() {
    // --- KHỞI TẠO BIẾN ---
    const sortModal = document.getElementById('sortModal');
    const sortableList = document.getElementById('sortableList'); // list container
    const saveSortBtn = document.getElementById('saveSortBtn');
    const editorContainer = document.getElementById('editor-container');
    const chapterContentInput = document.getElementById('chapterContentInput');
    const wordCountNumber = document.getElementById('wordCountNumber');
    const openFindReplaceBtn = document.getElementById('openFindReplaceBtn');
    const findReplaceModal = document.getElementById('findReplaceModal');
    const closeFindReplaceModal = document.getElementById('closeFindReplaceModal');
    const closeFindReplaceBtn = document.getElementById('closeFindReplaceBtn');
    const findPrevBtn = document.getElementById('findPrevBtn');
    const findNextBtn = document.getElementById('findNextBtn');
    const replaceBtn = document.getElementById('replaceBtn');
    const replaceAllBtn = document.getElementById('replaceAllBtn');
    const matchCaseCheckbox = document.getElementById('matchCaseCheckbox');
    const findMatchCount = document.getElementById('findMatchCount');
    const findInput = document.getElementById('findInput');
    const replaceInput = document.getElementById('replaceInput');
    let currentSortType = ''; // 'volume' hoặc 'chapter'
    let quillEditor = null;
    let searchMatches = [];
    let currentMatchIndex = -1;

    function updateChapterContentFromQuill() {
        if (!quillEditor || !chapterContentInput) return;
        const html = quillEditor.root.innerHTML;
        chapterContentInput.value = html === '<p><br></p>' ? '' : html;
        if (wordCountNumber) {
            const text = quillEditor.getText().trim();
            wordCountNumber.innerText = text ? text.split(/\s+/).length.toLocaleString() : '0';
        }
    }

    function initQuillEditor() {
        if (!editorContainer || !window.Quill) return;
        quillEditor = new Quill(editorContainer, {
            theme: 'snow',
            modules: {
                toolbar: [
                    [{ header: [1, 2, 3, false] }],
                    ['bold', 'italic', 'underline', 'strike'],
                    [{ color: [] }, { background: [] }],
                    [{ list: 'ordered' }, { list: 'bullet' }],
                    ['blockquote', 'code-block'],
                    ['link', 'image'],
                    ['clean']
                ]
            }
        });
        quillEditor.on('text-change', updateChapterContentFromQuill);
        if (chapterContentInput && chapterContentInput.value.trim()) {
            quillEditor.root.innerHTML = chapterContentInput.value;
            updateChapterContentFromQuill();
        }
    }

    initQuillEditor();

    function setChapterContent(content = '') {
        if (!quillEditor || !chapterContentInput) return;
        quillEditor.root.innerHTML = content || '';
        updateChapterContentFromQuill();
    }

    window.setChapterContent = setChapterContent;

    function escapeRegExp(value) {
        return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    function escapeHtml(value) {
        return value
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function updateMatchCountLabel() {
        if (!findMatchCount) return;
        if (searchMatches.length === 0) {
            findMatchCount.innerText = '0 kết quả';
            return;
        }
        findMatchCount.innerText = `${currentMatchIndex + 1}/${searchMatches.length} kết quả`;
    }

    function selectCurrentMatch() {
        if (!quillEditor || searchMatches.length === 0 || currentMatchIndex < 0) return;
        const match = searchMatches[currentMatchIndex];
        quillEditor.setSelection(match.index, match.length, 'silent');
    }

    function refreshFindMatches() {
        searchMatches = [];
        currentMatchIndex = -1;
        if (!quillEditor || !findInput) return updateMatchCountLabel();

        const query = findInput.value.trim();
        if (!query) return updateMatchCountLabel();

        const source = quillEditor.getText();
        const matchCase = matchCaseCheckbox?.checked;
        const haystack = matchCase ? source : source.toLowerCase();
        const needle = matchCase ? query : query.toLowerCase();

        let offset = 0;
        while (true) {
            const index = haystack.indexOf(needle, offset);
            if (index === -1) break;
            searchMatches.push({ index, length: query.length });
            offset = index + query.length;
        }

        if (searchMatches.length > 0) {
            currentMatchIndex = 0;
            selectCurrentMatch();
        }
        updateMatchCountLabel();
    }

    function changeMatch(step) {
        if (searchMatches.length === 0) return;
        currentMatchIndex = (currentMatchIndex + step + searchMatches.length) % searchMatches.length;
        selectCurrentMatch();
        updateMatchCountLabel();
    }

    function replaceCurrentMatch() {
        if (!quillEditor || searchMatches.length === 0 || currentMatchIndex < 0) return;
        const match = searchMatches[currentMatchIndex];
        const replacement = replaceInput?.value || '';
        quillEditor.deleteText(match.index, match.length, 'silent');
        quillEditor.insertText(match.index, replacement, 'silent');
        updateChapterContentFromQuill();
        refreshFindMatches();
    }

    function replaceAllMatches() {
        if (!quillEditor || !findInput) return;
        const query = findInput.value.trim();
        if (!query) return;
        const matchCase = matchCaseCheckbox?.checked;
        const source = quillEditor.getText();
        const haystack = matchCase ? source : source.toLowerCase();
        const needle = matchCase ? query : query.toLowerCase();
        const replacement = replaceInput?.value || '';

        const matchIndexes = [];
        let offset = 0;
        while (true) {
            const index = haystack.indexOf(needle, offset);
            if (index === -1) break;
            matchIndexes.push(index);
            offset = index + query.length;
        }

        for (let i = matchIndexes.length - 1; i >= 0; i--) {
            quillEditor.deleteText(matchIndexes[i], query.length, 'silent');
            quillEditor.insertText(matchIndexes[i], replacement, 'silent');
        }

        updateChapterContentFromQuill();
        refreshFindMatches();
    }

    function openFindReplace() {
        if (!findReplaceModal) return;
        findReplaceModal.classList.remove('hidden');
        setTimeout(() => findInput?.focus(), 50);
        refreshFindMatches();
    }

    function closeFindReplace() {
        if (!findReplaceModal) return;
        findReplaceModal.classList.add('hidden');
    }

    if (openFindReplaceBtn) openFindReplaceBtn.onclick = openFindReplace;
    if (closeFindReplaceModal) closeFindReplaceModal.onclick = closeFindReplace;
    if (closeFindReplaceBtn) closeFindReplaceBtn.onclick = closeFindReplace;
    if (findPrevBtn) findPrevBtn.onclick = () => changeMatch(-1);
    if (findNextBtn) findNextBtn.onclick = () => changeMatch(1);
    if (replaceBtn) replaceBtn.onclick = replaceCurrentMatch;
    if (replaceAllBtn) replaceAllBtn.onclick = replaceAllMatches;
    if (findInput) findInput.addEventListener('input', refreshFindMatches);
    if (matchCaseCheckbox) matchCaseCheckbox.addEventListener('change', refreshFindMatches);

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