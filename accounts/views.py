from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from progress.models import FavoriteText, ReadingProgress
from progress.services import category_reading_stats, completed_read_count

from .forms import SignUpForm, UserProfileForm
from .models import UserAvatar, UserProfile


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("profile")
    else:
        form = SignUpForm()

    return render(request, "registration/signup.html", {"form": form})


@login_required
def profile(request):
    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)
    UserAvatar.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=profile_obj)
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = UserProfileForm(instance=profile_obj)

    favorites = FavoriteText.objects.filter(user=request.user).select_related("text", "text__level", "text__category")
    reading_history = ReadingProgress.objects.filter(user=request.user).select_related("text", "text__level", "text__category")
    category_stats = category_reading_stats(request.user)
    achievements = request.user.achievements.select_related("achievement")[:6]

    return render(
        request,
        "accounts/profile.html",
        {
            "form": form,
            "profile": profile_obj,
            "favorites": favorites,
            "reading_history": reading_history,
            "total_completed_reads": completed_read_count(request.user),
            "category_stats": category_stats,
            "achievements": achievements,
        },
    )
