# matches/views.py
from django.shortcuts import render
from .models import Match
from django.utils import timezone
from django.utils.timezone import localtime
from datetime import timedelta
from django.shortcuts import render, get_object_or_404
from .models import Match, BlogPost


def match_list(request):
    matches = Match.objects.all().order_by('date')
    featured_match = matches.filter(is_featured=True).first()
    blog_posts = BlogPost.objects.all().order_by('-created_at')[:5]  # Display latest 5 blog posts
    context = {
        'matches': matches,
        'featured_match': featured_match,
        'blog_posts': blog_posts
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

