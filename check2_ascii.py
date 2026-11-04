import os, sys
sys.path.insert(0, r"C:\Users\Jessa S. Datul\Downloads\TabuLink_Final")
os.environ["DJANGO_SETTINGS_MODULE"] = "tabulink.settings"
import django
django.setup()
from users.models import assignable_roles
for r in assignable_roles():
    print(r.key + ":" + r.name)
