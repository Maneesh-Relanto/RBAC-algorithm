# Branch Protection Configuration

## Overview
This document outlines the recommended branch protection settings for the RBAC Algorithm repository to ensure code quality, security, and proper review processes.

## Repository Information
- **Repository**: `Maneesh-Relanto/RBAC-algorithm`
- **Type**: Public
- **Protected Branches**: `main`, `gh-pages`

## Branch Protection Rules

### 🔐 Main Branch (`main`)

#### Required Settings

**1. Require Pull Request Reviews Before Merging**
- ✅ **Enable**: Require a pull request before merging
- **Required approving reviews**: 1 (minimum recommended)
- ✅ **Dismiss stale pull request approvals when new commits are pushed**
- ✅ **Require review from Code Owners** (if CODEOWNERS file exists)
- ⚠️ **Do not allow bypassing the above settings** (recommended for production)

**2. Require Status Checks to Pass Before Merging**
- ✅ **Enable**: Require status checks to pass before merging
- ✅ **Require branches to be up to date before merging**

**Required Status Checks** (based on CI workflows):
- `test (3.8)` - Tests on Python 3.8
- `test (3.9)` - Tests on Python 3.9
- `test (3.10)` - Tests on Python 3.10
- `test (3.11)` - Tests on Python 3.11
- `security` - Security scanning
- `build` - Package build verification

**3. Require Conversation Resolution Before Merging**
- ✅ **Enable**: All conversations on code must be resolved before merging

**4. Require Signed Commits**
- 🔶 **Optional but recommended**: Require signed commits for authenticity

**5. Require Linear History**
- 🔶 **Optional**: Require linear history (no merge commits)
- Alternative: Allow squash merging for cleaner history

**6. Include Administrators**
- ✅ **Enable**: Include administrators in these restrictions (recommended)
- Ensures even repository admins follow the same rules

**7. Restrict Who Can Push to Matching Branches**
- 🔶 **Optional**: Restrict pushes to specific people/teams/apps
- Recommended for high-security projects

**8. Allow Force Pushes**
- ❌ **Disable**: Do not allow force pushes (highly recommended)

**9. Allow Deletions**
- ❌ **Disable**: Do not allow deletions (highly recommended)

### 📄 GH-Pages Branch (`gh-pages`)

#### Recommended Settings (Less Restrictive)

Since `gh-pages` is typically used for automated documentation deployments:

**1. Require Pull Request Reviews**
- 🔶 **Optional**: May allow direct pushes for automated deployments

**2. Require Status Checks**
- ✅ **Enable**: Basic checks for deployment validation
- Required checks:
  - Documentation build validation (if applicable)

**3. Allow Force Pushes**
- ⚠️ **Consider allowing**: May be needed for documentation rebuilds
- Restrict to specific users/teams only

**4. Allow Deletions**
- ❌ **Disable**: Do not allow deletions

## Implementation Steps

### Step 1: Access Branch Protection Settings
```
1. Go to: https://github.com/Maneesh-Relanto/RBAC-algorithm
2. Navigate to: Settings → Branches
3. Click "Add branch protection rule" or edit existing rules
```

### Step 2: Configure Main Branch Protection

**Pattern**: `main`

```yaml
Branch name pattern: main

Protection rules:
  ☑ Require a pull request before merging
    • Required approvals: 1
    ☑ Dismiss stale pull request approvals when new commits are pushed
    ☑ Require review from Code Owners
  
  ☑ Require status checks to pass before merging
    ☑ Require branches to be up to date before merging
    Status checks that are required:
      • test (3.8)
      • test (3.9)
      • test (3.10)
      • test (3.11)
      • security
      • build
  
  ☑ Require conversation resolution before merging
  ☑ Require signed commits (optional)
  ☑ Require linear history (optional)
  ☑ Include administrators
  
  ☐ Allow force pushes (keep disabled)
  ☐ Allow deletions (keep disabled)
```

### Step 3: Configure GH-Pages Branch Protection

**Pattern**: `gh-pages`

```yaml
Branch name pattern: gh-pages

Protection rules:
  ☐ Require a pull request before merging (optional for automated deployments)
  
  ☑ Require status checks to pass before merging (if applicable)
  
  ☐ Allow force pushes
    • Specify who can force push: github-actions[bot] (if needed)
  
  ☐ Allow deletions (keep disabled)
```

## Additional Security Measures

### 1. Enable GitHub Security Features

#### Dependabot
```
Settings → Code security and analysis
☑ Dependabot alerts
☑ Dependabot security updates
☑ Dependabot version updates
```

#### Code Scanning
```
Settings → Code security and analysis
☑ CodeQL analysis (enabled via security.yml workflow)
```

#### Secret Scanning
```
Settings → Code security and analysis
☑ Secret scanning
☑ Push protection
```

### 2. Create CODEOWNERS File

Create `.github/CODEOWNERS`:
```
# RBAC Algorithm Code Owners

# Default owner for everything
* @Maneesh-Relanto

# Core RBAC implementation
/src/rbac/ @Maneesh-Relanto

# Tests require review
/tests/ @Maneesh-Relanto

# Documentation
/docs/ @Maneesh-Relanto
*.md @Maneesh-Relanto

# Security-sensitive files
/schemas/ @Maneesh-Relanto
/scripts/ @Maneesh-Relanto
```

### 3. Repository Settings Checklist

```
Settings → General
☑ Disable: Allow merge commits (optional - depends on preference)
☑ Enable: Allow squash merging
☑ Enable: Allow rebase merging
☑ Enable: Always suggest updating pull request branches
☑ Enable: Automatically delete head branches

Settings → Moderation options
☑ Enable: Limit interactions to prior contributors (optional)

Settings → Code security and analysis
☑ Enable: Private vulnerability reporting
```

## Testing Branch Protection

After setting up branch protection, test it by:

1. **Create a test branch**:
   ```bash
   git checkout -b test-branch-protection
   echo "test" > test.txt
   git add test.txt
   git commit -m "Test branch protection"
   git push origin test-branch-protection
   ```

2. **Create a pull request** to `main`

3. **Verify**:
   - Cannot merge without approval
   - Cannot merge with failing status checks
   - Direct pushes to `main` are blocked

## Monitoring and Maintenance

### Weekly Tasks
- Review failed CI runs
- Check security alerts from Dependabot
- Review CodeQL findings

### Monthly Tasks
- Review branch protection effectiveness
- Update required status checks if workflows change
- Review and update CODEOWNERS as team grows

## Rollout Plan

### Phase 1: Enable Basic Protection (Immediate)
- [x] Create CI workflow
- [x] Create security workflow
- [ ] Enable basic branch protection on `main`
- [ ] Test with a sample PR

### Phase 2: Enable Full Protection (Week 1)
- [ ] Add all required status checks
- [ ] Enable conversation resolution requirement
- [ ] Create CODEOWNERS file

### Phase 3: Harden Security (Week 2)
- [ ] Enable signed commits requirement
- [ ] Configure gh-pages protection
- [ ] Enable all GitHub security features

## Resources

- [GitHub Branch Protection Rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [GitHub Actions Status Checks](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/about-status-checks)
- [GitHub Security Features](https://docs.github.com/en/code-security)

## Notes

- These settings balance security with development velocity
- Adjust based on team size and project maturity
- For solo projects, some restrictions can be relaxed
- Always test changes in a non-production repository first
