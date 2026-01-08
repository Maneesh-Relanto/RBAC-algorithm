# RBAC Algorithm Documentation Site

This directory contains the Docusaurus-based documentation website for RBAC Algorithm.

## Quick Start

### Install Dependencies

```bash
cd docs
npm install
```

### Run Development Server

```bash
npm start
```

The site will open at `http://localhost:3000`

### Build for Production

```bash
npm run build
```

Output will be in `build/` directory.

### Serve Production Build

```bash
npm run serve
```

## Project Structure

```
docs/
├── docs/                          # Documentation markdown files
│   ├── getting-started/          # Installation, quick start, first app
│   ├── concepts/                 # Core concepts and theory
│   ├── guides/                   # How-to guides
│   ├── api/                      # API reference
│   ├── adapters/                 # Language-specific guides
│   └── advanced/                 # Advanced topics
├── src/
│   ├── components/               # React components
│   │   ├── HomepageFeatures/    # Landing page features
│   │   ├── RBACPlayground/      # Interactive code playground
│   │   └── RoleHierarchyVisualizer/  # Visual hierarchy viewer
│   ├── css/                      # Custom styles
│   └── pages/                    # Custom pages (playground, etc.)
├── static/                       # Static assets (images, etc.)
├── docusaurus.config.js         # Docusaurus configuration
├── sidebars.js                  # Documentation sidebar structure
└── package.json                 # Dependencies

## Features

### Interactive Components

- **Playground** - Run RBAC code examples in browser
- **Hierarchy Visualizer** - See role inheritance diagrams
- **Code Tabs** - Multi-language code examples

### Documentation Sections

1. **Getting Started** - Installation, quick start, tutorials
2. **Concepts** - RBAC/ABAC theory, architecture
3. **Guides** - Step-by-step how-tos
4. **API Reference** - Complete API documentation
5. **Adapters** - Language-specific integration guides
6. **Advanced** - Security, performance, migration

## Customization

### Add New Documentation Page

1. Create markdown file in `docs/` directory
2. Add frontmatter:
   ```markdown
   ---
   sidebar_position: 1
   title: My Page
   ---
   ```
3. Page automatically appears in sidebar

### Add Interactive Component

1. Create component in `src/components/`
2. Import in markdown:
   ```markdown
   import MyComponent from '@site/src/components/MyComponent';
   
   <MyComponent />
   ```

### Modify Theme

Edit `src/css/custom.css` for styling changes.

### Update Navigation

Edit `docusaurus.config.js` → `themeConfig.navbar`

## Deployment

### GitHub Pages

```bash
GIT_USER=<username> npm run deploy
```

### Netlify

1. Connect repository
2. Build command: `npm run build`
3. Publish directory: `build`

### Vercel

1. Import project
2. Framework: Docusaurus
3. Deploy

### Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
FROM nginx:alpine
COPY --from=0 /app/build /usr/share/nginx/html
```

## Search Configuration

The site is configured for Algolia DocSearch. To enable:

1. Apply for DocSearch: https://docsearch.algolia.com/apply
2. Update `docusaurus.config.js` with your credentials:
   ```js
   algolia: {
     appId: 'YOUR_APP_ID',
     apiKey: 'YOUR_API_KEY',
     indexName: 'rbac-algorithm',
   }
   ```

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for documentation contribution guidelines.

## Resources

- [Docusaurus Documentation](https://docusaurus.io/)
- [Markdown Features](https://docusaurus.io/docs/markdown-features)
- [MDX](https://mdxjs.com/) - Markdown + JSX
