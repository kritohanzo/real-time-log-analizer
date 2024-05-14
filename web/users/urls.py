from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required, permission_required
from core.decorators import admin_required, specialist_required
from users.forms import LoginForm
from users.views import UserAddView, UserListView, UserEditView, UserDeleteView

app_name = "users"

urlpatterns = [
    path("logout/", login_required(LogoutView.as_view(template_name="users/logout.html")), name="user_logout"),
    path("login/", LoginView.as_view(template_name="users/login.html", form_class=LoginForm), name="user_login"),
    path("add/", admin_required(UserAddView.as_view()), name="user_add"),
    path("<int:user_id>/edit/", admin_required(UserEditView.as_view()), name="user_edit"),
    path("<int:user_id>/delete/", admin_required(UserDeleteView.as_view()), name="user_delete"),
    path("", admin_required(UserListView.as_view()), name="users_list"),
]