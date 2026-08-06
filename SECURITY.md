# Security Policy

## Reporting Security Vulnerabilities

If you discover a security vulnerability in UPI, please **do not** open a public GitHub issue. Instead, please email the maintainers privately with:

1. Description of the vulnerability
2. Affected component (e.g., `src/upi/validation.py`)
3. Steps to reproduce
4. Potential impact
5. Suggested fix (if applicable)

We will acknowledge receipt within 48 hours and provide a timeline for a fix.

## Security Considerations

### Input Validation

All numeric inputs in physics functions are validated:
- ✓ NaN rejection
- ✓ Infinity rejection
- ✓ Sign validation
- ✓ Range bounds checking

### JSON Schema Validation

- ✓ Unknown status labels rejected
- ✓ Missing required fields detected
- ✓ Bridges without relation types rejected
- ✓ STOP nodes without `stop_reason` rejected

### No Credentials in Repository

- ✓ No API keys, secrets, or credentials stored
- ✓ `.gitignore` prevents accidental commits
- ✓ No embedded authentication

### Known Limitations

- This is alpha software (v0.1.0-alpha)
- Do not rely on this for critical decision-making
- Always verify against original scientific literature
- Use in research and educational contexts only

## Dependency Security

Dependencies are minimal to reduce attack surface:
- `jsonschema` — For JSON validation only

No runtime dependencies on external services or APIs.

## Compliance

- MIT License
- No usage restrictions
- Open for security audits
- Community-driven improvements welcome

## Version Support

Security patches are provided for:
- Latest release (current)
- Previous release (6 months)

Older versions should be upgraded to the latest stable release.
