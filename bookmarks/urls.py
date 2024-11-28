from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('collections/', views.collection_list, name='collection_list'),
    path('collections/create/', views.collection_create, name='collection_create'),
    path('collections/<int:pk>/update/', views.collection_update, name='collection_update'),
    path('collections/<int:pk>/delete/', views.collection_delete, name='collection_delete'),
]

urlpatterns += [
    path('collections/<int:collection_id>/categories/', views.category_list, name='category_list'),
    path('collections/<int:collection_id>/categories/create/', views.category_create, name='category_create'),
    path('collections/<int:collection_id>/categories/<int:pk>/update/', views.category_update, name='category_update'),
    path('collections/<int:collection_id>/categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
]

urlpatterns += [
    path('collections/<int:collection_id>/categories/<int:category_id>/bookmarks/', views.bookmark_list, name='bookmark_list'),
    path('collections/<int:collection_id>/categories/<int:category_id>/bookmarks/create/', views.bookmark_create, name='bookmark_create'),
    path('collections/<int:collection_id>/categories/<int:category_id>/bookmarks/<int:pk>/update/', views.bookmark_update, name='bookmark_update'),
    path('collections/<int:collection_id>/categories/<int:category_id>/bookmarks/<int:pk>/delete/', views.bookmark_delete, name='bookmark_delete'),
    path('collections/<int:collection_id>/categories/<int:category_id>/bookmarks/<int:pk>/edit/',views.bookmark_edit,name='bookmark_edit',),
]

urlpatterns += [
    # Account management
    path('account/', views.account, name='account'),
    path('account/change-password/', views.change_password, name='change_password'),
    path('account/delete/', views.delete_account, name='delete_account'),
]

urlpatterns += [
    # Registration
    path('register/', views.register, name='register'),
]

urlpatterns += [
    # Import bookmarks
    path('account/import-bookmarks/', views.import_bookmarks, name='import_bookmarks'),
]

urlpatterns += [
    # Password reset URLs...
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset_done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]

urlpatterns += [
    # Rename or delete a collection paths...
    path('collections/<int:collection_id>/categories/<int:category_id>/update/', views.category_update, name='category_update'),
    path('collections/<int:collection_id>/categories/<int:category_id>/delete/', views.category_delete, name='category_delete'),
]