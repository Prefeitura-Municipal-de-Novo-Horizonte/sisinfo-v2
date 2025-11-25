
import os
import django
from django.utils.text import slugify

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')
django.setup()

from dashboard.models import Material

print("Checking Material slugs...")
materials = Material.objects.all()
count = 0
fixed = 0

for material in materials:
    count += 1
    if not material.slug:
        print(f"Fixing empty slug for Material ID {material.id}: {material.name}")
        base_slug = slugify(material.name)
        if not base_slug:
            base_slug = f"material-{material.id}"
        
        # Ensure uniqueness
        slug = base_slug
        counter = 1
        while Material.objects.filter(slug=slug).exclude(id=material.id).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
            
        material.slug = slug
        material.save()
        fixed += 1
        print(f"  -> New slug: {material.slug}")

print(f"Finished. Checked {count} materials. Fixed {fixed} empty slugs.")
