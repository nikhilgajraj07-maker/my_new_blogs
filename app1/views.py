from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login
from django.contrib import messages
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.http import require_POST
from django.core.management import call_command
import cloudinary.uploader

from .models import Blogs, ContactMessage, Feedback, Profile, Comment
from .forms import BlogsForms, SignUpForm, ProfileForm

from django.urls import reverse
from django.contrib.admin.views.decorators import staff_member_required
import json, os
from openai import OpenAI
from django.conf import settings
import markdown
from markdown.extensions import Extension
from markdown.extensions.fenced_code import FencedCodeExtension

# ---------------- Signup ----------------
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            # 1) create the User
            user = form.save()

            # 2) make sure Profile exists
            profile = user.profile

            # 3) attach uploaded file (works for CloudinaryField)
            image = form.cleaned_data.get('image') or request.FILES.get('image')
            if image and getattr(image, 'size', 0) > 0:
                profile.image = image
                profile.save()

            login(request, user)
            return redirect('profile')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})
# ---------------- Static Pages ----------------
def homepage(request):
    return render(request, "my first.html")

def homepage2(request):
    return render(request, "my sec.html")

def about(request):
    return render(request, "about page.html")


# ---------------- Home + Blogs ----------------
def home(request):
    blogs = Blogs.objects.all().order_by('-created_at')[:9]
    return render(request, 'homepage.html', {'blogs': blogs})


# ---------------- Profile ----------------
@login_required
def profile(request):
    profile_obj, _ = Profile.objects.get_or_create(user=request.user)
    return render(request, "profile.html", {"user": request.user, "profile": profile_obj})

@login_required
def edit_profile(request):
    profile_obj, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile_obj)
        if form.is_valid():
            form.save()
            # update user info
            user = request.user
            user.first_name = request.POST.get('first_name', user.first_name)
            user.last_name = request.POST.get('last_name', user.last_name)
            user.email = request.POST.get('email', user.email)
            user.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile_obj)

    return render(request, 'edit_profile.html', {'form': form})


# ---------------- Auth ----------------
def custom_logout_view(request):
    logout(request)
    return redirect('/')

class CustomLoginView(LoginView):
    template_name = 'login.html'


# ---------------- Blog CRUD ----------------
@login_required
def blog_view(request):
    if request.method == 'POST':
        form = BlogsForms(request.POST, request.FILES)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = request.user
            blog.save()
            messages.success(request, "Your blog has been saved!")
            return redirect('blog_view')
    else:
        form = BlogsForms()

    blogs = Blogs.objects.all().order_by('-id')
    return render(request, 'blog_page.html', {'form': form, 'blogs': blogs})


def blog_detail(request, blog_id):
    blog = get_object_or_404(
        Blogs.objects.select_related("author").prefetch_related("comments__user"),
        id=blog_id
    )
    return render(request, 'blog_detail.html', {'blog': blog})


def single_blog(request, blog_id):
    blog = get_object_or_404(Blogs, id=blog_id)
    return render(request, 'single_blog.html', {'blog': blog})


