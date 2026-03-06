// Base template JavaScript - Notification system
document.addEventListener('DOMContentLoaded', function() {
  const notificationBell = document.getElementById('notificationBell');
  const notificationCount = document.getElementById('notificationCount');
  
  const heartIcon = document.querySelector('.icon.heart');
  const followNotificationCount = document.getElementById('followNotificationCount');
  
  const isAuthenticated = '{{ user.is_authenticated }}' === 'True';
  
  if (!isAuthenticated) return;
  
  // ===== UPDATE BADGE COUNT =====
  function updateBellBadge() {
    fetch('/notifications/')
      .then(r => r.json())
      .then(data => {
        const unreadCount = data.notifications.filter(n => !n.da_doc).length;
        if (unreadCount > 0) {
          notificationCount.textContent = unreadCount;
          notificationCount.style.display = 'flex';
        } else {
          notificationCount.style.display = 'none';
        }
      });
  }
  
  function updateHeartBadge() {
    fetch('/notifications/follow/')
      .then(r => r.json())
      .then(data => {
        const unreadCount = data.notifications.filter(n => !n.da_doc).length;
        if (unreadCount > 0) {
          followNotificationCount.textContent = unreadCount;
          followNotificationCount.style.display = 'flex';
        } else {
          followNotificationCount.style.display = 'none';
        }
      });
  }
  
  // Update badges on load
  updateBellBadge();
  updateHeartBadge();
  
  // Update every 5 seconds
  setInterval(updateBellBadge, 5000);
  setInterval(updateHeartBadge, 5000);
  
  // Bell click navigates to notifications page
  if (notificationBell) {
    notificationBell.addEventListener('click', function(e) {
      e.preventDefault();
      window.location.href = '/notifications/list/';
    });
  }
  
  // Heart click navigates to notifications page
  if (heartIcon) {
    heartIcon.addEventListener('click', function(e) {
      e.preventDefault();
      window.location.href = '/notifications/list/';
    });
  }
  
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
});


document.addEventListener('DOMContentLoaded', function() {
    const darkModeToggle = document.getElementById('darkModeToggle');
    const htmlElement = document.documentElement;

    // 1. Kiểm tra trạng thái ban đầu để đồng bộ nút gạt
    if (localStorage.getItem('theme') === 'dark') {
        darkModeToggle.checked = true;
    }

    // 2. Lắng nghe sự kiện thay đổi
    darkModeToggle.addEventListener('change', function() {
        if (this.checked) {
            htmlElement.classList.add('dark-mode');
            localStorage.setItem('theme', 'dark');
        } else {
            htmlElement.classList.remove('dark-mode');
            localStorage.setItem('theme', 'light');
        }
    });
});