# UMS GCMC Project - Case Study A.1

Adsorption in slit-like pores using Grand-Canonical Monte Carlo simulation.

## Team
- Sami
- Guido
- Ida

## Setup Guide

### Windows (WSL + VSCode)

1. Open Ubuntu terminal (search "Ubuntu" in Start menu)

2. Clone the repo to your home folder:
```bash
cd ~
git clone https://github.com/thefinepotato/ums-gcmc-project.git
```
Your files are now at: `\\wsl.localhost\Ubuntu\home\YOUR-USERNAME\ums-gcmc-project`

3. Open in VSCode:
```bash
cd ~/ums-gcmc-project
code .
```
Or: Open VSCode → Install "WSL" extension → Click green button bottom-left → "Connect to WSL" → Open folder → `/home/YOUR-USERNAME/ums-gcmc-project`

### Mac

1. Open Terminal

2. Clone to your home folder:
```bash
cd ~
git clone https://github.com/thefinepotato/ums-gcmc-project.git
```
Your files are now at: `/Users/YOUR-USERNAME/ums-gcmc-project`

3. Open in VSCode:
```bash
cd ~/ums-gcmc-project
code .
```

---

## First time Git setup (all systems)
```bash
git config --global user.name "Your Name"
git config --global user.email "your-github-email@example.com"
```

Then create your own branch:
```bash
cd ~/ums-gcmc-project
git checkout -b your-name
```

---## Setup Guide

### Windows (WSL + VSCode)

1. Open Ubuntu terminal (search "Ubuntu" in Start menu)

2. Clone the repo to your home folder:
```bash
cd ~
git clone https://github.com/thefinepotato/ums-gcmc-project.git
```
Your files are now at: `\\wsl.localhost\Ubuntu\home\YOUR-USERNAME\ums-gcmc-project`

3. Open in VSCode:
```bash
cd ~/ums-gcmc-project
code .
```
Or: Open VSCode → Install "WSL" extension → Click green button bottom-left → "Connect to WSL" → Open folder → `/home/YOUR-USERNAME/ums-gcmc-project`

### Mac

1. Open Terminal

2. Clone to your home folder:
```bash
cd ~
git clone https://github.com/thefinepotato/ums-gcmc-project.git
```
Your files are now at: `/Users/YOUR-USERNAME/ums-gcmc-project`

3. Open in VSCode:
```bash
cd ~/ums-gcmc-project
code .
```

---

## First time Git setup (all systems)
```bash
git config --global user.name "Your Name"
git config --global user.email "your-github-email@example.com"
```

Then create your own branch:
```bash
cd ~/ums-gcmc-project
git checkout -b your-name
```

---
# Daily workflow

## First time setup (after cloning)
```bash
git clone https://github.com/thefinepotato/ums-gcmc-project.git
cd ums-gcmc-project
git checkout -b your-name          # Create your own branch (e.g., guido, ida, sabo)
```

## Working on your branch
```bash
git checkout your-name             # Make sure you're on YOUR branch, not main
git pull origin main               # Get latest changes from main

# ... do your work ...

git status                         # Check what you changed
git add             # Add only files you meant to change
git commit -m "Description of what you did"
git push origin your-name          # Push to YOUR branch, not main
```

## Merging to main (after team agrees)
```bash
git checkout main
git pull origin main
git merge your-name
git push origin main
git checkout your-name             # Go back to your branch
```

## Golden rules
- **Never work directly on main**
- Never use `git add .`
- Always check `git status` before committing
- Communicate on Discord before merging to main