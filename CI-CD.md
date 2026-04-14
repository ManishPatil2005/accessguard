# CI-CD.md - Continuous Integration and Deployment

## GitHub Actions Workflow

### Basic Test & Build (.github/workflows/test.yml)

```yaml
name: Test Suite
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.11', '3.12', '3.13']
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov pylint
    
    - name: Lint with pylint
      run: pylint --fail-under=8.0 main.py
    
    - name: Run tests
      run: pytest --cov=. --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### Security Scanning (.github/workflows/security.yml)

```yaml
name: Security Scan
on: [push, pull_request]

jobs:
  bandit:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
    - run: pip install bandit
    - run: bandit -r . -f json -o bandit-report.json || true
    
  dependency-check:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
    - run: pip install safety
    - run: safety check --json || true
```

### Build & Push Docker (.github/workflows/docker.yml)

```yaml
name: Docker Build & Push
on:
  push:
    tags: ['v*']

jobs:
  docker:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to Docker Hub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}
    
    - name: Build and push
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: |
          ${{ secrets.DOCKER_USERNAME }}/accessguard:${{ github.ref_name }}
          ${{ secrets.DOCKER_USERNAME }}/accessguard:latest
```

---

## GitLab CI/CD

### .gitlab-ci.yml

```yaml
stages:
  - test
  - build
  - deploy

variables:
  DOCKER_IMAGE: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  DOCKER_DRIVER: overlay2

test:
  stage: test
  image: python:3.13
  script:
    - pip install -r requirements.txt pytest pylint
    - pytest --cov=.
    - pylint main.py
  coverage: '/TOTAL.*\s+(\d+%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml

security:
  stage: test
  image: python:3.13
  script:
    - pip install bandit safety
    - bandit -r . || true
    - safety check || true

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t $DOCKER_IMAGE .
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker push $DOCKER_IMAGE

deploy:
  stage: deploy
  image: bitnami/kubectl:latest
  script:
    - kubectl set image deployment/accessguard accessguard=$DOCKER_IMAGE --record
  only:
    - main
```

---

## Jenkins Pipeline

### Jenkinsfile

```groovy
pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/youruser/accessguard.git'
            }
        }
        
        stage('Install Dependencies') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }
        
        stage('Test') {
            steps {
                sh 'pytest --junitxml=results.xml'
            }
        }
        
        stage('Lint') {
            steps {
                sh 'pylint --fail-under=8.0 main.py || true'
            }
        }
        
        stage('Security Scan') {
            steps {
                sh 'bandit -r . || true'
                sh 'safety check || true'
            }
        }
        
        stage('Build Docker Image') {
            steps {
                sh 'docker build -t accessguard:$BUILD_NUMBER .'
            }
        }
        
        stage('Deploy to Dev') {
            when {
                branch 'develop'
            }
            steps {
                sh 'docker run -d -p 8001:8000 accessguard:$BUILD_NUMBER'
            }
        }
        
        stage('Deploy to Prod') {
            when {
                branch 'main'
            }
            steps {
                sh 'kubectl set image deployment/accessguard accessguard=accessguard:$BUILD_NUMBER'
            }
        }
    }
    
    post {
        always {
            junit 'results.xml'
        }
    }
}
```

---

## Deployment Triggers

### Staging Environment
- Triggered by: Merge to `develop` branch
- Tests: Run all unit tests
- Build: Create Docker image
- Deploy: Push to staging K8s cluster
- URL: https://staging.accessguard.io

### Production Environment
- Triggered by: Git tag `v*` or merge to `main`
- Tests: Run all tests + integration tests
- Security: Bandit + Safety
- Build: Create Docker image, push to registry
- Deploy: Blue-green deployment to prod K8s
- Approval: Manual approval required
- URL: https://accessguard.io

---

## Release Process

### Step 1: Prepare Release
```bash
git checkout main
git pull origin main
```

### Step 2: Bump Version
```bash
# Update version in main.py
# Update version in pyproject.toml
# Update CHANGELOG.md
git add .
git commit -m "chore: bump version to 1.1.0"
```

### Step 3: Create Tag
```bash
git tag -a v1.1.0 -m "Release version 1.1.0"
git push origin v1.1.0
```

### Step 4: Watch CI/CD
- GitHub Actions automatically:
  - Runs all tests
  - Creates Docker image
  - Pushes to registry
  - Creates GitHub release
  - Deploys to production

### Step 5: Verify Production
```bash
curl https://accessguard.io/health
# Should return {"status": "healthy"}
```

---

## Monitoring After Deployment

### Key Metrics
```
- Error rate: Should stay < 0.1%
- Response time: p95 < 500ms
- Uptime: Target 99.9%
- Failed logins/sec: Monitor for attacks
- Database connections: < 100
```

### Automated Rollback
If error rate spikes above 5% in 5 minutes:
- Automatic rollback to previous version
- Alert sent to ops team
- Incident created

---

**Version**: 1.0.0 | **Last Updated**: April 14, 2026
