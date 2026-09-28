from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"), path("register/", views.register, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="exchange/form_page.html", extra_context={"title": "Welcome back"}), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"), path("dashboard/", views.dashboard, name="dashboard"),
    path("marketplace/", views.marketplace, name="marketplace"), path("skills/add/", views.add_skill, name="add_skill"),
    path("profile/", views.profile, name="profile"), path("students/<int:user_id>/", views.student_profile, name="student_profile"),
    path("request/<int:skill_id>/", views.send_request, name="send_request"), path("requests/", views.requests_page, name="requests"),
    path("requests/<int:request_id>/<str:action>/", views.request_action, name="request_action"), path("requests/<int:request_id>/schedule/", views.schedule_session, name="schedule_session"),
    path("sessions/", views.sessions_page, name="sessions"), path("sessions/<int:session_id>/complete/", views.complete_session, name="complete_session"),
    path("reviews/<int:request_id>/", views.review_exchange, name="review_exchange"), path("notifications/", views.notifications, name="notifications"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
]
