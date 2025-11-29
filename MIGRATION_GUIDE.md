# Migration Guide: Updating Test Imports

## Overview

Tests need to be updated to use the new import paths after reorganization.

## Old Imports → New Imports

### Backend Code

| Old Import | New Import |
|------------|------------|
| `from handlers.X import Y` | `from app.api.X import Y` |
| `from utils.X import Y` | `from app.core.X import Y` |
| `from common.dynamodb import db` | `from app.repositories.dynamodb import db` |
| `from common.auth_lambda import X` | `from app.core.auth import X` |
| `from monitoring.X import Y` | `from app.core.X import Y` |
| `from main import handler` | `from app.main import handler` |

### Test Files

Update test files to:
1. Add `src/` to Python path: `sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))`
2. Use new import paths: `from app.X import Y`

## Example Test Update

**Before:**
```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../services/api'))
from main import handler
from common.dynamodb import db
```

**After:**
```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))
from app.main import handler
from app.repositories.dynamodb import db
```

## Quick Fix Script

Run this to update common patterns in test files:

```bash
# Update Python path in tests
find tests/ -name "*.py" -exec sed -i '' 's|../../services/api|../../src|g' {} \;

# Update imports (manual review recommended)
find tests/ -name "*.py" -exec sed -i '' 's|from common\.|from app.repositories.|g' {} \;
find tests/ -name "*.py" -exec sed -i '' 's|from common\.|from app.core.|g' {} \;
find tests/ -name "*.py" -exec sed -i '' 's|from handlers\.|from app.api.|g' {} \;
find tests/ -name "*.py" -exec sed -i '' 's|from utils\.|from app.core.|g' {} \;
find tests/ -name "*.py" -exec sed -i '' 's|from monitoring\.|from app.core.|g' {} \;
```

## Verification

Run the import test:
```bash
python tests/unit/test_imports.py
```

This will verify all imports work correctly.

