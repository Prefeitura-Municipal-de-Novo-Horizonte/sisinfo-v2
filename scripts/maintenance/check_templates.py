import os

base_path = "organizational_structure/templates/organizational_structure"
files_to_check = [
    "diretorias.html",
    "diretoria_detail.html",
    "setores.html",
    "setor_detail.html",
    "include/_search_setor.html",
    "include/_table_setor.html"
]

all_exist = True
for file in files_to_check:
    path = os.path.join(base_path, file)
    if os.path.exists(path):
        print(f"✓ Found {path}")
    else:
        print(f"✗ Missing {path}")
        all_exist = False

if all_exist:
    print("All templates found.")
else:
    print("Some templates are missing.")
    exit(1)
