# Security, Secrets Management & Legal Compliance Reference

On-demand detailed reference for the AI Principal Engineer skill.
Read this file when you need specific templates, CI configurations, vault integration patterns,
or license audit procedures.

---

## 1. AMD Copyright Header Templates

Every source file must begin with the copyright header **before any code or imports**.
Update the year when the file is created or substantively modified.

### Python (.py)

```python
# Copyright (c) 2026 Advanced Micro Devices, Inc. All rights reserved.
# SPDX-License-Identifier: MIT
```

### Rust (.rs)

```rust
// Copyright (c) 2026 Advanced Micro Devices, Inc. All rights reserved.
// SPDX-License-Identifier: MIT
```

### Shell (.sh, .bash)

```bash
#!/usr/bin/env bash
# Copyright (c) 2026 Advanced Micro Devices, Inc. All rights reserved.
# SPDX-License-Identifier: MIT
```

### TOML (.toml) / YAML (.yaml, .yml)

```toml
# Copyright (c) 2026 Advanced Micro Devices, Inc. All rights reserved.
# SPDX-License-Identifier: MIT
```

### Dockerfile

```dockerfile
# Copyright (c) 2026 Advanced Micro Devices, Inc. All rights reserved.
# SPDX-License-Identifier: MIT
```

### Markdown (.md) — optional but recommended for docs

```markdown
<!-- Copyright (c) 2026 Advanced Micro Devices, Inc. All rights reserved. -->
<!-- SPDX-License-Identifier: MIT -->
```

### Multi-year range

If a file was created in a prior year and modified in the current year:

```python
# Copyright (c) 2024-2026 Advanced Micro Devices, Inc. All rights reserved.
# SPDX-License-Identifier: MIT
```

---

## 2. LICENSE File

Place at the repo root. Must match the SPDX identifier used in headers.

**MIT License (recommended for AMD open-source tools):**

```text
MIT License

Copyright (c) 2026 Advanced Micro Devices, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 3. Dependency License Audit

### Automated audit with pip-licenses

```bash
pip install pip-licenses
pip-licenses --format=table --with-urls --order=license
```

### CI enforcement with liccheck

**`pyproject.toml` config:**

```toml
[tool.liccheck]
authorized_licenses = [
    "MIT",
    "MIT License",
    "BSD",
    "BSD License",
    "BSD-2-Clause",
    "BSD-3-Clause",
    "Apache Software License",
    "Apache-2.0",
    "ISC",
    "ISC License",
    "Python Software Foundation License",
    "PSF",
]
unauthorized_licenses = [
    "GPL",
    "GPLv2",
    "GPLv3",
    "GNU General Public License",
    "AGPL",
    "AGPLv3",
    "Server Side Public License",
    "SSPL",
    "Business Source License",
    "BSL",
]
```

**CI step (GitHub Actions):**

```yaml
- name: License audit
  run: |
    pip install liccheck pip-licenses
    pip-licenses --format=json > licenses.json
    liccheck -s pyproject.toml -r requirements.txt
```

### THIRD_PARTY_NOTICES.md template

```markdown
# Third-Party Notices

This project uses the following third-party libraries:

| Package | Version | License | Copyright |
|---------|---------|---------|-----------|
| langgraph | 0.2.x | MIT | LangChain, Inc. |
| pydantic | 2.x | MIT | Samuel Colvin |
| aiohttp | 3.x | Apache-2.0 | aio-libs contributors |
| structlog | 24.x | Apache-2.0 | Hynek Schlawack |

Generated with: `pip-licenses --format=markdown`
```

---

## 4. Copyright Header CI Enforcement

### Pre-commit hook (recommended)

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/Lucas-C/pre-commit-hooks
    rev: v1.5.5
    hooks:
      - id: insert-license
        name: AMD copyright header (Python)
        types: [python]
        args:
          - --license-filepath=.copyright-header.txt
          - --comment-style=#
          - --detect-license-in-X-top-lines=3

      - id: insert-license
        name: AMD copyright header (Rust)
        types: [rust]
        args:
          - --license-filepath=.copyright-header.txt
          - --comment-style=//
          - --detect-license-in-X-top-lines=3
```

**.copyright-header.txt:**

```text
Copyright (c) 2026 Advanced Micro Devices, Inc. All rights reserved.
SPDX-License-Identifier: MIT
```

### GitHub Actions check (alternative)

```yaml
- name: Check copyright headers
  run: |
    MISSING=$(find src tests -name '*.py' -exec grep -L 'Copyright.*Advanced Micro Devices' {} \;)
    if [ -n "$MISSING" ]; then
      echo "ERROR: Missing AMD copyright header in:"
      echo "$MISSING"
      exit 1
    fi
```

---

## 5. Secure Secret Storage Patterns

### Priority 1: Vault (Production)

**HashiCorp Vault:**

```python
import hvac

def get_secret(path: str, key: str) -> str:
    client = hvac.Client(url=os.environ["VAULT_ADDR"], token=os.environ["VAULT_TOKEN"])
    secret = client.secrets.kv.v2.read_secret_version(path=path)
    return secret["data"]["data"][key]

JIRA_TOKEN = get_secret("prysm/jira", "api_token")
```

**Azure Key Vault:**

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()
client = SecretClient(vault_url="https://prysm-vault.vault.azure.net/", credential=credential)
JIRA_TOKEN = client.get_secret("jira-api-token").value
```

**AWS Secrets Manager:**

```python
import boto3
import json

def get_secret(secret_name: str, region: str = "us-west-2") -> dict:
    client = boto3.client("secretsmanager", region_name=region)
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response["SecretString"])

