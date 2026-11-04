# MPP TRON Method
## SW System Requirements & SW System Test Spec (SSTS)

### Repo Layout
- `requirements/base-httpauth-payment.md`  BASE-001..060 from draft-httpauth-payment-01 (chain-agnostic core scheme, used as reference only)
- `requirements/evm-charge.md`             EVM-001..042 from draft-evm-charge-00 (Used as reference only)
- `requirements/`                          collection of tron mpp requirements (SW System, evm reference and base reference)
- `tests/`                                 test cases: markdown (`## TC-nnn`) or code comments containing `Covers: SSR-012`
- `tests/_template.md`                     template for new test cases
- `tools/trace.py`                         coverage check and matrix generator
- `traceability.md`                        auto-generated traceability matrix; do not edit

### Workflow
1. Write or update requirements (SSR); never renumber IDs.
    1.1 Mark a requirement not applicable with `- Status: n/a (reason)`; it leaves the coverage count but stays in the matrix.
    1.2 Mark a requirement "doc", meaning its covered by at least 1 TC.
2. Add test cases that name their requirements in a `Covers:` line.
3. `python tools/trace.py --write` (add `--strict` in CI to fail on gaps). # Not ready



Pin the draft versions in each requirements file header and update them deliberately.
