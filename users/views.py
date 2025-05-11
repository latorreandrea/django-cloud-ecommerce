from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from .models import UserProfile
from checkout.models import Order
from .forms import UserProfileForm


class UserProfileDetailView(LoginRequiredMixin, DetailView):
    """View to display user profile information."""
    model = UserProfile
    template_name = 'users/profile.html'
    context_object_name = 'userprofile'
    
    def get_object(self, queryset=None):
        """Override get_object to return the user's profile."""
        return UserProfile.objects.get(user=self.request.user)

    def get_context_data(self, **kwargs):
        """Add order history to the context."""
        context = super().get_context_data(**kwargs)
        # get order list for the logged-in user
        order_list = Order.objects.filter(user=self.request.user).order_by('-created_at')
        
        # pagination
        paginator = Paginator(order_list, 5) # Mostra 5 ordini per pagina
        page_number = self.request.GET.get('page')
        
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            # if the number is not an integer, show the first page
            page_obj = paginator.page(1)
        except EmptyPage:
            # if the page number is out of range (e.g. 9999), show the last page.
            page_obj = paginator.page(paginator.num_pages)

        context['page_obj'] = page_obj # Add the paginated orders to the context
        return context



class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    """View to update user profile."""
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'users/profile_edit.html'
    success_url = reverse_lazy('user_profile')

    def get_object(self, queryset=None):
        """Override get_object to return the user's profile."""
        return UserProfile.objects.get(user=self.request.user)