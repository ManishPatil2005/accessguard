# GitHub Repository Configuration

## Repository Settings

### Branch Protection
- **Protected Branch**: `master`
- **Require PR Reviews**: Yes (1 approval)
- **Require Status Checks**: Yes (All must pass)
- **Require Branch to be Up to Date**: Yes
- **Auto-merge**: Disabled
- **Delete Head Branch**: Enabled after PR merge

### Issues
- **Issue Templates**: Enabled (Bug, Feature, PR)
- **Issues Enabled**: Yes
- **Discussions Enabled**: No

### Pull Requests
- **Auto-merge**: Disabled
- **Require Code Review**: Yes
- **Dismiss Stale Reviews**: No
- **Require Status Check**: Yes

### Security
- **Dependency Alerts**: Enabled
- **Dependabot**: Enabled
- **Code Scanning**: Disabled (Can be enabled)
- **Secret Scanning**: Enabled

### Features
- **Projects**: Enabled (for issue tracking)
- **Wiki**: Enabled (for documentation)
- **Discussions**: Can be enabled
- **Sponsorships**: Can be enabled

### Webhooks
- None configured (Configure as needed)

## Labels

Auto-create labels for organization:

### Priority
- `critical` - Red (#ee0701) - Needs immediate attention
- `high` - Orange (#ff7619) - Important, next sprint
- `medium` - Yellow (#fbca04) - Normal priority
- `low` - Green (#0075ca) - Can wait

### Type
- `bug` - Red (#d73a4a) - Something isn't working
- `feature` - Blue (#0075ca) - New feature
- `enhancement` - Blue (#a2eeef) - Improvement
- `documentation` - Cyan (#0369a1) - Documentation needed
- `security` - Red (#b60205) - Security issue

### Status
- `needs-triage` - Gray (#cccccc) - Needs review
- `in-progress` - Blue (#0075ca) - Currently working
- `blocked` - Red (#d73a4a) - Blocked by something
- `wontfix` - Gray (#cccccc) - Will not be implemented
- `duplicate` - Gray (#cccccc) - Duplicate issue

### Community
- `good first issue` - Green (#90ee90) - Good for newcomers
- `help wanted` - Green (#128a0c) - Community help needed
- `question` - Purple (#cc317c) - Question about code
