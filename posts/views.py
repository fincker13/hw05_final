from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .models import Comment, Post, Group, User, Follow
from .forms import PostForm, CommentForm


def index(request):
    post_list = Post.objects.select_related('group')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
         request,
         'index.html',
         {
            'page': page,
            'paginator': paginator,
         }
     ) 

def group_post(request, slug):
    group = get_object_or_404(Group, slug=slug) 
    post_list = Post.objects.filter(group=group).all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request, 
        "group.html", 
        {
            "group": group,
            'page': page,
            'paginator': paginator
        }
        )

@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == "POST":
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            form.save()
            return redirect("index")
        return render(request, "new.html", {"form": form})
    form = PostForm()
    return render(request, "new.html", {"form": form})
    
def profile(request, username):
    profile = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=profile).all()
    post_count = post_list.count()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    followers = Follow.objects.filter(author=profile.id).count()
    follows = Follow.objects.filter(user=profile.id).count()
    following = Follow.objects.filter(user=request.user.id, author=profile.id).all()
    context = {
        'profile': profile,
        'post_count': post_count,
        'page': page,
        'paginator': paginator,
        "followers": followers,
        "follows": follows, 
        "following": following,
    }
    return render(request, 'profile.html', context)
 
 
def post_view(request, username, post_id):
    profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id)
    post_list = Post.objects.filter(author=profile).all()
    post_count = post_list.count()
    form = CommentForm()
    comments = Comment.objects.filter(post=post).all() 
    followers = Follow.objects.filter(author=profile.id).count()
    follows = Follow.objects.filter(user=profile.id).count()
    following = Follow.objects.filter(user=request.user.id, author=profile.id).all()
    context = {
        'profile': profile,
        'post': post,
        'post_count': post_count,
        'comments': comments,
        'form': form,
        "followers": followers,
        "follows": follows, 
        "following": following, 
    }   
    return render(request, 'post.html', context)

@login_required
def post_edit(request, username, post_id):
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id)
    if request.user != user:
        return redirect('/')
    form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
    if request.method == "POST":
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            form.save()
            return redirect("post", username=request.user.username, post_id=post_id) 
        return render(request, 'post_new.html', {'form':form, 'post':post})
    form = PostForm(instance=post)    
    return render(request, 'post_new.html', {'form':form, 'post':post})

@login_required
def add_comment(request, username, post_id):
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            form.save()
        return redirect("post", username=request.user.username, post_id=post_id)
    form = PostForm()
    return redirect("post", username=request.user.username, post_id=post_id)

@login_required
def follow_index(request):
    following = Follow.objects.filter(user=request.user).all()
    author_list = []
    for author in following:
        author_list.append(author.author.id)
    post_list = Post.objects.filter(author__in=author_list).all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "follow.html", {"page": page, "paginator": paginator})

@login_required
def profile_follow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    follow_check = Follow.objects.filter(user=user.id, author=author.id).count()
    if follow_check == 0 and author.id != user.id:
        Follow.objects.create(user=request.user, author=author)
    return redirect("profile", username=username)

@login_required
def profile_unfollow(request, username):
    user = request.user.id
    author = get_object_or_404(User, username=username)
    follow_check = Follow.objects.filter(user=user, author=author.id).count()
    if follow_check == 1:
        Follow.objects.filter(user=request.user, author=author).delete()
    return redirect("profile", username=username)

def page_not_found(request, exception):
    return render(
        request, 
        "misc/404.html", 
        {"path": request.path}, 
        status=404
    )

def server_error(request):
    return render(request, "misc/500.html", status=500)
