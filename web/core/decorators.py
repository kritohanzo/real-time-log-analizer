from django.shortcuts import redirect

def admin_required(view):
    def request_handler(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == "ADMIN":
            return view(request, *args, **kwargs)
        return redirect("logs:main_page")
    return request_handler

def specialist_required(view):
    def request_handler(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role in ["ADMIN", "SPECIALIST"]:
            return view(request, *args, **kwargs)
        return redirect("logs:main_page")
    return request_handler