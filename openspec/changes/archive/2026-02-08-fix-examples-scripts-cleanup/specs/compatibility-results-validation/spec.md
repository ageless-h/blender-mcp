## MODIFIED Requirements

### Requirement: Compatibility results have required fields
Compatibility results SHALL include status and checked_at fields for each supported version. The results file SHALL use the key `test_results` as the canonical top-level key for the array of per-version entries. All tools that read or write this file SHALL use the same key.

#### Scenario: Compatibility results validation
- **WHEN** compatibility results are read
- **THEN** each entry includes status and checked_at

#### Scenario: Writer and reader use consistent key
- **WHEN** `run_real_blender_tests.py` writes compatibility results
- **THEN** the output JSON uses the key `test_results` for the per-version array

#### Scenario: Reader consumes writer output
- **WHEN** `check_compatibility.py` reads a file produced by `run_real_blender_tests.py`
- **THEN** it successfully locates all per-version entries without data loss

## ADDED Requirements

### Requirement: Test result parsing uses structured output
The compatibility test runner SHALL parse test results from structured output (JUnit XML) rather than counting string occurrences in stdout.

#### Scenario: Accurate test count from structured output
- **WHEN** `run_real_blender_tests.py` collects pytest results
- **THEN** test counts (total, passed, failed) are parsed from JUnit XML, not from stdout string matching
