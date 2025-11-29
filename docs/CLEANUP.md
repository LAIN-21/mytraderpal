# Cleanup Guide - Folders to Delete

## ✅ Safe to Delete (Old Structure)

### 1. **`cdk/`** - Old CDK Location
- **Reason**: Moved to `infra/cdk/`
- **Action**: `rm -rf cdk/`
- **Note**: CDK code is now in `infra/cdk/`

### 2. **`frontend/`** - Old Frontend Location
- **Reason**: Moved to `src/frontend/`
- **Action**: `rm -rf frontend/`
- **Note**: Frontend code is now in `src/frontend/`

### 3. **`services/`** - Old Backend Location
- **Reason**: Moved to `src/app/`
- **Action**: `rm -rf services/`
- **Note**: Backend code is now in `src/app/`

## 🗑️ Optional Cleanup (Temporary/Redundant Files)

### 4. **`htmlcov/`** - Coverage Reports
- **Reason**: Generated files, can be regenerated
- **Action**: `rm -rf htmlcov/`
- **Note**: Will be regenerated when running tests with `--cov-report=html`

### 5. **Temporary Documentation Files**
- **`REORGANIZATION.md`** - Temporary migration doc
- **`REORGANIZATION_COMPLETE.md`** - Temporary completion doc
- **`MIGRATION_GUIDE.md`** - Can keep if useful, or move to docs/
- **Action**: `rm REORGANIZATION.md REORGANIZATION_COMPLETE.md`

### 6. **Redundant Documentation** (Optional)
- **`DEPLOYMENT.md`** - Info now in README.md and docs/
- **`TESTING.md`** - Info now in README.md
- **Action**: Review and optionally delete or move to `docs/`

## 📋 Quick Cleanup Script

```bash
# Delete old structure directories
rm -rf cdk/
rm -rf frontend/
rm -rf services/

# Delete generated coverage reports (will regenerate)
rm -rf htmlcov/

# Delete temporary reorganization docs
rm -f REORGANIZATION.md REORGANIZATION_COMPLETE.md

# Optional: Delete redundant docs (review first!)
# rm -f DEPLOYMENT.md TESTING.md
```

## ✅ Keep These Directories

- `src/` - New application structure
- `infra/` - Infrastructure (CDK, Docker)
- `docs/` - Documentation
- `tests/` - Test suite
- `scripts/` - Utility scripts
- `monitoring/` - Monitoring configs
- `.github/` - CI/CD workflows
- `node_modules/` - Dependencies (gitignored)
- `__pycache__/` - Python cache (gitignored)
- `.pytest_cache/` - Pytest cache (gitignored)

## ⚠️ Before Deleting

1. **Verify new structure works:**
   ```bash
   # Test imports
   python tests/unit/test_imports.py
   
   # Run tests
   ./scripts/test.sh
   ```

2. **Check CI/CD still works:**
   - Verify `.github/workflows/ci.yml` uses new paths
   - All paths should point to `src/`, `infra/`, etc.

3. **Backup if unsure:**
   ```bash
   # Create backup
   tar -czf backup-old-structure.tar.gz cdk/ frontend/ services/
   ```

## 📊 Size Savings

After cleanup, you'll free up space from:
- Duplicate code in old locations
- Old node_modules in `cdk/` and `frontend/`
- Old build artifacts in `cdk/cdk.out/`
- Generated coverage reports

## 🎯 Recommended Cleanup Order

1. **First**: Delete `cdk/`, `frontend/`, `services/` (after verifying new structure works)
2. **Second**: Delete `htmlcov/` (will regenerate)
3. **Third**: Clean up temporary docs
4. **Last**: Review and optionally remove redundant docs

