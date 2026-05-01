document.addEventListener('DOMContentLoaded', function() {
    // --- KHAI BÁO BIẾN ---
    const readerMain = document.getElementById('reader-main');
    const content = document.getElementById('chapter-content');
    const readerContainer = document.getElementById('reader-container');
    const settingsPanel = document.getElementById('settings-panel');
    const tocSidebar = document.getElementById('toc-sidebar');
    const overlay = document.getElementById('overlay');
    const fsRange = document.getElementById('fs-range');
    const fsLabel = document.getElementById('fs-label');
    const fontSelect = document.getElementById('font-select');
    
    const commentInput = document.getElementById('comment-content-main');
    const submitCommentBtn = document.getElementById('submit-comment-ajax');
    const commentsContainer = document.getElementById('comments-list-container');
    
    // Đảm bảo các input ẩn này có trong HTML để lấy ID chương và Token bảo mật
    const chuongId = document.getElementById('chuong-id')?.value;
    const csrfToken = document.getElementById('csrf-token')?.value;

    // --- UTILS ---
    function closeAllPanels() {
        if(tocSidebar) tocSidebar.classList.remove('active');
        if(overlay) overlay.classList.remove('active');
        if(settingsPanel) settingsPanel.style.display = 'none';
    }

    // --- 1. TẢI CẤU HÌNH GIAO DIỆN ---
    const savedBg = localStorage.getItem('reader-bg');
    const savedTxt = localStorage.getItem('reader-txt');
    const savedFs = localStorage.getItem('reader-fs');
    const savedFont = localStorage.getItem('reader-font');

    if (savedBg && readerMain) {
        readerMain.style.backgroundColor = savedBg;
        if (readerContainer) readerContainer.style.backgroundColor = (savedBg === '#000000' || savedBg === '#222222') ? '#111' : '#f6f6f1';
    }
    if (savedTxt) {
        if (readerMain) readerMain.style.color = savedTxt;
        if (content) content.style.color = savedTxt;
    }
    if (savedFs && content && fsRange && fsLabel) {
        content.style.fontSize = savedFs + 'px';
        fsRange.value = savedFs;
        fsLabel.innerText = savedFs + 'px';
    }
    if (savedFont && content && fontSelect) {
        content.style.fontFamily = savedFont;
        fontSelect.value = savedFont;
    }

    // --- 2. LOGIC ĐIỀU KHIỂN (UI) ---
    const btnToc = document.getElementById('btn-toc');
    if(btnToc) btnToc.onclick = () => { tocSidebar.classList.add('active'); overlay.classList.add('active'); };
    
    const btnCloseToc = document.getElementById('close-toc');
    if(btnCloseToc) btnCloseToc.onclick = closeAllPanels;
    if(overlay) overlay.onclick = closeAllPanels;

    const btnSettings = document.getElementById('btn-settings');
    if(btnSettings) {
        btnSettings.onclick = (e) => { 
            e.stopPropagation(); 
            settingsPanel.style.display = (settingsPanel.style.display === 'block') ? 'none' : 'block'; 
        };
    }

    document.querySelectorAll('.c-dot').forEach(dot => {
        dot.onclick = function() {
            const bg = this.getAttribute('data-bg');
            const txt = this.getAttribute('data-text');
            if (readerMain) { readerMain.style.backgroundColor = bg; readerMain.style.color = txt; }
            if (content) content.style.color = txt;
            localStorage.setItem('reader-bg', bg);
            localStorage.setItem('reader-txt', txt);
        };
    });

    if(fsRange) {
        fsRange.oninput = function() {
            const size = this.value + 'px';
            if (content) content.style.fontSize = size;
            if (fsLabel) fsLabel.innerText = size;
            localStorage.setItem('reader-fs', this.value);
        };
    }

    // --- 3. LOGIC BÌNH LUẬN ---

    // Hàm render đệ quy để hiển thị đa cấp phản hồi
    function renderCommentTree(comment, level = 0) {
        const isReply = level > 0;
        const avatarPath = comment.avatar || '/static/img/avatar.jpg';
        
        let repliesHtml = '';
        if (comment.replies && comment.replies.length > 0) {
            // Càng vào sâu đường kẻ càng rõ, thụt lề chuẩn để "chui vào trong" cha
            repliesHtml = `
                <div class="replies-container" style="margin-left: ${level === 0 ? '20px' : '30px'}; border-left: 1px solid #e2e8f0; padding-left: 15px; margin-top: 5px;">
                    ${comment.replies.map(r => renderCommentTree(r, level + 1)).join('')}
                </div>`;
        }

        return `
            <div class="comment-item" id="comment-${comment.id}" style="margin-top: 15px;">
                <div style="display: flex; gap: 12px; align-items: flex-start;">
                    <div style="width: ${isReply ? '32px' : '40px'}; height: ${isReply ? '32px' : '40px'}; border-radius: 50%; overflow: hidden; flex-shrink: 0; border: 1px solid #eee;">
                        <img src="${avatarPath}" onerror="this.src='/static/img/avatar.jpg'" style="width: 100%; height: 100%; object-fit: cover;">
                    </div>
                    <div style="flex: 1;">
                        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 2px;">
                            <span style="font-weight: 600; color: #334155; font-size: 14px;">${comment.username}</span>
                            <span style="font-size: 11px; color: #94a3b8;">${comment.ngay_tao}</span>
                        </div>
                        <div class="comment-body" style="font-size: 14px; line-height: 1.5; color: #1e293b; margin-bottom: 6px;">
                            ${comment.noi_dung}
                        </div>
                        <div class="comment-actions" style="display: flex; gap: 16px; font-size: 12px; color: #64748b;">
                            <span style="cursor: pointer; display: flex; align-items: center; gap: 4px;" onclick="likeComment(${comment.id})">
                                👍 <b class="like-count">${comment.total_likes || 0}</b>
                            </span>
                            <span style="cursor: pointer; font-weight: 500;" onclick="focusReply(${comment.id}, '${comment.username}')">Phản hồi</span>
                            ${comment.can_delete ? `<span style="cursor: pointer; color: #f87171;" onclick="deleteComment(${comment.id})">Xóa</span>` : ''}
                        </div>
                    </div>
                </div>
                ${repliesHtml}
            </div>
        `;
    }

    // Tải bình luận
    window.loadComments = function() {
        if (!chuongId || !commentsContainer) return;
        
        fetch(`/chuong/${chuongId}/get-comments/`, { 
            headers: { 'X-Requested-With': 'XMLHttpRequest' } 
        })
        .then(res => res.json())
        .then(data => {
            if (!data.comments || data.comments.length === 0) {
                commentsContainer.innerHTML = '<p style="text-align: center; color: #94a3b8; padding: 20px;">Chưa có bình luận nào.</p>';
                return;
            }
            commentsContainer.innerHTML = data.comments.map(c => renderCommentTree(c)).join('');
        })
        .catch(err => console.error("Lỗi tải dữ liệu:", err));
    };

    loadComments();

    // Xử lý Thích (Like)
    window.likeComment = function(id) {
        if (!csrfToken) return alert("Vui lòng đăng nhập!");

        fetch(`/comment/${id}/like/`, { 
            method: 'POST', 
            headers: { 'X-CSRFToken': csrfToken, 'X-Requested-With': 'XMLHttpRequest' } 
        })
        .then(res => res.json())
        .then(data => { 
            if (data.status === 'success') {
                const commentEl = document.getElementById(`comment-${id}`);
                if (commentEl) {
                    const likeCountEl = commentEl.querySelector('.like-count');
                    if (likeCountEl) likeCountEl.innerText = data.total_likes;
                }
            } else {
                alert(data.message || "Bạn cần đăng nhập để thực hiện.");
            }
        });
    };

    // Phản hồi bình luận
    window.focusReply = function(id, username) {
        if (!commentInput) return;
        commentInput.focus();
        commentInput.placeholder = `Trả lời ${username}...`;
        commentInput.dataset.parentId = id;
        commentInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
    };

    // Gửi bình luận qua AJAX
    if (submitCommentBtn) {
        submitCommentBtn.onclick = function() {
            const contentText = commentInput.value.trim();
            if (!contentText) return;

            const bodyData = new URLSearchParams({
                'noi_dung': contentText,
                'parent_id': commentInput.dataset.parentId || ''
            });

            fetch(`/chuong/${chuongId}/comment/`, {
                method: 'POST',
                headers: { 
                    'X-CSRFToken': csrfToken, 
                    'Content-Type': 'application/x-www-form-urlencoded', 
                    'X-Requested-With': 'XMLHttpRequest' 
                },
                body: bodyData
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') {
                    commentInput.value = '';
                    commentInput.placeholder = "Nhập bình luận của bạn...";
                    delete commentInput.dataset.parentId;
                    loadComments(); // Tải lại toàn bộ cây bình luận để cập nhật vị trí mới
                }
            });
        };
    }

    // Xóa bình luận
    window.deleteComment = function(id) {
        if (!confirm('Bạn chắc chắn muốn xóa bình luận này?')) return;

        fetch(`/comment/${id}/delete/`, {
            method: 'POST',
            headers: { 'X-CSRFToken': csrfToken, 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') loadComments();
            else alert(data.message);
        });
    };
});