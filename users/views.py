from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from .models import UserProfile
from .forms import UserProfileForm


class UserProfileDetailView(LoginRequiredMixin, DetailView):
    """View to display user profile information."""
    model = UserProfile
    template_name = 'users/profile.html'

    def get_object(self, queryset=None):
        """Override get_object to return the user's profile."""
        return UserProfile.objects.get(user=self.request.user)



class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    """View to update user profile."""
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'users/profile_edit.html'
    success_url = reverse_lazy('user_profile')

    def get_object(self, queryset=None):
        """Override get_object to return the user's profile."""
        return UserProfile.objects.get(user=self.request.user)