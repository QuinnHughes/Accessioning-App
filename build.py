#!/usr/bin/env python3
"""Build script for packaging the Accessioning App"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and print output"""
    print(f"\n→ Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if result.returncode != 0:
        print(f"✗ Command failed with exit code {result.returncode}")
        sys.exit(1)
    print("✓ Success")
    return result

def main():
    root_dir = Path(__file__).parent
    frontend_dir = root_dir / "Frontend"
    backend_dir = root_dir / "Backend"
    dist_dir = frontend_dir / "dist"
    
    print("=" * 60)
    print("Accessioning App - Build Tool")
    print("=" * 60)
    
    # Step 1: Build React frontend
    print("\n[1/5] Building React frontend...")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    run_command("npm run build", cwd=frontend_dir)
    
    # Step 2: Install PyInstaller if needed
    print("\n[2/5] Checking PyInstaller...")
    try:
        import PyInstaller
        print("✓ PyInstaller already installed")
    except ImportError:
        print("Installing PyInstaller...")
        run_command(f'"{sys.executable}" -m pip install pyinstaller')
    
    # Step 3: Create PyInstaller build
    print("\n[3/5] Building executable with PyInstaller...")
    
    # Clean dist folder if it exists
    dist_app_dir = root_dir / 'dist' / 'AccessioningApp'
    if dist_app_dir.exists():
        print(f"Cleaning existing dist folder: {dist_app_dir}")
        shutil.rmtree(dist_app_dir)
    
    spec_file = root_dir / "accessioning.spec"
    if spec_file.exists():
        run_command(f'"{sys.executable}" -m PyInstaller accessioning.spec', cwd=root_dir)
    else:
        print("✗ accessioning.spec not found. Creating it...")
        create_spec_file(root_dir)
        run_command(f'"{sys.executable}" -m PyInstaller accessioning.spec', cwd=root_dir)
    
    # Step 4: Create ZIP archive
    print("\n[4/5] Creating ZIP archive...")
    zip_path = root_dir / "AccessioningApp.zip"
    if zip_path.exists():
        zip_path.unlink()
    
    shutil.make_archive(
        str(root_dir / "AccessioningApp"),
        'zip',
        root_dir / 'dist',
        'AccessioningApp'
    )
    
    # Step 5: Package results
    print("\n[5/5] Packaging complete!")
    print(f"\n✓ Executable folder: {root_dir / 'dist' / 'AccessioningApp'}")
    print(f"✓ ZIP archive created: {zip_path}")
    
    # Get zip file size
    zip_size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"  Size: {zip_size_mb:.1f} MB")
    
    print("\n" + "=" * 60)
    print("DISTRIBUTION INSTRUCTIONS")
    print("=" * 60)
    print(f"\n1. Share the ZIP file: {zip_path.name}")
    print("2. Extract on target machines")
    print("3. Ensure PostgreSQL is running with 'accessioning_app' database")
    print("4. Run AccessioningApp.exe")
    print("\nNo Python or Node.js installation required on target machines!")
    
def create_spec_file(root_dir):
    """Create PyInstaller spec file"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['launcher.py'],
    pathex=['Backend'],
    binaries=[],
    datas=[
        ('Frontend/dist', 'Frontend/dist'),
        ('Backend/main.py', 'Backend'),
        ('Backend/api', 'Backend/api'),
        ('Backend/core', 'Backend/core'),
        ('Backend/db', 'Backend/db'),
        ('Backend/schemas', 'Backend/schemas'),
    ],
    hiddenimports=[
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'sqlalchemy.sql.default_comparator',
        'psycopg',
        'psycopg2',
        'bcrypt',
        'passlib',
        'jose',
        'pandas',
        'openpyxl',
        'main',
        'Backend.main',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AccessioningApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AccessioningApp',
)
'''
    
    spec_path = root_dir / 'accessioning.spec'
    spec_path.write_text(spec_content)
    print(f"✓ Created {spec_path}")

if __name__ == "__main__":
    main()
