import os, glob

# Simulate what dependencies.py does
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath("app/api/v1/dependencies.py"))))
print("base_dir:", base_dir)
print("CWD:", os.getcwd())

cache_dirs = [
    ".cache",
    os.path.join(base_dir, "data", "cache"),
    os.path.join(base_dir, ".cache"),
    "data/cache",
    ".cache",
    os.path.join(os.getcwd(), "data", "cache"),
]

for cdir in cache_dirs:
    exists = os.path.exists(cdir)
    pkls = glob.glob(os.path.join(cdir, "*.pkl"))
    print(f"  '{cdir}' exists={exists} pkls={pkls}")
