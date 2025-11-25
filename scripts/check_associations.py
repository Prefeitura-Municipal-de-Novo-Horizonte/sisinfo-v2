
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')
django.setup()

from bidding_procurement.models import Bidding, MaterialBidding

print("Checking MaterialBidding associations...")
biddings = Bidding.objects.all()
for b in biddings:
    count = b.material_associations.count()
    print(f"Bidding: {b.name} (Slug: {b.slug}) - Count: {count}")
    if count > 0:
        print("  Associations:")
        for assoc in b.material_associations.all():
            print(f"    - Material: {assoc.material.name} | Status: {assoc.status} | Price: {assoc.price_snapshot}")
