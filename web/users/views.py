from django.shortcuts import render
from django import views
from users.forms import UserForm
from django.contrib.auth import get_user_model
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.shortcuts import get_object_or_404
from users.models import User
from logs.models import NotificationType


class UserListView(views.View):
    def get(self, request, *args, **kwargs):
        users = User.objects.all()
        return render(request, template_name="users/users-list.html", context={"users": users})
    

class UserAddView(views.View):
    def get(self, request, *args, **kwargs):
        form = UserForm()
        return render(request, template_name="users/user-form.html", context={"form": form})
    
    def post(self, request, *args, **kwargs):
        form = UserForm(request.POST)
        if not form.is_valid():
            return render(request, template_name="users/user-form.html", context={"form": form})
        notification_types = NotificationType.objects.filter(method="websocket") | form.cleaned_data.pop("notification_types")
        password = form.cleaned_data.pop("password")
        user = User.objects.create(**form.cleaned_data)
        user.notification_types.set(notification_types)
        user.set_password(password)
        user.save()
        return render(request, template_name="success.html", context={"message": "Вы успешно добавили пользователя"})
    

class UserEditView(views.View):
    def get(self, request, user_id, *args, **kwargs):
        user = get_object_or_404(User, id=user_id)
        form = UserForm(instance=user)
        return render(request, template_name="users/user-form.html", context={"form": form, "user_id": user_id, "is_edit": True})
    
    def post(self, request, user_id, *args, **kwargs):
        user = get_object_or_404(User, id=user_id)
        user_password = user.password
        form = UserForm(request.POST, instance=user)
        if not form.is_valid():
            return render(request, template_name="users/user-form.html", context={"form": form, "user_id": user_id, "is_edit": True})
        form.save()
        notification_types = NotificationType.objects.filter(method="websocket") | form.cleaned_data.pop("notification_types")
        user.notification_types.set(notification_types)
        new_password = form.cleaned_data.pop("password")
        if new_password != user_password:
            user.set_password(new_password)
            user.save()
        return render(request, template_name="success.html", context={"message": "Вы успешно изменили пользователя"})


class UserDeleteView(views.View):
    def get(self, request, user_id, *args, **kwargs):
        user = get_object_or_404(User, id=user_id)
        user.delete()
        return render(request, template_name="success.html", context={"message": "Вы успешно удалили пользователя"})