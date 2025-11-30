# Backend AWS Credentials Setup

The backend needs AWS credentials to connect to DynamoDB for local development.

## The Problem

The backend uses `boto3` to connect to DynamoDB:
```python
self.dynamodb = boto3.resource('dynamodb')
```

Boto3 needs AWS credentials to authenticate. For local development, you have two options:

## Solution 1: Use AWS Credentials File (Recommended)

### Setup

1. **Configure AWS CLI** (if not already done):
   ```bash
   aws configure
   ```
   This creates `~/.aws/credentials` and `~/.aws/config`

2. **Docker Compose automatically mounts** your AWS credentials:
   ```yaml
   volumes:
     - ${HOME}/.aws:/root/.aws:ro
   ```

3. **That's it!** The backend will use your AWS credentials automatically.

### Verify

```bash
# Check AWS credentials are configured
aws sts get-caller-identity

# Should show your AWS account info
```

## Solution 2: Use Environment Variables

If you prefer not to mount the credentials file, you can pass credentials as environment variables:

### Option A: Set in shell before starting

```bash
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
export AWS_REGION=us-east-1

make start
```

### Option B: Add to `src/app/.env`

```env
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
```

**Note:** Never commit `.env` files with real credentials to git!

## Solution 3: Use AWS Profile

If you have multiple AWS profiles:

```bash
# Set profile in environment
export AWS_PROFILE=your-profile-name
make start
```

## Verification

After starting the backend, test it:

```bash
# Test health endpoint
curl http://localhost:9000/v1/health

# Should return JSON with status: "healthy"
```

If you see errors about credentials, check:

1. **AWS credentials are configured:**
   ```bash
   aws sts get-caller-identity
   ```

2. **Credentials file exists:**
   ```bash
   ls -la ~/.aws/credentials
   ```

3. **Docker can access credentials:**
   ```bash
   docker-compose exec api ls -la /root/.aws/
   ```

## Troubleshooting

### Error: "Unable to locate credentials"

**Cause:** Boto3 can't find AWS credentials

**Fix:**
1. Run `aws configure` to set up credentials
2. Or set `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables
3. Restart containers: `make restart`

### Error: "Access Denied" or "Unauthorized"

**Cause:** Credentials don't have DynamoDB permissions

**Fix:**
1. Ensure your AWS user/role has DynamoDB permissions
2. Check IAM policies allow:
   - `dynamodb:GetItem`
   - `dynamodb:PutItem`
   - `dynamodb:UpdateItem`
   - `dynamodb:DeleteItem`
   - `dynamodb:Query`
   - `dynamodb:Scan`

### Error: "Table not found"

**Cause:** DynamoDB table doesn't exist in your AWS account

**Fix:**
1. Deploy infrastructure with Terraform:
   ```bash
   make deploy
   ```
2. Or create table manually in AWS Console
3. Update `TABLE_NAME` in `src/app/.env` to match

## For Production

In production (AWS Lambda), credentials are handled automatically:
- Lambda execution role provides credentials
- No manual configuration needed
- Terraform sets up IAM roles with proper permissions

## Security Notes

⚠️ **Never commit credentials to git!**

- ✅ `.env` files are in `.gitignore`
- ✅ `~/.aws/` is in `.gitignore`
- ❌ Don't add credentials to `docker-compose.yml`
- ❌ Don't hardcode credentials in code

## Quick Setup Checklist

- [ ] Run `aws configure` (or have AWS credentials set up)
- [ ] Verify: `aws sts get-caller-identity` works
- [ ] Run `make install` (creates `.env` files)
- [ ] Run `make start` (starts containers with credentials)
- [ ] Test: `curl http://localhost:9000/v1/health`

