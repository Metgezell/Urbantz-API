# AI Integration Security & Backup Guide

This document explains the security measures implemented to protect your working AI integration from accidental modifications.

## 🛡️ Protection Overview

Your AI integration is now protected by multiple layers of security:

1. **Pre-commit Hooks** - Block changes to AI core files
2. **CODEOWNERS** - Require approval for AI core modifications  
3. **CI/CD Tests** - Validate functionality before merging
4. **Branch Protection** - Prevent direct pushes to main branch
5. **Version Tags** - Immutable snapshots of working states

## 🔒 Protected Files

The following files are protected from accidental modifications:

```
/api/smart-analyze.js          # Claude AI integration
/api/analyze-document.js       # Google Vision + AI extraction
/scripts/local-server.js       # AI extraction functions
/ai-core/                      # Future AI core directory
```

## 🚫 What Happens When You Try to Modify AI Core

### Local Development
```bash
# This will be BLOCKED by pre-commit hook:
git add api/smart-analyze.js
git commit -m "fix: improve AI prompt"

# Output:
# ⛔ BLOCKED: Changes to AI core files detected!
# To override this protection, add [ALLOW_AI_CORE_CHANGE] to your commit message
```

### GitHub Pull Requests
- AI core changes require approval from `@koen-domus`
- CI tests must pass
- Security checks run automatically
- Changes are flagged for review

## ✅ How to Make Legitimate AI Core Changes

### Method 1: Override Flag (Recommended)
```bash
git commit -m "feat(ai): improve table parsing [ALLOW_AI_CORE_CHANGE]"
```

### Method 2: Pull Request with Approval
1. Create a feature branch
2. Make your changes
3. Create a pull request
4. Get approval from code owners
5. Ensure CI tests pass

## 🧪 Testing Your Changes

### Run Tests Locally
```bash
npm test                    # Run all tests
npm run lint               # Run linting
npm run test:coverage      # Run with coverage
```

### Test AI Extraction
```bash
# Test with sample documents
node tests/ai-extraction.test.js
```

## 📋 CI/CD Pipeline

Every pull request automatically runs:

1. **Install Dependencies** - `npm ci`
2. **Linting** - Code quality checks
3. **Tests** - Unit and integration tests
4. **Security Audit** - `npm audit`
5. **AI Core Protection** - Flag AI core changes
6. **Secrets Scan** - Check for exposed credentials

## 🏷️ Version Management

### Current Stable Version
```bash
git tag -l                    # List all tags
git show ai-core@1.0.0       # View current stable version
```

### Creating New Releases
```bash
# Tag a new version
git tag -a ai-core@1.1.0 -m "AI Core v1.1.0 - Improved table parsing"

# Push tags
git push --tags
```

## 🔧 Configuration Files

### Environment Variables
```bash
# Copy and configure
cp .env.required .env

# Required variables:
ANTHROPIC_API_KEY=your_key_here
URBANTZ_API_KEY=your_key_here
```

### Husky Pre-commit Hook
Location: `.husky/pre-commit`
- Blocks AI core changes
- Runs linting and tests
- Allows override with `[ALLOW_AI_CORE_CHANGE]`

### CODEOWNERS
Location: `CODEOWNERS`
- Defines who can approve AI core changes
- Requires `@koen-domus` approval for protected files

## 🚨 Emergency Procedures

### If AI Integration Breaks
1. **Revert to last working tag:**
   ```bash
   git checkout ai-core@1.0.0
   ```

2. **Create hotfix branch:**
   ```bash
   git checkout -b hotfix/ai-core-fix
   # Make minimal fix
   git commit -m "fix(ai): restore functionality [ALLOW_AI_CORE_CHANGE]"
   ```

3. **Test thoroughly before merging**

### If Pre-commit Hook Breaks
```bash
# Temporarily bypass (use with caution)
git commit --no-verify -m "fix: emergency fix [ALLOW_AI_CORE_CHANGE]"
```

## 📊 Monitoring & Alerts

### GitHub Actions
- Check `.github/workflows/ci.yml` for workflow status
- Monitor Actions tab for failed runs
- Review security scan results

### Test Coverage
- Minimum 70% coverage required
- AI extraction tests must pass
- Golden file tests validate output

## 🔄 Backup Strategy

### Code Backup
- **Primary**: GitHub repository with branch protection
- **Secondary**: Tagged releases (immutable)
- **Local**: Working directory with Git history

### Data Backup
- **AI Prompts**: Version controlled in code
- **Test Fixtures**: Stored in `test-fixtures/`
- **Configuration**: Documented in `docs/`

## 🆘 Troubleshooting

### "Pre-commit hook failed"
```bash
# Check hook status
ls -la .husky/pre-commit

# Reinstall if needed
npx husky install
```

### "Tests failing"
```bash
# Run tests individually
npm test -- --testNamePattern="AI Extraction"

# Check test fixtures
ls test-fixtures/expected/
```

### "Permission denied"
```bash
# Check CODEOWNERS file
cat CODEOWNERS

# Ensure you have write access to repository
```

## 📞 Support

For issues with the AI integration security system:

1. Check this documentation first
2. Review GitHub Actions logs
3. Test with `[ALLOW_AI_CORE_CHANGE]` override
4. Create issue with security label

## 🎯 Success Criteria

Your AI integration is properly secured when:

- ✅ Pre-commit hooks block accidental AI core changes
- ✅ CI tests pass on every pull request
- ✅ AI core changes require explicit approval
- ✅ Working state is tagged and backed up
- ✅ Cursor/AI tools cannot silently break functionality

---

**Remember**: The goal is to protect your working AI integration while still allowing legitimate improvements. Use the override mechanism responsibly!

