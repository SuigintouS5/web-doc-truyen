document.addEventListener('DOMContentLoaded', function() {
    // --- KHAI BÁO BIẾN (GIỮ NGUYÊN) ---
    const readerMain = document.getElementById('reader-main');
    const content = document.getElementById('chapter-content');
    const readerContainer = document.getElementById('reader-container');
    
    const settingsPanel = document.getElementById('settings-panel');
    const tocSidebar = document.getElementById('toc-sidebar');
    const overlay = document.getElementById('overlay');
    
    const fsRange = document.getElementById('fs-range');
    const fsLabel = document.getElementById('fs-label');
    const fontSelect = document.getElementById('font-select');
    const bookmarkBtn = document.getElementById('btn-bookmark');

    const commentInput = document.getElementById('comment-content-main');
    const submitCommentBtn = document.getElementById('submit-comment-ajax');
    const commentsContainer = document.getElementById('comments-list-container');
    const chuongId = document.getElementById('chuong-id')?.value;
    const csrfToken = document.getElementById('csrf-token')?.value;

    // --- 1. TỰ ĐỘNG LOAD CẤU HÌNH (GIỮ NGUYÊN) ---
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

    // --- 2. LOGIC UI (TOC & SETTINGS - GIỮ NGUYÊN) ---
    const btnToc = document.getElementById('btn-toc');
    if(btnToc && tocSidebar && overlay) {
        btnToc.onclick = () => { tocSidebar.classList.add('active'); overlay.classList.add('active'); };
    }
    const btnCloseToc = document.getElementById('close-toc');
    if(btnCloseToc) btnCloseToc.onclick = closeAllPanels;

    const btnSettings = document.getElementById('btn-settings');
    if(btnSettings && settingsPanel) {
        btnSettings.onclick = (e) => { e.stopPropagation(); settingsPanel.style.display = (settingsPanel.style.display === 'block') ? 'none' : 'block'; };
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

    // --- 3. LOGIC BÌNH LUẬN (FINAL CẬP NHẬT) ---

    window.loadComments = function() {
        if (!chuongId || !commentsContainer) return;
        fetch(`/chuong/${chuongId}/get-comments/`, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
        .then(res => res.json())
        .then(data => renderComments(data.comments))
        .catch(err => console.error("Lỗi tải bình luận:", err));
    }

    function renderComments(comments) {
        if (!comments || comments.length === 0) {
            commentsContainer.innerHTML = '<p class="no-comment">Chưa có bình luận nào.</p>';
            return;
        }
        let html = '';
        comments.forEach(cmt => {
            const avatarPath = cmt.user_avatar || cmt.avatar || '/static/img/avatar.jpg';
            
            html += `
                <div class="comment-item" style="padding: 15px 0; border-bottom: 1px solid #eee;">
                    <div style="display: flex; gap: 15px;">
                        <img src="${avatarPath}" onerror="this.src='/static/img/avatar.jpg'" style="width:45px; height:45px; border-radius:50%; object-fit:cover;">
                        <div style="flex:1;">
                            <div style="display: flex; justify-content: space-between;">
                                <span style="font-weight:bold;">${cmt.username}</span>
                                <span style="font-size:12px; color:#999;">${cmt.created_at || cmt.ngay_tao}</span>
                            </div>
                            <p style="margin: 8px 0;">${cmt.noi_dung}</p>
                            <div style="display:flex; gap:20px; font-size:13px; color:#777;">
                                <span style="cursor:pointer;" onclick="likeComment(${cmt.id})">👍 ${cmt.likes || cmt.total_likes || 0}</span>
                                <span style="cursor:pointer;" onclick="focusReply(${cmt.id}, '${cmt.username}')">💬 Phản hồi</span>
                                ${cmt.can_delete ? `<span style="cursor:pointer; color:#e74c3c;" onclick="deleteComment(${cmt.id})">Xóa</span>` : ''}
                            </div>

                            <div class="replies-list" style="margin-top: 12px; margin-left: 20px; padding-left: 15px; border-left: 2px solid #f0f0f0;">
                                ${cmt.replies && cmt.replies.length > 0 ? cmt.replies.map(reply => `
                                    <div class="reply-item" style="margin-bottom: 8px; display: flex; gap: 10px;">
                                        <img src="${reply.avatar || '/static/img/avatar.jpg'}" onerror="this.src='/static/img/avatar.jpg'" style="width:30px; height:30px; border-radius:50%; object-fit:cover;">
                                        <div style="flex:1;">
                                            <div style="font-size:12px;">
                                                <span style="font-weight:bold;">${reply.username}</span>
                                                <span style="color:#999; margin-left:10px;">${reply.ngay_tao}</span>
                                            </div>
                                            <p style="margin: 2px 0; font-size:13.5px;">${reply.noi_dung}</p>
                                        </div>
                                    </div>
                                `).join('') : ''}
                            </div>
                        </div>
                    </div>
                </div>`;
        });
        commentsContainer.innerHTML = html;
    }

    window.likeComment = function(id) {
        fetch(`/comment/${id}/like/`, { 
            method: 'POST', 
            headers: { 'X-CSRFToken': csrfToken, 'X-Requested-With': 'XMLHttpRequest' } 
        })
        .then(res => res.json())
        .then(data => { if (data.status === 'success') loadComments(); })
        .catch(() => alert("Vui lòng đăng nhập để thích!"));
    };

    window.deleteComment = function(id) {
        if (!confirm("Bạn có chắc muốn xóa bình luận này?")) return;
        fetch(`/comment/${id}/delete/`, { 
            method: 'POST', 
            headers: { 'X-CSRFToken': csrfToken, 'X-Requested-With': 'XMLHttpRequest' } 
        })
        .then(res => res.json())
        .then(data => { if (data.status === 'success') loadComments(); });
    };

    window.focusReply = function(id, username) {
        if (commentInput) {
            commentInput.focus();
            commentInput.placeholder = "Trả lời " + (username || "người dùng") + "...";
            commentInput.dataset.parentId = id; 
            commentInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    };

    if (submitCommentBtn) {
        submitCommentBtn.onclick = function() {
            const contentText = commentInput.value.trim();
            if (!contentText) return;

            const parentId = commentInput.dataset.parentId || '';
            const bodyData = { 'noi_dung': contentText };
            if (parentId) bodyData['parent_id'] = parentId;

            fetch(`/chuong/${chuongId}/comment/`, {
                method: 'POST',
                headers: { 
                    'X-CSRFToken': csrfToken, 
                    'Content-Type': 'application/x-www-form-urlencoded', 
                    'X-Requested-With': 'XMLHttpRequest' 
                },
                body: new URLSearchParams(bodyData)
            })
            .then(res => res.json())
            .then(data => { 
                if (data.status === 'success') { 
                    commentInput.value = ''; 
                    commentInput.placeholder = "Nhập bình luận của bạn...";
                    delete commentInput.dataset.parentId; 
                    loadComments(); 
                } else {
                    alert(data.message || "Không thể gửi bình luận.");
                }
            });
        };
    }

    loadComments();

    // --- 4. LOGIC BOOKMARK (GIỮ NGUYÊN) ---
    if (bookmarkBtn) {
        bookmarkBtn.onclick = function() {
            fetch(`/chuong/${chuongId}/bookmark/`, { 
                method: 'POST', 
                headers: { 
                    'X-CSRFToken': csrfToken, 
                    'X-Requested-With': 'XMLHttpRequest' 
                } 
            })
            .then(res => res.json())
            .then(data => { 
                if (data.status === 'success') {
                    this.classList.toggle('active');
                    alert(data.action === 'added' ? 'Đã lưu đánh dấu!' : 'Đã bỏ đánh dấu.');
                } 
            })
            .catch(() => alert("Vui lòng đăng nhập để lưu dấu trang!"));
        };
    }

    // --- 5. TIỆN ÍCH (GIỮ NGUYÊN) ---
    function closeAllPanels() {
        if(tocSidebar) tocSidebar.classList.remove('active');
        if(overlay) overlay.classList.remove('active');
        if(settingsPanel) settingsPanel.style.display = 'none';
    }
    if(overlay) overlay.onclick = closeAllPanels;
});