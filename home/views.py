from django.shortcuts import render
from .models import InstagramPost
# Create your views here.
def index(request):
    """ A view to render homepage """
    instagram_posts = InstagramPost.objects.filter(approved=True)[:5]
    context = {
        'instagram_posts': instagram_posts,
        # Altri context data
    }
    return render(request, 'home/index.html', context)

def about(request):
    """A view to render the About Us page"""
    return render(request, "home/about.html")

def our_mission(request):
    """
    A view to render the Our Mission page.
    Our mission is to make you smile and help you break the ice in any situation by saying what everyone thinks but no one wants to say.
    With one of our accessories, you won't have to say it yourself XD.
    """
    return render(request, "home/our_mission.html")

def contact(request):
    """
    A view to render the Contact page.
    Contact us at info@blunttee.com for questions, compliments, or dad jokes.
    """
    return render(request, "home/contact.html")

def support(request):
    """
    A view to render the Support page.
    """
    return render(request, "home/support.html")

def faq(request):
    """
    A view to render the FAQ page.
    """
    return render(request, "home/faq.html")

def privacy_policy(request):
    """
    A view to render the Privacy Policy page.
    """
    return render(request, "home/privacy_policy.html")

def terms_of_service(request):
    """
    A view to render the Terms of Service page.
    """
    return render(request, "home/terms_of_service.html")

def shipping_returns(request):
    """
    A view to render the Shipping & Returns page.
    """
    return render(request, "home/shipping_returns.html")
