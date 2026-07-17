# Validation Error Codes

| Code | Meaning |
|---|---|
| UPI-E001 | Missing or unsupported status |
| UPI-E002 | Missing unit |
| UPI-E003 | Frequency type unspecified |
| UPI-E004 | Hypothesis lacks test/falsification metadata |
| UPI-E005 | Symbolic statement marked established |
| UPI-E006 | Dimensional inconsistency |
| UPI-E007 | Missing provenance |
| UPI-E008 | Unsupported evidence promotion |
| UPI-E009 | Duplicate identifier |
| UPI-E010 | Cyclic dependency |

Errors are stable machine-readable identifiers; messages and paths provide human context. v0.1.0-alpha implements structural guards and reserves E006/E008 for expanded validation.
