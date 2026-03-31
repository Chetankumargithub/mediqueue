# GitHub Setup Guide for MediQueue

## Step-by-Step Instructions to Push to GitHub

### Step 1: Create GitHub Account (if needed)
1. Go to [GitHub.com](https://github.com)
2. Click **Sign up**
3. Enter email, create password, username
4. Verify email

---

### Step 2: Create New Repository on GitHub

1. Log in to GitHub
2. Click **+** icon (top right) → **New repository**
3. Fill in details:
   - **Repository name:** `mediqueue`
   - **Description:** Emergency Triage Priority System
   - **Visibility:** Choose **Public** (or Private if preferred)
   - **Initialize with:** Do NOT check any boxes
     - We already have README.md, .gitignore, LICENSE
4. Click **Create repository**

**Result:** GitHub shows you commands to push existing code

---

### Step 3: Open PowerShell Terminal

1. Open VS Code (your workspace)
2. Press **Ctrl + `** to open terminal
3. Ensure you're in mediqueue directory:
   ```powershell
   cd "c:\Users\Sumit and Chetan\OneDrive\Desktop\Mediqueue"
   ```

---

### Step 4: Initialize Git & Commit

```powershell
# Check git is installed
git --version
# Should show: git version 2.x.x

# Initialize git repository
git init

# Configure git (one-time setup)
git config --global user.name "Your Name"
git config --global user.email "your.email@gmail.com"

# Verify configuration
git config --list

# Add all files (respects .gitignore)
git add .

# Check what will be committed
git status
# Should show all files except .venv, __pycache__, output/

# Create initial commit
git commit -m "Initial commit: MediQueue triage system

- Core triage engine with acuity scoring
- Flask REST API with 7 endpoints  
- Interactive dashboard with real-time charts
- CSV import/export functionality
- Input validation (frontend + backend)
- Min-heap priority queue with O(log n) performance
- 17 unit tests with validation coverage"
```

**Expected output:**
```
[main 3f5a9c2] Initial commit: MediQueue triage system
 12 files changed, 2345 insertions(+)
 create mode 100644 .gitignore
 create mode 100644 LICENSE
 create mode 100644 README.md
 create mode 100644 app.py
 ... etc
```

---

### Step 5: Connect to GitHub Repository

Replace `yourusername` with your actual GitHub username:

```powershell
# Add GitHub repository as remote
git remote add origin https://github.com/yourusername/mediqueue.git

# Verify remote was added
git remote -v
# Should show:
# origin  https://github.com/yourusername/mediqueue.git (fetch)
# origin  https://github.com/yourusername/mediqueue.git (push)
```

---

### Step 6: Rename Branch to Main (if needed)

```powershell
# Check current branch
git branch
# Shows: * master (or main)

# If it shows "master", rename to "main"
git branch -M main

# Verify
git branch
# Should show: * main
```

---

### Step 7: Push to GitHub

**First push requires authentication:**

```powershell
git push -u origin main
```

**GitHub will prompt for authentication.**

#### Option A: Use Personal Access Token (Recommended)
1. GitHub displays: **Authenticate with GitHub using a browser** → Click link
2. Authorize GitHub in browser
3. Returns to terminal, pushes automatically

#### Option B: Manual Token Entry
1. Go to GitHub → **Settings** → **Developer settings** → **Personal access tokens**
2. Click **Generate new token**
3. Name: "mediqueue"
4. Select: `repo` (full control)
5. Click **Generate token**
6. Copy token (appears once!)
7. In terminal, paste as password when prompted

**Expected output:**
```
Enumerating objects: 15, done.
Counting objects: 100% (15/15), done.
Writing objects: 100% (15/15), 23.5 KiB | 1.5 MiB/s, done.
Total 15 (delta 0), reused 0 (delta 0), pack-reused 0

To https://github.com/yourusername/mediqueue.git
 * [new branch]      main -> main
Branch 'main' is set up to track 'origin/main'.
```

---

## Step 8: Verify on GitHub

1. Go to: `https://github.com/yourusername/mediqueue`
2. You should see:
   - ✅ All code files (app.py, triage_engine.py, etc.)
   - ✅ README.md displayed on main page
   - ✅ templates/, static/ folders
   - ✅ LICENSE file
   - ✅ .gitignore file
   - ❌ No .venv folder (excluded by .gitignore)
   - ❌ No __pycache__ (excluded)
   - ❌ No output/ CSV files (excluded)

---

## Future Commits (Add/Update Code)

### After you make changes:

```powershell
# Check what changed
git status

# Stage changes
git add .

# Commit with message
git commit -m "Feature: [describe what changed]"

# Push to GitHub
git push origin main
```

### Examples:
```powershell
git commit -m "Add patient filter by priority"
git commit -m "Fix: Acuity score calculation edge case"
git commit -m "Update: Improve dashboard responsiveness"
```

---

## Common Issues & Solutions

### Issue: "fatal: not a git repository"
**Solution:** You're in wrong directory
```powershell
cd "c:\Users\Sumit and Chetan\OneDrive\Desktop\Mediqueue"
git init
```

### Issue: "remote origin already exists"
**Solution:** Remove old remote first
```powershell
git remote remove origin
git remote add origin https://github.com/yourusername/mediqueue.git
```

### Issue: "error: failed to push some refs"
**Solution:** Your local is behind remote
```powershell
git pull origin main
git push origin main
```

### Issue: "Please tell me who you are"
**Solution:** Configure git user
```powershell
git config --global user.name "Your Name"
git config --global user.email "your.email@gmail.com"
```

### Issue: "fatal: Authentication failed"
**Solution:** Use Personal Access Token instead of password
- Generate token on GitHub
- Paste as password when prompted

---

## Share Your Repository

Once uploaded, share the link:
```
https://github.com/yourusername/mediqueue
```

---

## Clone Your Project (From Another Computer)

```powershell
cd Desktop
git clone https://github.com/yourusername/mediqueue.git
cd mediqueue

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run
python app.py
```

---

## Commands Reference

| Command | Purpose |
|---------|---------|
| `git init` | Initialize repository |
| `git add .` | Stage all changes |
| `git commit -m "msg"` | Create commit |
| `git remote add origin [url]` | Connect to GitHub |
| `git push origin main` | Upload to GitHub |
| `git pull origin main` | Download from GitHub |
| `git status` | Check what changed |
| `git log` | View commit history |
| `git branch` | View branches |

---

## You're Done! 🎉

Your MediQueue project is now on GitHub!

**Next steps:**
- ✅ Share the repository link with others
- ✅ Continue making commits as you update code
- ✅ Open issues for bug tracking
- ✅ Accept pull requests from contributors (if public)

---

**Need help?** Check GitHub documentation: [docs.github.com](https://docs.github.com)
