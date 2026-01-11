# RBAC Algorithm Logo

Simple, professional logo representing security, hierarchy, and access control.

## Logo Variants

### 1. Main Logo (`logo.svg`)
- **Size**: 200x200px
- **Usage**: Navigation bar, documentation headers
- **Design**: Shield with hierarchical layers and key symbol
- **Colors**: Purple-blue gradient (#667eea → #764ba2)

**Symbolism**:
- 🛡️ **Shield**: Security and protection
- 📊 **Layers**: Role hierarchy (3 tiers)
- 🔑 **Key**: Access control

### 2. Full Logo with Text (`logo-full.svg`)
- **Size**: 400x100px
- **Usage**: Landing page, presentations, marketing
- **Includes**: Logo icon + "RBAC Algorithm" text
- **Tagline**: "ENTERPRISE ACCESS CONTROL"

### 3. Favicon (`favicon.ico`)
- **Size**: 32x32px
- **Usage**: Browser tab icon
- **Design**: Simplified version of main logo

## Color Palette

```
Primary Purple: #667eea
Secondary Purple: #764ba2
White: #ffffff
Dark Text: #2d3748
Light Text: #718096
```

## Usage Guidelines

### In Documentation Site
The logo is automatically used in:
- Navigation bar (top left)
- Browser tab (favicon)
- Social media cards

### File Locations
```
docs/static/img/
├── logo.svg          # Main logo (navbar)
├── logo-full.svg     # Full logo with text
└── favicon.ico       # Browser favicon
```

### Updating Logo
The Docusaurus config automatically references these files. No code changes needed when updating logo files.

## Design Principles

1. **Simple** - Clear at any size
2. **Memorable** - Unique shield + layers + key concept
3. **Professional** - Enterprise-grade appearance
4. **Scalable** - SVG format, works from 16px to poster size
5. **Meaningful** - Every element represents RBAC concepts

## Alternatives (Not Included)

If you want variations:
- **Dark mode version**: Invert colors for dark backgrounds
- **Monochrome**: Single color for print/embroidery
- **Icon only**: Just the shield without circle
- **Horizontal**: Logo + text side-by-side

## Export Formats

Current format: **SVG** (vector, infinite scaling)

To create other formats:
1. Open SVG in browser
2. Take screenshot for PNG
3. Use online converter for ICO, WebP, etc.

Or use ImageMagick:
```bash
# Convert to PNG
magick logo.svg logo.png

# Convert to multiple sizes
magick logo.svg -resize 512x512 logo-512.png
magick logo.svg -resize 256x256 logo-256.png
magick logo.svg -resize 128x128 logo-128.png
```

## License

Logo follows the same license as the project. Free to use with attribution.
