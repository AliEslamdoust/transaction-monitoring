from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model


@receiver(post_migrate)
def create_test_user(sender, **kwargs):
    """Create a test user on app startup if there is not one already

    Args:
        sender (str): app name
    """
    if sender.name == "transactions":
        User = get_user_model()
        username = "testuser"
        password = "testpassword"

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, password=password)
            print(f"Created startup user '{username}'")
