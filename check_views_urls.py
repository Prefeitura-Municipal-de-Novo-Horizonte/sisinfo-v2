import os
import django
import sys
from django.urls import reverse, resolve

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')
django.setup()

try:
    # Check imports
    from organizational_structure.views import directions, sectors
    print("✓ View imports verified successfully")

    # Check URL resolution
    # Note: We need to use the full path including the prefix defined in core/urls.py
    # 'structure/' is the prefix for organizational_structure.urls
    
    url = reverse('organizational_structure:diretorias')
    print(f"✓ URL reverse 'organizational_structure:diretorias' -> {url}")
    
    match = resolve('/structure/diretorias/')
    print(f"✓ URL resolve '/structure/diretorias/' -> {match.view_name}")

    url = reverse('organizational_structure:setores')
    print(f"✓ URL reverse 'organizational_structure:setores' -> {url}")

    match = resolve('/structure/setores/')
    print(f"✓ URL resolve '/structure/setores/' -> {match.view_name}")

except ImportError as e:
    print(f"✗ Import Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
