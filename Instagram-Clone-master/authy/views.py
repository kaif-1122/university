from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from django.db import transaction
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from post.models import Post, Follow, Stream
from authy.models import Profile
from .forms import EditProfileForm, UserRegisterForm
from django.urls import resolve
from comment.models import Comment
from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import render
from django.http import JsonResponse


def welcome(request):
    """Show welcome page for unauthenticated users"""
    if request.user.is_authenticated:
        return redirect('index')
    return render(request, 'welcome.html')

def sign_in(request):
    """Handle user login"""
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Invalid username or password')
            return render(request, 'sign-in.html', {'error': 'Invalid credentials'})
    
    return render(request, 'sign-in.html')

def register(request):
    """Handle new user registration"""
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            Profile.objects.get_or_create(user=new_user)
            messages.success(request, 'Account created successfully!')
            
            # Automatically log in the new user
            new_user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1']
            )
            login(request, new_user)
            return redirect('index')
    else:
        form = UserRegisterForm()
    
    context = {'form': form}
    return render(request, 'sign-up.html', context)

def sign_out(request):
    """Handle user logout"""
    logout(request)
    return redirect('welcome')

@login_required
def index(request):
    """Main app dashboard"""
    post_items = Post.objects.all().order_by('-posted')
    all_users = User.objects.exclude(id=request.user.id)
    
    context = {
        'post_items': post_items,
        'all_users': all_users,
    }
    return render(request, 'index.html', context)

# Profile-related views remain the same as in your original code
def UserProfile(request, username):
    Profile.objects.get_or_create(user=request.user)
    user = get_object_or_404(User, username=username)
    profile = Profile.objects.get(user=user)
    url_name = resolve(request.path).url_name
    posts = Post.objects.filter(user=user).order_by('-posted')

    if url_name == 'profile':
        posts = Post.objects.filter(user=user).order_by('-posted')
    else:
        posts = profile.favourite.all()
    
    # Profile Stats
    posts_count = Post.objects.filter(user=user).count()
    following_count = Follow.objects.filter(follower=user).count()
    followers_count = Follow.objects.filter(following=user).count()
    follow_status = Follow.objects.filter(following=user, follower=request.user).exists()

    # Pagination
    paginator = Paginator(posts, 8)
    page_number = request.GET.get('page')
    posts_paginator = paginator.get_page(page_number)

    context = {
        'posts': posts,
        'profile': profile,
        'posts_count': posts_count,
        'following_count': following_count,
        'followers_count': followers_count,
        'posts_paginator': posts_paginator,
        'follow_status': follow_status,
    }
    return render(request, 'profile.html', context)

def EditProfile(request):
    user = request.user.id
    profile = Profile.objects.get(user__id=user)

    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            profile.image = form.cleaned_data.get('image')
            profile.first_name = form.cleaned_data.get('first_name')
            profile.last_name = form.cleaned_data.get('last_name')
            profile.location = form.cleaned_data.get('location')
            profile.url = form.cleaned_data.get('url')
            profile.bio = form.cleaned_data.get('bio')
            profile.save()
            return redirect('profile', profile.user.username)
    else:
        form = EditProfileForm(instance=request.user.profile)

    context = {'form': form}
    return render(request, 'editprofile.html', context)

def follow(request, username, option):
    user = request.user
    following = get_object_or_404(User, username=username)

    try:
        f, created = Follow.objects.get_or_create(follower=request.user, following=following)

        if int(option) == 0:
            f.delete()
            Stream.objects.filter(following=following, user=request.user).all().delete()
        else:
            posts = Post.objects.all().filter(user=following)[:25]
            with transaction.atomic():
                for post in posts:
                    stream = Stream(post=post, user=request.user, date=post.posted, following=following)
                    stream.save()
        return HttpResponseRedirect(reverse('profile', args=[username]))

    except User.DoesNotExist:
        return HttpResponseRedirect(reverse('profile', args=[username]))
        # ai.html

# Static university data
UNIVERSITIES = [
    {"name": "LUMS", "type": "Private", "fields": ["Computer Science","software engineering", "BSIT" "Business"]},
    {"name": "FAST", "type": "Private", "fields": ["Computer Science","software Engineering","BSIT"]},
    {"name": "NUST", "type": "Public", "fields": ["Engineering", "Computer Science","software Engineering","BSIT"]},
    {"name": "COMSATS", "type": "Public", "fields": ["IT", "Computer Science","software Engineering","BSIT"]},
    {"name": "Punjab University", "type": "Public", "fields": ["Business", "Arts", "Biology","software Engineering","BSIT"]},
    {"name": "IBA", "type": "Private", "fields": ["Business", "Economics"]}
]

def chatbot_view(request):
    return render(request, 'chat.html')  # Your existing template

def get_university_suggestions(request):
    if request.method == "POST":
        msg = request.POST.get('message', '').strip().lower()

        if msg in ['hi', 'hello', 'hey']:
            return JsonResponse({
                "reply": "Please provide your field of interest, Inter marks, and favorite subject (e.g. Computer Science, 850, Math)"
            })

        try:
            parts = msg.split(',')
            field = parts[0].strip().title()
            marks = int(parts[1].strip())
            subject = parts[2].strip().title()

            matched = []
            for u in UNIVERSITIES:
                if field in u['fields']:
                    matched.append(f"{u['name']} ({u['type']})")

            if matched:
                return JsonResponse({
                    "reply": "Based on your input, here are suitable universities:\n" + "\n".join(matched)
                })
            else:
                return JsonResponse({
                    "reply": "Sorry, no matching universities found for the given field."
                })

        except:
            return JsonResponse({
                "reply": "Invalid format. Please enter like this:\nField, Marks, Subject\nExample: Computer Science, 850, Math"
            })

    return JsonResponse({"reply": "Invalid request method."})
