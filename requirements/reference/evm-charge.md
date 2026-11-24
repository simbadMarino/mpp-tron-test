# Requirements: EVM charge method (spec-derived baseline)

Baseline: `draft-evm-charge-00` (2 Nov 2026, expires 6 May 2027).
Base scheme requirements: see `base-httpauth-payment.md` (BASE-xxx).
Not yet extracted: `draft-payment-intent-charge` (charge intent) -> `CHG-xxx`.

Field guide
- Level: MUST / SHOULD as in the spec (RFC 2119)
- Layer: V = framing vector, M = method-level, E = end-to-end testnet
- TRON: same = applies as written, adapt = needs adaptation, review = unsure if TRON supports it
- Status: open | n/a (give reason) -- n/a requirements are excluded from coverage gaps

Rules: IDs are permanent. Never renumber or reuse; mark deprecated instead.
Parser contract: each requirement starts with `## <ID> <title>` and uses `- Key: value` lines.

## EVM-001 JCS serialization of request
- Spec: §4
- Level: MUST
- Layer: V
- TRON: same
- Status: open
- Text: The request JSON is serialized with JCS (RFC 8785) before base64url encoding.

## EVM-002 Required shared fields
- Spec: §4.1
- Level: MUST
- Layer: V/M
- TRON: same
- Status: open
- Text: amount (integer string in base units), currency and recipient are present in the request.

## EVM-003 Address format and comparison
- Spec: §4.1
- Level: MUST/SHOULD
- Layer: M
- TRON: adapt
- Status: open
- Text: Addresses are 0x-prefixed 20-byte hex; EIP-55 casing preferred; comparison is by decoded bytes, not string form. TRON: Base58 T-addresses need a mapping decision.

## EVM-004 Required methodDetails
- Spec: §4.2
- Level: MUST
- Layer: V/M
- TRON: review
- Status: open
- Text: methodDetails.chainId and permit2Address are present.

## EVM-005 Client rejects unsupported chainId
- Spec: §4.2.1
- Level: MUST
- Layer: M
- TRON: adapt
- Status: open
- Text: Clients reject challenges whose chainId they do not support.

## EVM-006 Default accepted credential types
- Spec: §4.2.2
- Level: MUST/SHOULD
- Layer: M
- TRON: adapt
- Status: open
- Text: If credentialTypes is omitted, servers accept transaction (MUST) and hash (SHOULD).

## EVM-007 authorization only for EIP-3009 tokens
- Spec: §4.2.2
- Level: MUST
- Layer: M
- TRON: review
- Status: open
- Text: Servers list authorization only when the currency token is known to implement EIP-3009.

## EVM-008 Credential type preference order
- Spec: §4.2.2
- Level: SHOULD
- Layer: M
- TRON: review
- Status: open
- Text: Permit2-supporting servers list permit2 first; clients use the first listed type they support.

## EVM-009 Splits require permit2
- Spec: §4.2.3, 5.3.2, 5.4, 5.5, 6
- Level: MUST
- Layer: M/E
- TRON: review
- Status: open
- Text: Servers reject split challenges fulfilled with transaction, authorization or hash credentials.

## EVM-010 Splits sum strictly below amount
- Spec: §4.2.3
- Level: MUST
- Layer: M
- TRON: same
- Status: open
- Text: Sum of splits[].amount is strictly less than amount; clients reject violations.

## EVM-011 Splits count and memo limits
- Spec: §4.2.3
- Level: MUST/SHOULD
- Layer: M
- TRON: same
- Status: open
- Text: If present, splits has at least 1 entry; servers limit to 10; memo is at most 256 chars.

## EVM-012 Splits share one currency
- Spec: §4.2.3
- Level: MUST
- Layer: M
- TRON: same
- Status: open
- Text: All transfers (primary and splits) use the same currency token.

## EVM-013 Transfer ordering and primary remainder
- Spec: §4.2.3
- Level: MUST
- Layer: M
- TRON: same
- Status: open
- Text: Primary recipient gets amount minus splits; transferDetails[0] is primary and [i+1] is splits[i]; clients emit this order; servers verify it.

## EVM-014 Credential structure and source
- Spec: §5.1
- Level: MUST/SHOULD
- Layer: V
- TRON: adapt
- Status: open
- Text: Credential has an echoed challenge and a payload; source is optional and, if used, is a did:pkh DID with the challenge chain ID.

## EVM-015 Permit2 payload fields
- Spec: §5.2
- Level: MUST
- Layer: V/M
- TRON: review
- Status: open
- Text: permit2 payload has type, permit, transferDetails, witness and signature.

## EVM-016 permitted/transferDetails shape
- Spec: §5.2.1, 5.2.2
- Level: MUST
- Layer: M
- TRON: review
- Status: open
- Text: permitted is always an array (length 1 for single transfers); transferDetails has the same length.

## EVM-017 Witness externalId handling
- Spec: §5.2.3
- Level: MUST
- Layer: M
- TRON: review
- Status: open
- Text: Witness includes externalId when present in the request and empty string when absent; server verifies the witness before submitting.

## EVM-018 challengeHash and witness type string
- Spec: §5.2.3
- Level: MUST
- Layer: M
- TRON: review
- Status: open
- Text: challengeHash = keccak256(packed(challenge.id, challenge.realm)); the exact EIP-712 type string from the spec is used. NOTE: type string looked garbled in the text rendering; verify against canonical source.

## EVM-019 Single vs batch Permit2 call
- Spec: §5.2.4
- Level: MUST (implied)
- Layer: E
- TRON: review
- Status: open
- Text: Single transfers use permitWitnessTransferFrom, batches use permitBatchWitnessTransferFrom; a batch reverts as a whole on any failure.

