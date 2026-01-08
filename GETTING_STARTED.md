# Getting Started with RBAC Algorithm

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

### Option 1: Install from PyPI (when published)

```bash
pip install rbac-algorithm
```

### Option 2: Install from source

```bash
# Clone the repository
git clone https://github.com/rbac-algorithm/rbac-python.git
cd rbac-python

# Install in development mode
pip install -e .
```

### Option 3: Copy to your project

```bash
# Copy the src/rbac directory to your project
cp -r src/rbac /path/to/your/project/
```

## Running the Examples

### 1. Set up Python path

```bash
cd "c:\Users\Maneesh Thakur\Downloads\My Projects\RBAC algorithm"
set PYTHONPATH=%CD%\src
```

### 2. Run basic example

```bash
python examples\basic_usage.py
```

**Expected output:**
```
======================================================================
RBAC Algorithm - Basic Example
======================================================================

1. Initializing RBAC with in-memory storage...
   ✓ RBAC initialized

2. Creating permissions...
   ✓ Created permission: perm_doc_read
   ✓ Created permission: perm_doc_write
   ✓ Created permission: perm_doc_delete
   ✓ Created permission: perm_user_read

3. Creating roles with hierarchy...
   ✓ Created role: Viewer (permissions: read)
   ✓ Created role: Editor (inherits from Viewer, adds write)
   ✓ Created role: Administrator (inherits from Editor, adds delete & user mgmt)

4. Creating users...
   ✓ Created user: Alice Johnson (alice@example.com)
   ✓ Created user: Bob Smith (bob@example.com)
   ✓ Created user: Carol Williams (carol@example.com)

5. Assigning roles to users...
   ✓ Assigned role 'Viewer' to Alice
   ✓ Assigned role 'Editor' to Bob
   ✓ Assigned role 'Administrator' to Carol

6. Checking permissions...
   ✓ ALLOWED: Alice trying to READ a document
   ✗ DENIED: Alice trying to WRITE a document
   ✗ DENIED: Alice trying to DELETE a document
   ✓ ALLOWED: Bob trying to READ a document
   ✓ ALLOWED: Bob trying to WRITE a document
   ✗ DENIED: Bob trying to DELETE a document
   ✓ ALLOWED: Carol trying to READ a document
   ✓ ALLOWED: Carol trying to WRITE a document
   ✓ ALLOWED: Carol trying to DELETE a document
   ✓ ALLOWED: Carol trying to VIEW a user

...
```

### 3. Run ABAC example

```bash
python examples\abac_example.py
```

## Quick Test in Python REPL

```python
# Start Python
python

# Import RBAC
from rbac import RBAC

# Create instance
rbac = RBAC(storage='memory')

# Create a permission
perm = rbac.create_permission(
    permission_id="perm_test",
    resource_type="test",
    action="read"
)
print(f"Created permission: {perm.id}")

# Create a role
role = rbac.create_role(
    role_id="role_test",
    name="Test Role",
    permissions=["perm_test"]
)
print(f"Created role: {role.name}")

# Create a user
user = rbac.create_user(
    user_id="user_test",
    email="test@example.com",
    name="Test User"
)
print(f"Created user: {user.name}")

# Assign role
assignment = rbac.assign_role("user_test", "role_test")
print(f"Assigned role to user")

# Check permission
allowed = rbac.can("user_test", "read", "test")
print(f"User can read test: {allowed}")
# Output: True

# Get detailed result
result = rbac.check("user_test", "read", "test")
print(f"Allowed: {result['allowed']}")
print(f"Reason: {result['reason']}")
```

## Integration Examples

### Flask Application

```python
from flask import Flask, request, jsonify
from rbac import RBAC, PermissionDenied

app = Flask(__name__)
rbac = RBAC(storage='memory')

# Setup RBAC (in production, load from database)
def setup_rbac():
    rbac.create_permission("perm_doc_read", "document", "read")
    rbac.create_permission("perm_doc_write", "document", "write")
    
    rbac.create_role("role_viewer", "Viewer", ["perm_doc_read"])
    rbac.create_role("role_editor", "Editor", ["perm_doc_read", "perm_doc_write"])

# Call once at startup
setup_rbac()

@app.route('/api/documents/<doc_id>', methods=['GET'])
def get_document(doc_id):
    user_id = request.headers.get('X-User-ID')
    
    if not user_id:
        return jsonify({"error": "User ID required"}), 401
    
    try:
        # Check permission
        rbac.require(user_id, 'read', 'document')
        
        # If allowed, return document
        return jsonify({
            "id": doc_id,
            "title": "My Document",
            "content": "Document content here..."
        })
    except PermissionDenied as e:
        return jsonify({"error": str(e)}), 403

@app.route('/api/documents/<doc_id>', methods=['PUT'])
def update_document(doc_id):
    user_id = request.headers.get('X-User-ID')
    
    try:
        rbac.require(user_id, 'write', 'document')
        
        # Update document
        return jsonify({"message": "Document updated"})
    except PermissionDenied as e:
        return jsonify({"error": str(e)}), 403

if __name__ == '__main__':
    app.run(debug=True)
```

### FastAPI Application

