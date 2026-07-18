# Contributing to UPI

Thank you for your interest in contributing to the Universal Physics Index!

## How to Contribute

### Submitting a New Node

1. **Create a JSON file** following `schemas/node.schema.json`
2. **Include**:
   - Valid UPI address: `UPI<Domain,Generation,Torus,Node>`
   - Status label: EST, DER, HYP, STOP, ERR, or SYM
   - Title, description, and definitions
   - Evidence records with confidence levels
   - Falsification conditions
   - For STOP nodes: explicit `stop_reason` explaining what's missing

3. **Example**:
   ```json
   {
     "address": "UPI<physics,1,classical,mass>",
     "title": "Mass",
     "description": "Inertial property of matter",
     "status": "EST",
     "quantities": [{"name": "m", "unit": "kg"}],
     "equations": ["F = ma"],
     "evidence": [{"type": "observation", "source": "classical mechanics"}],
     "tags": ["fundamental"]
   }
   ```

4. **Validate**: `upi validate your_file.json`

5. **Submit a PR** with:
   - File in appropriate `data/` subdirectory
   - Description of scientific basis
   - References or sources

### Submitting a Bridge (Relation)

1. **Create a JSON file** following `schemas/bridge.schema.json`
2. **Specify**:
   - `source` and `target` (valid UPI addresses)
   - `relation` type (16 types available)
   - Equations connecting source to target
   - Evidence supporting the relation
   - Status (EST, DER, HYP, STOP, ERR, SYM)

3. **Example**:
   ```json
   {
     "source": "UPI<physics,1,classical,force>",
     "target": "UPI<physics,1,classical,acceleration>",
     "relation": "CAUSES",
     "equations": ["F = ma"],
     "status": "EST"
   }
   ```

### Adding or Improving Physics Functions

1. All functions in `src/upi/physics.py` must:
   - Validate inputs (reject NaN, infinity, invalid signs)
   - Include docstrings with equation references
   - Have comprehensive test coverage

2. Add tests to `tests/test_upi.py`

3. Run validation:
   ```bash
   pytest tests/ -v
   ruff check src tests
   mypy src/upi
   ```

## Code Quality Standards

### Testing

- **Minimum coverage**: All new functions tested
- **Test types**: Unit tests for functions, integration tests for workflows
- **Run tests before PR**: `pytest tests/ -v`

### Linting & Type Checking

```bash
# Format code
black src tests

# Lint
ruff check src tests --fix

# Type check
mypy src/upi --ignore-missing-imports
```

### Documentation

- All public functions must have docstrings
- Include equation references in physics functions
- Document status labels clearly
- Provide examples in docstrings

## Scientific Integrity

### Status Labels

Use these labels accurately:
- **EST**: Experimentally verified, widely accepted
- **DER**: Logically derived from stated assumptions
- **HYP**: Testable but unverified
- **STOP**: Evidence/proof missing (always include `stop_reason`)
- **ERR**: Known to be wrong
- **SYM**: Symbolic representation only

### Stop Nodes

Any unresolved scientific question should be a STOP node:
- Clearly state what is known
- Clearly state what is missing
- List candidate solutions or bridges
- Specify falsification conditions
- Provide primary source references

### Confusion Guards

Include `confusion_guard` fields to prevent common misinterpretations:
```json
"confusion_guard": "Dark matter is not antimatter, dark energy, or ordinary matter in unknown form."
```

## Submission Process

1. **Fork** the repository
2. **Create a branch**: `git checkout -b your-feature`
3. **Make changes** and validate
4. **Commit**: Include a clear message describing what and why
5. **Push** to your fork
6. **Open a PR** with:
   - Description of changes
   - Justification (scientific references)
   - Any new dependencies
   - Test results

## Pull Request Checklist

- [ ] JSON validates against schema (`upi validate`)
- [ ] Tests pass: `pytest tests/ -v`
- [ ] Linting passes: `ruff check src tests`
- [ ] Type checking passes: `mypy src/upi`
- [ ] Docstrings added/updated
- [ ] For new nodes: evidence and falsification conditions included
- [ ] For STOP nodes: `stop_reason` specified
- [ ] No credentials or secrets committed

## Questions?

- Check existing documentation in `docs/`
- Review similar examples in `data/`
- Read the specification: `docs/index-specification.md`
- Open an issue with the question label

## License

By contributing, you agree that your contributions are licensed under the MIT License.
