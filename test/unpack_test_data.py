"""
Script to unpack pre-generated testdata that is required for the testsuite.
"""
import zipfile
from pathlib import Path

# Define paths
base_dir = Path(__file__).parent
zip_path = base_dir / "testdata-2.17.9.zip"
extract_dir = base_dir / "dezyne_models"

# Ensure target directory exists
extract_dir.mkdir(parents=True, exist_ok=True)

# Unpack the zip file
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(extract_dir)

print(f"Extracted '{zip_path.name}' to '{extract_dir}'. The testsuite can be executed.")
