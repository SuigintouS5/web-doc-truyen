from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.truyen_list, name='truyen-list'),

    # --- QUẢN LÝ VOLUME (AJAX) ---
    path('truyen/add-volume/<int:truyen_id>/', views.add_volume_ajax, name='add-volume-ajax'),
    path('truyen/edit-volume-ajax/<int:vol_id>/', views.edit_volume_ajax, name='edit-volume-ajax'),
    path('truyen/delete-volume-ajax/<int:vol_id>/', views.delete_volume_ajax, name='delete-volume-ajax'),

    # --- QUẢN LÝ CHƯƠNG (AJAX) ---
    path('truyen/add-chapter-ajax/<int:vol_id>/', views.add_chapter_ajax, name='add-chapter-ajax'),
    path('truyen/get-chapter/<int:chuong_id>/', views.get_chapter, name='get-chapter'),
    path('truyen/edit-chapter-ajax/<int:chuong_id>/', views.edit_chapter_ajax, name='edit-chapter-ajax'),
    path('truyen/delete-chapter-ajax/<int:chuong_id>/', views.delete_chapter_ajax, name='delete-chapter-ajax'),

    # --- TRANG CÁ NHÂN & ĐĂNG TRUYỆN ---
    path('profile/', views.profile_view, name='profile'),
    path('profile/chi-tiet/', views.profile_detail_view, name='profile-detail'),
    path('profile/update-image/', views.update_profile_image_ajax, name='update-profile-image-ajax'),
    path('profile/update-info/', views.update_profile_ajax, name='update-profile-ajax'),
    path('profile/change-password/', views.change_password_ajax, name='change-password-ajax'),
    path('profile/them-truyen/', views.truyen_create, name='truyen-create'),
    path('truyen/<slug:slug>/edit/', views.truyen_edit, name='truyen-edit'),
    path('lich-su-doc/', views.lich_su_view, name='lich-su-doc'),
    path('bookmarks/', views.bookmarks_view, name='bookmarks'),

    # --- TRUYỆN DETAIL (MỚI) ---
    path('truyen/<slug:slug>/read-now/', views.read_now_view, name='read-now'),
    path('truyen/<int:truyen_id>/follow/', views.toggle_follow_ajax, name='toggle-follow'),
    path('truyen/<int:truyen_id>/is-following/', views.is_following_ajax, name='is-following'),

    # --- RATING (MỚI) ---
    path('truyen/<int:truyen_id>/rating/', views.add_rating_ajax, name='add-rating'),
    path('truyen/<int:truyen_id>/get-rating/', views.get_user_rating_ajax, name='get-rating'),

    # --- COMMENT (MỚI) ---
    path('truyen/<int:truyen_id>/add-comment/', views.add_comment_ajax, name='add-comment'),
    path('truyen/<int:truyen_id>/get-comments/', views.get_comments_ajax, name='get-comments'),
    path('comment/<int:comment_id>/like/', views.like_comment_ajax, name='like-comment'),
    path('comment/<int:comment_id>/reply/', views.reply_comment_ajax, name='reply-comment'),
    path('comment/<int:comment_id>/edit/', views.edit_comment_ajax, name='edit-comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment_ajax, name='delete-comment'),
    path('comment/<int:comment_id>/pin/', views.pin_comment_ajax, name='pin-comment'),

    # --- BOOKMARK (MỚI) ---
    path('chuong/<int:chuong_id>/bookmark/', views.toggle_bookmark_ajax, name='toggle-bookmark'),
    path('chuong/<int:chuong_id>/is-bookmarked/', views.is_bookmarked_ajax, name='is-bookmarked'),

    # --- NOTIFICATION (MỚI) ---
    path('notifications/', views.get_notifications_ajax, name='get-notifications'),
    path('notifications/follow/', views.get_follow_notifications_ajax, name='get-follow-notifications'),
    path('notifications/count/', views.count_unread_notifications_ajax, name='count-unread'),
    path('notifications/follow/count/', views.count_follow_notifications_ajax, name='count-follow-unread'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read_ajax, name='mark-read'),

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

# Phục vụ file Media (Avatar, Banner, Cover) trong môi trường phát triển
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)