```python
from fastapi import FastAPI, HTTPException, Header
from rbac import RBAC, PermissionDenied

app = FastAPI()
rbac = RBAC(storage='memory')

# Setup RBAC
@app.on_event("startup")
def setup_rbac():
    rbac.create_permission("perm_doc_read", "document", "read")
    rbac.create_permission("perm_doc_write", "document", "write")
    
    rbac.create_role("role_viewer", "Viewer", ["perm_doc_read"])
    rbac.create_role("role_editor", "Editor", ["perm_doc_read", "perm_doc_write"])

@app.get("/api/documents/{doc_id}")
async def get_document(doc_id: str, x_user_id: str = Header(...)):
    try:
        rbac.require(x_user_id, 'read', 'document')
        return {"id": doc_id, "title": "My Document"}
    except PermissionDenied as e:
        raise HTTPException(status_code=403, detail=str(e))

@app.put("/api/documents/{doc_id}")
async def update_document(doc_id: str, x_user_id: str = Header(...)):
    try:
        rbac.require(x_user_id, 'write', 'document')
        return {"message": "Document updated"}
    except PermissionDenied as e:
        raise HTTPException(status_code=403, detail=str(e))
```

### Django Integration

```python
# middleware.py
from django.http import JsonResponse
from rbac import RBAC, PermissionDenied

rbac = RBAC(storage='memory')

def rbac_middleware(get_response):
    def middleware(request):
        # Get user from session
        user_id = request.session.get('user_id')
        
        # Store RBAC instance in request
        request.rbac = rbac
        request.user_id = user_id
        
        response = get_response(request)
        return response
    
    return middleware

# views.py
from django.views import View
from django.http import JsonResponse
from rbac import PermissionDenied

class DocumentView(View):
    def get(self, request, doc_id):
        try:
            request.rbac.require(request.user_id, 'read', 'document')
            return JsonResponse({"id": doc_id, "title": "Document"})
        except PermissionDenied as e:
            return JsonResponse({"error": str(e)}, status=403)
    
    def put(self, request, doc_id):
        try:
            request.rbac.require(request.user_id, 'write', 'document')
            return JsonResponse({"message": "Updated"})
        except PermissionDenied as e:
            return JsonResponse({"error": str(e)}, status=403)
```

## Common Patterns

### Pattern 1: Check Multiple Permissions

```python
# Check if user has ALL permissions
permissions = [
    ('read', 'document'),
    ('write', 'document'),
    ('read', 'user')
]

all_allowed = all(
    rbac.can(user_id, action, resource)
    for action, resource in permissions
)

# Check if user has ANY permission
any_allowed = any(
    rbac.can(user_id, action, resource)
    for action, resource in permissions
)
```

### Pattern 2: Context-Based Authorization

```python
# Check with specific resource
result = rbac.check(
    "user_alice",
    "write",
    {"type": "document", "id": "resource_doc_123"}
)

# With additional context
result = rbac.check(
    "user_alice",
    "write",
    {"type": "document", "id": "resource_doc_123"},
    context={"ip_address": "192.168.1.1", "device": "mobile"}
)
```

### Pattern 3: Bulk Permission Checks

```python
# Check multiple permissions for same user
checks = [
    {"action": "read", "resource_type": "document"},
    {"action": "write", "resource_type": "document"},
    {"action": "delete", "resource_type": "document"},
]

results = rbac.engine.check_permission_batch("user_alice", checks)

for check, result in zip(checks, results):
    print(f"{check['action']}: {result.allowed}")
```

### Pattern 4: Temporary Elevated Access

```python
from datetime import datetime, timedelta

# Grant temporary admin access for 1 hour
expires_at = datetime.utcnow() + timedelta(hours=1)

rbac.assign_role(
    user_id="user_alice",
    role_id="role_admin",
    granted_by="user_supervisor",
    expires_at=expires_at
)

# Check will automatically respect expiration
allowed = rbac.can("user_alice", "admin_action", "resource")
```

## Troubleshooting

### Issue: Import Error

```
ImportError: No module named 'rbac'
```

**Solution:**
```bash
# Make sure PYTHONPATH includes the src directory
export PYTHONPATH="${PYTHONPATH}:/path/to/project/src"

# Or install the package
pip install -e .
```

### Issue: ValidationError for IDs

```
ValidationError: User ID must start with 'user_'
```

**Solution:** Follow ID naming conventions:
- Users: `user_<identifier>`
- Roles: `role_<identifier>`
- Permissions: `perm_<identifier>`
- Resources: `resource_<identifier>`

```python
# Correct
rbac.create_user("user_alice", "alice@example.com", "Alice")

# Wrong
rbac.create_user("alice", "alice@example.com", "Alice")
```

### Issue: Permission Always Denied

**Checklist:**
1. ✓ User exists and is ACTIVE
2. ✓ Role exists and is ACTIVE
3. ✓ Role is assigned to user
4. ✓ Permission is added to role
5. ✓ Action and resource type match
6. ✓ ABAC conditions are satisfied (if any)

**Debug:**
```python
# Get detailed info
result = rbac.check(user_id, action, resource)
print(f"Allowed: {result['allowed']}")
print(f"Reason: {result['reason']}")
print(f"Matched: {result['matched_permissions']}")

# Check user's roles
roles = rbac.get_user_roles(user_id)
print(f"User roles: {[r.name for r in roles]}")

# Check user's permissions
perms = rbac.get_user_permissions(user_id)
print(f"User permissions: {[p.id for p in perms]}")
```

## Next Steps

1. **Read Examples:** Check [examples/](examples/) directory
2. **Read Protocol:** Understand [PROTOCOL.md](PROTOCOL.md)
3. **Review Architecture:** See [ARCHITECTURE.md](ARCHITECTURE.md)
4. **Contribute:** Follow [CONTRIBUTING.md](CONTRIBUTING.md)

## Support

- GitHub Issues: https://github.com/rbac-algorithm/issues
- Documentation: [docs/](docs/)
- Examples: [examples/](examples/)

## License

MIT License - see [LICENSE](LICENSE) file
