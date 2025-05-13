from django.db import models
from aplications.authentication.models import CustomUser
# Create your models here.

class Post(models.Model):
    """
    Represents a blog post or article.

    Fields:
        title (CharField): The title of the post.
        content (TextField): The main content of the post.
        author (ForeignKey): Reference to the CustomUser who created the post.
        image (ImageField): Optional image associated with the post.
        tag (ManyToManyField): Tags associated with the post.
        created_at (DateTimeField): Timestamp when the post was created.
        updated_at (DateTimeField): Timestamp when the post was last updated.
    """
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='posts/images/', null=True, blank=True)
    tag = models.ManyToManyField('Tags', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

class Comment(models.Model):
    """
    Represents a comment made on a post.

    Fields:
        post (ForeignKey): The post this comment is related to.
        author (ForeignKey): The user who wrote the comment.
        content (TextField): The content of the comment.
        created_at (DateTimeField): Timestamp when the comment was created.
        updated_at (DateTimeField): Timestamp when the comment was last updated.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.author} on {self.post}"

class Like(models.Model):
    """
    Represents a 'like' given by a user to a post.

    Fields:
        post (ForeignKey): The post that was liked.
        user (ForeignKey): The user who liked the post.
        created_at (DateTimeField): Timestamp when the like was created.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Like by {self.user} on {self.post}"

class Favorite(models.Model):
    """
    Represents a post marked as favorite by a user.

    Fields:
        post (ForeignKey): The post that was favorited.
        user (ForeignKey): The user who favorited the post.
        created_at (DateTimeField): Timestamp when the favorite was created.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='favorites')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Favorite by {self.user} on {self.post}"

class Tags(models.Model):
    """
    Represents a tag that can be associated with posts.

    Fields:
        name (CharField): The name of the tag (unique).
        type (CharField): Optional type/category of the tag.
    """
    name = models.CharField(max_length=50, unique=True)
    type = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.name