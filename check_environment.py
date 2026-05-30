"""Quick environment check for local setup."""

import importlib

packages = ["pandas", "numpy", "matplotlib", "sklearn", "statsmodels", "sqlalchemy"]

for package in packages:
    importlib.import_module(package)
    print(f"OK: {package}")

print("Environment check passed.")
