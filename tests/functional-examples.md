# Example test cases (replace or delete)

## TC-001 Replay of a consumed credential is rejected
Covers: EVM-035, EVM-036, BASE-003, BASE-050
Layer: system
Status: draft
Env: Nile testnet

**Preconditions**
- Server running with funded fee payer; client holds test token balance

**Steps**
1. Request a paid resource and complete payment with a valid credential (200 + receipt).
2. Submit the identical credential again.

**Expected result**
- Second request returns 402 with a fresh challenge and a problem+json body; no Payment-Receipt header.

## TC-002 Splits rejected for non-permit2 credential types
Covers: EVM-009, EVM-036
Layer: method
Status: draft
Env: local compliance server

**Steps**
1. Issue a challenge containing splits.
2. Respond with a transaction credential, then an authorization credential, then a hash credential.

**Expected result**
- Each attempt is rejected with 402 and verification-failed.