@login_required
def blog_edit(request, pk):
    blog = get_object_or_404(Blogs, pk=pk)

    if request.user != blog.author and not request.user.is_staff:
        messages.error(request, "You are not allowed to edit this blog.")
        return redirect('blog_detail', blog_id=blog.id)

    if request.method == 'POST':
        form = BlogsForms(request.POST, request.FILES, instance=blog)
        form.instance.content = request.POST.get('content', '').strip()

        if form.is_valid():
            updated_blog = form.save(commit=False)
            updated_blog.author = blog.author
            updated_blog.save()
            messages.success(request, "Blog updated.")
            return redirect('blog_detail', blog_id=blog.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = BlogsForms(instance=blog)

    return render(request, 'blog_edit.html', {'form': form, 'blog': blog})


@login_required
def blog_delete(request, pk):
    blog = get_object_or_404(Blogs, pk=pk)

    if request.user != blog.author and not request.user.is_staff:
        return redirect('all_blogs')

    if request.method == 'POST':
        blog.delete()
        return redirect('all_blogs')

    return render(request, 'blog_confirm_delete.html', {'blog': blog})


# ---------------- Comments ----------------
@require_POST
@login_required
def add_comment(request, blog_id):
    blog = get_object_or_404(Blogs, id=blog_id)
    content = (request.POST.get("content") or "").strip()

    if not content:
        return redirect("blog_detail", blog_id=blog.id)

    Comment.objects.create(blog=blog, user=request.user, content=content)
    return redirect("blog_detail", blog_id=blog.id)


@require_POST
@staff_member_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    blog_id = comment.blog.pk
    comment.delete()
    return redirect("blog_detail", blog_id=blog_id)


# ---------------- Feedback + Contact ----------------
@login_required
def feedback_view(request):
    if request.method == 'POST':
        Feedback.objects.create(
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            message=request.POST.get('message')
        )
        messages.success(request, 'Thank you for your feedback!')
        return redirect('feedback')
    return render(request, 'feedback.html')


def contact_view(request):
    if request.method == 'POST':
        ContactMessage.objects.create(
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            message=request.POST.get('message')
        )
        messages.success(request, "Thank you for contacting us!")
        return redirect('contact')
    return render(request, 'contact_us.html')


# ---------------- Blogs List ----------------
def load_more_blogs(request):
    offset = int(request.GET.get("offset", 0))
    limit = 2
    blogs = Blogs.objects.all().order_by('-created_at')[offset:offset + limit]
    return render(request, "partials/blog_list_partial.html", {"blogs": blogs})


def all_blogs(request):
    query = request.GET.get('q')
    if query:
        blogs = Blogs.objects.filter(title__icontains=query)
    else:
        blogs = Blogs.objects.all()
    return render(request, 'all_blogs.html', {'blogs': blogs})

# ---------------- AI Assistant ----------------
client = OpenAI(api_key=settings.OPENAI_API_KEY)
@csrf_exempt 
def ai_assistant(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_text = data.get("text")

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant."},
                    {"role": "user", "content": user_text}
                ]
            )

            suggestion = response.choices[0].message.content
            # If AI response has ``` but no language specified, force python
            if "```" in suggestion and "```python" not in suggestion:
             suggestion = suggestion.replace("```", "```python", 1)
            # Convert AI output (Markdown → HTML with code blocks)
            suggestion_html = markdown.markdown(
              suggestion,
              extensions=["fenced_code", "codehilite"]
            )

            return JsonResponse({"suggestion": suggestion_html})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

@login_required
@require_POST
def toggle_like(request, pk):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    blog = get_object_or_404(Blogs, pk=pk)
    if request.user in blog.likes.all():
        blog.likes.remove(request.user)
        liked = False
    else:
        blog.likes.add(request.user)
        liked = True
    return JsonResponse({"liked": liked, "count": blog.likes.count()})

@login_required
@require_POST
def toggle_bookmark(request, pk):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    blog = get_object_or_404(Blogs, pk=pk)
    if request.user in blog.bookmarks.all():
        blog.bookmarks.remove(request.user)
        bookmarked = False
    else:
        blog.bookmarks.add(request.user)
        bookmarked = True
    return JsonResponse({"bookmarked": bookmarked})

def import_data(request):
    try:
        call_command("loaddata", "data.json")
        return HttpResponse("✅ Data imported successfully!")
    except Exception as e:
        return HttpResponse(f"❌ Error: {e}")


@csrf_exempt
def upload_image(request):
    """
    Handles CKEditor image upload and stores in Cloudinary.
    """
    if request.method == "POST" and request.FILES.get("upload"):
        image = request.FILES["upload"]
        try:
            result = cloudinary.uploader.upload(image)
            return JsonResponse({
                "uploaded": 1,
                "fileName": image.name,
                "url": result["secure_url"]
            })
        except Exception as e:
            return JsonResponse({"uploaded": 0, "error": {"message": str(e)}})
    return JsonResponse({"uploaded": 0, "error": {"message": "Invalid request"}})