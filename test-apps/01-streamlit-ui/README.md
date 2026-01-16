# 01-streamlit-ui: Visual RBAC Validator

**Purpose:** Interactive web-based UI for visually testing and validating all RBAC algorithm features in real-time.

## 🎯 Features

### 🏠 Dashboard
- Real-time statistics (users, roles, permissions)
- Quick actions (load sample data, reset)
- System information display

### 👤 User Management
- Create new users with email and name
- View all existing users
- Assign/revoke roles interactively
- See user's assigned roles and permissions

### 🔑 Role Management
- Create roles with permissions
- Set up role hierarchy (parent-child)
- View role details and inherited permissions
- Visual role structure

### ✓ Permission Management
- Create permissions (resource_type + action)
- View all permissions in table format
- See which permissions have ABAC conditions

### 🔍 Permission Checker
- Interactive permission testing
- Select user, action, and resource
- Instant visual feedback (✅ ALLOWED / ❌ DENIED)
- See detailed reasons and matched permissions
- View user's complete role/permission set

### 📊 Permissions Matrix
- Visual grid of roles vs permissions
- Shows direct permissions (✓)
- Shows inherited permissions (↑)
- Easy-to-read table format

## 🚀 Quick Start

### Prerequisites
```bash
# Install Streamlit
pip install -r requirements.txt

# Or install directly
pip install streamlit
```

### Run the App
```bash
# From this directory
cd test-apps/01-streamlit-ui

# Run Streamlit
streamlit run app.py

# Or from project root
streamlit run test-apps/01-streamlit-ui/app.py
```

The app will open in your browser at `http://localhost:8501`

## 📋 Usage Guide

### First Time Setup
1. **Load Sample Data** - Click "Load Sample Data" on dashboard
   - Creates **20 users** (Aarav, Priya, Arjun, Ananya, Rohan, Diya, and 14 more Indian users)
   - Creates **10 roles** (Guest, Viewer, Contributor, Editor, Moderator, Admin, Superuser, Analyst, Developer, Auditor)
   - Creates **20 permissions** across 5 resource types (document, user, api, report, system)
   - Role hierarchy: Guest → Viewer → Contributor → Editor → Moderator → Admin
   - Specialized roles: Analyst, Developer, Auditor (no hierarchy)
   - Diverse role assignments demonstrating different access levels

2. **Explore** - Navigate using the sidebar
   - 👤 Users - Manage users and role assignments
   - 🔑 Roles - Create/view roles and hierarchy
   - ✓ Permissions - Manage permissions
   - 🔍 Checker - Test permission checks
   - 📊 Matrix - Visualize role-permission mappings

### Testing Scenarios

#### Scenario 1: Basic Permission Check
1. Go to **🔍 Checker** tab
2. Select user: "Alice"
3. Action: "read"
4. Resource: "document"
5. Click "Check Permission"
6. Result: ✅ ALLOWED (Alice has viewer role with read permission)

#### Scenario 2: Role Hierarchy
1. Go to **👤 Users** tab
2. Find Bob (has Editor role)
3. Expand his details
4. See he has "write" directly + "read" inherited from Viewer parent role
5. Go to **🔍 Checker**
6. Test Bob reading documents → ✅ ALLOWED (inherited)

#### Scenario 3: Permission Denied
1. Go to **🔍 Checker** tab
2. Select user: "Alice" (Viewer role)
3. Action: "delete"
4. Resource: "document"
5. Click "Check Permission"
6. Result: ❌ DENIED (Alice lacks delete permission)

#### Scenario 4: Create Custom Role
1. Go to **🔑 Roles** tab
2. Click "Create New Role"
3. Role ID: "role_moderator"
4. Name: "Moderator"
5. Select permissions: "read", "write"
6. Parent role: "Viewer"
7. Create role
8. Go to **👤 Users** and assign it to a user

#### Scenario 5: Visual Matrix
1. Go to **📊 Matrix** tab
2. See grid showing all role-permission combinations
3. ✓ = Has permission
4. ↑ = Inherited from parent
5. ✗ = No permission

### Advanced Features

#### Reset Everything
- Dashboard → "Reset All Data"
- Clears all users, roles, permissions
- Start fresh

#### Custom Permissions
- Go to **✓ Permissions** tab
- Create custom resource types
- Define custom actions
- Test with checker

#### Role Hierarchy Testing
- Create multi-level hierarchy (A → B → C)
- Test inherited permissions at each level
- See inheritance in matrix view

## 🎨 UI Components

### Color Coding
- 🟢 **Green boxes** = Success/Allowed
- 🔴 **Red boxes** = Error/Denied
- 🔵 **Blue boxes** = Information
- ⚪ **Gray boxes** = Statistics

### Icons
- 👤 Users
- 🔑 Roles
- ✓ Permissions
- 🔍 Checker
- 📊 Matrix
- ↑ Inherited
- ✅ Allowed
- ❌ Denied

## 📊 Sample Data Structure

When you load sample data, you get:

**Users:**
- Alice (alice@example.com) → Viewer role
- Bob (bob@example.com) → Editor role
- Charlie (charlie@example.com) → Admin role

**Roles (with hierarchy):**
```
Superuser (admin on *)
    │
Admin (delete)
    │
Editor (write)
    │
Viewer (read)
```

**Permissions:**
- perm_read: read on document
- perm_write: write on document
- perm_delete: delete on document
- perm_admin: * on * (wildcard)

## 🔧 Customization

### Add More Sample Data
Edit `initialize_sample_data()` in `app.py`:
```python
def initialize_sample_data():
    rbac = st.session_state.rbac
    
    # Add your custom data
    rbac.create_permission("perm_custom", "api", "execute")
    rbac.create_role("role_custom", "Custom", permissions=["perm_custom"])
    # ... etc
```

### Modify UI Styling
Edit CSS in `app.py` under `st.markdown("""<style>...`)

### Add New Pages
Add new functions like `show_custom_tab()` and add to navigation

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Use different port
streamlit run app.py --server.port 8502
```

### Module Not Found
```bash
# Install from project root
pip install -e .
```

### Data Not Persisting
- Data is in-memory only
- Resets when you reload the page
- This is intentional for testing

## 📈 Performance

- **Load Time:** < 1 second
- **Response Time:** Instant (in-memory)
- **Concurrent Users:** Single instance
- **Data Limits:** Thousands of entities (in-memory)

## 🎯 Use Cases

### Development
- Test RBAC features while developing
- Validate permission logic
- Debug role hierarchies
- Experiment with configurations

### Demos
- Show stakeholders how RBAC works
- Interactive presentations
- Live permission testing
- Visual role structures

### Learning
- Learn RBAC concepts visually
- Understand role inheritance
- See permission matching in action
- Experiment safely

### Documentation
- Take screenshots for docs
- Create video tutorials
- Show real-world examples
- Validate documentation accuracy

## 🚀 Next Steps

After exploring this UI:
1. ✅ Understand all RBAC features visually
2. ➡️ Try [00-simple-cli](../00-simple-cli/) for programmatic testing
3. ➡️ Build your own integration using the patterns learned
4. ➡️ Check [examples/](../../examples/) for code snippets

## 💡 Tips

- **Start with sample data** - Makes exploration easier
- **Use checker frequently** - Test changes immediately
- **Watch the matrix** - Visualize permission inheritance
- **Reset often** - Start fresh for different scenarios
- **Combine features** - Create user → assign role → check permission

---

**Status:** ✅ Fully functional  
**Type:** Interactive Web UI  
**Tech:** Streamlit + RBAC Algorithm  
**Runtime:** < 1 second startup  
**Last Updated:** January 17, 2026
