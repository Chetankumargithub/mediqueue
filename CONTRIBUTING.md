# Contributing to MediQueue

Thank you for your interest in contributing to MediQueue! This guide explains how to contribute code, report bugs, and suggest improvements.

---

## 📋 Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on code quality and clarity
- Help others learn and improve

---

## 🐛 Report Bugs

### Before Creating Issue
- Check [existing issues](../../issues) (it might already be reported)
- Provide clear, minimal reproduction steps
- Include Python version and OS

### Create Issue
1. Click **Issues** → **New Issue**
2. Choose **Bug Report** template
3. Fill in:
   - **Title:** Brief description
   - **Description:** What happened vs. what should happen
   - **Steps to Reproduce:**
     ```
     1. Load dashboard
     2. Enter invalid O₂ value (-50)
     3. Expected: Error message shown
     4. Actual: No validation
     ```
   - **Environment:** Python 3.11, Windows, etc.
   - **Screenshots:** If applicable

---

## 💡 Suggest Enhancements

1. Click **Issues** → **New Issue**
2. Choose **Feature Request** template
3. Describe:
   - **Problem:** What issue does this solve?
   - **Solution:** Proposed feature
   - **Examples:** How would it work?
   - **Benefits:** Why is this useful?

---

## 📝 Contribute Code

### Step 1: Fork Repository
1. Click **Fork** (top right)
2. This creates your own copy: `yourusername/mediqueue`

### Step 2: Clone Your Fork
```bash
git clone https://github.com/yourusername/mediqueue.git
cd mediqueue
git remote add upstream https://github.com/originalowner/mediqueue.git
```

### Step 3: Create Feature Branch
```bash
# Get latest code from upstream
git fetch upstream
git checkout -b feature/your-feature-name

# Example:
git checkout -b feature/add-patient-notes
```

**Branch naming:**
- `feature/description` — New feature
- `bugfix/description` — Bug fix
- `docs/description` — Documentation
- `refactor/description` — Code cleanup

### Step 4: Make Changes

Edit files, test thoroughly:

```bash
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Test changes
python app.py
# Visit http://localhost:5000

# Run test suite (if available)
python -m pytest
```

**Code style:**
- Follow Python PEP 8
- Use descriptive variable names
- Add comments for complex logic
- Write docstrings for functions

### Step 5: Commit Changes

```bash
# Check what changed
git status

# Stage files
git add .

# Commit with descriptive message
git commit -m "Feature: Add patient notes functionality

- Store notes in patient record
- Display notes in dashboard
- Add edit/delete functionality
- Validate text length (max 500 chars)"

# Example commit messages:
# "Fix: Correct O2 validation range"
# "Docs: Update README with API examples"
# "Refactor: Simplify score calculation"
```

**Commit message format:**
```
[Type]: [Concise description]

[Detailed explanation of changes]
- Bullet point 1
- Bullet point 2

Fixes #123  (if fixing an issue)
Closes #456 (if closing an issue)
```

### Step 6: Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### Step 7: Create Pull Request

