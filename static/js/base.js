// Base template JavaScript - Notification system
document.addEventListener('DOMContentLoaded', function() {
  const notificationBell = document.getElementById('notificationBell');
  const notificationDropdown = document.getElementById('notificationDropdown');
  const notificationList = document.getElementById('notificationList');
  const notificationCount = document.getElementById('notificationCount');
  
  const heartIcon = document.querySelector('.icon.heart');
  const followNotificationDropdown = document.getElementById('followNotificationDropdown');
  const followNotificationList = document.getElementById('followNotificationList');
  const followNotificationCount = document.getElementById('followNotificationCount');
  
  const isAuthenticated = '{{ user.is_authenticated }}' === 'True';
  
  if (!isAuthenticated) return;
  
  // ===== BELL NOTIFICATIONS (Comments/Likes) =====
  function loadNotifications() {
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
        
        if (data.notifications.length === 0) {
          notificationList.innerHTML = '<p style="text-align: center; color: #999; padding: 20px;">Không có thông báo</p>';
          return;
        }
        
        notificationList.innerHTML = data.notifications.map(notif => `
          <div class="notification-item ${!notif.da_doc ? 'unread' : ''}" onclick="markAsRead(${notif.id})">
            <div class="notification-item-text">${notif.noi_dung}</div>
            <div class="notification-item-time">${notif.ngay_tao}</div>
          </div>
        `).join('');
      });
  }
  
  // ===== HEART NOTIFICATIONS (New Chapters/Follows) =====
  function loadFollowNotifications() {
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
        
        if (data.notifications.length === 0) {
          followNotificationList.innerHTML = '<p style="text-align: center; color: #999; padding: 20px;">Không có thông báo mới</p>';
          return;
        }
        
        followNotificationList.innerHTML = data.notifications.map(notif => `
          <div class="notification-item ${!notif.da_doc ? 'unread' : ''}" onclick="markAsRead(${notif.id})">
            <div class="notification-item-text">${notif.noi_dung}</div>
            <div class="notification-item-time">${notif.ngay_tao}</div>
          </div>
        `).join('');
      });
  }
  
  // Load notifications on page load
  loadNotifications();
  loadFollowNotifications();
  
  // Reload every 30 seconds
  setInterval(loadNotifications, 30000);
  setInterval(loadFollowNotifications, 30000);
  
  // Toggle bell dropdown
  if (notificationBell) {
    notificationBell.addEventListener('click', function(e) {
      e.preventDefault();
      notificationDropdown.style.display = notificationDropdown.style.display === 'none' ? 'block' : 'none';
      followNotificationDropdown.style.display = 'none';
    });
  }
  
  // Toggle heart dropdown
  if (heartIcon) {
    heartIcon.addEventListener('click', function(e) {
      if (e.target.closest('.notification-badge')) {
        e.preventDefault();
        followNotificationDropdown.style.display = followNotificationDropdown.style.display === 'none' ? 'block' : 'none';
        notificationDropdown.style.display = 'none';
      }
    });
  }
  
  // Close dropdowns on click outside
  document.addEventListener('click', function(e) {
    if (!e.target.closest('.notification-dropdown') && 
        !e.target.closest('.icon.bell') && 
        !e.target.closest('.icon.heart .notification-badge')) {
      notificationDropdown.style.display = 'none';
      followNotificationDropdown.style.display = 'none';
    }
  });
  
  // Mark as read function
  window.markAsRead = function(notifId) {
    fetch(`/notifications/${notifId}/read/`, { method: 'POST', headers: { 'X-CSRFToken': getCookie('csrftoken') } })
      .then(() => {
        loadNotifications();
        loadFollowNotifications();
      });
  };
  
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