## EVM-020 Server pays gas for off-chain types
- Spec: §5.6
- Level: MUST
- Layer: E
- TRON: adapt
- Status: open
- Text: For permit2 and authorization the server pays gas and maintains sufficient native balance. TRON: energy and bandwidth model.

## EVM-021 Authorization payload fields and matching
- Spec: §5.3
- Level: MUST
- Layer: M
- TRON: review
- Status: open
- Text: authorization payload fields are present; to matches challenge recipient; value matches challenge amount.

## EVM-022 EIP-3009 nonce equals challengeHash
- Spec: §5.3.1
- Level: MUST
- Layer: M
- TRON: review
- Status: open
- Text: The EIP-3009 nonce is set to challengeHash.

## EVM-023 validBefore tied to expires
- Spec: §5.3.2
- Level: SHOULD
- Layer: M
- TRON: review
- Status: open
- Text: validBefore corresponds to the challenge expires timestamp.

## EVM-024 Transaction payload
- Spec: §5.4
- Level: MUST
- Layer: M/E
- TRON: adapt
- Status: open
- Text: transaction payload is an RLP-encoded EIP-1559 tx calling transfer(address,uint256) on currency; client signs a fully valid tx and pays gas. TRON: protobuf transactions, not RLP.

## EVM-025 Hash payload
- Spec: §5.5
- Level: MUST
- Layer: M
- TRON: same
- Status: open
- Text: hash payload carries a 32-byte tx hash; client pays gas; server cannot modify or retry.

## EVM-026 Common verification steps
- Spec: §6
- Level: MUST
- Layer: M
- TRON: same
- Status: open
- Text: Decode credential; payload.type is valid; stored challenge is found by id (reject if none); all echoed challenge fields exactly match the stored challenge.

## EVM-027 Permit2 pre-submit verification
- Spec: §6.1
- Level: MUST
- Layer: M
- TRON: review
- Status: open
- Text: Signature recovers to source, deadline not passed, balance and allowance sufficient, witness matches, array lengths equal, token matches currency, primary and split to/amount match.

## EVM-028 Permit2 post-submit verification
- Spec: §6.1
- Level: MUST/SHOULD
- Layer: E
- TRON: adapt
- Status: open
- Text: After submitting, check receipt success and that Transfer logs match all expected transfers; simulate via eth_call first (SHOULD).

## EVM-029 Authorization verification and submit
- Spec: §6.2
- Level: MUST
- Layer: M/E
- TRON: review
- Status: open
- Text: Token supports EIP-3009, signature, to, value, nonce, validBefore, balance checks; then submit and verify receipt success and Transfer log.

## EVM-030 Transaction verification and broadcast
- Spec: §6.3
- Level: MUST
- Layer: M/E
- TRON: adapt
- Status: open
- Text: chainId, to = token, selector 0xa9059cbb, decoded recipient/amount match; then broadcast, wait, status success, Transfer log matches.

## EVM-031 Hash verification
- Spec: §6.4
- Level: MUST
- Layer: M/E
- TRON: same
- Status: open
- Text: Hash not already consumed; receipt fetched; success status; Transfer log with matching address, to and value; then mark consumed.

## EVM-032 Confirmation before receipt
- Spec: §7.5
- Level: MUST
- Layer: E
- TRON: review
- Status: open
- Text: Server waits for a successful receipt (at least 1 block) before returning Payment-Receipt; deeper confirmation is server policy. TRON: decide solidified vs confirmed.

## EVM-033 Receipt content
- Spec: §7.6
- Level: MUST
- Layer: V/M
- TRON: adapt
- Status: open
- Text: Receipt has method=evm, challengeId, reference (tx hash), status=success, RFC 3339 timestamp, chainId; externalId optional echo.

## EVM-034 No receipt on errors
- Spec: §7.6
- Level: MUST
- Layer: M/E
- TRON: same
- Status: open
- Text: Payment-Receipt header is not included on error responses.

## EVM-035 Replay protection
- Spec: §8
- Level: MUST
- Layer: M/E
- TRON: same
- Status: open
- Text: Server keeps a consumed-replay set with a per-type token, checks it before accepting, and atomically marks it consumed after verification.

## EVM-036 Error responses
- Spec: §9
- Level: MUST/SHOULD
- Layer: M/E
- TRON: same
- Status: open
- Text: Rejections return 402 with a fresh challenge using standard problem types (malformed-credential, invalid-challenge, verification-failed); problem+json body recommended.

## EVM-037 Transport security
- Spec: §10.1
- Level: MUST
- Layer: E
- TRON: same
- Status: open
- Text: TLS 1.2 or higher; credentials only over HTTPS.

## EVM-038 Client pre-sign validation
- Spec: §10.3
- Level: MUST
- Layer: M
- TRON: same
- Status: open
- Text: Clients check amount, currency, recipient, chainId and splits before signing.

## EVM-039 Permit2 nonce and address handling
- Spec: §10.5
- Level: MUST/SHOULD
- Layer: M
- TRON: review
- Status: open
- Text: Servers handle Permit2 nonce conflicts gracefully; clients verify the Permit2 address is the canonical deployment.

## EVM-040 Fee payer balance monitoring
- Spec: §10.6
- Level: MUST
- Layer: E
- TRON: adapt
- Status: open
- Text: Server monitors native balance and rejects new requests when it cannot cover gas.

## EVM-041 Fee payer DoS mitigations
- Spec: §10.6
- Level: SHOULD
- Layer: E
- TRON: same
- Status: open
- Text: Simulate before broadcast, rate limit per client, check client token balance.

## EVM-042 Split transparency to user
- Spec: §10.7
- Level: SHOULD
- Layer: E
- TRON: same
- Status: open
- Text: Clients present each split recipient and amount to the user.

