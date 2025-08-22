from django.core.management.base import BaseCommand
from app1.models import Blogs   # your app is app1 and model is Blogs

class Command(BaseCommand):
    help = "Clean template code like {{ ... }} from Blogs.title, Blogs.content, Blogs.author"

    def handle(self, *args, **options):
        def remove_template_code(value):
            """
            Remove occurrences of {{ ... }} from the string.
            If value is not a string, return as-is.
            """
            if not isinstance(value, str):
                return value
            # Remove all balanced occurrences of {{ ... }}
            while "{{" in value and "}}" in value:
                start = value.find("{{")
                end = value.find("}}", start)
                if end != -1:
                    value = value[:start] + value[end + 2:]
                else:
                    # no matching closing braces; break to avoid infinite loop
                    break
            return value.strip()

        blogs = Blogs.objects.all()
        cleaned_count = 0
        cleaned_ids = []

        for blog in blogs:
            orig_title = blog.title
            orig_content = blog.content
            orig_author = blog.author

            new_title = remove_template_code(orig_title)
            new_content = remove_template_code(orig_content)
            new_author = remove_template_code(orig_author)

            if new_title != orig_title or new_content != orig_content or new_author != orig_author:
                blog.title = new_title
                blog.content = new_content
                blog.author = new_author
                blog.save()
                cleaned_count += 1
                cleaned_ids.append(blog.id)

        self.stdout.write(self.style.SUCCESS(f"Cleaned {cleaned_count} blog(s)."))
        if cleaned_ids:
            self.stdout.write("Cleaned blog ids: " + ", ".join(map(str, cleaned_ids)))
