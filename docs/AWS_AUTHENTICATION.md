# AWS Authentication in GitHub Actions

## 🤔 Why GitHub Secrets Instead of `~/.aws/credentials`?

### The Problem

When you run `aws configure` on your **local machine**, it creates credentials in:
```
~/.aws/credentials
```

These credentials work great for:
- ✅ Local development
- ✅ Running Terraform locally
- ✅ Manual AWS CLI commands
- ✅ Docker containers that mount `~/.aws` (like your local dev setup)

### Why GitHub Actions Can't Use `~/.aws/credentials`

**GitHub Actions runs in GitHub's cloud infrastructure**, not on your machine:

```
Your Local Machine          GitHub's Cloud
├── ~/.aws/credentials  ❌  Not accessible
├── Your code          ✅  Cloned from repo
└── Your environment    ❌  Different environment
```

**GitHub Actions:**
- Runs on GitHub's servers (Ubuntu runners)
- Doesn't have access to your local files
- Needs credentials provided via GitHub Secrets
- Each workflow run is a fresh, isolated environment

## 🔐 Authentication Options

### Option 1: GitHub Secrets (Current Setup) ⚠️

**How it works:**
1. You store AWS credentials in GitHub Secrets
2. GitHub Actions reads secrets and configures AWS CLI
3. Actions can then authenticate with AWS

**Pros:**
- ✅ Simple to set up
- ✅ Works immediately
- ✅ No additional AWS configuration needed

**Cons:**
- ⚠️ Long-lived credentials (access keys)
- ⚠️ Credentials stored in GitHub (encrypted, but still stored)
- ⚠️ Need to rotate manually
- ⚠️ If leaked, need to revoke and recreate

**Setup:**
```yaml
# .github/workflows/ci.yml
- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
    aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    aws-region: us-east-1
```

### Option 2: OIDC (OpenID Connect) ✅ **Recommended**

**How it works:**
1. GitHub and AWS are connected via OIDC
2. GitHub Actions requests a temporary token from AWS
3. AWS verifies the request came from GitHub
4. AWS issues temporary credentials (no long-lived keys!)

**Pros:**
- ✅ **No long-lived credentials** (most secure)
- ✅ **Automatic credential rotation** (temporary tokens)
- ✅ **Fine-grained permissions** (IAM roles)
- ✅ **Audit trail** (can see which workflow assumed which role)
- ✅ **No secrets to manage** (except IAM role ARN)

**Cons:**
- ⚠️ Requires initial AWS setup (OIDC provider + IAM role)
- ⚠️ Slightly more complex configuration

**Setup:**
```yaml
# .github/workflows/ci.yml
- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::123456789012:role/github-actions-role
    aws-region: us-east-1
```

**GitHub Secret needed:**
- `AWS_ROLE_ARN` (instead of access keys)

## 🔄 Current vs Recommended Setup

### Current (GitHub Secrets with Access Keys)

```yaml
# Requires these GitHub Secrets:
# - AWS_ACCESS_KEY_ID
# - AWS_SECRET_ACCESS_KEY
- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
    aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

### Recommended (OIDC with IAM Role)

```yaml
# Requires this GitHub Secret:
# - AWS_ROLE_ARN
- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
    aws-region: us-east-1
```

## 📋 Migration to OIDC (Optional)

If you want to use OIDC instead of access keys:

### Step 1: Create OIDC Provider in AWS

```bash
# Create OIDC identity provider for GitHub
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
```

### Step 2: Create IAM Role for GitHub Actions

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:YOUR_USERNAME/mytraderpal:*"
        }
      }
    }
  ]
}
```

### Step 3: Attach Permissions to Role

The role needs permissions for:
- ECR (push/pull images)
- Lambda (create/update functions)
- API Gateway (create/update APIs)
- DynamoDB (create tables)
- Cognito (create user pools)
- IAM (create roles/policies)
- CloudWatch Logs

### Step 4: Update GitHub Actions Workflow

```yaml
- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
    aws-region: us-east-1
```

### Step 5: Add GitHub Secret

- Secret name: `AWS_ROLE_ARN`
- Value: `arn:aws:iam::123456789012:role/github-actions-role`

## 🎯 Recommendation

### For Now (Quick Start)

**Use GitHub Secrets with access keys:**
- ✅ Faster to set up
- ✅ Works immediately
- ✅ Good enough for development/testing
- ⚠️ Remember to rotate keys periodically

### For Production (Best Practice)

**Migrate to OIDC:**
- ✅ More secure (no long-lived credentials)
- ✅ Better audit trail
- ✅ Industry best practice
- ⚠️ Requires initial setup

## 📝 Summary

**Why GitHub Secrets?**
- GitHub Actions runs in GitHub's cloud, not your machine
- Can't access your local `~/.aws/credentials`
- Needs credentials provided via GitHub Secrets

**Current Setup:**
- Uses access keys stored in GitHub Secrets
- Simple but requires manual key rotation

**Better Option:**
- Use OIDC with IAM roles
- No long-lived credentials
- More secure and follows AWS best practices

**For Local Development:**
- `aws configure` and `~/.aws/credentials` work perfectly
- Docker can mount `~/.aws` directory
- No changes needed for local dev

---

**Bottom Line:** GitHub Actions needs credentials because it runs in GitHub's cloud, not on your machine. You can use access keys (simpler) or OIDC (more secure).

