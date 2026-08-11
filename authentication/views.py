from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from authentication.forms import UserRegistrationForm, CustomAuthenticationForm


# Create your views here.

def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("shop:home")
    else:
        form = UserRegistrationForm()

    return render(
        request,
        template_name="",
        context={
            "form": form,
        },
    )
class UserLoginView(FormView):
    template_name = 'admin/login.html'
    form_class = CustomAuthenticationForm
    success_url = reverse_lazy('shop:home')   # default

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)

        redirect_to = self.kwargs.get('redirect_to') or self.request.GET.get('next')
        if redirect_to:
            return redirect(redirect_to)
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'نام کاربری و رمز عبور اشتباه است.')
        return super().form_invalid(form)


def logout_view(request):
    logout(request)
    messages.success(request, "با موفقیت از حساب کاربری خارج شدید.")
    return redirect('shop:home')