1. Go to original repo: [https://github.com/yourusername/mediqueue](https://github.com/yourusername/mediqueue)
2. Click **Pull Requests** → **New Pull Request**
3. Click **compare across forks**
4. Set:
   - **Base:** originalowner/mediqueue:main
   - **Compare:** yourusername/mediqueue:feature/your-feature-name
5. Click **Create Pull Request**
6. Fill in:
   - **Title:** Brief description
   - **Description:** What does this PR do? Why?
   - **Related Issues:** Links to issues (#123, #456)
   - **Screenshots:** If UI changes

### Step 8: Respond to Review

Maintainers will review your code:
- ✅ Approve — Your PR is accepted!
- ❓ Request Changes — Make updates
- 💬 Comment — Questions or suggestions

If changes requested:
```bash
# Make changes to files
# ...

# Commit and push (same branch)
git add .
git commit -m "Address review feedback: [description]"
git push origin feature/your-feature-name

# PR automatically updates with new commits
```

### Step 9: Merge & Cleanup

Once approved and merged:
```bash
# Switch back to main
git checkout main

# Get latest from upstream
git fetch upstream
git pull upstream main

# Delete feature branch locally
git branch -d feature/your-feature-name

# Delete feature branch on GitHub
git push origin --delete feature/your-feature-name
```

---

## 📚 Documentation Changes

1. Fork & clone as above
2. Edit relevant `.md` files
3. Preview markdown locally (or on GitHub)
4. Commit with message: `docs: [what changed]`
5. Open PR

---

## ✅ Testing Checklist

Before submitting PR, ensure:

- [ ] Code runs without errors (`python app.py`)
- [ ] No console errors (check browser dev tools)
- [ ] Input validation works (test invalid values)
- [ ] Edge cases handled (None, empty, negative values)
- [ ] Tests pass (if applicable)
- [ ] Code follows style guide
- [ ] Comments added for complex logic
- [ ] README updated (if needed)
- [ ] No breaking changes to API

---

## 🔍 Code Review Criteria

Your code should:

✅ **Solve the problem** — Does it fix the issue or add the feature?

✅ **Follow conventions** — Consistent style, naming, structure

✅ **Handle errors** — Try-except for failures, validation for inputs

✅ **Performance** — No unnecessary loops, efficient algorithms

✅ **Security** — Input validation, no hardcoded secrets

✅ **Documentation** — Comments, docstrings, README updates

✅ **Tests** — Verify functionality, edge cases

❌ **Code smells:**
- Duplicate code → Extract to function
- Long functions → Break into smaller parts
- Magic numbers → Use constants
- Unclear names → Rename for clarity

---

## 📦 File Structure Rules

Keep structure clean:

```
mediqueue/
├── app.py                 # API routes only (thin layer)
├── triage_engine.py       # All business logic
├── requirements.txt       # Update if adding packages
├── templates/
│   └── index.html         # Don't edit excessively
├── static/
│   ├── main.js            # Frontend logic
│   └── style.css          # Styling
├── output/                # Generated files (not tracked)
└── docs/                  # Documentation (new folder if needed)
```

---

## 🚀 Adding Dependencies

If your feature needs a new package:

1. **Discuss first** — Open issue, ask maintainers
2. **Install locally:**
   ```bash
   pip install package-name
   ```
3. **Update requirements.txt:**
   ```bash
   pip freeze > requirements.txt
   ```
4. **Justify in PR** — Why is this library needed?
5. **Check size** — Don't add bloat (Pandas/Matplotlib are discouraged)

---

## 📈 Improving Performance

If optimizing code, provide metrics:

```python
# Before (with timing)
import time
start = time.time()
result = old_algorithm()
print(f"Time: {time.time() - start:.3f}s")

# After
result = new_algorithm()
print(f"Time: {time.time() - start:.3f}s")

# In PR: "Improved X by 3x (100ms → 33ms)"
```

---

## 🎓 Learning Resources

- **Python PEP 8:** [PEP 8 Style Guide](https://pep8.org/)
- **Git Guide:** [Git Handbook](https://guides.github.com/introduction/git-handbook/)
- **PR Tips:** [How to Write Good PR](https://github.com/blog/1943-how-to-write-the-perfect-pull-request)
- **Commit Messages:** [Conventional Commits](https://www.conventionalcommits.org/)

---

## ❓ Questions?

- Check existing issues & discussions
- Ask in PR comments
- Email: [your-email-if-applicable]

---

## 🙏 Thank You!

Every contribution helps make MediQueue better. Whether it's code, documentation, bug reports, or ideas — **we appreciate it!**

---

## 📋 Quick Contributor Checklist

```
Before opening PR:
☐ Forked repository
☐ Created feature branch
☐ Made changes to relevant files
☐ Tested locally (python app.py)
☐ Validated input/edge cases
☐ Ran any existing tests
☐ Updated documentation (if needed)
☐ Committed with clear message
☐ Pushed to your fork
☐ Created PR with description
☐ Linked related issues
```

---

**Happy Contributing!** 🎉
