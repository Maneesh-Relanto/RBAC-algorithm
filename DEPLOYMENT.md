# Deployment Guide

This guide covers deploying both the Python library and the documentation site.

## Python Library Deployment

### Prerequisites

- PyPI account (https://pypi.org/account/register/)
- Twine installed (`pip install twine`)
- Build tools installed (`pip install build`)

### Step 1: Prepare for Release

1. **Update version** in `src/rbac/__init__.py`:
   ```python
   __version__ = "0.2.0"
   ```

2. **Update CHANGELOG.md** with release notes

3. **Run tests**:
   ```bash
   pytest
   black --check src/
   flake8 src/
   mypy src/
   ```

### Step 2: Build Distribution

```bash
# Clean previous builds
rm -rf build/ dist/ *.egg-info

# Build source distribution and wheel
python -m build

# Verify the build
ls dist/
# Should show:
#   rbac-algorithm-0.2.0-py3-none-any.whl
#   rbac-algorithm-0.2.0.tar.gz
```

### Step 3: Test on TestPyPI

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ rbac-algorithm
```

### Step 4: Deploy to PyPI

```bash
# Upload to production PyPI
python -m twine upload dist/*

# Verify at https://pypi.org/project/rbac-algorithm/
```

### Step 5: Create GitHub Release

```bash
# Tag the release
git tag -a v0.2.0 -m "Release version 0.2.0"
git push origin v0.2.0

# Create release on GitHub with release notes
```

## Documentation Site Deployment

### Option 1: GitHub Pages (Recommended)

#### Prerequisites

- GitHub repository
- GitHub Pages enabled

#### Configuration

1. **Update `docusaurus.config.js`**:
   ```javascript
   module.exports = {
     url: 'https://yourusername.github.io',
     baseUrl: '/rbac-algorithm/',
     organizationName: 'yourusername',
     projectName: 'rbac-algorithm',
   };
   ```

2. **Configure GitHub Actions** (create `.github/workflows/deploy-docs.yml`):
   ```yaml
   name: Deploy Docs

   on:
     push:
       branches: [main]
       paths:
         - 'docs/**'

   jobs:
     deploy:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         
         - name: Setup Node.js
           uses: actions/setup-node@v3
           with:
             node-version: 18

         - name: Install dependencies
           working-directory: ./docs
           run: npm install

         - name: Build
           working-directory: ./docs
           run: npm run build

         - name: Deploy to GitHub Pages
           uses: peaceiris/actions-gh-pages@v3
           with:
             github_token: ${{ secrets.GITHUB_TOKEN }}
             publish_dir: ./docs/build
   ```

3. **Manual Deployment**:
   ```bash
   cd docs
   
   # Build
   npm run build
   
   # Deploy (requires git credentials)
   GIT_USER=<Your GitHub username> npm run deploy
   ```

### Option 2: Netlify

1. **Sign up** at https://netlify.com

2. **Connect GitHub repository**

3. **Configure build settings**:
   - Base directory: `docs`
   - Build command: `npm run build`
   - Publish directory: `docs/build`

4. **Environment variables** (if needed):
   - `NODE_VERSION`: 18

5. **Deploy**:
   - Automatic deployment on git push
   - Manual deploy via Netlify dashboard

### Option 3: Vercel

1. **Sign up** at https://vercel.com

2. **Import project** from GitHub

3. **Configure settings**:
   - Framework: Docusaurus
   - Root directory: `docs`
   - Build command: `npm run build`
   - Output directory: `build`

4. **Deploy**:
   - Automatic deployment on git push
   - Preview deployments for PRs

### Option 4: Custom Server

#### Prerequisites

- Web server (Nginx, Apache, etc.)
- Node.js installed on server
- SSH access

#### Deployment Steps

1. **Build locally**:
   ```bash
   cd docs
   npm run build
   ```

2. **Transfer files to server**:
   ```bash
   # Using rsync
   rsync -avz --delete docs/build/ user@server:/var/www/rbac-docs/

   # Using scp
   scp -r docs/build/* user@server:/var/www/rbac-docs/
   ```

3. **Configure Nginx**:
   ```nginx
   server {
       listen 80;
       server_name docs.rbac-algorithm.dev;

       root /var/www/rbac-docs;
       index index.html;

       location / {
           try_files $uri $uri/ /index.html;
       }

       # Enable gzip compression
       gzip on;
       gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

       # Cache static assets
       location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
           expires 1y;
           add_header Cache-Control "public, immutable";
       }
   }
   ```

4. **Restart Nginx**:
   ```bash
   sudo systemctl restart nginx
   ```

## Docker Deployment

### Dockerfile for Documentation Site

Create `docs/Dockerfile`:

```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build
RUN npm run build

# Production image
FROM nginx:alpine

# Copy built files
COPY --from=builder /app/build /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### Build and Run

```bash
# Build image
docker build -t rbac-docs ./docs

# Run container
docker run -d -p 80:80 rbac-docs

# Access at http://localhost
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  docs:
    build: ./docs
    ports:
      - "3000:80"
    restart: unless-stopped
```

Run with:
```bash
docker-compose up -d
```

## Continuous Deployment

### Automated Release Workflow

Create `.github/workflows/release.yml`:

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build-and-publish:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build twine
      
      - name: Build package
        run: python -m build
      
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
        run: twine upload dist/*
      
      - name: Create GitHub Release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          release_name: Release ${{ github.ref }}
          draft: false
          prerelease: false

  deploy-docs:
    runs-on: ubuntu-latest
    needs: build-and-publish
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: 18
      
      - name: Build docs
        working-directory: ./docs
        run: |
          npm install
          npm run build
      
      - name: Deploy
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs/build
```

## Post-Deployment Checklist

- [ ] PyPI package is accessible
- [ ] Documentation site loads correctly
- [ ] All internal links work
- [ ] Search functionality works (if using Algolia)
- [ ] SSL certificate is valid (for custom domains)
- [ ] Analytics are tracking (if configured)
- [ ] Social media cards display correctly
- [ ] Mobile responsiveness verified
- [ ] Performance metrics are acceptable
- [ ] Update announcement on Discord/Twitter
- [ ] Update version in repository README
- [ ] Create changelog entry

## Monitoring

### Documentation Site Monitoring

- **Uptime**: Use UptimeRobot or Pingdom
- **Analytics**: Google Analytics or Plausible
- **Performance**: Lighthouse CI
- **Errors**: Sentry or LogRocket

### Package Monitoring

- **Downloads**: Check PyPI stats
- **Issues**: Monitor GitHub issues
- **Security**: Dependabot alerts
- **Usage**: Anonymous telemetry (opt-in)

## Rollback Procedures

### Rolling Back PyPI Release

```bash
# You cannot delete releases from PyPI
# Instead, release a new patch version fixing the issue

# Mark version as yanked (prevents new installs)
# This must be done via PyPI web interface
```

### Rolling Back Documentation

```bash
# GitHub Pages
git revert <commit-hash>
git push origin main

# Netlify/Vercel
# Use dashboard to rollback to previous deployment
```

## Support

For deployment issues:
- Check GitHub Issues
- Ask on Discord
- Email: devops@rbac-algorithm.dev

---

**Last Updated**: January 2026
