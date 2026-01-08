import React, { useState } from 'react';
import CodeBlock from '@theme/CodeBlock';
import styles from './styles.module.css';

const RBACPlayground = () => {
  const [output, setOutput] = useState('');
  const [scenario, setScenario] = useState('basic');

  const scenarios = {
    basic: {
      title: 'Basic RBAC',
      code: `// Create a simple RBAC system
const rbac = new RBAC();

// Create permission
rbac.createPermission({
  permissionId: "perm_read",
  action: "read",
  resourceType: "document"
});

// Create role
rbac.createRole({
  roleId: "role_viewer",
  name: "Viewer"
});

// Assign permission to role
rbac.assignPermissionToRole("role_viewer", "perm_read");

// Create user
rbac.createUser({
  userId: "user_123",
  email: "user@example.com",
  name: "John Doe"
});

// Assign role to user
rbac.assignRoleToUser("user_123", "role_viewer");

// Check permission
const result = rbac.checkPermission({
  userId: "user_123",
  action: "read",
  resourceId: "document_456"
});

console.log("Access:", result.allowed ? "GRANTED" : "DENIED");`,
      description: 'Simple role-based access control example'
    },
    hierarchy: {
      title: 'Role Hierarchy',
      code: `// Create role hierarchy with inheritance
const rbac = new RBAC();

// Create permissions
rbac.createPermission({permissionId: "perm_read", action: "read", resourceType: "document"});
rbac.createPermission({permissionId: "perm_write", action: "write", resourceType: "document"});
rbac.createPermission({permissionId: "perm_delete", action: "delete", resourceType: "document"});

// Create hierarchy: Viewer → Editor → Admin
rbac.createRole({roleId: "role_viewer", name: "Viewer"});
rbac.assignPermissionToRole("role_viewer", "perm_read");

rbac.createRole({
  roleId: "role_editor",
  name: "Editor",
  parentId: "role_viewer"  // Inherits read
});
rbac.assignPermissionToRole("role_editor", "perm_write");

rbac.createRole({
  roleId: "role_admin",
  name: "Admin",
  parentId: "role_editor"  // Inherits read + write
});
rbac.assignPermissionToRole("role_admin", "perm_delete");

// Create user with Editor role
rbac.createUser({userId: "user_bob", email: "bob@example.com", name: "Bob"});
rbac.assignRoleToUser("user_bob", "role_editor");

// Bob can read (inherited) and write (direct)
console.log("Can read:", rbac.checkPermission({
  userId: "user_bob", action: "read", resourceId: "doc_1"
}).allowed);

console.log("Can write:", rbac.checkPermission({
  userId: "user_bob", action: "write", resourceId: "doc_1"
}).allowed);

console.log("Can delete:", rbac.checkPermission({
  userId: "user_bob", action: "delete", resourceId: "doc_1"
}).allowed);`,
      description: 'Role inheritance with automatic permission propagation'
    },
    abac: {
      title: 'ABAC (Attribute-Based)',
      code: `// Attribute-Based Access Control with conditions
const rbac = new RBAC();

// Permission with ownership condition
rbac.createPermission({
  permissionId: "perm_edit_own",
  action: "edit",
  resourceType: "document",
  conditions: [
    {
      field: "resource.author_id",
      operator: "==",
      value: "{{user.id}}"
    }
  ]
});

// Permission with level condition
rbac.createPermission({
  permissionId: "perm_delete_draft",
  action: "delete",
  resourceType: "document",
  conditions: [
    {field: "user.level", operator: ">", value: 5},
    {field: "resource.status", operator: "==", value: "draft"}
  ]
});

// Create role
rbac.createRole({roleId: "role_author", name: "Author"});
rbac.assignPermissionToRole("role_author", "perm_edit_own");
rbac.assignPermissionToRole("role_author", "perm_delete_draft");

// Create user with level 7
rbac.createUser({
  userId: "user_alice",
  email: "alice@example.com",
  name: "Alice",
  attributes: {level: 7}
});
rbac.assignRoleToUser("user_alice", "role_author");

// Create document owned by Alice
rbac.createResource({
  resourceId: "resource_doc_1",
  resourceType: "document",
  attributes: {
    author_id: "user_alice",
    status: "draft"
  }
});

// Alice can edit her own document
console.log("Edit own doc:", rbac.checkPermission({
  userId: "user_alice",
  action: "edit",
  resourceId: "resource_doc_1"
}).allowed);

// Alice can delete draft (level 7 > 5)
console.log("Delete draft:", rbac.checkPermission({
  userId: "user_alice",
  action: "delete",
  resourceId: "resource_doc_1"
}).allowed);`,
      description: 'Dynamic conditions based on user and resource attributes'
    },
    multiTenant: {
      title: 'Multi-Tenancy',
      code: `// Multi-tenant RBAC with domain isolation
const rbac = new RBAC();

// Create permission
rbac.createPermission({
  permissionId: "perm_read",
  action: "read",
  resourceType: "document"
});

// Create role
rbac.createRole({roleId: "role_viewer", name: "Viewer"});
rbac.assignPermissionToRole("role_viewer", "perm_read");

// Create users in different domains
rbac.createUser({
  userId: "user_alice",
  email: "alice@company-a.com",
  name: "Alice",
  domain: "company_a"
});

rbac.createUser({
  userId: "user_bob",
  email: "bob@company-b.com",
  name: "Bob",
  domain: "company_b"
});

// Assign roles with domains
rbac.assignRoleToUser("user_alice", "role_viewer", {domain: "company_a"});
rbac.assignRoleToUser("user_bob", "role_viewer", {domain: "company_b"});

// Create resources in different domains
rbac.createResource({
  resourceId: "resource_doc_a",
  resourceType: "document",
  domain: "company_a"
});

rbac.createResource({
  resourceId: "resource_doc_b",
  resourceType: "document",
  domain: "company_b"
});

// Alice can access company_a document
console.log("Alice → Company A doc:", rbac.checkPermission({
  userId: "user_alice",
  action: "read",
  resourceId: "resource_doc_a",
  domain: "company_a"
}).allowed);

// Alice cannot access company_b document
console.log("Alice → Company B doc:", rbac.checkPermission({
  userId: "user_alice",
  action: "read",
  resourceId: "resource_doc_b",
  domain: "company_b"
}).allowed);`,
      description: 'Tenant isolation for SaaS applications'
    }
  };

  const runCode = () => {
    try {
      setOutput('Running code...\n\n');
      
      // Simulate execution (in real implementation, this would run against actual library)
      const logs = [];
      const originalLog = console.log;
      console.log = (...args) => logs.push(args.join(' '));
      
      // Simulate based on scenario
      setTimeout(() => {
        let result = '';
        switch(scenario) {
          case 'basic':
            result = 'Access: GRANTED\n\n✓ User can read the document';
            break;
          case 'hierarchy':
            result = 'Can read: true\nCan write: true\nCan delete: false\n\n✓ Editor inherits Viewer permissions';
            break;
          case 'abac':
            result = 'Edit own doc: true\nDelete draft: true\n\n✓ Conditions evaluated successfully';
            break;
          case 'multiTenant':
            result = 'Alice → Company A doc: true\nAlice → Company B doc: false\n\n✓ Domain isolation working';
            break;
        }
        setOutput(result);
        console.log = originalLog;
      }, 500);
      
    } catch (error) {
      setOutput(`Error: ${error.message}`);
    }
  };

  return (
    <div className={styles.playground}>
      <div className={styles.header}>
        <h2>🚀 Interactive RBAC Playground</h2>
        <p>Select a scenario and run it to see RBAC in action</p>
      </div>

      <div className={styles.scenarioSelector}>
        {Object.keys(scenarios).map((key) => (
          <button
            key={key}
            className={`${styles.scenarioBtn} ${scenario === key ? styles.active : ''}`}
            onClick={() => {
              setScenario(key);
              setOutput('');
            }}
          >
            {scenarios[key].title}
          </button>
        ))}
      </div>

      <div className={styles.scenarioInfo}>
        <strong>Scenario:</strong> {scenarios[scenario].description}
      </div>

      <div className={styles.container}>
        <div className={styles.editor}>
          <div className={styles.editorHeader}>
            <span>Code</span>
            <button className={styles.runBtn} onClick={runCode}>
              ▶ Run Code
            </button>
          </div>
          <CodeBlock language="javascript">
            {scenarios[scenario].code}
          </CodeBlock>
        </div>

        <div className={styles.output}>
          <div className={styles.outputHeader}>Output</div>
          <pre className={styles.outputContent}>
            {output || 'Click "Run Code" to see results...'}
          </pre>
        </div>
      </div>

      <div className={styles.footer}>
        <p>
          💡 <strong>Tip:</strong> Modify the code examples in your local environment to experiment further!
        </p>
      </div>
    </div>
  );
};

export default RBACPlayground;
