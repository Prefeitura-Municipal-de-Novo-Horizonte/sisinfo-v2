#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

try:
    django.setup()
    print("✓ Django setup successful")
    
    from dashboard.models import Material, Bidding, MaterialBidding
    print("✓ Models imported successfully")
    
    print(f"✓ Material fields: {[f.name for f in Material._meta.get_fields()]}")
    print(f"✓ Bidding fields: {[f.name for f in Bidding._meta.get_fields()]}")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
