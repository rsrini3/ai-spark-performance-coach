# Setting Up GitHub Repository

This guide will help you set up your GitHub repository and ensure sensitive files like `.env` are not committed.

## Step 1: Verify .env is Ignored

The `.env` file is already in `.gitignore`. Verify it's not tracked:

```bash
# Check if .env is ignored
git check-ignore -v .env src/ai_spark_coach/.env

# Should show: .gitignore:46:.env
```

## Step 2: Initialize Git Repository (if not already done)

```bash
cd ai-spark-performance-coach
git init
```

## Step 3: Add Files to Git

```bash
# Add all files (except those in .gitignore)
git add .

# Verify .env is NOT in the staging area
git status | grep -E "\.env"

# Should show nothing (no .env files)
```

## Step 4: Create Initial Commit

```bash
git commit -m "Initial commit: AI Spark Performance Coach v0.1.0"
```

## Step 5: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `ai-spark-performance-coach` (or your preferred name)
3. Description: "AI-assisted Spark performance analysis tool"
4. Choose Public or Private
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

## Step 6: Connect Local Repository to GitHub

```bash
# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/ai-spark-performance-coach.git

# Or if using SSH:
# git remote add origin git@github.com:YOUR_USERNAME/ai-spark-performance-coach.git

# Verify remote
git remote -v
```

## Step 7: Push to GitHub

```bash
# Push to main branch
git branch -M main
git push -u origin main
```

## Step 8: Verify .env is Not on GitHub

1. Go to your repository on GitHub
2. Check the file list - you should **NOT** see `.env` or `src/ai_spark_coach/.env`
3. If you see `.env`, it was committed before adding to `.gitignore`. See "Removing .env from Git History" below.

## Removing .env from Git History (if already committed)

If `.env` was accidentally committed before, remove it:

```bash
# Remove from git history (but keep local file)
git rm --cached .env
git rm --cached src/ai_spark_coach/.env

# Commit the removal
git commit -m "Remove .env files from repository"

# Push to GitHub
git push origin main
```

**Note:** If `.env` was already pushed to GitHub with sensitive data:
1. Consider rotating your API keys
2. The file will still be in git history - consider using `git filter-branch` or BFG Repo-Cleaner for complete removal

## Security Checklist

- [ ] `.env` is in `.gitignore`
- [ ] `.env.example` is committed (template file)
- [ ] No `.env` files in `git status`
- [ ] `.env` not visible on GitHub
- [ ] API keys are not in any committed files
- [ ] README mentions `.env.example` for setup

## Using .env.example

Users cloning your repository should:

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add their actual API key
# .env is in .gitignore, so it won't be committed
```

## Additional Security Tips

1. **Never commit API keys** - Always use environment variables or `.env` files
2. **Use GitHub Secrets** - For CI/CD, use GitHub Actions secrets
3. **Rotate keys** - If a key is accidentally exposed, rotate it immediately
4. **Review commits** - Before pushing, review what's being committed: `git diff --cached`

