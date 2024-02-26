from django.shortcuts import render
from django import views
from users.forms import CreateUserForm
from django.contrib.auth import get_user_model
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from users.models import User

class CreateUserView(views.View):
    def get(self, request, *args, **kwargs):
        form = CreateUserForm()
        return render(request, template_name="users/create.html", context={"form": form})
    
    def post(self, request, *args, **kwargs):
        form = CreateUserForm(request.POST)
        if not form.is_valid():
            return render(request, template_name="users/create.html", context={"form": form})
        User.objects.create_user(**form.cleaned_data)
        return render(request, template_name="users/create-success.html")
    
class UsersView(views.View):
    def get(self, request, *args, **kwargs):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)("logs", message={
            "type": "websocket.broadcast",
            "message": "Кто-то проверяет пользователей =)"
        })
        users = User.objects.all()
        return render(request, template_name="users/users.html", context={"users": users})