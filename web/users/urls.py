from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from users.forms import LoginForm
from users.views import CreateUserView, UsersView

app_name = "auth"

urlpatterns = [
    # path("", views)
    path("logout/", login_required(LogoutView.as_view(template_name="users/logout.html")), name="logout"),
    path("login/", LoginView.as_view(template_name="users/login.html", form_class=LoginForm), name="login"),
    path("create/", CreateUserView.as_view(), name="create"),
    path("users/", UsersView.as_view(), name="users"),
    # path("", views.index, name="index"),
    # path("group/<slug:slug>/", views.group_posts, name="group_list"),
    # path("profile/<str:username>/", views.profile, name="profile"),
    # path("posts/<int:post_id>/", views.post_detail, name="post_detail"),
    # path("create/", PostCreateView.as_view(), name="post_create"),
    # path("posts/<int:post_id>/edit/", views.post_edit, name="post_edit"),
    # path(
    #     "posts/<int:post_id>/comment/",
    #     CommentCreateView.as_view(),
    #     name="add_comment",
    # ),
    # path("follow/", views.follow_index, name="follow_index"),
    # path(
    #     "profile/<str:username>/follow/",
    #     views.profile_follow,
    #     name="profile_follow",
    # ),
    # path(
    #     "profile/<str:username>/unfollow/",
    #     views.profile_unfollow,
    #     name="profile_unfollow",
    # ),
]