@echo off
echo.
echo Product Energy Level Validator - Push to GitHub
echo ===============================================

REM Check if Git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git not found. Please install Git first.
    echo Download: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo Git is installed.

REM Get user input
set /p GITHUB_USERNAME="Enter GitHub username: "
set /p REPO_NAME="Enter repository name (default: product-energy-level-validator): "

if "%REPO_NAME%"=="" set REPO_NAME=product-energy-level-validator

echo.
echo Configuration:
echo    GitHub Username: %GITHUB_USERNAME%
echo    Repository Name: %REPO_NAME%
echo    Remote URL: https://github.com/%GITHUB_USERNAME%/%REPO_NAME%.git
echo.

set /p CONFIRM="Confirm push? (y/n): "
if /i not "%CONFIRM%"=="y" (
    echo Operation cancelled.
    pause
    exit /b 0
)

echo.
echo Starting push process...
echo.

REM Create .gitignore file
echo Creating .gitignore file...
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
echo Initializing Git repository...
git init

REM Add all files
echo Adding files to staging area...
git add .

REM Create initial commit
echo Creating initial commit...
git commit -m "Initial commit: Product Energy Level Validation System

Features:
- Automatic data validation and comparison
- Smart model number extraction
- Version suffix handling
- Time filtering logic
- Product relevance checking
- Excel missing data detection
- Anti-crawler mechanisms

Tech Stack:
- Python 3.7+
- pandas, requests, openpyxl
- Multi-threaded batch processing
- Intelligent algorithm optimization"

REM Set remote repository
echo Connecting to remote repository...
git remote add origin https://github.com/%GITHUB_USERNAME%/%REPO_NAME%.git

REM Set main branch
echo Setting main branch...
git branch -M main

REM Push to GitHub
echo Pushing to GitHub...
git push -u origin main

if errorlevel 1 (
    echo.
    echo Push failed! Possible reasons:
    echo    1. Repository does not exist on GitHub
    echo    2. Network connection issues
    echo    3. Authentication failed
    echo.
    echo Solutions:
    echo    1. Visit https://github.com/%GITHUB_USERNAME%/%REPO_NAME%
    echo    2. Create repository if it doesn't exist
    echo    3. Make sure you're logged into GitHub
    pause
    exit /b 1
)

echo.
echo Push successful!
echo.
echo Repository Info:
echo    URL: https://github.com/%GITHUB_USERNAME%/%REPO_NAME%
echo    README: https://github.com/%GITHUB_USERNAME%/%REPO_NAME%/blob/main/README.md
echo    Clone: git clone https://github.com/%GITHUB_USERNAME%/%REPO_NAME%.git
echo.
echo Project successfully pushed to GitHub!

pause
