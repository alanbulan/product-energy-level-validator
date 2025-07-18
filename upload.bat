@echo off
echo Uploading to GitHub...

REM Check if Git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git not found. Please install Git first.
    pause
    exit /b 1
)

REM Create .gitignore file
(
echo __pycache__/
echo *.pyc
echo *.pyo
echo *.pyd
echo .Python
echo *.so
echo .coverage
echo .pytest_cache/
echo *.egg-info/
echo dist/
echo build/
echo *.xlsx
echo !*.xlsx
echo .env
echo *.log
echo temp/
echo test_*.xlsx
) > .gitignore

REM Initialize Git repository
git init

REM Add all files
git add .

REM Create initial commit
git commit -m "Initial commit: Product Energy Level Validation System"

REM Set remote repository (replace with your GitHub repo)
git remote add origin https://github.com/alanbulan/product-energy-level-validator.git

REM Set main branch
git branch -M main

REM Push to GitHub with force
git push -u origin main --force

if errorlevel 1 (
    echo Push failed! Check your GitHub credentials and repository.
    pause
    exit /b 1
)

echo Upload successful!
echo Repository: https://github.com/alanbulan/product-energy-level-validator
pause
