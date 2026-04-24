from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.truyen_list, name='truyen-list'),

    # --- QUẢN LÝ VOLUME (AJAX) ---
    path('truyen/add-volume/<int:truyen_id>/', views.add_volume_ajax, name='add-volume-ajax'),
    path('truyen/edit-volume-ajax/<int:volume_id>/', views.edit_volume_ajax, name='edit-volume-ajax'),
    path('truyen/delete-volume-ajax/<int:volume_id>/', views.delete_volume_ajax, name='delete-volume-ajax'),
    path('truyen/reorder-volumes/', views.reorder_volumes, name='reorder-volumes'),

    # --- QUẢN LÝ CHƯƠNG (AJAX) ---
    path('truyen/add-chapter-ajax/<int:volume_id>/', views.add_chapter_ajax, name='add-chapter-ajax'),
    path('truyen/get-chapter/<int:chapter_id>/', views.get_chapter_ajax, name='get-chapter'),
    path('truyen/edit-chapter-ajax/<int:chapter_id>/', views.edit_chapter_ajax, name='edit-chapter-ajax'),
    path('truyen/delete-chapter-ajax/<int:chapter_id>/', views.delete_chapter_ajax, name='delete-chapter-ajax'),
    path('truyen/reorder-chapters/', views.reorder_chapters, name='reorder-chapters'),

    # --- TRANG CÁ NHÂN & CHI TIẾT HỒ SƠ ---
    path('user/<str:username>/', views.profile_view, name='user-profile'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/chi-tiet/', views.profile_detail_view, name='profile-detail'),
    path('profile/update-image/', views.update_profile_image_ajax, name='update-profile-image-ajax'),
    path('profile/update-info/', views.update_profile_ajax, name='update-profile-ajax'),
    path('profile/change-password/', views.change_password_ajax, name='change-password-ajax'),
    path('profile/update-extra/', views.update_profile_extra_ajax, name='update_extra'),
    path('profile/update-privacy/', views.update_privacy_ajax, name='update_privacy'),
    path('profile/them-truyen/', views.truyen_create, name='truyen-create'),
    path('truyen/<slug:slug>/edit/', views.truyen_edit, name='truyen-edit'),
    path('lich-su-doc/', views.lich_su_view, name='lich-su-doc'),
    path('bookmarks/', views.bookmarks_view, name='bookmarks'),

    # --- TRUYỆN DETAIL ---
    path('truyen/<slug:slug>/read-now/', views.read_now_view, name='read-now'),
    path('truyen/<int:truyen_id>/follow/', views.toggle_follow_ajax, name='toggle-follow'),
    path('truyen/<int:truyen_id>/is-following/', views.is_following_ajax, name='is-following'),

    # --- RATING ---
    path('truyen/<int:truyen_id>/rating/', views.add_rating_ajax, name='add-rating'),
    path('truyen/<int:truyen_id>/get-rating/', views.get_user_rating_ajax, name='get-rating'),

    # --- COMMENT ---
    path('truyen/<int:truyen_id>/add-comment/', views.add_comment_ajax, name='add-comment'),
    path('truyen/<int:truyen_id>/get-comments/', views.get_comments_ajax, name='get-comments'),
    path('comment/<int:comment_id>/like/', views.like_comment_ajax, name='like-comment'),
    path('comment/<int:comment_id>/reply/', views.reply_comment_ajax, name='reply-comment'),
    path('comment/<int:comment_id>/edit/', views.edit_comment_ajax, name='edit-comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment_ajax, name='delete-comment'), # Đảm bảo views.py có hàm này
    path('comment/<int:comment_id>/pin/', views.pin_comment_ajax, name='pin-comment'),
    path('chuong/<int:chuong_id>/comment/', views.add_chuong_comment_ajax, name='add-chuong-comment'),# urls.py
path('chuong/<int:chuong_id>/get-comments/', views.get_chuong_comments_ajax, name='get-chuong-comments-ajax'),

    # --- BOOKMARK ---
    path('chuong/<int:chuong_id>/bookmark/', views.toggle_bookmark_ajax, name='toggle-bookmark-ajax'),
    

    # --- NOTIFICATION (CHỈNH SỬA TẠI ĐÂY) ---
    # Trang danh sách thông báo chính (Nút Chuông dẫn vào đây)
    path('notifications/', views.notifications_view, name='notifications'), 
    
    # API lấy danh sách cho Dropdown của Tim
    path('notifications/api/get-follow/', views.get_follow_notifications_ajax, name='get-follow-notifications'),
    
    # API đếm số lượng thông báo chưa đọc (Dùng chung cho cả 2 Badge)
    path('notifications/api/count/', views.count_unread_notifications_ajax, name='count-unread'),
    
    # Các thao tác phụ
    path('notifications/<int:notification_id>/read/', views.mark_notification_read_ajax, name='mark-read'),
    path('notifications/<int:notification_id>/accept/', views.accept_notification_ajax, name='accept-notification'),
    path('notifications/<int:notification_id>/decline/', views.decline_notification_ajax, name='decline-notification'),
    path('notifications/api/create/', views.create_notification_ajax, name='create-notification-ajax'),

    # --- TÀI KHOẢN ---
    path("dang-nhap/", views.login_view, name="user-login"),
    path("dang-ky/", views.register_view, name="user-register"),
    path("dang-xuat/", views.logout_view, name="logout"),

    # --- CHI TIẾT TRUYỆN & CHƯƠNG ---
    path('the-loai/<slug:slug>/', views.genre_detail, name='genre-detail'),
    path('search/', views.search_view, name='search'),
    path('truyen/<slug:slug>/', views.truyen_detail, name='truyen-detail'),
    path('truyen/<slug:truyen_slug>/<slug:chuong_slug>/', views.chuong_detail, name='chuong-detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    