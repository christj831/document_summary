from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_documents, name='upload_documents'),
    path('history/', views.view_history, name='view_history'),
    path('history/delete/<int:history_id>/', views.delete_history, name='delete_history'),
    path('summarize-checked-history/', views.summarize_checked_history, name='summarize_checked_history'),
]
