# Test Applications - End-to-End Validation

This folder contains complete test applications demonstrating real-world usage of the RBAC Algorithm library. Each test app is a standalone, runnable application that validates the library's capabilities in different scenarios.

---

## 📁 Structure

```
test-apps/
├── 00-simple-cli/              # Basic CLI app - simplest possible
├── 01-flask-blog-api/          # Flask REST API with blog posts
├── 02-fastapi-docs-api/        # FastAPI async API with documents
├── 03-multi-tenant-saas/       # Multi-tenant SaaS application
├── 04-django-admin/            # Django integration (future)
├── 05-microservice-auth/       # Microservice auth gateway (future)
└── README.md                   # This file
```

---

## 🎯 Purpose

### **Validation Goals:**
1. **End-to-End Testing** - Verify library works in real applications
2. **Developer Examples** - Show best practices and patterns
3. **Integration Testing** - Test with popular frameworks
4. **Performance Validation** - Measure real-world performance
5. **Documentation by Example** - Living documentation

### **What Makes These Different from /examples/?**
| `/examples/` | `/test-apps/` |
|--------------|---------------|
| Code snippets | Full applications |
| Feature demos | Real-world scenarios |
| 50-200 lines | 500-2000 lines |
| Educational | Production-like |
| Single file | Multi-file structure |

---

## 🚀 Quick Start

### Prerequisites
```bash
# Install RBAC library in development mode
cd "C:\Users\Maneesh Thakur\Downloads\My Projects\RBAC algorithm"
pip install -e .
```

### Run a Test App
```bash
# Navigate to any test app
cd test-apps/00-simple-cli

# Install app-specific dependencies
pip install -r requirements.txt

# Run the app
python main.py
```

---

## 📋 Test Apps Overview

### **00-simple-cli** (Simplest - Start Here!)
**Purpose:** Basic validation of core RBAC features  
**Tech:** Pure Python CLI  
**Time:** 5 minutes  
**Lines:** ~200

**Features Tested:**
- ✅ User, Role, Permission CRUD
- ✅ Role assignment
- ✅ Permission checking
- ✅ Basic hierarchy

**Run:**
```bash
cd test-apps/00-simple-cli
python main.py
```

---

### **01-flask-blog-api** (Most Important!)
**Purpose:** REST API with realistic authorization  
**Tech:** Flask + JWT  
**Time:** 10 minutes  
**Lines:** ~800

**Features Tested:**
- ✅ Role-based endpoints (`/admin`, `/editor`, `/viewer`)
- ✅ Resource ownership (edit own posts)
- ✅ ABAC conditions (context-aware)
- ✅ Request-scoped authorization
- ✅ Error handling
- ✅ Audit logging

**Roles:**
- `viewer` - Read published posts
- `author` - Create posts, edit own
- `editor` - Edit all posts
- `admin` - Full access

**Run:**
```bash
cd test-apps/01-flask-blog-api
pip install -r requirements.txt
python app.py
# Visit http://localhost:5000
```

**Test:**
```bash
# Test requests included
python test_api.py
```

---

### **02-fastapi-docs-api** (Modern Async)
**Purpose:** Async API with OpenAPI documentation  
**Tech:** FastAPI + Pydantic  
**Time:** 10 minutes  
**Lines:** ~700

**Features Tested:**
- ✅ Async permission checks
- ✅ Dependency injection
- ✅ OpenAPI/Swagger integration
- ✅ Pydantic validation
- ✅ JWT authentication
- ✅ Auto-generated docs

**Run:**
```bash
cd test-apps/02-fastapi-docs-api
pip install -r requirements.txt
uvicorn main:app --reload
# Visit http://localhost:8000/docs
```

---

### **03-multi-tenant-saas** (Enterprise)
**Purpose:** Multi-organization SaaS application  
**Tech:** Flask + SQLAlchemy  
**Time:** 15 minutes  
**Lines:** ~1200

**Features Tested:**
- ✅ Domain/tenant isolation
- ✅ Same role names across tenants
- ✅ Cross-tenant security
- ✅ Tenant context middleware
- ✅ Tenant admin management

**Run:**
```bash
cd test-apps/03-multi-tenant-saas
pip install -r requirements.txt
python app.py
```

---

## 🧪 Running All Tests

### Automated Test Suite
```bash
# From test-apps root
python run_all_tests.py
```

This will:
1. Run each test app
2. Execute validation tests
3. Generate performance report
4. Create summary report

---

## 📊 Validation Checklist

Each test app must validate:

### **Core Functionality**
- [ ] Create users, roles, permissions
- [ ] Assign roles to users
- [ ] Check permissions (simple)
- [ ] Check permissions (with context)
- [ ] Role hierarchy (inheritance)
- [ ] ABAC conditions

### **Performance**
- [ ] 1000+ permission checks/sec
- [ ] Sub-millisecond latency
- [ ] Memory usage < 50MB
- [ ] Concurrent request handling

### **Error Handling**
- [ ] Invalid user ID
- [ ] Missing permissions
- [ ] Circular role dependencies
- [ ] Malformed context

### **Security**
- [ ] No permission escalation
- [ ] Domain isolation (if applicable)
- [ ] Input validation
- [ ] Safe ABAC evaluation

---

## 📈 Success Criteria

### **All Test Apps Must:**
1. ✅ Run without errors
2. ✅ Complete in < 60 seconds
3. ✅ Pass all assertions
4. ✅ Generate valid output
5. ✅ Clean up resources

### **Performance Targets:**
- Simple permission check: < 1ms
- Complex ABAC check: < 5ms
- 1000 checks: < 1 second
- Memory: < 100MB per app

---

## 🎓 Learning Path

**For New Users:**
1. Start with `00-simple-cli` - Understand basics
2. Move to `01-flask-blog-api` - See real API
3. Try `02-fastapi-docs-api` - Modern async patterns
4. Explore `03-multi-tenant-saas` - Enterprise features

**For Evaluators:**
1. Run automated test suite
2. Review performance report
3. Check error handling
4. Validate security

---

## 🔧 Development

### Adding a New Test App

1. Create folder: `test-apps/XX-app-name/`
2. Required files:
   ```
   XX-app-name/
   ├── README.md              # App description
   ├── requirements.txt       # Dependencies
   ├── main.py or app.py     # Entry point
   ├── test_app.py           # Validation tests
   └── .env.example          # Config template
   ```

3. Update this README
4. Add to automated test suite

### Testing Checklist
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
python main.py

# 3. Run tests
python test_app.py

# 4. Check performance
python benchmark.py
```

---

## 📝 Notes

### **Why These Apps?**
- **00-simple-cli**: Baseline validation, easiest to debug
- **01-flask-blog-api**: Most common use case (Flask is #1 Python framework)
- **02-fastapi-docs-api**: Modern async patterns, growing adoption
- **03-multi-tenant-saas**: Enterprise requirement, complex scenario

### **Future Test Apps:**
- `04-django-admin` - Django integration with admin panel
- `05-microservice-auth` - Auth gateway for microservices
- `06-websocket-realtime` - Real-time permissions with WebSockets
- `07-graphql-api` - GraphQL with field-level permissions

---

## 🤝 Contributing

When adding test apps:
1. Follow existing patterns
2. Include comprehensive README
3. Add validation tests
4. Document setup steps
5. Keep it simple and focused

---

## 📬 Questions?

- 📖 [Main Documentation](../docs/README.md)
- 💻 [Code Examples](../examples/README.md)
- 🧪 [Test Suite](../tests/README.md)
- 📊 [Project Structure](../PROJECT_STRUCTURE.md)

---

*Last Updated: January 16, 2026*
