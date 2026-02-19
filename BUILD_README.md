# Accessioning App - Build & Distribution Guide

## Overview
This guide explains how to build and distribute the Accessioning App as a standalone executable.

## Prerequisites

### For Building
1. **Python 3.11+** installed
2. **Node.js 18+** and npm installed
3. **PostgreSQL** database server (for runtime)

### For Development
- Backend dependencies in `Backend/requirements.txt`
- Frontend dependencies in `Frontend/package.json`

## Quick Build

Run the build script from the project root:

```bash
python build.py
```

This will:
1. Build the React frontend (production build)
2. Install PyInstaller if needed
3. Create a standalone executable with PyInstaller
4. Package everything into `dist/AccessioningApp/`

## Manual Build Steps

### 1. Install Backend Dependencies

```bash
cd Backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install pyinstaller
```

### 2. Build Frontend

```bash
cd Frontend
npm install
npm run build
```

This creates `Frontend/dist/` with the production build.

### 3. Create Executable

```bash
# From project root
python -m PyInstaller accessioning.spec --clean
```

## Distribution

The executable is created in `dist/AccessioningApp/`:

```
dist/AccessioningApp/
├── AccessioningApp.exe    # Main executable
├── Frontend/              # Built frontend assets
│   └── dist/
├── Backend/               # Backend Python modules
│   ├── api/
│   ├── core/
│   ├── db/
│   └── schemas/
└── [Python runtime files]
```

### Deployment Steps

1. **Copy the entire `AccessioningApp` folder** to target machines
2. **Ensure PostgreSQL is running** with the database configured
3. **Run `AccessioningApp.exe`**

The application will:
- Start the backend server on port 8000
- Automatically open a browser to `http://localhost:8000`

## Database Configuration

The app requires a PostgreSQL database. Default connection:

```
Host: localhost
Port: 5432
Database: accessioning_app
Username: postgres
Password: password
```

### Setting Up the Database

1. Install PostgreSQL
2. Create the database:
   ```sql
   CREATE DATABASE accessioning_app;
   ```
3. The application will create tables automatically on first run

To use a different database, modify `Backend/db/session.py` before building.

## Application Structure

### Frontend (React + Vite)
- **Pages**: Login, Projects, Empty Shelves, Accessioning, Batch Printing, Upload/Export
- **Components**: Layout, ConnectionManager
- **API Client**: Handles all backend requests

### Backend (FastAPI)
- **API Routes**: `/api/auth`, `/api/projects`, `/api/shelves`, `/api/accession`, `/api/batch-print`, `/api/items`
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Features**: JWT authentication, Excel generation, batch label printing

## Troubleshooting

### Build Failures

**Frontend build fails:**
```bash
cd Frontend
npm install --force
npm run build
```

**PyInstaller fails:**
```bash
pip install --upgrade pyinstaller
python -m PyInstaller accessioning.spec --clean
```

### Runtime Issues

**Database connection fails:**
- Ensure PostgreSQL is running
- Check database credentials in `Backend/db/session.py`
- Verify the `accessioning_app` database exists

**Port 8000 already in use:**
- Close other applications using port 8000
- Or modify the port in `launcher.py`

**Browser doesn't open automatically:**
- Manually navigate to `http://localhost:8000`

## Development Mode

To run in development mode (recommended for testing):

### Backend
```bash
cd Backend
venv\Scripts\activate
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd Frontend
npm run dev
```

Frontend dev server runs on `http://localhost:5174` and proxies API calls to backend.

## Creating an Installer (Optional)

### Using Inno Setup (Windows)

1. Install [Inno Setup](https://jrsoftware.org/isdl.php)
2. Create an Inno Setup script (`.iss` file)
3. Run: `iscc installer.iss`

### Using MSI (Windows)

See `create_msi.py` for details on creating MSI installers with cx_Freeze.

## Notes

- The executable is **self-contained** except for the PostgreSQL requirement
- Total size: ~150-200 MB (includes Python runtime and all dependencies)
- First launch may take 10-15 seconds while Python initializes
- The console window shows server logs and must remain open

## Support

For issues or questions, contact the development team.
