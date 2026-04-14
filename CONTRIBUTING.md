# CONTRIBUTING.md - Contributing to AccessGuard

## Code of Conduct
Be respectful, inclusive, and professional in all interactions.

## How to Contribute

### 1. Fork and Clone
```bash
git clone https://github.com/your-fork/AccessGuard.git
cd AccessGuard
```

### 2. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 3. Make Changes
- Follow Python PEP 8 style guide
- Add comments for complex logic
- Test your changes thoroughly

### 4. Commit Messages
Format: `<type>: <description>`

Types:
- `feature`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style
- `refactor`: Code refactoring
- `test`: Test cases
- `security`: Security improvement
- `perf`: Performance improvement

Example:
```bash
git commit -m "feature: add email verification on registration"
```

### 5. Push and Create PR
```bash
git push origin feature/your-feature-name
```

## Development Setup
```bash
python -m venv .venv
source .venv/bin/activate  # or .\.venv\Scripts\activate on Windows
pip install -r requirements.txt
python main.py
```

## Testing Before PR
- [ ] All unit tests pass
- [ ] No SQL injection vulnerabilities
- [ ] No plaintext passwords
- [ ] Brute-force protection working
- [ ] Audit logs recorded
- [ ] RBAC enforced
- [ ] No security warnings

## Pull Request Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] Security improvement

## Testing
- [ ] Manually tested
- [ ] All tests pass

## Security Checklist
- [ ] No new SQL injection risks
- [ ] No plaintext data exposure
- [ ] Parameterized queries used
- [ ] Error messages sanitized
```

---

**Version**: 1.0.0 | **Last Updated**: April 14, 2026
