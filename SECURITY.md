# Security Policy

UPI treats JSON and future YAML inputs as untrusted. Parsing must never execute code; YAML support, if added, must use a safe loader. The project contains no telemetry, automatic uploads, credentials, shell execution from records, or runtime network requirement.

## Reporting a vulnerability

For sensitive reports, use the repository's private GitHub Security Advisory reporting feature when available. Otherwise open a GitHub issue containing no exploit secrets and ask a maintainer for a private channel. Do not publish tokens, personal data, or working exploits.

Supported security fixes target the current release line. Never commit API keys, cookies, tokens, or personal credentials.
