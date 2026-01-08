---
sidebar_position: 1
---

# Installation

Get started with RBAC Algorithm in less than 5 minutes.

## Choose Your Language

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="python" label="Python" default>

### Requirements

- Python 3.8 or higher
- pip

### Install via pip

```bash
pip install rbac-algorithm
```

### Verify Installation

```python
import rbac
print(rbac.__version__)
```

</TabItem>

<TabItem value="javascript" label="JavaScript/Node.js">

### Requirements

- Node.js 16 or higher
- npm or yarn

### Install via npm

```bash
npm install rbac-algorithm
```

### Install via yarn

```bash
yarn add rbac-algorithm
```

### Verify Installation

```javascript
const { RBAC } = require('rbac-algorithm');
console.log(RBAC.version);
```

</TabItem>

<TabItem value="go" label="Go">

### Requirements

- Go 1.19 or higher

### Install

```bash
go get github.com/your-org/rbac-algorithm
```

### Verify Installation

```go
package main

import (
    "fmt"
    "github.com/your-org/rbac-algorithm"
)

func main() {
    fmt.Println(rbac.Version)
}
```

</TabItem>

<TabItem value="java" label="Java">

### Requirements

- Java 11 or higher
- Maven or Gradle

### Maven

Add to your `pom.xml`:

```xml
<dependency>
    <groupId>com.rbac-algorithm</groupId>
    <artifactId>rbac-algorithm</artifactId>
    <version>1.0.0</version>
</dependency>
```

### Gradle

Add to your `build.gradle`:

```groovy
implementation 'com.rbac-algorithm:rbac-algorithm:1.0.0'
```

</TabItem>

<TabItem value="csharp" label="C#/.NET">

### Requirements

- .NET 6.0 or higher

### Install via NuGet

```bash
dotnet add package RbacAlgorithm
```

### Package Manager Console

```powershell
Install-Package RbacAlgorithm
```

</TabItem>
</Tabs>

## Development Installation

If you want to contribute or customize the library:

### Clone the Repository

```bash
git clone https://github.com/your-org/rbac-algorithm.git
cd rbac-algorithm
```

### Install Dependencies

<Tabs>
<TabItem value="python" label="Python" default>

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest
```

</TabItem>

<TabItem value="javascript" label="JavaScript">

```bash
# Install dependencies
npm install

# Run tests
npm test

# Build
npm run build
```

</TabItem>
</Tabs>

## Storage Backends

By default, RBAC Algorithm uses in-memory storage. For production, you'll want a persistent storage backend:

### PostgreSQL

```bash
pip install rbac-algorithm[postgres]
```

### MongoDB

```bash
pip install rbac-algorithm[mongodb]
```

### Redis

```bash
pip install rbac-algorithm[redis]
```

### MySQL

```bash
pip install rbac-algorithm[mysql]
```

See [Custom Storage Guide](/docs/guides/custom-storage) for details.

## Docker

Run RBAC Algorithm in a container:

```bash
docker pull rbac-algorithm/rbac-algorithm:latest

docker run -p 8080:8080 rbac-algorithm/rbac-algorithm:latest
```

## Troubleshooting

### Python: Module Not Found

```bash
# Ensure pip is up to date
pip install --upgrade pip

# Install with verbose output
pip install -v rbac-algorithm
```

### Node.js: Permission Errors

```bash
# Use npx or install globally with sudo
sudo npm install -g rbac-algorithm
```

### Version Conflicts

```bash
# Check installed version
pip show rbac-algorithm  # Python
npm list rbac-algorithm  # Node.js
```

## Next Steps

- 📖 [Quick Start Guide](/docs/getting-started/quick-start)
- 🚀 [Build Your First App](/docs/getting-started/first-app)
- 💡 [Core Concepts](/docs/concepts/overview)
