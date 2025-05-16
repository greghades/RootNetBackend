import os
import random

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from aplications.authentication.models import CustomUser

from aplications.posts.models import Post, Tags


def get_random_user():
    users = list(CustomUser.objects.all())
    return random.choice(users) if users else None


def get_random_tags():
    tags = list(Tags.objects.all())
    return random.sample(tags, k=random.randint(0, min(3, len(tags)))) if tags else []


def create_posts(n=120):
    users = CustomUser.objects.all()
    if not users.exists():
        print("No users found. Please create users first.")
        return

    for _ in range(n):
        author = get_random_user()
        post = Post.objects.create(
            title="What is Lorem Ipsum?",
            content="Lorem Ipsum is simply dummy text of the printing and typesetting industry. ",
            author=author,
        )
        tags = get_random_tags()
        post.tag.set(tags)
        post.save()
    print(f"Successfully created {n} posts.")


if __name__ == "__main__":
    create_posts(120)
