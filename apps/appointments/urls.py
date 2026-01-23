from django.urls import path

from apps.appointments import views

app_name = "appointments"

urlpatterns = [
    path("", views.HomeRedirectView.as_view(), name="home"),
    path("services/", views.ServiceListView.as_view(), name="service_list"),
    path("services/<int:pk>/", views.ServiceDetailView.as_view(), name="service_detail"),
    path("book/<int:slot_id>/", views.BookingCreateView.as_view(), name="booking_create"),
    path("booking/<int:booking_id>/success/", views.BookingSuccessView.as_view(), name="booking_success"),
]
