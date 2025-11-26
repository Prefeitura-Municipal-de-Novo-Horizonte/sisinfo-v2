
import os
import django
from django.utils.text import slugify

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')
django.setup()

from organizational_structure.models import Direction, Sector

def fix_slugs(model, name_field='name'):
    print(f"Checking {model.__name__} slugs...")
    objects = model.objects.all()
    count = 0
    fixed = 0
    for obj in objects:
        count += 1
        if not obj.slug:
            print(f"Fixing empty slug for {model.__name__} ID {obj.id}: {getattr(obj, name_field)}")
            base_slug = slugify(getattr(obj, name_field))
            if not base_slug:
                base_slug = f"{model.__name__.lower()}-{obj.id}"
            
            slug = base_slug
            counter = 1
            while model.objects.filter(slug=slug).exclude(id=obj.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
                
            obj.slug = slug
            obj.save()
            fixed += 1
            print(f"  -> New slug: {obj.slug}")
    print(f"Finished {model.__name__}. Checked {count}. Fixed {fixed}.")

fix_slugs(Direction)
fix_slugs(Sector)
