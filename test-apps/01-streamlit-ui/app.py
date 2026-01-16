"""
Streamlit UI Test App - RBAC Algorithm Visual Validator

This is an interactive web-based UI for visually testing and validating
all features of the RBAC Algorithm library.

Run with: streamlit run app.py
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import rbac
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from rbac import RBAC, PermissionDenied, EntityStatus, PermissionsMatrixManager


# Page configuration
st.set_page_config(
    page_title="RBAC Algorithm Validator",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stat-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        text-align: center;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)


# Initialize RBAC instance in session state
if 'rbac' not in st.session_state:
    st.session_state.rbac = RBAC(storage='memory', enable_hierarchy=True, enable_abac=True)
    st.session_state.initialized = False


def initialize_sample_data():
    """Initialize with comprehensive sample data for testing."""
    rbac = st.session_state.rbac
    
    try:
        # Create comprehensive permissions across different resources
        permissions = [
            # Document permissions
            ("perm_doc_read", "document", "read", "Read documents"),
            ("perm_doc_write", "document", "write", "Write/edit documents"),
            ("perm_doc_delete", "document", "delete", "Delete documents"),
            ("perm_doc_publish", "document", "publish", "Publish documents"),
            ("perm_doc_archive", "document", "archive", "Archive documents"),
            
            # User management permissions
            ("perm_user_view", "user", "view", "View user profiles"),
            ("perm_user_create", "user", "create", "Create new users"),
            ("perm_user_edit", "user", "edit", "Edit user details"),
            ("perm_user_delete", "user", "delete", "Delete users"),
            ("perm_user_suspend", "user", "suspend", "Suspend user accounts"),
            
            # API permissions
            ("perm_api_read", "api", "read", "Read API data"),
            ("perm_api_write", "api", "write", "Write API data"),
            ("perm_api_admin", "api", "admin", "API administration"),
            
            # Report permissions
            ("perm_report_view", "report", "view", "View reports"),
            ("perm_report_generate", "report", "generate", "Generate new reports"),
            ("perm_report_export", "report", "export", "Export reports"),
            
            # System permissions
            ("perm_system_config", "system", "configure", "Configure system settings"),
            ("perm_system_audit", "system", "audit", "View audit logs"),
            ("perm_system_backup", "system", "backup", "Backup system data"),
            
            # Admin wildcard
            ("perm_admin_all", "*", "*", "Admin access to everything"),
        ]
        
        for perm_id, resource, action, desc in permissions:
            rbac.create_permission(perm_id, resource, action, desc)
        
        # Create roles with hierarchy and diverse permissions
        rbac.create_role(
            "role_guest", 
            "Guest", 
            permissions=["perm_doc_read", "perm_report_view"], 
            description="Basic read-only access"
        )
        
        rbac.create_role(
            "role_viewer", 
            "Viewer", 
            permissions=["perm_user_view", "perm_api_read"], 
            parent_id="role_guest",
            description="Can view documents and users"
        )
        
        rbac.create_role(
            "role_contributor", 
            "Contributor", 
            permissions=["perm_doc_write"], 
            parent_id="role_viewer",
            description="Can write and edit documents"
        )
        
        rbac.create_role(
            "role_editor", 
            "Editor", 
            permissions=["perm_doc_publish", "perm_report_generate"], 
            parent_id="role_contributor",
            description="Can publish documents and generate reports"
        )
        
        rbac.create_role(
            "role_moderator", 
            "Moderator", 
            permissions=["perm_doc_archive", "perm_user_suspend", "perm_report_export"], 
            parent_id="role_editor",
            description="Can moderate content and users"
        )
        
        rbac.create_role(
            "role_admin", 
            "Admin", 
            permissions=["perm_doc_delete", "perm_user_create", "perm_user_edit", "perm_api_write", "perm_system_audit"], 
            parent_id="role_moderator",
            description="Full management access"
        )
        
        rbac.create_role(
            "role_superuser", 
            "Superuser", 
            permissions=["perm_admin_all", "perm_system_config", "perm_system_backup"], 
            description="Unrestricted system access"
        )
        
        # Additional specialized roles without hierarchy
        rbac.create_role(
            "role_analyst", 
            "Analyst", 
            permissions=["perm_doc_read", "perm_report_view", "perm_report_generate", "perm_report_export", "perm_api_read"], 
            description="Data analysis and reporting"
        )
        
        rbac.create_role(
            "role_developer", 
            "Developer", 
            permissions=["perm_api_read", "perm_api_write", "perm_system_audit"], 
            description="API and development access"
        )
        
        rbac.create_role(
            "role_auditor", 
            "Auditor", 
            permissions=["perm_doc_read", "perm_user_view", "perm_system_audit", "perm_report_view"], 
            description="Audit and compliance access"
        )
        
        # Create 20 test users with Indian names
        users = [
            ("user_aarav", "aarav.sharma@example.com", "Aarav Sharma"),
            ("user_priya", "priya.patel@example.com", "Priya Patel"),
            ("user_arjun", "arjun.kumar@example.com", "Arjun Kumar"),
            ("user_ananya", "ananya.reddy@example.com", "Ananya Reddy"),
            ("user_rohan", "rohan.singh@example.com", "Rohan Singh"),
            ("user_diya", "diya.gupta@example.com", "Diya Gupta"),
            ("user_vikram", "vikram.iyer@example.com", "Vikram Iyer"),
            ("user_aisha", "aisha.khan@example.com", "Aisha Khan"),
            ("user_karthik", "karthik.nair@example.com", "Karthik Nair"),
            ("user_meera", "meera.joshi@example.com", "Meera Joshi"),
            ("user_siddharth", "siddharth.verma@example.com", "Siddharth Verma"),
            ("user_kavya", "kavya.menon@example.com", "Kavya Menon"),
            ("user_aditya", "aditya.desai@example.com", "Aditya Desai"),
            ("user_riya", "riya.chatterjee@example.com", "Riya Chatterjee"),
            ("user_rahul", "rahul.mehta@example.com", "Rahul Mehta"),
            ("user_neha", "neha.kapoor@example.com", "Neha Kapoor"),
            ("user_akash", "akash.rao@example.com", "Akash Rao"),
            ("user_ishita", "ishita.bansal@example.com", "Ishita Bansal"),
            ("user_arnav", "arnav.malhotra@example.com", "Arnav Malhotra"),
            ("user_tanya", "tanya.bhatt@example.com", "Tanya Bhatt"),
        ]
        
        for user_id, email, name in users:
            rbac.create_user(user_id, email, name)
        
        # Assign diverse roles to users (demonstrating different access levels)
        role_assignments = [
            ("user_aarav", "role_guest"),           # Basic access
            ("user_priya", "role_viewer"),          # Viewer access
            ("user_arjun", "role_contributor"),     # Can write
            ("user_ananya", "role_editor"),         # Can publish
            ("user_rohan", "role_moderator"),       # Can moderate
            ("user_diya", "role_admin"),            # Admin access
            ("user_vikram", "role_superuser"),      # Full access
            ("user_aisha", "role_analyst"),         # Specialized analyst
            ("user_karthik", "role_developer"),     # Specialized developer
            ("user_meera", "role_auditor"),         # Specialized auditor
            ("user_siddharth", "role_contributor"), # Another contributor
            ("user_kavya", "role_viewer"),          # Another viewer
            ("user_aditya", "role_editor"),         # Another editor
            ("user_riya", "role_analyst"),          # Another analyst
            ("user_rahul", "role_guest"),           # Another guest
            ("user_neha", "role_moderator"),        # Another moderator
            ("user_akash", "role_developer"),       # Another developer
            ("user_ishita", "role_contributor"),    # Another contributor
            ("user_arnav", "role_admin"),           # Another admin
            ("user_tanya", "role_auditor"),         # Another auditor
        ]
        
        for user_id, role_id in role_assignments:
            rbac.assign_role(user_id, role_id)
        
        st.session_state.initialized = True
        return True
    except Exception as e:
        st.error(f"Error initializing sample data: {e}")
        return False


def show_dashboard():
    """Display dashboard with statistics."""
    st.markdown('<div class="main-header">🔐 RBAC Algorithm - Visual Validator</div>', unsafe_allow_html=True)
    
    rbac = st.session_state.rbac
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        users = rbac.list_users()
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        st.metric("👤 Users", len(users))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        roles = rbac.list_roles()
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        st.metric("🔑 Roles", len(roles))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        perms = rbac.list_permissions()
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        st.metric("✓ Permissions", len(perms))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        st.metric("🏗️ Hierarchy", "Enabled" if rbac._engine._enable_hierarchy else "Disabled")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick actions
    st.subheader("🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Load Sample Data", use_container_width=True):
            if initialize_sample_data():
                st.success("✅ Sample data loaded: 20 users, 10 roles, 20 permissions!")
                st.rerun()
    
    with col2:
        if st.button("🔄 Reset All Data", use_container_width=True):
            st.session_state.rbac = RBAC(storage='memory', enable_hierarchy=True, enable_abac=True)
            st.session_state.initialized = False
            st.success("✅ All data reset!")
            st.rerun()
    
    with col3:
        if st.button("📋 View System Info", use_container_width=True):
            st.info(f"""
            **System Information:**
            - RBAC Version: 0.1.0
            - Storage: In-Memory
            - Hierarchy: Enabled
            - ABAC: Enabled
            - Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """)


def show_users_tab():
    """User management interface."""
    st.header("👤 User Management")
    
    rbac = st.session_state.rbac
    
    # Create new user
    with st.expander("➕ Create New User", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            user_id = st.text_input("User ID", key="new_user_id", placeholder="user_john")
        with col2:
            email = st.text_input("Email", key="new_user_email", placeholder="john@example.com")
        with col3:
            name = st.text_input("Name", key="new_user_name", placeholder="John Doe")
        
        if st.button("Create User"):
            try:
                rbac.create_user(user_id, email, name)
                st.success(f"✅ User '{name}' created successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {e}")
    
    st.markdown("---")
    
    # List existing users
    st.subheader("📋 Existing Users")
    users = rbac.list_users()
    
    if not users:
        st.info("No users found. Create one above or load sample data.")
    else:
        for user in users:
            with st.expander(f"👤 {user.name} ({user.email})", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**ID:** `{user.id}`")
                    st.write(f"**Status:** {user.status.value}")
                    st.write(f"**Created:** {user.created_at.strftime('%Y-%m-%d %H:%M')}")
                
                with col2:
                    # Show assigned roles
                    user_roles = rbac.get_user_roles(user.id)
                    st.write("**Assigned Roles:**")
                    if user_roles:
                        for role in user_roles:
                            st.write(f"  🔑 {role.name}")
                    else:
                        st.write("  _No roles assigned_")
                
                # Role assignment
                st.markdown("---")
                st.write("**Assign/Revoke Role:**")
                
                col1, col2 = st.columns(2)
                with col1:
                    all_roles = rbac.list_roles()
                    if all_roles:
                        role_options = {role.name: role.id for role in all_roles}
                        selected_role = st.selectbox(
                            "Select Role",
                            options=list(role_options.keys()),
                            key=f"role_select_{user.id}"
                        )
                        
                        if st.button("Assign Role", key=f"assign_{user.id}"):
                            try:
                                rbac.assign_role(user.id, role_options[selected_role])
                                st.success(f"✅ Assigned '{selected_role}' to {user.name}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error: {e}")
                
                with col2:
                    if user_roles:
                        revoke_options = {role.name: role.id for role in user_roles}
                        selected_revoke = st.selectbox(
                            "Select Role to Revoke",
                            options=list(revoke_options.keys()),
                            key=f"revoke_select_{user.id}"
                        )
                        
                        if st.button("Revoke Role", key=f"revoke_{user.id}"):
                            try:
                                rbac.revoke_role(user.id, revoke_options[selected_revoke])
                                st.success(f"✅ Revoked '{selected_revoke}' from {user.name}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error: {e}")


def show_roles_tab():
    """Role management interface."""
    st.header("🔑 Role Management")
    
    rbac = st.session_state.rbac
    
    # Create new role
    with st.expander("➕ Create New Role", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            role_id = st.text_input("Role ID", key="new_role_id", placeholder="role_manager")
            name = st.text_input("Role Name", key="new_role_name", placeholder="Manager")
            description = st.text_area("Description", key="new_role_desc")
        
        with col2:
            # Parent role selection
            all_roles = rbac.list_roles()
            parent_options = ["None"] + [role.name for role in all_roles]
            parent_role = st.selectbox("Parent Role (for hierarchy)", parent_options, key="new_role_parent")
            
            # Permission selection
            all_perms = rbac.list_permissions()
            if all_perms:
                perm_options = {f"{p.action} on {p.resource_type}": p.id for p in all_perms}
                selected_perms = st.multiselect(
                    "Select Permissions",
                    options=list(perm_options.keys()),
                    key="new_role_perms"
                )
        
        if st.button("Create Role"):
            try:
                parent_id = None
                if parent_role != "None":
                    parent_id = next((r.id for r in all_roles if r.name == parent_role), None)
                
                permission_ids = [perm_options[p] for p in selected_perms] if all_perms else []
                
                rbac.create_role(role_id, name, permissions=permission_ids, parent_id=parent_id, description=description)
                st.success(f"✅ Role '{name}' created successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {e}")
    
    st.markdown("---")
    
    # List existing roles
    st.subheader("📋 Existing Roles")
    roles = rbac.list_roles()
    
    if not roles:
        st.info("No roles found. Create one above or load sample data.")
    else:
        for role in roles:
            with st.expander(f"🔑 {role.name}", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**ID:** `{role.id}`")
                    st.write(f"**Description:** {role.description or '_No description_'}")
                    st.write(f"**Parent:** {role.parent_id or '_None (root role)_'}")
                    st.write(f"**Status:** {role.status.value}")
                
                with col2:
                    st.write("**Direct Permissions:**")
                    if role.permissions:
                        for perm_id in role.permissions:
                            try:
                                perm = rbac.get_permission(perm_id)
                                st.write(f"  ✓ {perm.action} on {perm.resource_type}")
                            except:
                                st.write(f"  ✓ {perm_id}")
                    else:
                        st.write("  _No direct permissions_")


def show_permissions_tab():
    """Permission management interface."""
    st.header("✓ Permission Management")
    
    rbac = st.session_state.rbac
    
    # Create new permission
    with st.expander("➕ Create New Permission", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            perm_id = st.text_input("Permission ID", key="new_perm_id", placeholder="perm_update")
        with col2:
            resource_type = st.text_input("Resource Type", key="new_perm_resource", placeholder="document")
        with col3:
            action = st.text_input("Action", key="new_perm_action", placeholder="update")
        
        description = st.text_input("Description", key="new_perm_desc", placeholder="Update documents")
        
        if st.button("Create Permission"):
            try:
                rbac.create_permission(perm_id, resource_type, action, description)
                st.success(f"✅ Permission '{action} on {resource_type}' created successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {e}")
    
    st.markdown("---")
    
    # List existing permissions
    st.subheader("📋 Existing Permissions")
    perms = rbac.list_permissions()
    
    if not perms:
        st.info("No permissions found. Create one above or load sample data.")
    else:
        # Display as table
        perm_data = []
        for perm in perms:
            perm_data.append({
                "ID": perm.id,
                "Action": perm.action,
                "Resource Type": perm.resource_type,
                "Description": perm.description or "_No description_",
                "Has Conditions": "Yes" if perm.conditions else "No"
            })
        
        st.dataframe(perm_data, use_container_width=True)


def show_checker_tab():
    """Permission checker interface."""
    st.header("🔍 Permission Checker")
    
    st.markdown("""
    Test whether a specific user can perform an action on a resource.
    This validates your RBAC configuration in real-time.
    """)
    
    rbac = st.session_state.rbac
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        users = rbac.list_users()
        if users:
            user_options = {f"{u.name} ({u.email})": u.id for u in users}
            selected_user_display = st.selectbox("Select User", list(user_options.keys()))
            selected_user = user_options[selected_user_display]
        else:
            st.warning("No users found. Create users first.")
            selected_user = None
    
    with col2:
        action = st.text_input("Action", value="read", placeholder="read, write, delete, etc.")
    
    with col3:
        resource_type = st.text_input("Resource Type", value="document", placeholder="document, api, user, etc.")
    
    st.markdown("---")
    
    if st.button("🔍 Check Permission", use_container_width=True, type="primary"):
        if selected_user:
            try:
                # Perform check
                can_access = rbac.can(selected_user, action, resource_type)
                result = rbac.check(selected_user, action, resource_type)
                
                # Display result
                if can_access:
                    st.markdown('<div class="success-box">', unsafe_allow_html=True)
                    st.success(f"✅ **ALLOWED**: User can {action} on {resource_type}")
                    st.write(f"**Reason:** {result['reason']}")
                    st.write(f"**Matched Permissions:** {', '.join(result['matched_permissions']) if result['matched_permissions'] else 'None'}")
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="error-box">', unsafe_allow_html=True)
                    st.error(f"❌ **DENIED**: User cannot {action} on {resource_type}")
                    st.write(f"**Reason:** {result['reason']}")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Show user's roles and permissions
                st.markdown("---")
                st.subheader("📊 User Details")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Assigned Roles:**")
                    user_roles = rbac.get_user_roles(selected_user)
                    if user_roles:
                        for role in user_roles:
                            st.write(f"  🔑 {role.name}")
                    else:
                        st.write("  _No roles assigned_")
                
                with col2:
                    st.write("**All Permissions (including inherited):**")
                    user_perms = rbac.get_user_permissions(selected_user)
                    if user_perms:
                        for perm in user_perms:
                            st.write(f"  ✓ {perm.action} on {perm.resource_type}")
                    else:
                        st.write("  _No permissions_")
                
            except Exception as e:
                st.error(f"❌ Error checking permission: {e}")
        else:
            st.warning("Please select a user first.")


def show_matrix_tab():
    """Permissions matrix viewer."""
    st.header("📊 Permissions Matrix")
    
    st.markdown("""
    Visual representation of which roles have which permissions.
    ✓ = Has permission | ✗ = No permission | ↑ = Inherited from parent
    """)
    
    rbac = st.session_state.rbac
    
    try:
        # Create matrix
        matrix_manager = PermissionsMatrixManager(rbac.storage)
        matrix = matrix_manager.create_matrix()
        
        if not matrix.roles or not matrix.permissions:
            st.info("No roles or permissions found. Load sample data first.")
            return
        
        # Build matrix data
        matrix_data = []
        
        for perm in matrix.permissions:
            row = {
                "Permission": f"{perm.action} on {perm.resource_type}",
            }
            
            for role in matrix.roles:
                # Check if role has this permission (directly or inherited)
                has_perm = perm.id in role.permissions
                
                # Check for inherited permission
                if not has_perm and role.parent_id:
                    try:
                        parent = rbac.get_role(role.parent_id)
                        has_perm = perm.id in parent.permissions
                        if has_perm:
                            row[role.name] = "↑"  # Inherited
                            continue
                    except:
                        pass
                
                row[role.name] = "✓" if has_perm else "✗"
            
            matrix_data.append(row)
        
        # Display matrix
        st.dataframe(matrix_data, use_container_width=True, height=400)
        
        # Legend
        st.markdown("""
        **Legend:**
        - ✓ = Direct permission
        - ↑ = Inherited from parent role
        - ✗ = No permission
        """)
        
    except Exception as e:
        st.error(f"Error generating matrix: {e}")


def main():
    """Main application."""
    
    # Sidebar
    with st.sidebar:
        st.markdown("# 🔐 RBAC")
        st.title("Navigation")
        
        page = st.radio(
            "Select Page",
            ["🏠 Dashboard", "👤 Users", "🔑 Roles", "✓ Permissions", "🔍 Checker", "📊 Matrix"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        st.markdown("""
        ### About
        Visual validator for the RBAC Algorithm library.
        
        **Features:**
        - Interactive testing
        - Visual feedback
        - Real-time validation
        - Role hierarchy support
        
        **Version:** 0.1.0
        """)
    
    # Show selected page
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "👤 Users":
        show_users_tab()
    elif page == "🔑 Roles":
        show_roles_tab()
    elif page == "✓ Permissions":
        show_permissions_tab()
    elif page == "🔍 Checker":
        show_checker_tab()
    elif page == "📊 Matrix":
        show_matrix_tab()


if __name__ == "__main__":
    main()
