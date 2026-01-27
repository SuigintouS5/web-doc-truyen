document.addEventListener('DOMContentLoaded', function() {
    const readerMain = document.getElementById('reader-main');
    const content = document.getElementById('chapter-content');
    const panel = document.getElementById('settings-panel');

    // 1. Mở/Đóng bảng tùy chỉnh
    document.getElementById('btn-settings').onclick = (e) => {
        e.stopPropagation();
        panel.style.display = (panel.style.display === 'block') ? 'none' : 'block';
    };

    document.getElementById('close-settings').onclick = () => panel.style.display = 'none';

    // 2. Đổi màu nền & chữ
    document.querySelectorAll('.c-dot').forEach(dot => {
        dot.onclick = function() {
            const bg = this.getAttribute('data-bg');
            const txt = this.getAttribute('data-text');
            readerMain.style.backgroundColor = bg;
            readerMain.style.color = txt;
            content.style.color = txt;
            
            // Đổi màu nền container ngoài để đồng bộ
            document.getElementById('reader-container').style.backgroundColor = 
                (bg === '#000000' || bg === '#222222') ? '#111' : '#f6f6f1';
        };
    });

    // 3. Đổi cỡ chữ
    const fsRange = document.getElementById('fs-range');
    const fsLabel = document.getElementById('fs-label');
    fsRange.oninput = function() {
        content.style.fontSize = this.value + 'px';
        fsLabel.innerText = this.value + 'px';
    };

    // 4. Đổi Font
    document.getElementById('font-select').onchange = function() {
        content.style.fontFamily = this.value;
    };
});