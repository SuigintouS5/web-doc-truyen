// Base template JavaScript - Notification system
document.addEventListener('DOMContentLoaded', function() {
  const notificationBell = document.getElementById('notificationBell');
  const notificationCount = document.getElementById('notificationCount');
  
  const heartIcon = document.querySelector('.icon.heart');
  const followNotificationCount = document.getElementById('followNotificationCount');
  
  const isAuthenticated = '{{ user.is_authenticated }}' === 'True';
  
  if (!isAuthenticated) return;
  
  // ===== UPDATE BADGE COUNT =====
  function updateNotificationBadges() {
    fetch('/notifications/')
      .then(r => r.json())
      .then(data => {
        const unreadBell = data.unread_counts?.bell ?? 0;
        const unreadFollow = data.unread_counts?.follow ?? 0;

        if (unreadBell > 0) {
          notificationCount.textContent = unreadBell;
          notificationCount.style.display = 'flex';
        } else {
          notificationCount.style.display = 'none';
        }

        if (unreadFollow > 0) {
          followNotificationCount.textContent = unreadFollow;
          followNotificationCount.style.display = 'flex';
        } else {
          followNotificationCount.style.display = 'none';
        }
      });
  }

  // Update badges on load
  updateNotificationBadges();
  
  // Update every 5 seconds
  setInterval(updateNotificationBadges, 5000);
  
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