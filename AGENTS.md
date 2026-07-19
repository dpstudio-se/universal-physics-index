# Repository instructions

## Use UPI for debugging

Use Universal Physics Index (UPI) as the default structure for debugging in this repository.

For every non-trivial diagnosis:

1. Record observations and tool output before proposing a cause.
2. Classify each claim with one UPI scientific status:
   - `EST`: directly established by logs, source, tests, or reproducible inspection.
   - `DER`: derived from declared `EST` facts and explicit assumptions.
   - `HYP`: falsifiable explanation that has not yet been verified.
   - `STOP`: progress is blocked by specifically named missing evidence or mechanism.
   - `ERR`: contradicted, invalid, obsolete, or superseded claim.
   - `SYM`: symbolic interpretation only; never treat it as executable authority or evidence.
3. Give every `STOP` claim a concrete `stop_reason` and the smallest next observation needed to continue.
4. Include reproduction steps, expected versus observed behavior, relevant versions or commit SHAs, and a falsification or failure condition.
5. Distinguish repository integrity, application behavior, connector behavior, and user-interface rendering; success in one layer does not prove correctness in another.
6. Label software tests as `verification_type: software_test`. Never present tests, simulations, normalization, correlation, or symbolic mappings as experimental verification or physical equivalence.
7. Use typed UPI relations where useful, such as `DERIVED_FROM`, `CAUSES`, `CONTRADICTS`, `STOPS_AT`, `MEASURED_BY`, or `FALSIFIED_BY`.
8. Preserve secrets and personal data. Transparency means auditable provenance for authorized reviewers, not public disclosure of sensitive content.

A concise debugging result should normally contain:

```text
Problem
EST observations
DER conclusions
HYP candidates
STOP reason, if any
ERR or superseded assumptions
Reproduction/control test
Falsification condition
Recommended next action
```

Prefer an honest `STOP` over an unsupported explanation. A green software test establishes software behavior only within its declared scope.
