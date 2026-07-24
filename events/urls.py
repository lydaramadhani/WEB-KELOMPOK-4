from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),

    # Public & Peserta
    path('', views.home_view, name='home'),
    path('event/<slug:slug>/', views.event_detail_view, name='event_detail'),
    path('event/<slug:slug>/checkout/', views.checkout_view, name='checkout'),
    path('order/<str:order_code>/confirmation/', views.order_confirmation_view, name='order_confirmation'),
    path('my-tickets/', views.my_tickets_view, name='my_tickets'),
    path('ticket/<str:ticket_code>/', views.ticket_detail_view, name='ticket_detail'),

    # Organizer / Admin Dashboard & Operations
    path('organizer/dashboard/', views.organizer_dashboard_view, name='organizer_dashboard'),
    path('organizer/events/', views.organizer_event_list_view, name='organizer_event_list'),
    path('organizer/events/add/', views.organizer_event_create_view, name='organizer_event_create'),
    path('organizer/events/<int:pk>/edit/', views.organizer_event_edit_view, name='organizer_event_edit'),
    path('organizer/events/<int:pk>/delete/', views.organizer_event_delete_view, name='organizer_event_delete'),
    path('organizer/categories/', views.organizer_category_list_view, name='organizer_category_list'),
    path('organizer/orders/', views.organizer_order_list_view, name='organizer_order_list'),
    path('organizer/orders/<int:pk>/', views.organizer_order_detail_view, name='organizer_order_detail'),
    path('organizer/validation/', views.organizer_ticket_validation_view, name='organizer_ticket_validation'),
    path('organizer/reports/', views.organizer_reports_view, name='organizer_reports'),
]
