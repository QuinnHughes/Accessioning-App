#!/usr/bin/env python3
"""
MSI Installer creator using cx_Freeze (MIT License)
Alternative to Inno Setup using only permissively-licensed tools
"""

import sys
import subprocess
from pathlib import Path

def create_msi_installer():
    """Create MSI installer using cx_Freeze"""
    
    print("=" * 60)
    print("MSI Installer Builder (cx_Freeze)")
    print("=" * 60)
    
    # Check if cx_Freeze is installed
    try:
        import cx_Freeze
        print("✓ cx_Freeze is installed")
    except ImportError:
        print("\nInstalling cx_Freeze (MIT License)...")
        subprocess.run([sys.executable, "-m", "pip", "install", "cx-Freeze"], check=True)
        import cx_Freeze
    
    print("\nNote: MSI creation requires:")
    print("  1. Run build.py first to create the executable")
    print("  2. cx_Freeze will bundle into MSI format")
    print("  3. Resulting MSI can be deployed via Group Policy")
    
    print("\nTo create MSI, run:")
    print("  python setup_msi.py bdist_msi")

def create_setup_msi():
    """Create cx_Freeze setup.py for MSI building"""
    
    setup_content = '''#!/usr/bin/env python3
"""
cx_Freeze setup for MSI installer creation
License: MIT (cx_Freeze is MIT licensed)
"""

import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but some may need explicit specification
build_exe_options = {
    "packages": [
        "fastapi", "uvicorn", "sqlalchemy", "psycopg", 
        "pymarc", "bcrypt", "jose", "passlib"
    ],
    "include_files": [
        ("Frontend/dist", "Frontend/dist"),
        ("Backend/cgp_sudoc_index.db", "cgp_sudoc_index.db"),
        ("Backend/Record_sets", "Record_sets"),
    ],
    "excludes": ["tkinter"],
}

# MSI-specific options
bdist_msi_options = {
    "add_to_path": False,
    "initial_target_dir": r"[ProgramFilesFolder]\\SuDoc Catalog",
    "install_icon": "Backend/icon.ico",
}

setup(
    name="SuDocCatalog",
    version="1.0.0",
    description="Government Document Cataloging",
    author="Quinn Hughes",
    options={
        "build_exe": build_exe_options,
        "bdist_msi": bdist_msi_options,
    },
    executables=[
        Executable(
            "launcher.py",
            base=None,  # Use "Win32GUI" to hide console
            target_name="SuDocCatalog.exe",
            icon="Backend/icon.ico",
        )
    ],
)
'''
    
    setup_path = Path(__file__).parent / "setup_msi.py"
    setup_path.write_text(setup_content)
    print(f"\n✓ Created {setup_path}")
    print("\nBuild MSI with: python setup_msi.py bdist_msi")

if __name__ == "__main__":
    create_msi_installer()
    create_setup_msi()
