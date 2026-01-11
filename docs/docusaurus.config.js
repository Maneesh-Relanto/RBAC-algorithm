// @ts-check
// Note: type annotations allow type checking and IDEs autocompletion

const lightCodeTheme = require('prism-react-renderer').themes.github;
const darkCodeTheme = require('prism-react-renderer').themes.dracula;

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'RBAC Algorithm',
  tagline: 'Enterprise-Grade Role-Based Access Control Library',
  favicon: 'img/favicon.ico',

  // Set the production url of your site here
  url: 'https://maneesh-relanto.github.io',
  // Set the /<baseUrl>/ pathname under which your site is served
  baseUrl: '/RBAC-algorithm/',

  // GitHub pages deployment config.
  organizationName: 'Maneesh-Relanto',
  projectName: 'RBAC-algorithm',
  deploymentBranch: 'gh-pages',
  trailingSlash: false,

  onBrokenLinks: 'warn',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl: 'https://github.com/your-org/rbac-algorithm/tree/main/docs/',
        },
        blog: {
          showReadingTime: true,
          editUrl: 'https://github.com/your-org/rbac-algorithm/tree/main/docs/',
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      image: 'img/logo-full.svg',
      navbar: {
        title: 'RBAC Algorithm',
        logo: {
          alt: 'RBAC Algorithm Logo',
          src: 'img/logo.svg',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'tutorialSidebar',
            position: 'left',
            label: 'Documentation',
          },
          {
            to: '/playground',
            label: 'Playground',
            position: 'left',
          },
          {
            href: 'https://github.com/your-org/rbac-algorithm',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Docs',
            items: [
              {
                label: 'Getting Started',
                to: '/docs/getting-started',
              },
              {
                label: 'Concepts',
                to: '/docs/concepts/overview',
              },
              {
                label: 'API Reference',
                to: '/docs/api/overview',
              },
            ],
          },
          {
            title: 'Adapters',
            items: [
              {
                label: 'Python',
                to: '/docs/adapters/python',
              },
              {
                label: 'JavaScript',
                to: '/docs/adapters/javascript',
              },
              {
                label: 'Other Languages',
                to: '/docs/adapters/overview',
              },
            ],
          },
          {
            title: 'More',
            items: [
              {
                label: 'GitHub',
                href: 'https://github.com/your-org/rbac-algorithm',
              },
              {
                label: 'Contributing',
                to: '/docs/contributing',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} RBAC Algorithm. Built with Docusaurus.`,
      },
      prism: {
        theme: lightCodeTheme,
        darkTheme: darkCodeTheme,
        additionalLanguages: ['python', 'java', 'csharp', 'go', 'ruby', 'rust'],
      },
      algolia: {
        appId: 'YOUR_APP_ID',
        apiKey: 'YOUR_API_KEY',
        indexName: 'rbac-algorithm',
        contextualSearch: true,
      },
    }),
};

module.exports = config;
