import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')
django.setup()

try:
    from organizational_structure.forms import DirectionForm, SectorForm
    from organizational_structure.filters import DirectionFilter, SectorFilter
    from dashboard.views import DirectionForm as ViewDirectionForm
    
    print("✓ Imports verified successfully")
except ImportError as e:
    print(f"✗ Import Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
