from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from cloudinary.models import CloudinaryField
from ckeditor.fields import RichTextField


class Blogs(models.Model):  # keep plural name as in your code
    title = models.CharField(max_length=255)  # Slightly longer title limit
    content = RichTextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)  # linked to User
    image = CloudinaryField('image', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='liked_blogs', blank=True
    )
    bookmarks = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='bookmarked_blogs', blank=True
    )

    def __str__(self):
        return self.title


class Comment(models.Model):
    blog = models.ForeignKey(Blogs, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']  # newest first

    def __str__(self):
        return f"{self.user} on {self.blog} ({self.created_at:%Y-%m-%d %H:%M})"


class Feedback(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Profile(models.Model):  # Stores profile image for each user
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Default image path is inside MEDIA_ROOT/profile_images/
    image = CloudinaryField(
        'image',
        blank=True,
        null=True
    )
        
    def __str__(self):
        return self.user.username

    @property
    def initials(self):
        """Generate initials from user's first and last name."""
        name_parts = (self.user.first_name + " " + self.user.last_name).strip().split()
        if len(name_parts) == 0:
            return self.user.username[:2].upper()
        return "".join([part[0].upper() for part in name_parts])[:2]