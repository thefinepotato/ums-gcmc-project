# UMS GCMC Project - Case Study A.1

Adsorption in slit-like pores using Grand-Canonical Monte Carlo simulation.

## Team
- Sabo
- Guido
- Ida

## Setup
1. Clone the repo: `git clone https://github.com/thefinepotato/ums-gcmc-project.git`
2. Navigate to case study: `cd "PROJECT FILES HERE/CaseStudy_9"`

## Daily workflow

### First time setup (after cloning)
```bash
git clone https://github.com/thefinepotato/ums-gcmc-project.git
cd ums-gcmc-project
git checkout -b your-name          # Create your own branch (e.g., guido, ida, sabo)
```

### Working on your branch
```bash
git checkout your-name             # Make sure you're on YOUR branch, not main
git pull origin main               # Get latest changes from main

# ... do your work ...

git status                         # Check what you changed
git add             # Add only files you meant to change
git commit -m "Description of what you did"
git push origin your-name          # Push to YOUR branch, not main
```

### Merging to main (after team agrees)
```bash
git checkout main
git pull origin main
git merge your-name
git push origin main
git checkout your-name             # Go back to your branch
```

### Golden rules
- **Never work directly on main**
- Never use `git add .`
- Always check `git status` before committing
- Communicate on Discord before merging to main