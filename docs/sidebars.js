/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation
 */

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  tutorialSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Getting Started',
      items: [
        'getting-started/installation',
        'getting-started/quick-start',
        'getting-started/first-app',
      ],
    },
    {
      type: 'category',
      label: 'Core Concepts',
      items: [
        'concepts/overview',
        'concepts/rbac-basics',
        'concepts/abac',
        'concepts/role-hierarchy',
        'concepts/multi-tenancy',
        'concepts/permissions',
        'concepts/protocols',
      ],
    },
    {
      type: 'category',
      label: 'Guides',
      items: [
        'guides/basic-rbac',
        'guides/hierarchical-roles',
        'guides/attribute-based',
        'guides/multi-tenant',
        'guides/custom-storage',
        'guides/performance',
      ],
    },
    {
      type: 'category',
      label: 'API Reference',
      items: [
        'api/overview',
        'api/rbac-api',
        'api/models',
        'api/storage',
        'api/engine',
        'api/protocols',
      ],
    },
    {
      type: 'category',
      label: 'Language Adapters',
      items: [
        'adapters/overview',
        'adapters/python',
        'adapters/javascript',
        'adapters/go',
        'adapters/java',
        'adapters/csharp',
      ],
    },
    {
      type: 'category',
      label: 'Advanced',
      items: [
        'advanced/architecture',
        'advanced/extending',
        'advanced/migration',
        'advanced/security',
      ],
    },
    'contributing',
    'faq',
  ],
};

module.exports = sidebars;