secrets = get_secret("prysm/jira")
JIRA_TOKEN = secrets["api_token"]
```

### Priority 2: System Keyring (Developer Workstations)

```python
import keyring

keyring.set_password("prysm", "jira_internal_token", "your-token-here")

token = keyring.get_password("prysm", "jira_internal_token")
```

**Supported backends**: macOS Keychain, Windows Credential Manager, GNOME Keyring, KDE Wallet.

### Priority 3: Environment Variables via pydantic-settings

**This is the minimum acceptable standard for any deployment.**

```python
from __future__ import annotations

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class PrysmSettings(BaseSettings):
    """Application settings loaded from environment or .env file."""

    model_config = SettingsConfigDict(
        env_prefix="PRYSM_",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    jira_internal_token: SecretStr
    jira_cloud_token: SecretStr
    github_token: SecretStr
    llm_api_key: SecretStr

    jira_internal_base_url: str = "https://ontrack-internal.amd.com"
    jira_cloud_base_url: str = "https://amd-hub.atlassian.net"
    llm_model: str = "gpt-4o"
    llm_temperature: float = 0.1
```

**Key points:**
- `SecretStr` prevents accidental logging — `str(settings.jira_internal_token)` returns `'**********'`.
- `.get_secret_value()` to access the actual value when needed.
- `.env` file is **always** gitignored.

### .env file template (.env.example — committed, no real values)

```bash
# Prysm environment configuration
# Copy to .env and fill in real values. NEVER commit .env to git.

PRYSM_JIRA_INTERNAL_TOKEN=your-bearer-pat-here
PRYSM_JIRA_CLOUD_TOKEN=your-cloud-api-token
PRYSM_GITHUB_TOKEN=ghp_your_github_pat
PRYSM_LLM_API_KEY=sk-your-openai-key

PRYSM_JIRA_INTERNAL_BASE_URL=https://ontrack-internal.amd.com
PRYSM_JIRA_CLOUD_BASE_URL=https://amd-hub.atlassian.net
PRYSM_LLM_MODEL=gpt-4o
```

---

## 6. Security Scanning CI Pipeline

### GitHub Actions (complete stage)

```yaml
name: Security & Legal

on: [push, pull_request]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # full history for gitleaks

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install bandit safety pip-audit pip-licenses liccheck

      - name: Bandit (Python SAST)
        run: bandit -r src/ -c pyproject.toml -f json -o bandit-report.json || true

      - name: pip-audit (CVE check)
        run: pip-audit --format=json --output=audit-report.json

      - name: License audit
        run: |
          pip-licenses --format=table --with-urls
          liccheck -s pyproject.toml

      - name: Copyright header check
        run: |
          MISSING=$(find src tests -name '*.py' -exec grep -L 'Copyright.*Advanced Micro Devices' {} \;)
          if [ -n "$MISSING" ]; then
            echo "::error::Missing AMD copyright in: $MISSING"
            exit 1
          fi

      - name: Gitleaks (secret scan)
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### pyproject.toml bandit config

```toml
[tool.bandit]
exclude_dirs = ["tests", ".venv"]
skips = ["B101"]  # allow assert in non-production code
targets = ["src"]
```

---

## 7. .gitignore Security Baseline

These patterns must always be present:

```gitignore
# Secrets — NEVER commit
.env
.env.*
!.env.example
*.pem
*.key
*.p12
*.pfx
credentials.json
secrets.yaml
secrets.yml
token.txt
service-account*.json

# Vault / cloud auth
.vault-token
.azure/
.aws/credentials

# IDE secrets
.idea/dataSources/
.vscode/launch.json  # may contain env vars
```

---

## 8. Token Rotation & Expiry

### Policy

| Token Type | Max Lifetime | Rotation Trigger |
|-----------|-------------|-----------------|
| JIRA PAT (internal) | 90 days | Calendar reminder + CI warning |
| JIRA Cloud API token | 180 days | Atlassian admin console |
| GitHub PAT (classic) | 90 days | Use fine-grained PAT with auto-expiry |
| GitHub PAT (fine-grained) | 30–365 days (configurable) | Set at creation |
| LLM API key (OpenAI/Anthropic) | No expiry | Rotate on personnel change or suspected leak |

### Expiry monitoring

```python
from datetime import datetime, timedelta
import warnings

TOKEN_CREATED = datetime(2026, 1, 15)
TOKEN_MAX_AGE = timedelta(days=90)

if datetime.now() > TOKEN_CREATED + TOKEN_MAX_AGE:
    warnings.warn(
        "JIRA internal token has exceeded 90-day rotation policy. "
        "Rotate immediately via ontrack-internal.amd.com/secure/ViewProfile.jspa",
        stacklevel=2,
    )
```

---

## 9. Secure Coding Checklist (Quick Reference)

Use this checklist during code review. Every item is a **must-pass**.

```
Security & Legal Review:
- [ ] AMD copyright header present on ALL source files
- [ ] SPDX-License-Identifier matches project LICENSE file
- [ ] No new GPL/AGPL/SSPL dependencies introduced
- [ ] THIRD_PARTY_NOTICES.md updated if dependencies changed
- [ ] No plaintext secrets in source code, comments, or docstrings
- [ ] No secrets in CLI --help output or example commands
- [ ] .env is gitignored; .env.example has placeholder values only
- [ ] All credentials loaded via pydantic SecretStr or vault
- [ ] No secrets logged at any log level (verify with grep)
- [ ] bandit passes with zero high-severity findings
- [ ] pip-audit / safety shows no known CVEs in dependencies
- [ ] gitleaks / trufflehog clean on full git history
```
