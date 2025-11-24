
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')
django.setup()

from dashboard.models import Bidding

print("Checking Biddings for empty slugs...")
biddings = Bidding.objects.all()
for b in biddings:
    print(f"ID: {b.id}, Name: {b.name}, Slug: '{b.slug}'")
    if not b.slug:
        print(f"⚠️  WARNING: Bidding {b.id} has empty slug! Fixing...")
        b.save() # Save should trigger slug generation
        print(f"   -> New slug: '{b.slug}'")
