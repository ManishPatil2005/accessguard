# TEAM-ONBOARDING.md - Team Onboarding Guide

## First Day

### Prerequisites
- [ ] Git access to repository
- [ ] Python 3.13+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed

### Quick Start (15 minutes)

```bash
# Clone repo
git clone https://github.com/your-org/accessguard.git

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py

# Visit http://localhost:8000
```

### First Task
- [ ] Create test account (email: firstname.lastname@company.com)
- [ ] Test login flow
- [ ] Read README.md and ARCHITECTURE.md
- [ ] Review code structure

---

## First Week

### Readings (Priority Order)
1. **ARCHITECTURE.md** (30 mins) - Understand system design
2. **SECURITY.md** (45 mins) - Learn security principles
3. **SETUP.md** (20 mins) - Verify local environment
4. **main.py** (60 mins) - Read backend code
5. **templates/*.html** (30 mins) - Understand frontend
6. **STANDARDS.md** (30 mins) - Code style guidelines

### Tasks
- [ ] Set up IDE (VS Code recommended plugins)
- [ ] Run TESTING.md test cases (verify all pass)
- [ ] Write one simple feature (add new field to user)
- [ ] Submit first PR with code review

---

## Code Review Guidelines

### Before Submitting PR

```
- [ ] Tests pass: pytest
- [ ] Code follows standards: pylint score >= 8.0
- [ ] Security checklist completed
- [ ] Documentation updated
- [ ] Commit messages descriptive
- [ ] No merge conflicts
```

### Review Comments

```python
# BAD: Too vague
"This is inefficient"

# GOOD: Specific with suggestion
"This query runs O(n) for every request. Consider caching with Redis 
for 5-minute TTL. Expected improvement: 50ms → 2ms latency"
```

---

## Development Workflow

### Creating a Feature

```bash
# 1. Create branch from main
git checkout main
git pull origin main
git checkout -b feature/user-profile

# 2. Implement feature
# ... Write code ...

# 3. Write tests
pytest test_user_profile.py

# 4. Commit changes
git add .
git commit -m "feat: add user profile page"

# 5. Push and create PR
git push origin feature/user-profile
# Create PR on GitHub

# 6. Address review comments
# ... Make changes ...
git add .
git commit -m "refactor: improve performance of profile page"
git push origin feature/user-profile

# 7. Merge (maintainer)
```

---

## Access Levels

```
Junior Developer:
- [ ] Read/write to branches
- [ ] Create PRs
- [ ] Review non-critical code
- [ ] Cannot merge to main

Senior Developer:
- [ ] All junior permissions
- [ ] Approve critical PRs
- [ ] Merge to main
- [ ] Deploy to staging

Maintainer:
- [ ] All permissions
- [ ] Deploy to production
- [ ] Manage releases
- [ ] Review high-level architecture
```

---

## Communication

### Channels

```
- Questions: #accessguard-dev (Slack)
- Bugs: GitHub Issues
- Discussions: GitHub Discussions
- Urgent: @on-call (PagerDuty)
- PRs: GitHub Notifications
```

### Meetings

```
Daily Standup: 9:00 AM (15 minutes)
- What did you do yesterday?
- What are you doing today?
- Any blockers?

Weekly Sync: Friday 10:00 AM (1 hour)
- Progress review
- Architecture decisions
- Demo new features
```

---

## Troubleshooting

### Database Issues

```bash
# Reset database to initial state
rm users.db
python main.py  # Auto-creates fresh database
```

### Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Permission Issues

```bash
# Windows: Run as administrator
# Linux: chmod +x main.py
```

---

**Version**: 1.0.0 | **Last Updated**: April 14, 2026
