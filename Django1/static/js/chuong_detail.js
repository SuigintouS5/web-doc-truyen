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
    const bookmarkBtn = document.getElementById('btn-bookmark');

    // Biến cho bình luận
    const commentInput = document.getElementById('comment-content');
    const submitCommentBtn = document.getElementById('submit-comment');
    const commentsContainer = document.getElementById('comments-container');

    // --- 1. TỰ ĐỘNG LOAD CẤU HÌNH ĐÃ LƯU (LOCAL STORAGE) ---
    const savedBg = localStorage.getItem('reader-bg');
    const savedTxt = localStorage.getItem('reader-txt');
    const savedFs = localStorage.getItem('reader-fs');
    const savedFont = localStorage.getItem('reader-font');

    if (savedBg && readerMain) {
        readerMain.style.backgroundColor = savedBg;
        if (readerContainer) {
            readerContainer.style.backgroundColor = (savedBg === '#000000' || savedBg === '#222222') ? '#111' : '#f6f6f1';
        }
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

    // --- 2. LOGIC MỤC LỤC (TOC) ---
    const btnToc = document.getElementById('btn-toc');
    if(btnToc && tocSidebar && overlay) {
        btnToc.onclick = () => {
            tocSidebar.classList.add('active');
            overlay.classList.add('active');
        };
    }

    const btnCloseToc = document.getElementById('close-toc');
    if(btnCloseToc) btnCloseToc.onclick = closeAllPanels;

    // --- 3. LOGIC TÙY CHỈNH (SETTINGS) ---
    const btnSettings = document.getElementById('btn-settings');
    if(btnSettings && settingsPanel) {
        btnSettings.onclick = (e) => {
            e.stopPropagation();
            settingsPanel.style.display = (settingsPanel.style.display === 'block') ? 'none' : 'block';
        };
    }

    const btnCloseSettings = document.getElementById('close-settings');
    if(btnCloseSettings) btnCloseSettings.onclick = () => settingsPanel.style.display = 'none';

    document.querySelectorAll('.c-dot').forEach(dot => {
        dot.onclick = function() {
            const bg = this.getAttribute('data-bg');
            const txt = this.getAttribute('data-text');
            if (readerMain) {
                readerMain.style.backgroundColor = bg;
                readerMain.style.color = txt;
            }
            if (content) content.style.color = txt;
            if (readerContainer) {
                readerContainer.style.backgroundColor = (bg === '#000000' || bg === '#222222') ? '#111' : '#f6f6f1';
            }
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

    if(fontSelect) {
        fontSelect.onchange = function() {
            if (content) content.style.fontFamily = this.value;
            localStorage.setItem('reader-font', this.value);
        };
    }

    // --- 4. LOGIC BOOKMARK & BÌNH LUẬN (AJAX) ---
    
    // Bookmark
    if (bookmarkBtn) {
        bookmarkBtn.onclick = function() {
            const chuongId = this.getAttribute('data-chuong-id');
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            fetch(`/chuong/${chuongId}/bookmark/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    this.classList.toggle('active');
                    alert(data.action === 'added' ? 'Đã lưu vị trí!' : 'Đã bỏ đánh dấu.');
                }
            })
            .catch(() => alert('Vui lòng đăng nhập!'));
        };
    }

    // Gửi Bình Luận
    if (submitCommentBtn && commentInput && commentsContainer) {
        submitCommentBtn.onclick = function() {
            const contentText = commentInput.value.trim();
            if (!contentText) {
                alert("Bạn chưa nhập nội dung bình luận!");
                return;
            }

            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            // SỬA LỖI 404: Lấy URL từ data-url của button hoặc fallback về ID
            let postUrl = this.getAttribute('data-url');
            if (!postUrl) {
                const chuongId = bookmarkBtn ? bookmarkBtn.getAttribute('data-chuong-id') : null;
                if (!chuongId) {
                    alert("Không tìm thấy ID chương!");
                    return;
                }
                postUrl = `/chuong/${chuongId}/comment/`;
            }

            fetch(postUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({ 'noi_dung': contentText })
            })
            .then(response => {
                if (!response.ok) throw new Error('Network response was not ok');
                return response.json();
            })
            .then(data => {
                if (data.status === 'success') {
                    const noCommentMsg = commentsContainer.querySelector('.no-comment') || 
                                       commentsContainer.innerText.includes('chưa có bình luận');
                    if (noCommentMsg && typeof noCommentMsg !== 'boolean') noCommentMsg.remove();
                    else if (typeof noCommentMsg === 'boolean') commentsContainer.innerHTML = '';

                    const newComment = `
                        <div class="comment-item">
                            <div class="comment-user-info">
                                <span class="user-name">${data.username}</span>
                                <span class="comment-date">Vừa xong</span>
                            </div>
                            <p class="comment-body">${data.noi_dung}</p>
                        </div>
                    `;
                    commentsContainer.insertAdjacentHTML('afterbegin', newComment);
                    commentInput.value = '';
                } else {
                    alert(data.message || "Lỗi khi gửi bình luận.");
                }
            })
            .catch(err => {
                console.error(err);
                alert("Vui lòng kiểm tra lại đường dẫn hoặc đăng nhập để bình luận!");
            });
        };
    }

    // --- 5. TIỆN ÍCH DÙNG CHUNG ---
    function closeAllPanels() {
        if(tocSidebar) tocSidebar.classList.remove('active');
        if(overlay) overlay.classList.remove('active');
        if(settingsPanel) settingsPanel.style.display = 'none';
    }

    if(overlay) overlay.onclick = closeAllPanels;

    document.addEventListener('click', (e) => {
        if (settingsPanel && !settingsPanel.contains(e.target) && e.target.id !== 'btn-settings' && 
            tocSidebar && !tocSidebar.contains(e.target) && e.target.id !== 'btn-toc') {
            settingsPanel.style.display = 'none';
        }
    });
});