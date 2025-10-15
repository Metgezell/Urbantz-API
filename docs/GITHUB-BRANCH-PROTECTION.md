# GitHub Branch Protection Setup

This document outlines the GitHub branch protection settings that should be configured for the AI integration repository.

## Required Settings

### 1. Navigate to Repository Settings
1. Go to your GitHub repository
2. Click on **Settings** tab
3. Click on **Branches** in the left sidebar

### 2. Add Branch Protection Rule
1. Click **Add rule**
2. In **Branch name pattern**, enter: `main` (or `master` if that's your default branch)

### 3. Configure Protection Settings

#### ✅ Require a pull request before merging
- **Required number of reviewers**: 1
- **Dismiss stale PR approvals when new commits are pushed**: ✅
- **Require review from code owners**: ✅ (This will use CODEOWNERS file)

#### ✅ Require status checks to pass before merging
- **Require branches to be up to date before merging**: ✅
- **Status checks that are required**:
  - `test` (from CI workflow)
  - `security` (from CI workflow)
  - `ai-core-protection` (from CI workflow)

#### ✅ Require conversation resolution before merging
- ✅ **Require conversation resolution before merging**

#### ✅ Require linear history
- ✅ **Require linear history**

#### ✅ Restrict pushes that create files
- ✅ **Restrict pushes that create files**

### 4. Additional Security Settings

#### ✅ Require signed commits (Optional but Recommended)
- ✅ **Require signed commits**

#### ✅ Lock branch (Optional)
- ✅ **Lock branch** (prevents force pushes)

#### ✅ Include administrators
- ✅ **Include administrators** (applies rules to admins too)

## CODEOWNERS Integration

The `CODEOWNERS` file in the repository root will automatically:
- Require approval from `@koen-domus` for AI core files
- Require approval for security-related files
- Allow other team members to modify non-critical files

## Expected Behavior

With these settings:

1. **Direct pushes to main branch are blocked**
2. **All changes must go through pull requests**
3. **AI core changes require explicit approval from code owners**
4. **CI tests must pass before merging**
5. **Security checks run on every PR**
6. **AI core modifications are flagged and require justification**

## Override Mechanism

For legitimate AI core changes:
1. Add `[ALLOW_AI_CORE_CHANGE]` to your commit message
2. Ensure all tests pass
3. Get approval from code owners
4. Update test fixtures if extraction logic changes

## Testing the Protection

To test that protection is working:

1. Try to push directly to main branch (should be blocked)
2. Create a PR modifying AI core files (should require approval)
3. Create a PR with failing tests (should be blocked)
4. Create a PR with `[ALLOW_AI_CORE_CHANGE]` (should work with approval)

## Troubleshooting

### "Status checks are pending"
- Wait for CI to complete
- Check Actions tab for workflow status
- Ensure all required status checks are enabled

### "Review required"
- Request review from code owners
- Ensure CODEOWNERS file is properly configured
- Check that reviewers have write access to repository

### "Conversation resolution required"
- Address all review comments
- Mark conversations as resolved
- Ensure no open discussions remain
