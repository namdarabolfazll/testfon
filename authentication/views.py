from django.contrib.auth import login
from django.shortcuts import render, redirect

from authentication.forms import UserRegistrationForm


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

