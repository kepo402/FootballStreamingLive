# matches/views.py
from django.shortcuts import render
from .models import Match
from django.utils import timezone
from django.utils.timezone import localtime
from datetime import timedelta
from django.shortcuts import render, get_object_or_404
from .models import Match, BlogPost
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.http import JsonResponse


def match_list(request):
    now = timezone.now()
    matches = Match.objects.all().order_by('date')
    featured_match = matches.filter(is_featured=True).first()

    live_matches = [match for match in matches if match.is_live()]
    upcoming_matches = [match for match in matches if not match.is_live() and match.date > now]
    
    blog_posts = BlogPost.objects.all().order_by('-created_at')[:5]  # Display latest 5 blog posts
    
    context = {
        'featured_match': featured_match,
        'live_matches': live_matches,
        'matches': upcoming_matches,
        'blog_posts': blog_posts,
    }
    return render(request, 'matches/match_list.html', context)







def match_detail(request, match_id):
    match = Match.objects.get(id=match_id)
    return render(request, 'matches/match_detail.html', {'match': match})

def live_matches(request):
    # Retrieve all live matches
    matches = Match.objects.filter(is_live=True)
    context = {
        'matches': matches
    }
    return render(request, 'matches/live_matches.html', context)

def blog_post_detail(request, pk):
    blog_post = get_object_or_404(BlogPost, pk=pk)
    context = {'blog_post': blog_post}
    return render(request, 'matches/blog_post_detail.html', context)

from django.utils import timezone
from django.utils.timezone import localtime
from datetime import timedelta


@require_http_methods(["GET", "POST"])
def donate(request):
    if request.method == "POST":
        amount = request.POST.get('amount')
        email = request.POST.get('email')
        
        # You could save this information to a database or process it as needed
        
        return render(request, 'matches/donate.html', {'amount': amount, 'email': email})
    
    # Handle GET request
    return render(request, 'matches/donate.html')


def blog_list(request):
    blog_posts = BlogPost.objects.all()
    paginator = Paginator(blog_posts, 10)  # Show 10 blog posts per page.

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'matches/blog_list.html', {'page_obj': page_obj})

def get_livestream_url(request, match_id):
    try:
        match = Match.objects.get(id=match_id)
        livestream_url = match.live_stream_url
        # Handle cases where the URL might not be set
        if not livestream_url:
            livestream_url = 'https://fallback-url.com/default-stream'
    except Match.DoesNotExist:
        livestream_url = 'https://fallback-url.com/default-stream'

    return JsonResponse({'livestream_url': livestream_url})


def advertise_with_us(request):
    return render(request, 'matches/advertise.html')