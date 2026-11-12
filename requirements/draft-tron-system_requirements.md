# TRON MPP System Requirements Specification (SyRS)

System requirements (SYS-xxx) for the "tron" payment method, charge and session intents.

Scope: the "charge" and "session" intents of the "tron" payment method, implemented as a TRON MPP first-party SDK
(https://mpp.dev/payment-methods/custom#first-party-sdk). TRC-20 only; native TRX and TRC-10 are out of scope.
Charge = one-time transfer per request. Session = escrow payment channel with off-chain cumulative vouchers.

Baseline
- base   = `draft-httpauth-payment-01` (9 Sep 2026, expires 13 Mar 2027) -> `base-httpauth-payment.md` (BASE-xxx)
- charge = `draft-evm-charge-00` (2 Nov 2026, expires 6 May 2027) -> `evm-charge.md` (EVM-xxx); section numbers are the
  same in the working copy `draft-tron-charge.txt`
- session = `draft-evm-session-00` (11 Nov 2026, expires 15 May 2027) -> `evm-session.md` (SES-xxx)
- sdk    = mpp.dev "Custom payment methods" page, First-party SDK section and Gotchas (read 12 Nov 2026)

Merge rule: the charge and session drafts win where they are specific; the base draft fills every gap. Each
BASE/EVM/SES requirement is carried by exactly one SYS requirement (see the source map at the end), so SYS is the only ID set
tests need to cover. A requirement that both intents share is written once, in the charge or common block.

Intent applicability
- Both intents: SYS-0xx (SDK), SYS-1xx (request flow), SYS-203 (addresses), SYS-301..305 (credential framing and
  client validation), SYS-503..507 and SYS-513 (on-chain result, broadcast, confirmation, node trust), SYS-602,
  SYS-701..705 (errors), SYS-8xx (security)
- Charge only: the rest of SYS-2xx..SYS-5xx, SYS-601, SYS-710..713
- Session only: SYS-10xx..SYS-18xx

System boundary
- The system: the TRON MPP first-party SDK (shared method definitions, SDK client, SDK server, wired into `mppx`) and,
  for the session intent, the channel escrow contract. The contract is a deliverable next to the SDK package.
- External to the system: the TRON network and its nodes, the TRC-20 token contracts, Permit2, and the applications
  that embed the SDK client or the SDK server. The system interacts with them; it does not specify them.
- The requirements describe behavior observable at that boundary (HTTP messages, signed data, transactions and
  on-chain state), not the internal design of the software.

Verification levels (test levels per ISTQB / ISO/IEC/IEEE 29119). A requirement has one ID and may be verified at more
than one level.
- ST = System test: the SDK client and SDK server as a whole, with the TRON network simulated by a mock or stub node.
  Covers framing, schemas, verification logic and HTTP behavior.
- SIT = System integration test (end-to-end): the system together with a live TRON network (Nile testnet by default,
  chain ID 3448148188) and a TRC-20 test token. Covers everything that needs real blocks, resources
  (Energy/Bandwidth) and node responses. For session this includes the deployed channel escrow contract.
- CT = Component test: the channel escrow contract by itself, called directly on a TRON network or local TVM without
  the SDK. Session only.

Field guide
- Spec: section in base / charge / sdk (see Baseline). "project" = no spec clause; decided for this SDK.
- Level: MUST / SHOULD / MAY as in the spec (RFC 2119). Combined values mean the clause has several parts.
  "(project)" marks a level assigned by this project because the source is not normative.
- Role: Client (SDK client), Server (SDK server), Both, SDK (package as a whole), Contract (channel escrow contract)
- Verification: verification level(s), ST / SIT / CT as defined above; ST/SIT = both
- Source: BASE/EVM/SES requirements merged into this one; "-" = TRON- or SDK-specific, no upstream requirement
- TRON: same = upstream text applies as written, adapt = adapted to TRON, review = open design decision (see Note and
  the open decisions table), new = added for TRON or the SDK
- Status: open | n/a (give reason) | doc (covered by at least one test case)
- Note: TRON adaptation detail or open question (optional)

Rules: IDs are permanent; never renumber or reuse; mark deprecated instead. IDs are grouped in blocks of 100 per
section so new requirements can be added next to related ones.
Parser contract: each requirement starts with `## <ID> <title>` and uses `- Key: value` lines.

Sections
1. SDK packaging and configuration (SYS-0xx)
2. Request flow (SYS-1xx)
3. Charge request schema (SYS-2xx)
4. Credential schema and client behavior (SYS-3xx)
5. Server verification (SYS-4xx)
6. Charge flows: settlement on the TRON network (SYS-5xx)
7. Receipt (SYS-6xx)
8. Errors and replay protection (SYS-7xx)
9. Security and operations (SYS-8xx)
10. Session: SDK configuration and request schema (SYS-10xx)
11. Session: channel escrow contract (SYS-11xx)
12. Session: credential actions and client behavior (SYS-12xx, SYS-13xx)
13. Session: server verification (SYS-14xx)
14. Session flows: channel lifecycle on the TRON network (SYS-15xx)
15. Session: accounting, streaming and receipt (SYS-16xx)
16. Session: errors (SYS-17xx)
17. Session: security (SYS-18xx)
18. Open decisions
19. Source map


# 1. SDK packaging and configuration

## SYS-001 Package entry points
- Spec: sdk (Exports map)
- Level: MUST (project)
- Role: SDK
- Verification: ST
- Source: -
- TRON: new
- Status: open
- Text: The package is an ES module with `sideEffects: false` and exposes three entry points: `.` (shared schemas), `./client` and `./server`, each with types.

## SYS-002 mppx peer dependency and re-exports
- Spec: sdk (Exports map, Re-exports)
- Level: MUST (project)
- Role: SDK
- Verification: ST
- Source: -
- TRON: new
- Status: open
- Text: `mppx` is a peer dependency (single shared instance); `./server` re-exports `Mppx`, `Expires` and `Store`, `./client` re-exports `Mppx`, so one import gives the user both `Mppx` and the `charge` factory.

## SYS-003 Shared method definition
- Spec: sdk (Shared method definition)
- Level: MUST (project)
- Role: SDK
- Verification: ST
- Source: -
- TRON: new
- Status: open
- Text: One `Method.from` definition (name, intent, request schema, credential payload schema) is the single source for both client and server; neither side redefines the schemas.

## SYS-004 Method identifier is "tron"
- Spec: base §5.1.1, 6.1; charge §11.1
- Level: MUST
- Role: Both
- Verification: ST
- Source: BASE-014
- TRON: adapt
- Status: open
- Text: The method identifier is the lowercase ASCII string `tron` (1*LOWERALPHA, case-sensitive) in challenges, credentials and receipts; other casings are not accepted as this method.

## SYS-005 Intent is "charge" or "session"
- Spec: base §5.1.1, 7.1; charge §11.2
- Level: MUST
- Role: Both
- Verification: ST
- Source: BASE-015
- TRON: same
- Status: open
- Text: The intent parameter is a registered value, `charge` or `session` (syntax 1*(ALPHA/DIGIT/-)); the SDK issues and accepts only intents it implements and has configured.

## SYS-006 Server factory configuration
- Spec: project
- Level: MUST (project)
- Role: Server
- Verification: ST
- Source: -
- TRON: new
- Status: open
- Text: The server `charge(...)` factory takes recipient, currency, chainId, TRON node endpoint, accepted credential types, confirmation policy and (for server-paid types) a fee payer signer; invalid or inconsistent configuration fails at creation, not on the first request.

## SYS-007 Client factory configuration
- Spec: project
- Level: MUST (project)
- Role: Client
- Verification: ST
- Source: -
- TRON: new
- Status: open
- Text: The client `charge(...)` factory takes a signer abstraction (raw key or wallet adapter), the chain IDs it supports, a TRON node endpoint where the credential type needs one, and a payment policy (see SYS-304).

## SYS-008 Supported networks and endpoint consistency
- Spec: charge §4.2.1; project
- Level: MUST (project)
- Role: Both
- Verification: ST/SIT
- Source: -
- TRON: new
- Status: open
- Text: The SDK supports TRON mainnet (728126428), Nile (3448148188) and Shasta (2494104990); the configured node endpoint must report the configured chainId, otherwise the server refuses to start issuing challenges.

## SYS-009 Exact amount arithmetic
- Spec: sdk (Gotchas); charge §4.1
- Level: MUST (project)
- Role: Both
- Verification: ST
- Source: -
- TRON: new
- Status: open
- Text: Amounts are handled as arbitrary-precision integers in base units; any conversion from human-readable units uses the token decimals with exact arithmetic, never floating point.

## SYS-010 No secrets in challenge fields
- Spec: sdk (Gotchas)
- Level: MUST (project)
- Role: Server
- Verification: ST
- Source: -
- TRON: new
- Status: open
- Text: Private keys, node API keys and the challenge-binding secret never appear in request, opaque or any other challenge field.

## SYS-011 Request construction is deterministic
- Spec: sdk (Gotchas)
- Level: MUST (project)
- Role: Server
- Verification: ST
- Source: -
- TRON: new
- Status: open
- Text: Any request hook is idempotent: it runs on the initial 402 and again on credential submission and must not create duplicate orders or produce a different request for the same input.

## SYS-012 verify fails closed
- Spec: sdk (Gotchas)
- Level: MUST (project)
- Role: Server
- Verification: ST
- Source: -
- TRON: new
- Status: open
- Text: The server verify step returns a success receipt only after every check and the settlement succeeded; any failed, skipped or errored check (including node errors) throws and no resource is delivered.

## SYS-013 Client cleanup
- Spec: sdk (Advanced SDK patterns)
- Level: SHOULD (project)
- Role: Client
- Verification: ST
- Source: -
- TRON: new
- Status: open
- Text: If the client opens connections or listeners (for example node subscriptions), the method exposes `cleanup()` that releases them.


# 2. Request flow

Applies to every credential type. The TRON network is an external entity, not part of the SDK server: the SDK
client and the SDK server each reach it through their own configured node endpoint. At system test level it is replaced
by a stub node; at system integration (end-to-end) level it is the live network. Which side talks to it in steps (3) and (5) depends on
the credential type and is expanded in section 6.

```
   SDK Client                    SDK Server                  TRON network
      |                              |                             |
      |  (1) GET /resource           |                             |
      |----------------------------->|                             |
      |                              |                             |
      |  (2) 402 Payment Required    |                             |
      |      WWW-Authenticate:       |                             |
      |        Payment id="..",      |                             |
      |        realm="..",           |                             |
      |        method="tron",        |                             |
      |        intent="charge",      |                             |
      |        request="..",         |                             |
      |        expires=".."          |                             |
      |      Cache-Control: no-store |                             |
      |<-----------------------------|                             |
      |                              |                             |
      |  (3) Validate challenge, then fulfil it:                   |
      |      transaction: read reference block, sign               |
      |      hash:        sign, broadcast, wait for inclusion      |
      |      permit2 / authorization: sign only, no chain access   |
      |<---------------------------------------------------------->|
      |                              |                             |
      |  (4) GET /resource           |                             |
      |      Authorization:          |                             |
      |        Payment <credential>  |                             |
      |----------------------------->|                             |
      |                              |  (5a) verify binding and    |
      |                              |       payload               |
      |                              |  (5b) settle: broadcast or  |
      |                              |       submit (not for hash) |
      |                              |---------------------------->|
      |                              |  (5c) transaction info:     |
      |                              |       result, Transfer      |
      |                              |       event, confirmation   |
      |                              |<----------------------------|
      |                              |                             |
      |  (6) 200 OK                  |                             |
      |      Payment-Receipt: <..>   |                             |
      |      Cache-Control: private  |                             |
      |<-----------------------------|                             |
```

| Step | Requirements |
|---|---|
| (1)-(2) challenge issuance | SYS-101..SYS-115, SYS-119..SYS-125, SYS-201..SYS-214 |
| (3) client fulfilment | SYS-304, SYS-305, SYS-310..SYS-330 |
| (4) credential transport | SYS-116..SYS-118, SYS-301..SYS-303 |
| (5) verification and settlement | SYS-401..SYS-405, SYS-501..SYS-513, SYS-710..SYS-713 |
| (6) success response | SYS-601, SYS-124 |
| any rejection | SYS-602, SYS-701..SYS-705 |

## SYS-101 Unpaid request -> 402 with fresh challenge
- Spec: base §4.2, 4.4.2
- Level: MUST
- Role: Server
- Verification: ST/SIT
- Source: BASE-001, BASE-008
- TRON: same
- Status: open
- Text: A request for a paid resource without a credential gets 402 with a WWW-Authenticate header carrying at least one fresh Payment challenge (method=tron, intent=charge or session); 402 is never returned without one.

## SYS-102 When to return 402 (and when not)
- Spec: base §4.4.1, 4.4.2
- Level: SHOULD
- Role: Server
- Verification: ST
- Source: BASE-009
- TRON: same
- Status: open
- Text: 402 is returned when payment is the primary barrier and a challenge can be built; not for missing authentication (401), missing authorization (403), nonexistent resources (404) or when no challenge can be constructed.

## SYS-103 Authenticate before challenging for payment
- Spec: base §4.4.3
- Level: SHOULD
- Role: Server
- Verification: ST
- Source: BASE-010
- TRON: same
- Status: open
- Text: When both authentication and payment are required: authentication is verified first, failure returns 401, and the 402 Payment challenge is issued only after authentication succeeds.

## SYS-104 Challenge syntax and required parameters
- Spec: base §5.1, 5.1.1, App. A
- Level: MUST
- Role: Both
- Verification: ST
- Source: BASE-011, BASE-012, BASE-013
- TRON: same
- Status: open
- Text: The challenge is the scheme Payment followed by auth-params per the Appendix A ABNF, with non-empty id, realm, method, intent and request; the server never emits and the client rejects a missing or empty id.

## SYS-105 request parameter encoding
- Spec: base §5.1.1; charge §4
- Level: MUST
- Role: Both
- Verification: ST
- Source: BASE-016, EVM-001, SES-040
- TRON: same
- Status: open
- Text: request is the charge request JSON (RFC 8259) serialized with JCS (RFC 8785) and encoded as base64url (RFC 4648) without '=' padding.

## SYS-106 expires parameter
- Spec: base §5.1.2
- Level: SHOULD/MUST
- Role: Both
- Verification: ST
- Source: BASE-018
- TRON: same
- Status: open
- Text: The server includes expires as an RFC 3339 date-time (SHOULD); the client never submits a credential for an expired challenge (MUST).

## SYS-107 digest parameter and verification
- Spec: base §5.1.2, 5.1.3
- Level: SHOULD/MUST
- Role: Both
- Verification: ST
- Source: BASE-017, BASE-028
- TRON: same
- Status: open
- Text: For requests with a body the server includes digest (RFC 9530 format) (SHOULD); the client then resubmits a body matching it, and the server recomputes the digest of the credentialed request body and rejects on mismatch (MUST).

## SYS-108 opaque parameter
- Spec: base §5.1.2
- Level: MUST
- Role: Both
- Verification: ST
- Source: BASE-023
- TRON: same
- Status: open
- Text: opaque, when used, is base64url JCS JSON forming a flat string-to-string map; the client returns it unchanged and the server includes it in the challenge binding.

## SYS-109 description is display-only
- Spec: base §5.1.2, 11.6
- Level: MUST
- Role: Both
- Verification: ST
- Source: BASE-019
- TRON: same
- Status: open
- Text: description (challenge parameter and request field) is never used for payment verification and is excluded from the binding.

## SYS-110 Unknown parameters and versioning
- Spec: base §5.1.2, 9.2, 9.3
- Level: MUST/MAY
- Role: Both
- Verification: ST
- Source: BASE-024, BASE-044
- TRON: same
- Status: open
- Text: Clients ignore unknown challenge parameters and unknown fields; custom parameters use lowercase names; there is no wire version, and an optional methodDetails version means 1 when absent.

## SYS-111 Challenge binding coverage
- Spec: base §5.1.2.1, 5.1.2.1.1
- Level: MUST/SHOULD
- Role: Server
- Verification: ST
- Source: BASE-025, BASE-027
- TRON: same
- Status: open
- Text: id is bound to realm, method, intent and request, plus expires, digest, opaque and header when present (MUST); if HMAC-SHA256 is used it follows the positional layout: seven '|'-joined slots with empty strings for absent optionals, an eighth header slot only when present, base64url without padding (SHOULD).

## SYS-112 Challenge binding verification
- Spec: base §5.1.2.1; charge §6 steps 3-4
- Level: MUST
- Role: Server
- Verification: ST
- Source: BASE-026
- TRON: same
- Status: open
- Text: On every credential the server verifies the binding and rejects credentials whose echoed challenge parameters differ in any field from the challenge it issued.

## SYS-113 Multiple challenges
- Spec: base §7.3, B.4
- Level: MAY/SHOULD
- Role: Both
- Verification: ST
- Source: BASE-035
- TRON: same
- Status: open
- Text: The tron challenge can be issued next to challenges of other methods or intents; the client picks one and treats unrecognized methods and intents as unsupported.

## SYS-114 Accept-Payment request header
- Spec: base §7.4, App. A
- Level: MAY
- Role: Client
- Verification: ST
- Source: BASE-036
- TRON: same
- Status: open
- Text: The client may send Accept-Payment listing method/intent ranges (for example `tron/charge`) with wildcards and optional q weights (default q=1, q=0 means do not use).

## SYS-115 Accept-Payment server behavior
- Spec: base §7.4
- Level: SHOULD/MUST/MAY
- Role: Server
- Verification: ST
- Source: BASE-037, BASE-038
- TRON: same
- Status: open
- Text: With Accept-Payment the server filters to challenges matching a range with q>0, orders by descending q, keeps server order for ties and prefers the most specific range (SHOULD); absent header means anything is accepted (MUST); a malformed or unmatched header may be ignored (MAY).

## SYS-116 Client credential field selection
- Spec: base §5.1.2, 5.2
- Level: MUST
- Role: Client
- Verification: ST
- Source: BASE-020
- TRON: same
- Status: open
- Text: Without a header parameter the client sends the credential in Authorization; with header=Payment-Authorization it uses that field only; any other header value makes the challenge unrecognized and no credential is sent.

## SYS-117 Server accepts credential only from the selected field
- Spec: base §5.1.2, 5.2
- Level: MUST
- Role: Server
- Verification: ST
- Source: BASE-021, BASE-022
- TRON: same
- Status: open
- Text: The server emits no header value other than Payment-Authorization, and a credential arriving in a field other than the one the challenge selected does not satisfy the challenge.

## SYS-118 Single credential per request
- Spec: base §B.4
- Level: MUST/SHOULD
- Role: Both
- Verification: ST
- Source: BASE-060
- TRON: same
- Status: open
- Text: The client sends exactly one Payment credential per request (MUST); the server rejects requests carrying several Payment credentials with 400 (SHOULD).

## SYS-119 Size limits
- Spec: base §9.4
- Level: SHOULD/MUST
- Role: Both
- Verification: ST
- Source: BASE-045
- TRON: same
- Status: open
- Text: The server keeps challenges under 8KB (SHOULD); the client handles challenges of at least 4KB and the server handles credentials of at least 4KB (MUST), including a hex-encoded signed TRON transaction.

## SYS-120 No side effects for unpaid requests
- Spec: base §11.4
- Level: MUST
- Role: Server
- Verification: ST/SIT
- Source: BASE-051
- TRON: same
- Status: open
- Text: A request that ends in 402 changes no server state beyond recording the challenge, runs no application handler and causes no transaction to be broadcast to the TRON network.

## SYS-121 Idempotency-Key support
- Spec: base §11.4
- Level: SHOULD
- Role: Server
- Verification: ST/SIT
- Source: BASE-052, SES-120
- TRON: same
- Status: open
- Text: Clients include Idempotency-Key on paid requests (SHOULD, session); for POST/PUT/DELETE the server accepts Idempotency-Key; a retry with the same key and a valid credential returns the original response without re-executing the handler or settling again.

## SYS-122 Valid payment but policy denial -> 403
- Spec: base §4.2, 4.3
- Level: MUST
- Role: Server
- Verification: ST
- Source: BASE-006
- TRON: same
- Status: open
- Text: When payment verifies but policy denies access the response is 403 without a challenge; 401 stays reserved for authentication failures unrelated to payment.

## SYS-123 Character encoding and locale
- Spec: base §10
- Level: SHOULD
- Role: Both
- Verification: ST
- Source: BASE-046
- TRON: same
- Status: open
- Text: Strings are UTF-8; realm is ASCII; description follows Accept-Language.

## SYS-124 Caching headers
- Spec: base §11.10
- Level: MUST
- Role: Server
- Verification: ST
- Source: BASE-057
- TRON: same
- Status: open
- Text: 402 responses carry Cache-Control: no-store; responses with Payment-Receipt carry Cache-Control: private; when the credential travels in a non-Authorization field every response carries private or no-store.

## SYS-125 Retry-After
- Spec: base §8.3
- Level: SHOULD
- Role: Server
- Verification: ST
- Source: BASE-042
- TRON: same
- Status: open
- Text: The server uses Retry-After to tell clients when a retry makes sense (for example while rate limited or while the fee payer is out of resources).

## SYS-126 Request flow completes through the SDK
- Spec: base §3; sdk
- Level: MUST (project)
- Role: Both
- Verification: SIT
- Source: -
- TRON: new
- Status: open
- Text: With SDK client and SDK server wired into `mppx`, a single application-level request runs steps (1)-(6) without manual intervention: the client receives the 402, fulfils it, retries once, and gets 200 with a Payment-Receipt; the resource handler executes exactly once and exactly one TRC-20 payment is settled on the TRON network.


# 3. Charge request schema

Decoded `request` for the tron method (addresses per SYS-203):

```json
{
  "amount": "1000000",
  "currency": "T...(TRC-20 contract)",
  "recipient": "T...(payee)",
  "externalId": "order-123",
  "methodDetails": {
    "chainId": 3448148188,
    "credentialTypes": ["transaction", "hash"]
  }
}
```

## SYS-201 Shared request fields
- Spec: charge §4.1
- Level: MUST
- Role: Both
- Verification: ST
- Source: EVM-002
- TRON: same
- Status: open
- Text: amount (non-negative integer string in base units, no sign, decimals or exponent), currency and recipient are present; description and externalId are optional strings; the client rejects requests that violate this.

## SYS-202 TRC-20 only
- Spec: charge Abstract, §1
- Level: MUST
- Role: Both
- Verification: ST/SIT
- Source: -
- TRON: new
- Status: open
- Text: currency is the address of a TRC-20 contract; native TRX and TRC-10 assets cannot be configured or charged, and the server verifies at startup that currency is a deployed contract on the configured network (SHOULD).

## SYS-203 Address format and comparison
- Spec: charge §4.1
- Level: MUST/SHOULD
- Role: Both
- Verification: ST
- Source: EVM-003, SES-006
- TRON: review
- Status: open
- Text: Addresses in currency, recipient and splits[].recipient are TRON Base58Check addresses (34 characters, 0x41 version byte); the checksum is validated and invalid addresses are rejected; comparison is always by the decoded 20-byte value, never by string form.
- Note: Decision D1 -- the EVM draft uses 0x 20-byte hex. Base58Check is proposed for the wire; the SDK may accept 41-prefixed hex in configuration and normalize. Inside TIP-712 typed data and ABI calldata the 20-byte form is used.

## SYS-204 methodDetails and chainId
- Spec: charge §4.2, 4.2.1; sdk (Gotchas)
- Level: MUST
- Role: Both
- Verification: ST
- Source: EVM-004
- TRON: review
- Status: open
- Text: All TRON-specific fields are nested under methodDetails; methodDetails.chainId is a required number identifying the TRON network; permit2Address is present whenever permit2 is an accepted credential type.
- Note: Decision D2 -- the EVM draft makes permit2Address always required with a canonical default; TRON has no canonical Permit2 address, so it is proposed as required only when permit2 is offered.

## SYS-205 Client rejects unsupported chainId
- Spec: charge §4.2.1
- Level: MUST
- Role: Client
- Verification: ST
- Source: EVM-005
- TRON: same
- Status: open
- Text: The client rejects, without signing or broadcasting anything, a challenge whose chainId is not one it is configured for.

## SYS-206 Default accepted credential types
- Spec: charge §4.2.2
- Level: MUST/SHOULD
- Role: Server
- Verification: ST
- Source: EVM-006
- TRON: same
- Status: open
- Text: credentialTypes values are limited to permit2, authorization, transaction and hash; if the field is omitted the server accepts transaction (MUST) and hash (SHOULD); a credential of a type not accepted for the challenge is rejected.

## SYS-207 Credential type preference order
- Spec: charge §4.2.2
- Level: SHOULD
- Role: Both
- Verification: ST
- Source: EVM-008
- TRON: review
- Status: open
- Text: A server that supports permit2 lists it first; the client uses the first listed type it supports.
- Note: Depends on decision D3 (Permit2 on TRON).

## SYS-208 authorization only for supporting tokens
- Spec: charge §4.2.2, 5.3.2
- Level: MUST
- Role: Server
- Verification: ST
- Source: EVM-007
- TRON: review
- Status: open
- Text: The server lists authorization only when the currency token is known to implement transferWithAuthorization (EIP-3009 semantics).
- Note: Decision D4 -- to be confirmed per target token (USDT on TRON is not known to implement it); the type may end up n/a for the first release.

## SYS-209 decimals is a display aid
- Spec: charge §4.2
- Level: MAY/MUST (project)
- Role: Both
- Verification: ST
- Source: -
- TRON: new
- Status: open
- Text: methodDetails.decimals is optional; when present it is used only for display and never changes the base-unit amount that is signed or verified.

## SYS-210 Splits sum strictly below amount
- Spec: charge §4.2.3
- Level: MUST
- Role: Both
- Verification: ST
- Source: EVM-010
- TRON: same
- Status: open
- Text: The sum of splits[].amount is strictly less than amount; the server never issues and the client rejects a request that violates this.

## SYS-211 Splits count, memo and currency
- Spec: charge §4.2.3
- Level: MUST/SHOULD
- Role: Both
- Verification: ST
- Source: EVM-011, EVM-012
- TRON: same
- Status: open
- Text: If present, splits has at least 1 entry and the server limits it to 10 (SHOULD); memo is at most 256 characters; the primary transfer and all splits use the same currency token.

## SYS-212 Splits require permit2
- Spec: charge §4.2.3, 5.3.2, 5.4, 5.5, 6 step 5
- Level: MUST
- Role: Server
- Verification: ST/SIT
- Source: EVM-009
- TRON: review
- Status: open
- Text: The server rejects a challenge with splits that is fulfilled with a transaction, authorization or hash credential, and settles nothing on-chain for it.
- Note: Depends on decision D3; without Permit2 on TRON the server must not issue splits at all.

## SYS-213 Transfer ordering and primary remainder
- Spec: charge §4.2.3
- Level: MUST
- Role: Both
- Verification: ST
- Source: EVM-013
- TRON: same
- Status: open
- Text: The primary recipient receives amount minus the sum of splits; transferDetails[0] is the primary transfer and transferDetails[i+1] is splits[i]; the client emits this order and the server verifies it.

## SYS-214 Split transparency to the user
- Spec: charge §10.7
- Level: SHOULD
- Role: Client
- Verification: ST
- Source: EVM-042
- TRON: same
- Status: open
- Text: The client exposes every split recipient and amount to the confirmation hook (SYS-305) and flags a primary remainder that is small relative to the total.


# 4. Credential schema and client behavior

## SYS-301 Credential encoding and fields
- Spec: base §5.2; charge §5.1
- Level: MUST
- Role: Both
- Verification: ST
- Source: BASE-029, BASE-030, SES-064
- TRON: same
- Status: open
- Text: The credential field value is the scheme Payment, one or more spaces, then base64url (no padding) of a JSON object with challenge (required object), payload (required object) and source (optional string).

## SYS-302 Echoed challenge object
- Spec: base §5.1.1, 5.2
- Level: MUST
- Role: Client
- Verification: ST
- Source: BASE-031
- TRON: same
- Status: open
- Text: The echoed challenge carries id, realm, method, intent and request unchanged, plus description, opaque, digest, expires and header when they were present; header is not added when the challenge had none.

## SYS-303 source identifies the payer
- Spec: charge §5.1
- Level: SHOULD
- Role: Client
- Verification: ST
- Source: EVM-014, SES-066
- TRON: review
- Status: open
- Text: source, when present, is a did:pkh DID carrying the challenge chain and the payer address; for server-submitted types the recovered signer must equal the address in source.
- Note: Decision D5 -- DID form for TRON (`did:pkh:tron:<chain ref>:<Base58 address>` proposed versus the eip155 form with 20-byte hex).

## SYS-304 Client validates the challenge before paying
- Spec: base §7.4, 11.6; charge §10.3
- Level: MUST
- Role: Client
- Verification: ST
- Source: BASE-039, BASE-054, EVM-038
- TRON: same
- Status: open
- Text: Before signing or broadcasting, and regardless of any Accept-Payment sent, the client parses the request and checks amount, currency, recipient, chainId, splits and the validity window against its configured policy (maximum amount, allowed tokens and networks); a failed check produces no signature and no transaction.

## SYS-305 Origin display and user confirmation
- Spec: base §11.11
- Level: SHOULD
- Role: Client
- Verification: ST
- Source: BASE-058
- TRON: same
- Status: open
- Text: The client offers a confirmation hook that receives the requesting origin and the decoded request; payment proceeds automatically only inside the limits of an explicit policy.

## SYS-310 Transaction payload
- Spec: charge §5.4
- Level: MUST
- Role: Client
- Verification: ST/SIT
- Source: EVM-024
- TRON: adapt
- Status: open
- Text: payload is {type:"transaction", signature}; signature is the hex-encoded signed TRON transaction (protobuf raw_data plus signature) containing exactly one TriggerSmartContract with contract_address = currency, call_value 0, no TRC-10 value, and data = transfer(address,uint256) selector a9059cbb with the challenge recipient and amount; the client does not broadcast it.
- Note: Replaces RLP/EIP-1559 of the EVM draft. Field name `signature` kept for parity with the EVM draft; decision D6 covers the encoding (hex of the protobuf Transaction versus the node JSON form).

## SYS-311 Transaction validity and fees are the client's
- Spec: charge §5.4, 5.6
- Level: MUST
- Role: Client
- Verification: SIT
- Source: -
- TRON: new
- Status: open
- Text: The client signs a fully valid transaction: reference block taken from the network named by chainId, expiration in the future and not later than the challenge expires, a fee_limit that covers the transfer, and Energy/Bandwidth or TRX paid by the payer account; the server never tops it up.

## SYS-312 Hash payload
- Spec: charge §5.5
- Level: MUST
- Role: Client
- Verification: ST/SIT
- Source: EVM-025
- TRON: adapt
- Status: open
- Text: payload is {type:"hash", hash}; hash is the 32-byte transaction ID (64 hex characters) of a TRC-20 transfer the client broadcast and paid for itself; the server neither modifies nor rebroadcasts that transaction.
- Note: TRON tooling shows transaction IDs without 0x; the server accepts both forms and normalizes (see SYS-710).

## SYS-320 Permit2 payload fields and shape
- Spec: charge §5.2, 5.2.1, 5.2.2
- Level: MUST
- Role: Client
- Verification: ST
- Source: EVM-015, EVM-016
- TRON: review
- Status: open
- Text: The permit2 payload has type, permit {permitted, nonce, deadline}, transferDetails, witness and signature; permitted is always an array (length 1 for a single transfer), each token equals currency, and transferDetails has the same length.
- Note: Decision D3 -- which Permit2 deployment(s) on TRON are supported and whether TIP-712 signing matches the contract's domain separator.

## SYS-321 Permit2 witness and challengeHash
- Spec: charge §5.2.3
- Level: MUST
- Role: Both
- Verification: ST
- Source: EVM-017, EVM-018
- TRON: review
- Status: open
- Text: challengeHash = keccak256(packed(challenge.id, challenge.realm)); the witness carries challengeHash and externalId (empty string when the request has none); typed data uses the exact witness type string of the spec and is signed per TIP-712.
- Note: The type string is garbled in the text rendering of the draft; take it from the canonical source. Part of decision D3.

## SYS-330 Authorization payload
- Spec: charge §5.3, 5.3.1, 5.3.2
- Level: MUST/SHOULD
- Role: Client
- Verification: ST
- Source: EVM-021, EVM-022, EVM-023
- TRON: review
- Status: open
- Text: The authorization payload has type, from, to, value, validAfter, validBefore, nonce and signature; to equals the challenge recipient, value equals amount, nonce equals challengeHash (MUST); validBefore corresponds to the challenge expires (SHOULD).
- Note: Decision D4.


# 5. Server verification

Checks the server performs before anything is broadcast or accepted. All are verifiable at system test level with a stub node. The EVM
verification requirements (EVM-027..031) each mix pre-checks and on-chain steps; here the pre-checks are SYS-40x and
the on-chain half is the matching flow requirement in section 6, which is the one listed as carrier in the source map.

## SYS-401 Common verification steps
- Spec: charge §6 steps 1-5
- Level: MUST
- Role: Server
- Verification: ST
- Source: EVM-026
- TRON: same
- Status: open
- Text: In order: decode the base64url credential and parse the JSON; payload.type is one of the types accepted for the challenge; the challenge is found by id (reject if none); every echoed challenge field matches the stored challenge; a splits challenge is rejected unless payload.type is permit2; then type-specific verification runs.

## SYS-402 Transaction pre-broadcast verification
- Spec: charge §6.3 steps 1-5
- Level: MUST
- Role: Server
- Verification: ST
- Source: -
- TRON: adapt
- Status: open
- Text: Before broadcasting the server deserializes the transaction and verifies: the transaction ID equals SHA-256 of raw_data; exactly one contract of type TriggerSmartContract; contract_address equals currency; call_value and TRC-10 value are zero; calldata starts with a9059cbb and decodes to the challenge recipient and amount with no trailing data; the signature is valid for owner_address; expiration has not passed.
- Note: Pre-broadcast half of EVM-030 (carried by SYS-501). A TRON transaction has no chainId field: the network is bound by the reference block (TAPOS), which the node of the configured chain enforces on broadcast (SYS-504). Multi-signature / account-permission signers are decision D7.

## SYS-403 Hash pre-verification
- Spec: charge §6.4 step 1
- Level: MUST
- Role: Server
- Verification: ST
- Source: -
- TRON: adapt
- Status: open
- Text: payload.hash is exactly 32 bytes of hex; the normalized transaction ID is looked up in the consumed set and rejected if present, before any node query result is accepted.
- Note: First step of EVM-031 (carried by SYS-502).

## SYS-404 Permit2 pre-submit verification
- Spec: charge §6.1
- Level: MUST
- Role: Server
- Verification: ST/SIT
- Source: EVM-027
- TRON: review
- Status: open
- Text: Before submitting: the TIP-712 signature recovers to the source address; deadline has not passed; the signer's token balance covers the total and its Permit2 allowance is sufficient (read from the TRON network); witness.challengeHash matches; permitted and transferDetails have equal length; every token equals currency; primary and split to/requestedAmount match the request.
- Note: Decision D3.

## SYS-405 Authorization pre-submit verification
- Spec: charge §6.2 steps 1-7
- Level: MUST
- Role: Server
- Verification: ST/SIT
- Source: -
- TRON: review
- Status: open
- Text: Before submitting: the token implements transferWithAuthorization; the signature recovers to from; to, value and nonce match recipient, amount and challengeHash; validBefore has not passed; the signer's token balance is sufficient.
- Note: Pre-submit half of EVM-029 (carried by SYS-509). Decision D4.


# 6. Charge flows: settlement on the TRON network

Who pays network resources follows from the credential type:

| Type | Broadcasts | Pays Energy/Bandwidth | Splits | Challenge binding |
|---|---|---|---|---|
| transaction | Server | Client | no | weak (terms only) |
| hash | Client | Client | no | weak (terms only) |
| permit2 | Server | Server | yes | challengeHash in witness |
| authorization | Server | Server | no | challengeHash as nonce |

Transaction flow (default type):

```
   SDK Client               SDK Server                 TRON network
      |                         |                           |
      | (1) GET /resource       |                           |
      |------------------------>|                           |
      | (2) 402, intent=charge  |                           |
      |<------------------------|                           |
      | (3a) get reference block                            |
      |---------------------------------------------------->|
      | (3b) build + sign TRC-20 transfer (not broadcast)   |
      |                         |                           |
      | (4) Authorization:      |                           |
      |     Payment <cred>      |                           |
      |------------------------>|                           |
      |                         | (5a) verify (SYS-401/402) |
      |                         | (5b) broadcast            |
      |                         |-------------------------->|
      |                         | (5c) poll transaction info|
      |                         |<------------------------->|
      |                         | (5d) result SUCCESS +     |
      |                         |      Transfer log + depth |
      | (6) 200 OK + Receipt    |                           |
      |<------------------------|                           |
```

Hash flow (client broadcasts):

```
   SDK Client               SDK Server                 TRON network
      | (1)-(2) as above        |                           |
      | (3a) build, sign and broadcast TRC-20 transfer      |
      |---------------------------------------------------->|
      | (3b) wait until included                            |
      |<----------------------------------------------------|
      | (4) Authorization:      |                           |
      |     Payment <cred>      |                           |
      |     (transaction ID)    |                           |
      |------------------------>|                           |
      |                         | (5a) consumed-set check   |
      |                         | (5b) get transaction info |
      |                         |<------------------------->|
      |                         | (5c) result SUCCESS +     |
      |                         |      Transfer log + depth |
      |                         | (5d) mark consumed        |
      | (6) 200 OK + Receipt    |                           |
      |<------------------------|                           |
```

Permit2 and authorization flows (server submits and pays):

```
   SDK Client               SDK Server                 TRON network
      | (1)-(2) as above        |                           |
      | (3) sign TIP-712 typed data (no chain interaction)  |
      | (4) Authorization:      |                           |
      |     Payment <cred>      |                           |
      |------------------------>|                           |
      |                         | (5a) verify (SYS-404/405) |
      |                         | (5b) simulate (constant   |
      |                         |      call)                |
      |                         |<------------------------->|
      |                         | (5c) submit permit[Batch]-|
      |                         |      WitnessTransferFrom  |
      |                         |      or transferWith-     |
      |                         |      Authorization        |
      |                         |-------------------------->|
      |                         | (5d) result SUCCESS +     |
      |                         |      Transfer log(s)      |
      |                         |<--------------------------|
      | (6) 200 OK + Receipt    |                           |
      |<------------------------|                           |
```

## SYS-501 Transaction charge flow
- Spec: charge §6.3 steps 6-9, 7.3
- Level: MUST
- Role: Both
- Verification: SIT
- Source: EVM-030
- TRON: adapt
- Status: open
- Text: After SYS-402 passes the server broadcasts the client-signed transaction unchanged to the TRON network, waits for its transaction info, and delivers the resource with a receipt only when SYS-503, SYS-505 and SYS-506 hold; the payer's token balance decreases and the recipient's increases by exactly amount, and the reference in the receipt is that transaction's ID.

## SYS-502 Hash charge flow
- Spec: charge §6.4, 7.4
- Level: MUST
- Role: Both
- Verification: SIT
- Source: EVM-031
- TRON: adapt
- Status: open
- Text: The client broadcasts the transfer and presents its transaction ID; the server, without broadcasting anything, fetches the transaction info from the TRON network, requires SYS-503, SYS-505 and SYS-506, then marks the ID consumed and delivers the resource with a receipt; an unknown or not yet included ID is rejected.

## SYS-503 On-chain success determination
- Spec: charge §6.1-6.4 ("receipt status success")
- Level: MUST
- Role: Server
- Verification: SIT
- Source: SES-093, SES-094
- TRON: new
- Status: open
- Text: A transaction counts as successful only when it is included in a block and its execution result is SUCCESS; transactions that are included but failed (REVERT, OUT_OF_ENERGY, OUT_OF_TIME and any other non-SUCCESS result) are rejected with verification-failed (session: SYS-1703) even though they have a valid transaction ID and block; a failed result is definitive and the server does not keep polling for a change.
- Note: TRON counterpart of "status 0x1": failed TRON transactions are still recorded on-chain and still cost the fee payer, so the execution result in the transaction info must be checked explicitly.

## SYS-504 Broadcast rejection handling
- Spec: charge §6.3 step 6, 9
- Level: MUST
- Role: Server
- Verification: SIT
- Source: -
- TRON: new
- Status: open
- Text: When the node refuses a broadcast (bad signature, reference block not on this chain, expired transaction, insufficient bandwidth or balance, contract validation error) the server answers 402 with verification-failed, delivers nothing and records nothing as consumed.
- Note: Decision D8 -- handling of "duplicate transaction" (the client also broadcast it): reject, or continue as a hash-style verification of the same ID.

## SYS-505 Transfer event matching
- Spec: charge §6.1 step 4, 6.2 step 10, 6.3 step 9, 6.4 step 4
- Level: MUST
- Role: Server
- Verification: SIT
- Source: -
- TRON: adapt
- Status: open
- Text: The transaction info contains a Transfer event (topic ddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef) whose emitting contract equals currency, whose to equals recipient and whose value equals the expected amount, compared as decoded 20-byte addresses and integers; for permit2 with splits every expected transfer has its own matching event.
- Note: Shared log check of EVM-028..031. TRON event logs give addresses as 20-byte hex without the 0x41 prefix.

## SYS-506 Confirmation before receipt
- Spec: charge §7.5
- Level: MUST/SHOULD
- Role: Server
- Verification: SIT
- Source: EVM-032, SES-141
- TRON: review
- Status: open
- Text: The server returns Payment-Receipt only after the transaction is included in at least one block with a successful result (MUST); confirmation depth beyond that is a configurable server policy that includes a "solidified block" option; the server assumes no fixed confirmation latency (SHOULD).
- Note: Decision D9 -- default policy: first block (seconds) versus solidified (about a minute).

## SYS-507 Confirmation timeout
- Spec: charge §7.5; project
- Level: MUST (project)
- Role: Server
- Verification: SIT
- Source: SES-095
- TRON: new
- Status: open
- Text: A transaction that is not yet included may be awaited up to a bounded timeout; if the required confirmation is not reached within the configured timeout the server returns an error without Payment-Receipt and without delivering the resource; a server-broadcast transaction whose expiration has passed without inclusion is treated as definitively failed.
- Note: Decision D10 -- response code and whether the client may retry the same credential while the outcome is still unknown.

## SYS-508 Permit2 charge flow
- Spec: charge §5.2.4, 6.1, 7.1
- Level: MUST
- Role: Both
- Verification: SIT
- Source: EVM-019, EVM-028
- TRON: review
- Status: open
- Text: After SYS-404 passes the server submits permitWitnessTransferFrom for a single transfer or permitBatchWitnessTransferFrom for splits, then requires SYS-503, SYS-505 and SYS-506; a batch settles all transfers in one transaction or none.
- Note: Decision D3.

## SYS-509 Authorization charge flow
- Spec: charge §6.2 steps 8-10, 7.2
- Level: MUST
- Role: Both
- Verification: SIT
- Source: EVM-029
- TRON: review
- Status: open
- Text: After SYS-405 passes the server calls transferWithAuthorization on the currency contract with the client's signature, then requires SYS-503, SYS-505 and SYS-506.
- Note: Decision D4.

## SYS-510 Server fee payer resources
- Spec: charge §5.6, 10.6
- Level: MUST
- Role: Server
- Verification: SIT
- Source: EVM-020, EVM-040
- TRON: adapt
- Status: open
- Text: For permit2 and authorization the server account pays Energy and Bandwidth (staked, delegated or burned TRX) and sets a bounded fee_limit; the server monitors these resources and its TRX balance and stops accepting server-paid credential types (no new challenges offering them) when it cannot cover a settlement.

## SYS-511 Simulate before server-paid submission
- Spec: charge §6.1, 6.2, 10.6, 10.7
- Level: SHOULD
- Role: Server
- Verification: SIT
- Source: EVM-041
- TRON: adapt
- Status: open
- Text: Before submitting a server-paid transaction the server simulates it with a constant (read-only) contract call and checks the client's token balance; a failing simulation is rejected with verification-failed and nothing is broadcast; attempts are rate limited per client (SYS-806).

## SYS-512 Client does not pay twice
- Spec: base §11.3; project
- Level: MUST (project)
- Role: Client
- Verification: SIT
- Source: -
- TRON: new
- Status: open
- Text: After a rejected or timed-out credential the client does not sign or broadcast a second payment for the same application request without passing SYS-304 again; for the hash type it may present the already confirmed transaction ID against a fresh challenge with identical terms instead of paying again.
- Note: Decision D10.

## SYS-513 Node trust
- Spec: charge §10.8
- Level: SHOULD
- Role: Server
- Verification: SIT
- Source: -
- TRON: new
- Status: open
- Text: Settlement data comes only from the configured, trusted TRON node(s); node errors, timeouts and inconsistent answers are treated as verification failure, never as success.


# 7. Receipt

## SYS-601 Payment-Receipt on success
- Spec: base §5.3, 5.3.1; charge §7.6
- Level: MUST
- Role: Server
- Verification: ST/SIT
- Source: BASE-032, BASE-033, EVM-033
- TRON: adapt
- Status: open
- Text: Every successful settlement returns Payment-Receipt (base64url JSON) on a 2xx response with method "tron", challengeId, reference (the settling transaction ID), status "success", RFC 3339 timestamp and chainId, plus externalId when the request had one; the reference resolves on the network named by chainId to the transaction that paid.

## SYS-602 No receipt on error responses
- Spec: base §5.3.1; charge §7.6
- Level: MUST
- Role: Server
- Verification: ST/SIT
- Source: BASE-034, EVM-034
- TRON: same
- Status: open
- Text: Payment-Receipt never appears on a non-2xx response; failures are expressed only through status codes and Problem Details.


# 8. Errors and replay protection

## SYS-701 Problem Details on rejection
- Spec: base §4.2, 8.1, 8.2; charge §9
- Level: MUST/SHOULD
- Role: Server
- Verification: ST
- Source: BASE-007, BASE-040, BASE-041, EVM-036
- TRON: same
- Status: open
- Text: Every credential rejection returns 402 with a fresh challenge (MUST) and an application/problem+json body (RFC 9457) whose type is one of the https://paymentauth.org/problems/ types and whose detail describes the failure (SHOULD); error details never go into WWW-Authenticate parameters; method-unsupported uses 400.

## SYS-702 Malformed credential -> malformed-credential
- Spec: base §4.2, 8.2
- Level: MUST
- Role: Server
- Verification: ST
- Source: BASE-002
- TRON: same
- Status: open
- Text: Invalid base64url, invalid JSON, a missing challenge or payload object, or a payload that does not fit the schema of its type yields the malformed-credential problem.

## SYS-703 Unknown or used challenge id -> invalid-challenge
- Spec: base §4.2, 8.2
- Level: MUST
- Role: Server
- Verification: ST
- Source: BASE-003
- TRON: same
- Status: open
- Text: An unknown or already-used challenge id, or echoed parameters that fail the binding check, yields the invalid-challenge problem.

## SYS-704 Expired challenge -> payment-expired
- Spec: base §4.2, 8.2
- Level: MUST
- Role: Server
- Verification: ST
- Source: BASE-004
- TRON: same
- Status: open
- Text: A credential for an expired challenge yields the payment-expired problem and nothing is broadcast, even if the embedded TRON transaction is still valid.

## SYS-705 Failed verification -> verification-failed
- Spec: base §4.2, 5.3.1, 8.2
- Level: MUST
- Role: Server
- Verification: ST/SIT
- Source: BASE-005
- TRON: same
- Status: open
- Text: Any failed payload check, broadcast rejection, failed on-chain result or event mismatch yields the verification-failed problem.

## SYS-710 Replay protection
- Spec: base §11.3; charge §8
- Level: MUST
- Role: Server
- Verification: ST/SIT
- Source: BASE-050, EVM-035
- TRON: adapt
- Status: open
- Text: The server keeps a consumed set, checks it before accepting a credential and marks the token consumed atomically after verification; the token is the transaction ID for transaction and hash, and signer address plus nonce for permit2 and authorization; transaction IDs are normalized (lowercase hex, no prefix) so the same transaction cannot be presented twice in a different spelling.
- Note: TRON has no account nonce; a signed transaction is unique by its ID and bounded by its expiration.

## SYS-711 Consumed set durability
- Spec: charge §8, 10.4; project
- Level: SHOULD (project)
- Role: Server
- Verification: ST
- Source: -
- TRON: new
- Status: open
- Text: The consumed set lives in the configured `Store`, is shared by all server instances and survives restarts; hash-type tokens are kept without expiry because an on-chain transaction ID stays valid forever.

## SYS-712 Concurrent credential use
- Spec: base §11.5
- Level: MUST/SHOULD
- Role: Server
- Verification: ST/SIT
- Source: BASE-053
- TRON: same
- Status: open
- Text: Concurrent requests carrying the same credential result in at most one settlement on the TRON network and one resource delivery; the others are rejected.

## SYS-713 Permit2 nonce conflicts and contract address
- Spec: charge §10.5
- Level: MUST/SHOULD
- Role: Both
- Verification: ST/SIT
- Source: EVM-039
- TRON: review
- Status: open
- Text: The server handles an already-consumed Permit2 nonce as a normal verification failure (MUST); the client signs only for a permit2Address on its allowlist of known deployments for that chain (SHOULD).
- Note: Decision D3.


# 9. Security and operations

## SYS-801 TLS required
- Spec: base §11.2; charge §10.1
- Level: MUST
- Role: Both
- Verification: SIT
- Source: BASE-047, EVM-037
- TRON: same
- Status: open
- Text: TLS 1.2 or later (1.3 recommended); the server issues no challenge and the client sends no credential over plain HTTP.

## SYS-802 Sensitive data handling
- Spec: base §11.2.1, 11.7, 11.8
- Level: MUST/SHOULD
- Role: Both
- Verification: ST/SIT
- Source: BASE-048
- TRON: same
- Status: open
- Text: Credentials, receipts, signer keys and node API keys are not written to logs, error messages, debug output or analytics; credentials are held in memory only and cleared after use.

## SYS-803 Challenge-binding secret management
- Spec: base §11.2.2
- Level: MUST/SHOULD
- Role: Server
- Verification: ST
- Source: BASE-049
- TRON: same
- Status: open
- Text: The binding secret stays server-side and is never disclosed or logged; after rotation, challenges issued under the previous secret keep verifying until they expire.

## SYS-804 No account requirement
- Spec: base §11.7
- Level: MUST/SHOULD
- Role: Server
- Verification: SIT
- Source: BASE-055
- TRON: same
- Status: open
- Text: A payer needs nothing but a TRON address holding the token: no user account, registration or prior contact with the server.

## SYS-805 Intermediary handling of 402
- Spec: base §11.9
- Level: SHOULD/MUST
- Role: Both
- Verification: SIT
- Source: BASE-056
- TRON: same
- Status: open
- Text: The server does not rely on intermediary-specific 402 handling; the client completes the flow through proxies and gateways.

## SYS-806 Rate limiting
- Spec: base §11.12; charge §10.6
- Level: SHOULD
- Role: Server
- Verification: SIT
- Source: BASE-059
- TRON: same
- Status: open
- Text: Challenge issuance and credential verification attempts are rate limited, per client address and IP for server-paid credential types.


# 10. Session: SDK configuration and request schema

The session intent funds a channel in an escrow contract once and then pays per request with signed cumulative
vouchers. Requirements in sections 10-17 apply to the session intent only; the common blocks listed under "Intent
applicability" apply as well and are not repeated.

## SYS-1001 Session method definition and server factory
- Spec: sdk; project
- Level: MUST (project)
- Role: Server
- Verification: ST
- Source: -
- TRON: new
- Status: open
- Text: A `session` factory is exported from `./server` next to `charge`, built on one shared `Method.from` definition with intent `session`; it takes price per unit, currency, recipient (payee), chainId, node endpoint, escrow contract, settlement policy, a payee signer able to pay for settle and close, and a durable `Store`; invalid configuration fails at creation.

## SYS-1002 Session client factory
- Spec: sdk; project
- Level: MUST (project)
- Role: Client
- Verification: ST
- Source: -
- TRON: new
- Status: open
- Text: A `session` factory is exported from `./client`; it takes a signer, an optional delegated voucher signer, supported chain IDs, a node endpoint (the client transacts on-chain to open), an escrow allowlist and a deposit policy (see SYS-1311), and exposes close, forced close and `cleanup()`.

## SYS-1003 Escrow contract allowlist
- Spec: project
- Level: MUST (project)
- Role: Both
- Verification: ST
- Source: -
- TRON: review
- Status: open
- Text: The SDK ships the known escrow address per supported network; the client refuses to deposit into an escrowContract that is not on its allowlist unless the application opted in explicitly, and the server uses the shipped address unless configured otherwise.
- Note: Decision D14 -- who deploys and owns the reference escrow on Nile and mainnet.

## SYS-1004 Encoding conventions
- Spec: session §6.1, 6.2, 6.3
- Level: MUST
- Role: Both
- Verification: ST
- Source: SES-004, SES-007, SES-009
- TRON: review
- Status: open
- Text: channelId, signatures and hashes are lowercase hex without padding or truncation; integer values (amounts, deposits, signed-data timestamps) are decimal strings; HTTP and receipt timestamps are RFC 3339 while timestamps inside signed data are Unix seconds.
- Note: Decision D1 -- the draft also mandates the 0x prefix and hex addresses; TRON shows transaction IDs without 0x and addresses as Base58Check. One wire form must be chosen for both intents (addresses: SYS-203).

## SYS-1005 Signatures are 65 bytes
- Spec: session §6.1
- Level: MUST
- Role: Both
- Verification: ST
- Source: SES-005
- TRON: same
- Status: open
- Text: Every signature is 65 bytes, r then s then v, as one bytes value; the SDK never produces EIP-2098 compact 64-byte signatures, may accept them, and never requires them from a client.

## SYS-1006 Chain identifier consistency
- Spec: session §6.2
- Level: MUST
- Role: Both
- Verification: ST/SIT
- Source: SES-008
- TRON: review
- Status: open
- Text: chainId is a JSON number and is converted to uint256 for the typed-data domain; the value the SDK signs with, the value the escrow reads on-chain and the value in challenge and receipt are the same for a given network.
- Note: Decision D11 -- what the TVM returns for block.chainid and what TIP-712 wallets put in the domain must be pinned down and matched on and off chain.

## SYS-1010 Required session request fields
- Spec: session §8.1, 8.2
- Level: MUST
- Role: Server
- Verification: ST
- Source: SES-041, SES-043
- TRON: adapt
- Status: open
- Text: The request carries amount (price per unit of service in base units, not a total), currency (TRC-20 contract), recipient (payee), methodDetails.chainId and methodDetails.escrowContract.

## SYS-1011 Optional session request fields
- Spec: session §8.1, 8.2
- Level: MAY
- Role: Server
- Verification: ST
- Source: SES-042, SES-044, SES-045
- TRON: adapt
- Status: open
- Text: unitType, suggestedDeposit, description and externalId are optional; methodDetails.minVoucherDelta defaults to "0" (any positive increment); methodDetails.feePayer defaults to false; methodDetails.channelId is present only when the server proposes resuming an existing channel.

## SYS-1012 Session credentialTypes
- Spec: session §8.2, 9.1
- Level: MAY/MUST
- Role: Server
- Verification: ST
- Source: SES-046, SES-049
- TRON: review
- Status: open
- Text: credentialTypes is an ordered list drawn from permit2, authorization and hash (there is no signed-transaction type) and defaults to ["hash"]; with feePayer true the server lists at least one server-submitted type its escrow supports and may add hash as fallback.
- Note: Decision D12.

## SYS-1013 Client honors session credentialTypes
- Spec: session §8.2, 9.1, 9.2
- Level: MUST
- Role: Client
- Verification: ST
- Source: SES-047
- TRON: same
- Status: open
- Text: The client uses the first listed type it can produce unless its policy chooses another listed one, and never submits a type absent from the list (including hash when the list omits it).

## SYS-1014 No advertising of unimplemented capabilities
- Spec: session §7.3, 9.1, 9.4
- Level: MUST
- Role: Server
- Verification: ST/SIT
- Source: SES-016, SES-055
- TRON: review
- Status: open
- Text: The server advertises feePayer true, a server-submitted type or relayed settle/close only when the configured escrow implements the backing function and the currency token supports that path.
- Note: Decision D12.

## SYS-1015 permit2Contract advertisement
- Spec: session §8.2, 10.2.2
- Level: MUST
- Role: Both
- Verification: ST
- Source: SES-048
- TRON: review
- Status: open
- Text: When permit2 is offered the server advertises methodDetails.permit2Contract, the client uses it as verifyingContract, and it equals the Permit2 address configured in the escrow.
- Note: Decision D3 -- no canonical Permit2 address on TRON, so the field is always required when permit2 is offered.

## SYS-1016 Well-behaved tokens only
- Spec: session §7
- Level: MUST
- Role: Server
- Verification: ST/SIT
- Source: SES-010
- TRON: review
- Status: open
- Text: The server offers session only for tokens that transfer exactly the requested amount; fee-on-transfer and rebasing tokens are refused at configuration.
- Note: Decision D13 -- transfer behavior of each target TRC-20 (return values, fee parameters) must be verified against the deployed token before it is allowed.

## SYS-1017 Server checks the escrow grace period
- Spec: session §14.3
- Level: MUST
- Role: Server
- Verification: SIT
- Source: SES-129
- TRON: same
- Status: open
- Text: Before accepting channels on an escrow the server reads its forced-close grace period from the TRON network and refuses the contract if it is shorter than 10 minutes.



# 11. Session: channel escrow contract

Requirements on the contract itself (verification level CT). They are tested by calling the deployed contract directly; the SDK
relies on them. Core functions are mandatory; the relayed profile (SYS-1120..1125) is optional as a whole or in part.

## SYS-1101 Mandatory core functions
- Spec: session §7.3
- Level: MUST
- Role: Contract
- Verification: CT
- Source: SES-014
- TRON: same
- Status: open
- Text: The escrow implements open, settle, topUp, close, requestClose and withdraw.

## SYS-1102 Deterministic channelId
- Spec: session §7.1
- Level: MUST
- Role: Contract
- Verification: CT
- Source: SES-011
- TRON: review
- Status: open
- Text: channelId = keccak256(abi.encode(payer, payee, token, salt, authorizedSigner, address(this), block.chainid)), exposed through computeChannelId() or equivalent; the SDK computes the identical value off-chain.
- Note: Decision D11. Addresses enter the encoding in their 20-byte form.

## SYS-1103 open
- Spec: session §7.3.1, 7.4
- Level: MUST
- Role: Contract
- Verification: CT
- Source: SES-017
- TRON: adapt
- Status: open
- Text: open(payee, token, deposit, salt, authorizedSigner) can be called by anyone, makes the caller the payer, pulls the deposit with transferFrom after a prior approve, returns the channelId and reverts if that channelId already exists.
- Note: TRC-20 tokens with non-standard return values need tolerant transfer handling (decision D13).

## SYS-1104 Channels never expire and are never deleted
- Spec: session §7.2, 7.3.1, 15.2, 15.11
- Level: MUST
- Role: Contract
- Verification: CT
- Source: SES-013, SES-018
- TRON: same
- Status: open
- Text: Channels and vouchers have no expiry; finalized is set once and never cleared and the record is never deleted, so a used channelId can never be opened again.

## SYS-1105 settle
- Spec: session §7.3.4, 7.4, 15.5
- Level: MUST
- Role: Contract
- Verification: CT
- Source: SES-022, SES-023
- TRON: same
- Status: open
- Text: settle is payee-only; it reverts when cumulativeAmount is not greater than channel.settled or exceeds channel.deposit; otherwise it pays the difference to the payee, records the new settled amount and leaves the channel open.

## SYS-1106 topUp
- Spec: session §7.3.5, 7.4, 10.2.3
- Level: MUST
- Role: Contract
- Verification: CT
- Source: SES-024, SES-025
- TRON: same
- Status: open
- Text: topUp is payer-only, pulls the additional deposit after a prior approve and cancels a pending close request by resetting closeRequestedAt to 0.

## SYS-1107 close
- Spec: session §7.3.8, 7.4, 9.4.2, 15.16
- Level: MUST/MAY
- Role: Contract
- Verification: CT
- Source: SES-028, SES-029
- TRON: same
- Status: open
- Text: close is payee-only and in one transaction settles the outstanding voucher difference to the payee, refunds the remainder to the payer and finalizes the channel (MUST); when cumulativeAmount is not above channel.settled the voucher signature check may be skipped (MAY).

## SYS-1108 requestClose
- Spec: session §7.3.9, 7.4
- Level: MUST
- Role: Contract
- Verification: CT
- Source: SES-030
- TRON: same
- Status: open
- Text: requestClose is payer-only, records the request time and reverts for an unknown or finalized channel.

## SYS-1109 withdraw
- Spec: session §7.3.10, 7.4
- Level: MUST
- Role: Contract
- Verification: CT
- Source: SES-031, SES-032
- TRON: same
- Status: open
- Text: withdraw is payer-only and reverts if the channel is finalized, no close was requested or the grace period has not elapsed; on success it pays deposit minus settled to the payer and finalizes in the same step, so a second payout is impossible.

## SYS-1110 Reverts on invalid channel or deposit
- Spec: session §7.6
- Level: MUST
- Role: Contract
- Verification: CT
- Source: SES-037, SES-038
- TRON: same
- Status: open
- Text: settle, topUp, close, requestClose and withdraw (and their relayed variants) revert for an unknown or finalized channel; open and topUp (and variants) revert for a zero deposit or a deposit beyond the uint128 bound.

## SYS-1111 Recommended revert names
- Spec: session §7.6
- Level: SHOULD
- Role: Contract
- Verification: CT
- Source: SES-039
- TRON: same
- Status: open
- Text: The contract uses the recommended error names (ChannelAlreadyExists, ChannelNotFound, ChannelFinalized, NotPayee, NotPayer, AmountNotIncreasing, AmountExceedsDeposit, InvalidSignature, NonceMismatch, NonceAlreadyUsed, AuthorizationExpired, CloseNotReady, ZeroDeposit, DepositOverflow).

## SYS-1112 Voucher signature verification on-chain
- Spec: session §7.5, 15.1, 15.9
- Level: MUST
- Role: Contract
- Verification: CT
- Source: SES-033, SES-034, SES-036
- TRON: adapt
- Status: open
- Text: For every function taking a voucher the contract rejects high-s signatures, recovers the typed-data signer and requires it to equal channel.authorizedSigner when set, otherwise channel.payer, under a domain whose verifyingContract is the escrow itself.
- Note: Typed data per TIP-712; the contract address is used in 20-byte form.

## SYS-1113 Contract-wallet signers
- Spec: session §3, 7.5
- Level: MUST (implied)
- Role: Contract
- Verification: CT
- Source: SES-035
- TRON: adapt
- Status: open
- Text: The signer may be a key-controlled account (ECDSA) or a contract wallet verified through isValidSignature (ERC-1271 semantics).
- Note: TRON native multi-signature (account permissions) is not a contract wallet and cannot sign vouchers this way; such payers need a single-key authorizedSigner.

## SYS-1114 Grace period
- Spec: session §14.3, 15.16
- Level: MUST
- Role: Contract
- Verification: CT
- Source: SES-128, SES-130
- TRON: same
- Status: open
- Text: The forced-close grace period is a contract constant of at least 10 minutes (reference 15); the payee can still settle or close during it, and only after it elapses can the payer withdraw.

## SYS-1115 State before transfer
- Spec: session §15.10
- Level: MUST
- Role: Contract
- Verification: CT
- Source: SES-139
- TRON: same
- Status: open
- Text: settle, close, withdraw and their relayed variants commit all state changes before the external token transfer; relayed settle and close use a reentrancy guard or strict checks-effects-interactions.

## SYS-1116 No privileged role
- Spec: project
- Level: SHOULD (project)
- Role: Contract
- Verification: CT
- Source: -
- TRON: review
- Status: open
- Text: The reference escrow has no owner or admin function and is deployed without an upgrade proxy; a corrected version is a new deployment at a new address.
- Note: Decision D14 -- an immutable contract cannot be paused if a defect is found; a pause or upgrade switch brings back a privileged key.

## SYS-1120 Relayed profile is optional
- Spec: session §7.3, 9.3, 9.4
- Level: MAY
- Role: Contract
- Verification: CT
- Source: SES-015
- TRON: review
- Status: open
- Text: openWithAuthorization, topUpWithAuthorization, openWithPermit2, topUpWithPermit2, settleWithAuthorization and closeWithAuthorization may be omitted or implemented in any subset.
- Note: Decision D12.

## SYS-1121 Relayed open with token authorization
- Spec: session §7.1, 7.3.2, 7.4, 15.13
- Level: MUST/SHOULD
- Role: Contract
- Verification: CT
- Source: SES-012, SES-019, SES-020
- TRON: review
- Status: open
- Text: openWithAuthorization pulls funds with receiveWithAuthorization (bytes-signature form, never transferWithAuthorization); the payer is the from argument, not the submitter; the contract recomputes the nonce keccak256(abi.encode(from, payee, token, salt, authorizedSigner)) and reverts on mismatch before calling the token.
- Note: Decision D4.

## SYS-1122 Relayed open with Permit2
- Spec: session §7.3.3, 15.13
- Level: MUST
- Role: Contract
- Verification: CT
- Source: SES-021
- TRON: review
- Status: open
- Text: openWithPermit2 uses permitWitnessTransferFrom with a witness binding payee, salt and authorizedSigner, so a signature over other channel parameters reverts.
- Note: Decision D3.

## SYS-1123 Relayed top-up
- Spec: session §7.3.6, 7.3.7, 9.4.1, 15.13
- Level: MUST
- Role: Contract
- Verification: CT
- Source: SES-026, SES-027, SES-057
- TRON: review
- Status: open
- Text: topUpWithAuthorization validates the nonce keccak256(abi.encode(channelId, additionalDeposit, from, topUpSalt)); topUpWithPermit2 binds channelId as witness and uses the channel's token; the funder need not be the payer, and refunds still go to channel.payer.
- Note: Decisions D3 and D4.

## SYS-1124 Payee-authorized settle and close
- Spec: session §9.4.2
- Level: MUST
- Role: Contract
- Verification: CT
- Source: SES-058, SES-059, SES-060
- TRON: adapt
- Status: open
- Text: settleWithAuthorization and closeWithAuthorization accept any submitter, verify the voucher exactly as settle and close do, and require a typed-data SettleAuthorization or CloseAuthorization (channelId, cumulativeAmount, nonce, deadline) signed by channel.payee under the voucher domain.
- Note: TIP-712 typed data.

## SYS-1125 Payee authorization replay and deadline
- Spec: session §9.4.2
- Level: MUST
- Role: Contract
- Verification: CT
- Source: SES-061, SES-062
- TRON: same
- Status: open
- Text: The contract keeps one used-set keyed by (payee, channelId, nonce) shared by settle and close authorizations and reverts on reuse; it reverts when the block time is past the deadline.



# 12. Session: credential actions and client behavior

Every session credential carries payload.action. Only open and topUp have a payload.type.

| action | When | Chain interaction | Carries |
|---|---|---|---|
| open | first paid request | client opens the channel (or server submits, if server-paid) | channelId, salt, proof of funding, initial voucher |
| voucher | every further payment | none | channelId, cumulativeAmount, signature |
| topUp | deposit nearly used | client tops up (or server submits) | channelId, additionalDeposit, proof of funding |
| close | end of session | server closes | channelId, final cumulativeAmount, signature |

## SYS-1201 payload.action
- Spec: session §10.2
- Level: MUST
- Role: Client
- Verification: ST
- Source: SES-067
- TRON: same
- Status: open
- Text: payload.action is required and is one of open, topUp, voucher, close.

## SYS-1202 source for hash credentials
- Spec: session §10.1, 10.2.1, 10.2.3, 10.2.4
- Level: MUST
- Role: Client
- Verification: ST
- Source: SES-065
- TRON: same
- Status: open
- Text: source is required when payload.type is hash (open and topUp), not required for server-submitted types (payer is authorization.from) and optional for voucher and close.
- Note: Form of the DID: SYS-303.

## SYS-1203 Open payload, client-broadcast
- Spec: session §10.2.1
- Level: MUST
- Role: Client
- Verification: ST
- Source: SES-068
- TRON: adapt
- Status: open
- Text: payload has action open, type hash, channelId, hash (transaction ID of the on-chain open), cumulativeAmount, signature (initial voucher) and salt; authorizedSigner is optional and defaults to the payer.
- Note: No ERC-4337 path on TRON.

## SYS-1204 Initial voucher at open
- Spec: session §10.2.1, 10.2.2
- Level: MUST
- Role: Client
- Verification: ST
- Source: SES-069
- TRON: same
- Status: open
- Text: Every open payload contains a signed initial voucher (typically cumulativeAmount "0"), so the server can settle or close at any time.

## SYS-1205 TopUp payload, client-broadcast
- Spec: session §10.2.3
- Level: MUST
- Role: Client
- Verification: ST
- Source: SES-078
- TRON: adapt
- Status: open
- Text: payload has action topUp, type hash, channelId, hash (transaction ID of the on-chain topUp) and additionalDeposit.

## SYS-1206 Voucher payload
- Spec: session §10.2.4
- Level: MUST
- Role: Client
- Verification: ST
- Source: SES-081
- TRON: same
- Status: open
- Text: payload has action voucher, channelId, cumulativeAmount and signature.

## SYS-1207 Close payload
- Spec: session §10.2.5
- Level: MUST
- Role: Client
- Verification: ST
- Source: SES-086
- TRON: same
- Status: open
- Text: payload has action close, channelId, the final cumulativeAmount and signature.

## SYS-1210 Open payload, server-submitted
- Spec: session §10.2.2
- Level: MUST
- Role: Client
- Verification: ST
- Source: SES-070
- TRON: review
- Status: open
- Text: payload has action open, type authorization or permit2, channelId, authorization, signature, cumulativeAmount, voucherSignature and salt; authorizedSigner is optional.
- Note: Decision D12.

## SYS-1211 Token authorization object and nonce
- Spec: session §7.3.6, 10.2.2, 15.13
- Level: MUST
- Role: Client
- Verification: ST
- Source: SES-071, SES-072
- TRON: review
- Status: open
- Text: For type authorization the object has from, to (the escrow contract), value, validAfter, validBefore and nonce; the nonce is derived from the channel parameters exactly as the contract recomputes it (SYS-1121, SYS-1123) and is sent in the credential.
- Note: Decision D4.

## SYS-1212 Permit2 authorization object
- Spec: session §9.1, 10.2.2, 15.14
- Level: MUST
- Role: Client
- Verification: ST/SIT
- Source: SES-054, SES-073, SES-074, SES-075, SES-077
- TRON: review
- Status: open
- Text: For type permit2 the object has from, permitted {token = currency, amount = deposit}, nonce, deadline and witness; the spender is the escrow contract; the witness carries payee, salt and authorizedSigner (zero address when omitted) for open or channelId for topUp; domain and type strings are those of the spec; the payer has approved the Permit2 contract beforehand.
- Note: Decision D3.

## SYS-1213 TopUp payload, server-submitted
- Spec: session §10.2.3
- Level: MUST
- Role: Both
- Verification: ST
- Source: SES-079, SES-080
- TRON: review
- Status: open
- Text: payload has action topUp, type, channelId, authorization, signature and additionalDeposit (plus salt for type authorization); additionalDeposit equals the authorized amount and the server rejects a mismatch.
- Note: Decision D12.

## SYS-1214 Voucher deposit extension
- Spec: session §10.2.4
- Level: MAY/MUST
- Role: Client
- Verification: ST
- Source: SES-082, SES-083, SES-085
- TRON: review
- Status: open
- Text: A voucher payload may carry a deposit object (action, type, authorization, signature, salt where required, optional authorizedSigner for open); an omitted authorizedSigner means the zero address; for an existing channel deposit.action is topUp.
- Note: Decision D12.

## SYS-1301 Voucher typed data
- Spec: session §11.1, 11.2, 11.3, 15.3
- Level: MUST (implied)
- Role: Both
- Verification: ST
- Source: SES-087, SES-088, SES-089
- TRON: review
- Status: open
- Text: A voucher is typed data Voucher(bytes32 channelId,uint128 cumulativeAmount) under a domain with name, version "1", chainId and verifyingContract = escrow contract; the digest is signed with secp256k1 and v is 27 or 28.
- Note: Decision D15 -- domain name (the draft uses "EVM Payment Channel"); it must equal the constant in the deployed escrow. Signing per TIP-712; decision D11 for chainId.

## SYS-1303 Vouchers are cumulative totals
- Spec: session §11.4, 14.4
- Level: MUST (implied)
- Role: Both
- Verification: ST
- Source: SES-090
- TRON: same
- Status: open
- Text: cumulativeAmount is the running total for the channel, not an increment; consecutive sessions on one channel continue the same counter from the highest accepted amount.

## SYS-1304 New channel: salt and channelId
- Spec: session §8.2, 15.2
- Level: MUST
- Role: Client
- Verification: ST/SIT
- Source: SES-050, SES-136
- TRON: adapt
- Status: open
- Text: Without a channelId in the challenge the client generates a random salt, computes the channelId as in SYS-1102, opens the channel and returns the channelId; after a close it always uses a new salt.

## SYS-1305 Existing channel: balance check
- Spec: session §8.2
- Level: MUST
- Role: Client
- Verification: SIT
- Source: SES-051
- TRON: same
- Status: open
- Text: When the server proposes an existing channel the client reads it from the TRON network and resumes only if deposit minus settled is at least amount.

## SYS-1306 Client-paid open
- Spec: session §9.2, 10.2.1, 15.14
- Level: MUST (implied)/SHOULD
- Role: Client
- Verification: SIT
- Source: SES-056, SES-142
- TRON: adapt
- Status: open
- Text: With feePayer false or absent the client sends approve(escrow, deposit) and open() itself and pays Energy and Bandwidth for both; approve and open are batched when possible (SHOULD).
- Note: A TRON transaction holds one contract call and a helper contract would become the payer, so batching is probably not achievable; the approval is then limited to the deposit amount.

## SYS-1307 Vouchers and close use the resource URI
- Spec: session §4, 14.5
- Level: SHOULD/MAY
- Role: Both
- Verification: ST
- Source: SES-001
- TRON: same
- Status: open
- Text: Voucher and close credentials go to the same resource URI that requires payment; the server accepts voucher updates on any HTTP method; the client may use HEAD when no body is needed.

## SYS-1308 Top up before exceeding the deposit
- Spec: session §13.3
- Level: MUST
- Role: Client
- Verification: ST/SIT
- Source: SES-119
- TRON: same
- Status: open
- Text: When the required cumulative amount exceeds the deposit the client tops up the channel before sending the next voucher.

## SYS-1309 Voucher transport concurrency
- Spec: session §14.5
- Level: SHOULD
- Role: Client
- Verification: ST
- Source: SES-131
- TRON: same
- Status: open
- Text: The client sends voucher updates over HTTP/2 multiplexing or a separate connection from the content stream.

## SYS-1310 Contract wallets and session keys
- Spec: session §15.15
- Level: SHOULD
- Role: Both
- Verification: ST
- Source: SES-143, SES-144
- TRON: same
- Status: open
- Text: A contract-wallet payer delegates voucher signing to a short-lived key through authorizedSigner and avoids key rotation during a session; the server settles more often when the signer is a contract.

## SYS-1311 Client deposit and voucher policy
- Spec: base §11.6; project
- Level: MUST (project)
- Role: Client
- Verification: ST
- Source: -
- TRON: new
- Status: open
- Text: Before depositing the client checks price, currency, recipient, chainId and escrow contract against its policy (SYS-304, SYS-1003) and caps the deposit; it never signs a voucher above the deposit or above its configured spending limit for the session.

## SYS-1312 Client can always recover its funds
- Spec: session §14.3, 15.16, 15.17
- Level: MUST (project)
- Role: Client
- Verification: SIT
- Source: -
- TRON: new
- Status: open
- Text: The SDK client exposes forced close: requestClose on-chain, then withdraw after the grace period, returning the unsettled remainder to the payer without any cooperation from the server.



# 13. Session: server verification

## SYS-1401 Common session verification
- Spec: session §12.1
- Level: MUST
- Role: Server
- Verification: ST
- Source: SES-092
- TRON: same
- Status: open
- Text: Before action-specific checks the server decodes the credential, requires a recognized payload.action, finds the stored challenge by id, requires every echoed challenge field to match and requires the challenge not to be expired.
- Note: Binding rules: SYS-112.

## SYS-1402 Open by hash: transaction check
- Spec: session §12.3
- Level: MUST
- Role: Server
- Verification: SIT
- Source: SES-096
- TRON: adapt
- Status: open
- Text: For open with type hash the server looks up the transaction by ID on the TRON network and verifies that it executed open() successfully on the expected escrow and created exactly payload.channelId.
- Note: Success determination and confirmation depth: SYS-503, SYS-506.

## SYS-1403 Open: channel state checks
- Spec: session §12.3
- Level: MUST
- Role: Server
- Verification: SIT
- Source: SES-097
- TRON: same
- Status: open
- Text: On every open the server reads the channel from the escrow and requires: it exists under the given channelId, payee is the server's address, token equals currency, deposit minus settled is at least amount, it is not finalized and no close is requested.

## SYS-1404 Open: initial voucher and accounting
- Spec: session §12.3
- Level: MUST
- Role: Server
- Verification: ST
- Source: SES-098
- TRON: same
- Status: open
- Text: On every open the server verifies the initial voucher like any voucher and then creates the accounting state for the channel.

## SYS-1405 Open, server-submitted
- Spec: session §9.1, 10.2.2, 12.3
- Level: MUST
- Role: Both
- Verification: SIT
- Source: SES-053, SES-076, SES-099
- TRON: review
- Status: open
- Text: With feePayer true the client sends a token-pull authorization instead of broadcasting; the server validates its fields and signature, rejects a Permit2 witness that disagrees with the channel parameters, submits the matching escrow function at its own cost and then runs SYS-1403.
- Note: Decision D12.

## SYS-1406 TopUp by hash
- Spec: session §12.4
- Level: MUST
- Role: Server
- Verification: SIT
- Source: SES-100
- TRON: adapt
- Status: open
- Text: For topUp with type hash the server verifies that the transaction executed topUp() successfully on the expected escrow for payload.channelId, reads the channel, requires the deposit to have grown by exactly additionalDeposit and updates its balance.

## SYS-1407 TopUp, server-submitted
- Spec: session §12.4
- Level: MUST
- Role: Server
- Verification: SIT
- Source: SES-101
- TRON: review
- Status: open
- Text: For topUp with a server-submitted type the server validates the authorization, submits the matching escrow function, verifies the updated channel and updates its balance.
- Note: Decision D12.

## SYS-1408 Deposit before voucher
- Spec: session §10.2.4, 12.5
- Level: MUST
- Role: Server
- Verification: ST/SIT
- Source: SES-084
- TRON: review
- Status: open
- Text: When a voucher carries a deposit object the server processes the deposit first, verifies the resulting channel state, then validates the voucher; a failed deposit rejects the whole credential.
- Note: Decision D12.

## SYS-1410 No vouchers while a close is pending
- Spec: session §12.5
- Level: MUST
- Role: Server
- Verification: ST/SIT
- Source: SES-102
- TRON: same
- Status: open
- Text: The server rejects a voucher for a channel whose closeRequestedAt is not zero.

## SYS-1411 Voucher signature and signer
- Spec: session §12.5, 12.6
- Level: MUST
- Role: Server
- Verification: ST
- Source: SES-103, SES-104
- TRON: adapt
- Status: open
- Text: The server recovers the typed-data signer, requires a low-s signature and requires the signer to be the channel's authorizedSigner when set, otherwise the payer (contract wallets through a constant isValidSignature call); this happens before any idempotency shortcut, and a bad signature is an error whatever the amount.
- Note: TIP-712 digest.

## SYS-1412 Replay of an old or equal voucher
- Spec: session §12.5, 12.6
- Level: MUST/MAY
- Role: Server
- Verification: ST
- Source: SES-105, SES-109
- TRON: same
- Status: open
- Text: After the signature check a voucher whose amount is equal to or below the highest accepted one gets 200 OK with no state change (MUST); verified signatures may be cached by (channelId, cumulativeAmount, signature) (MAY).

## SYS-1413 Voucher amount rules
- Spec: session §11.4, 12.5, 15.5, 15.6, 15.7
- Level: MUST
- Role: Server
- Verification: ST
- Source: SES-091, SES-106, SES-107
- TRON: same
- Status: open
- Text: State advances only for a strictly higher cumulativeAmount whose increase is at least minVoucherDelta, which does not exceed the channel deposit and which fits in uint128.

## SYS-1414 Voucher persisted before service
- Spec: session §12.5
- Level: MUST
- Role: Server
- Verification: ST
- Source: SES-108
- TRON: same
- Status: open
- Text: An accepted voucher is written to durable storage before any service is delivered against it; only then does the highest accepted amount change.

## SYS-1415 Per-channel serialization
- Spec: session §5
- Level: MUST
- Role: Server
- Verification: ST
- Source: SES-003
- TRON: same
- Status: open
- Text: Vouchers may arrive on separate connections; voucher acceptance and balance deduction are atomic and serialized per channel.

## SYS-1416 New stream replaces the active session
- Spec: session §5
- Level: SHOULD
- Role: Server
- Verification: ST
- Source: SES-002
- TRON: same
- Status: open
- Text: A channel has one active session; a new streaming request on a channel with an active session ends the previous one.



# 14. Session flows: channel lifecycle on the TRON network

Open (client pays and broadcasts, the mode certain to work on TRON):

```
   SDK Client                    SDK Server                  TRON network
      |  (1) GET /resource           |                             |
      |----------------------------->|                             |
      |  (2) 402, intent="session",  |                             |
      |      price, escrowContract   |                             |
      |<-----------------------------|                             |
      |  (3a) approve(escrow, deposit)                             |
      |----------------------------------------------------------->|
      |  (3b) open(payee, token, deposit, salt, signer)            |
      |----------------------------------------------------------->|
      |  (3c) wait for inclusion, sign initial voucher             |
      |<-----------------------------------------------------------|
      |  (4) GET /resource           |                             |
      |      Authorization: Payment  |                             |
      |      action=open, type=hash  |                             |
      |----------------------------->|                             |
      |                              |  (5a) transaction info:     |
      |                              |       open() succeeded      |
      |                              |  (5b) read channel state    |
      |                              |<--------------------------->|
      |                              |  (5c) verify voucher, init  |
      |                              |       accounting            |
      |  (6) 200 OK + Receipt        |                             |
      |<-----------------------------|                             |
```

Paying, running low and topping up (no chain interaction for vouchers):

```
   SDK Client                    SDK Server                  TRON network
      |  (7) request + action=voucher (cumulative total)           |
      |----------------------------->|                             |
      |                              |  verify, persist, charge    |
      |  (8) 200 OK + Receipt        |                             |
      |<-----------------------------|                             |
      |        ... repeated; streaming responses may emit          |
      |            payment-need-voucher when balance runs out ...  |
      |  (9) topUp(channelId, additionalDeposit)                   |
      |----------------------------------------------------------->|
      |  (10) action=topUp, type=hash                              |
      |----------------------------->|                             |
      |                              |  (11) verify deposit grew   |
      |                              |<--------------------------->|
      |  (12) 200 OK + Receipt       |                             |
      |<-----------------------------|                             |
      |                              |  (13) settle(voucher) at    |
      |                              |       the server's timing   |
      |                              |---------------------------->|
```

Ending the channel:

```
   Cooperative close
   SDK Client                    SDK Server                  TRON network
      |  (14) action=close, final voucher                          |
      |----------------------------->|                             |
      |                              |  (15) close(voucher)        |
      |                              |---------------------------->|
      |                              |  (16) result SUCCESS:       |
      |                              |       payee paid, payer     |
      |                              |       refunded, finalized   |
      |                              |<----------------------------|
      |  (17) 200 OK + Receipt       |                             |
      |       (transaction ID)       |                             |
      |<-----------------------------|                             |

   Forced close (server unresponsive)
      |  (14') requestClose(channelId)                             |
      |----------------------------------------------------------->|
      |                              |  (15') may still settle or  |
      |                              |        close during grace   |
      |                              |---------------------------->|
      |  (16') after grace period: withdraw(channelId)             |
      |----------------------------------------------------------->|
```

## SYS-1501 Open flow, client-broadcast
- Spec: session §4, 9.2, 12.3
- Level: MUST
- Role: Both
- Verification: SIT
- Source: -
- TRON: new
- Status: open
- Text: Steps (1)-(6) complete through the SDK: after the client's approve and open are included, the escrow holds exactly the deposit for the new channelId, the server accepts the open credential only after SYS-1402..1404 pass, and the first response carries a receipt whose reference is the channelId.

## SYS-1502 Vouchers cause no transactions
- Spec: session §1, 4, 11.4
- Level: MUST (project)
- Role: Both
- Verification: SIT
- Source: -
- TRON: new
- Status: open
- Text: Between open and settlement any number of accepted vouchers results in zero transactions on the TRON network from either side and no change of the on-chain channel state.

## SYS-1503 Top-up flow, client-broadcast
- Spec: session §12.4, 13.3
- Level: MUST
- Role: Both
- Verification: SIT
- Source: -
- TRON: new
- Status: open
- Text: Steps (9)-(12) complete through the SDK: the on-chain deposit grows by additionalDeposit, the server's available balance grows by the same amount, and vouchers above the old deposit are accepted afterwards.

## SYS-1504 Settlement
- Spec: session §9.4.2, 14.1
- Level: MUST/SHOULD
- Role: Server
- Verification: SIT
- Source: SES-063, SES-124
- TRON: adapt
- Status: open
- Text: The server may settle at any time with its highest accepted voucher; for every settle or close it submits it checks the execution result (SYS-503) and treats a failure as definitive, surfacing a typed error and retrying as appropriate; after success the payee balance has grown by the settled difference; payee authorizations for relayed settlement carry a short deadline (SHOULD).

## SYS-1505 Cooperative close
- Spec: session §10.2.5, 14.2
- Level: MUST/SHOULD
- Role: Both
- Verification: SIT
- Source: SES-125, SES-126, SES-127
- TRON: adapt
- Status: open
- Text: On action close the server requires the final cumulativeAmount to cover what it has charged (using its highest accepted voucher if the client's is too low, SHOULD), submits close, and reports the channel closed only after a successful result: the payee has received the settled total, the payer the remainder, the channel is finalized, and the receipt carries the transaction ID; on a failed result it returns a typed error.

## SYS-1506 Forced close
- Spec: session §14.3, 15.16, 15.17
- Level: MUST
- Role: Both
- Verification: SIT
- Source: -
- TRON: new
- Status: open
- Text: When the client calls requestClose the server stops accepting vouchers for the channel (SYS-1410) and settles its highest accepted voucher within the grace period; after the grace period the client's withdraw returns exactly deposit minus settled; withdraw before the grace period fails.

## SYS-1507 Server-paid open and top-up flows
- Spec: session §4, 9.1
- Level: MUST
- Role: Both
- Verification: SIT
- Source: -
- TRON: review
- Status: open
- Text: With feePayer true the client makes no transaction: it signs a funding authorization and the initial voucher, the server submits the relayed escrow function and pays for it, and the resulting channel has the client as payer.
- Note: Decision D12.

## SYS-1508 Idle channels are settled and closed
- Spec: session §15.11, 15.17
- Level: SHOULD
- Role: Server
- Verification: ST/SIT
- Source: SES-140
- TRON: same
- Status: open
- Text: The server settles and closes channels that have been inactive for a configured period (for example 30 days).

## SYS-1509 Server pays for settle and close
- Spec: session §9, 9.3
- Level: MUST (implied)
- Role: Server
- Verification: SIT
- Source: SES-052
- TRON: adapt
- Status: open
- Text: feePayer only concerns open and topUp; settle and close are always paid by the server, so the payee account keeps Energy, Bandwidth or TRX for them under a bounded fee_limit and the server monitors these resources as in SYS-510.



# 15. Session: accounting, streaming and receipt

## SYS-1601 Per-channel accounting state
- Spec: session §13
- Level: MUST
- Role: Server
- Verification: ST
- Source: SES-114
- TRON: same
- Status: open
- Text: The server keeps acceptedCumulative (highest accepted voucher), spent (charged for delivered service) and settledOnChain per channel, all monotonically increasing; available = acceptedCumulative - spent.

## SYS-1602 Insufficient balance -> 402
- Spec: session §13.1
- Level: MUST (implied)
- Role: Server
- Verification: ST
- Source: SES-115
- TRON: same
- Status: open
- Text: Per request the server first applies any new voucher, then answers 402 with a session challenge if available is below the cost of the request.

## SYS-1603 Crash-safe ordering
- Spec: session §13.1, 13.2
- Level: MUST (implied)
- Role: Server
- Verification: ST
- Source: SES-116
- TRON: same
- Status: open
- Text: spent is increased and persisted before service is delivered, and acceptedCumulative is persisted before it is relied on, using transactional storage; after a crash and restart no delivered service is uncharged and no accepted voucher is lost.

## SYS-1604 Balance exhausted mid-stream
- Spec: session §13.3
- Level: MUST
- Role: Server
- Verification: ST
- Source: SES-117, SES-118
- TRON: same
- Status: open
- Text: When the balance runs out during a streaming response the server stops delivering metered content and emits a payment-need-voucher event whose data has channelId, requiredCumulative, acceptedCumulative and deposit as strings.

## SYS-1605 Cost models
- Spec: session §13.5
- Level: MUST/SHOULD
- Role: Server
- Verification: ST
- Source: SES-122, SES-123
- TRON: same
- Status: open
- Text: The server supports a fixed cost per request or a usage-based cost (MUST at least one); for streaming it reserves an estimate before delivery, adjusts spent to measured consumption and pauses when available is exhausted (SHOULD).

## SYS-1606 No double charge for duplicates
- Spec: session §13.4
- Level: MUST
- Role: Server
- Verification: ST
- Source: SES-121
- TRON: same
- Status: open
- Text: A duplicate of an idempotent request (same challenge and Idempotency-Key, SYS-121) never increases spent.

## SYS-1610 Receipt on every paid request
- Spec: session §14.6
- Level: MUST/MAY
- Role: Server
- Verification: ST
- Source: SES-132, SES-133
- TRON: same
- Status: open
- Text: Every successful paid request returns Payment-Receipt; streaming responses carry it in the initial headers and again as a final payment-receipt event; chunked responses may deliver the final one as a trailer when the client sent TE: trailers.

## SYS-1611 Session receipt fields
- Spec: session §14.6
- Level: MUST
- Role: Server
- Verification: ST/SIT
- Source: SES-134, SES-135
- TRON: adapt
- Status: open
- Text: The receipt has method "tron", intent "session", status "success", timestamp, reference equal to channelId, challengeId, channelId, acceptedCumulative, spent and chainId; units, the settlement transaction ID (on settle or close) and confirmations are optional.
- Note: The draft names the optional field txHash; keep the name, value is the TRON transaction ID.



# 16. Session: errors

## SYS-1701 Session HTTP status mapping
- Spec: session §12.7, 16.3
- Level: MUST (implied)
- Role: Server
- Verification: ST
- Source: SES-110
- TRON: same
- Status: open
- Text: 400 for a malformed payload or missing fields; 402 for an invalid signature, signer mismatch, amount above deposit, delta too small, insufficient balance or unknown challenge; 409 when a submitted or referenced transaction failed on-chain; 410 when the channel is unknown or finalized.

## SYS-1702 Session problem types
- Spec: session §12.7, 16.3
- Level: MUST
- Role: Server
- Verification: ST
- Source: SES-111
- TRON: same
- Status: open
- Text: Error bodies are Problem Details with type https://paymentauth.org/problems/session/ followed by invalid-signature, signer-mismatch, amount-exceeds-deposit, delta-too-small, channel-not-found, channel-finalized, challenge-not-found, insufficient-balance or transaction-reverted, the same on every deployment.
- Note: General error rules (fresh challenge, no receipt): SYS-602, SYS-701.

## SYS-1703 Most specific problem, never a raw revert
- Spec: session §7.6, 12.7
- Level: MUST/SHOULD
- Role: Server
- Verification: ST/SIT
- Source: SES-112, SES-113
- TRON: adapt
- Status: open
- Text: A failed validation or failed server-submitted transaction is reported with the most specific session problem type, falling back to transaction-reverted, and never with a raw revert selector or contract error string (MUST); contract errors map as recommended by the spec (SHOULD).
- Note: On TRON every non-SUCCESS execution result (including out of energy) maps to transaction-reverted unless a more specific type applies.



# 17. Session: security

## SYS-1801 Session denial-of-service limits
- Spec: session §15.8
- Level: SHOULD
- Role: Server
- Verification: ST/SIT
- Source: SES-137, SES-138
- TRON: adapt
- Status: open
- Text: The server rate limits voucher submissions (10 per second per session suggested), enforces minVoucherDelta and a minimum deposit, validates format before recovering signatures, and requires a larger minimum deposit when it pays for open and topUp.


# 18. Open decisions

Requirements marked `TRON: review` depend on these. Resolve, then update the requirement and set TRON to adapt or the Status to n/a.

| ID | Decision | Affects |
|---|---|---|
| D1 | Wire format of addresses and hex values: Base58Check addresses (proposed) or 0x hex as in the EVM drafts; 0x prefix on hashes and channelId | SYS-203, SYS-1004 |
| D2 | permit2Address required always, or only when permit2 is offered (proposed) | SYS-204 |
| D3 | Permit2 on TRON: supported deployment address(es) per network, TIP-712 domain compatibility, or drop permit2 (and charge splits) from the first release | SYS-207, SYS-212, SYS-320, SYS-321, SYS-404, SYS-508, SYS-713, SYS-1015, SYS-1122, SYS-1123, SYS-1212 |
| D4 | Token authorization (EIP-3009 semantics): any target TRC-20 implementing transferWithAuthorization (charge) and receiveWithAuthorization (session), or n/a | SYS-208, SYS-330, SYS-405, SYS-509, SYS-1121, SYS-1123, SYS-1211 |
| D5 | source DID form for TRON addresses | SYS-303 |
| D6 | Encoding of the signed transaction in payload.signature | SYS-310 |
| D7 | Accept transactions signed under account permissions / multi-signature | SYS-402 |
| D8 | Duplicate-transaction answer from the node on broadcast | SYS-504 |
| D9 | Default confirmation policy: first block or solidified (for session it delays every open and top-up) | SYS-506 |
| D10 | Behavior while a settlement outcome is unknown (timeout) | SYS-507, SYS-512 |
| D11 | Chain identifier: value of block.chainid on the TVM versus the chainId in TIP-712 domains, challenge and receipt | SYS-1006, SYS-1102, SYS-1301 |
| D12 | Server-paid session funding (feePayer true): depends on D3 or D4; if neither exists on TRON, drop it or define a TRON mechanism (for example resource delegation to the payer) | SYS-1012, SYS-1014, SYS-1120, SYS-1210, SYS-1213, SYS-1214, SYS-1405, SYS-1407, SYS-1408, SYS-1507 |
| D13 | Target tokens for session: verify transfer behavior of each TRC-20 (return values, fee parameters) | SYS-1016, SYS-1103 |
| D14 | Reference escrow: who deploys and owns it per network; immutable without admin (proposed) or with pause/upgrade | SYS-1003, SYS-1116 |
| D15 | Voucher typed-data domain name and version for TRON | SYS-1301 |


# 19. Source map

Every BASE, EVM and SES requirement and the SYS requirement that carries it. Not carried: BASE-043 (a requirement on method-spec
authors, satisfied by the method drafts, not by the SDK).

| Source | Carried by | Source | Carried by |
|---|---|---|---|
| BASE-001 | SYS-101 | EVM-001 | SYS-105 |
| BASE-002 | SYS-702 | EVM-002 | SYS-201 |
| BASE-003 | SYS-703 | EVM-003 | SYS-203 |
| BASE-004 | SYS-704 | EVM-004 | SYS-204 |
| BASE-005 | SYS-705 | EVM-005 | SYS-205 |
| BASE-006 | SYS-122 | EVM-006 | SYS-206 |
| BASE-007 | SYS-701 | EVM-007 | SYS-208 |
| BASE-008 | SYS-101 | EVM-008 | SYS-207 |
| BASE-009 | SYS-102 | EVM-009 | SYS-212 |
| BASE-010 | SYS-103 | EVM-010 | SYS-210 |
| BASE-011 | SYS-104 | EVM-011 | SYS-211 |
| BASE-012 | SYS-104 | EVM-012 | SYS-211 |
| BASE-013 | SYS-104 | EVM-013 | SYS-213 |
| BASE-014 | SYS-004 | EVM-014 | SYS-303 |
| BASE-015 | SYS-005 | EVM-015 | SYS-320 |
| BASE-016 | SYS-105 | EVM-016 | SYS-320 |
| BASE-017 | SYS-107 | EVM-017 | SYS-321 |
| BASE-018 | SYS-106 | EVM-018 | SYS-321 |
| BASE-019 | SYS-109 | EVM-019 | SYS-508 |
| BASE-020 | SYS-116 | EVM-020 | SYS-510 |
| BASE-021 | SYS-117 | EVM-021 | SYS-330 |
| BASE-022 | SYS-117 | EVM-022 | SYS-330 |
| BASE-023 | SYS-108 | EVM-023 | SYS-330 |
| BASE-024 | SYS-110 | EVM-024 | SYS-310 |
| BASE-025 | SYS-111 | EVM-025 | SYS-312 |
| BASE-026 | SYS-112 | EVM-026 | SYS-401 |
| BASE-027 | SYS-111 | EVM-027 | SYS-404 |
| BASE-028 | SYS-107 | EVM-028 | SYS-508 |
| BASE-029 | SYS-301 | EVM-029 | SYS-509 |
| BASE-030 | SYS-301 | EVM-030 | SYS-501 |
| BASE-031 | SYS-302 | EVM-031 | SYS-502 |
| BASE-032 | SYS-601 | EVM-032 | SYS-506 |
| BASE-033 | SYS-601 | EVM-033 | SYS-601 |
| BASE-034 | SYS-602 | EVM-034 | SYS-602 |
| BASE-035 | SYS-113 | EVM-035 | SYS-710 |
| BASE-036 | SYS-114 | EVM-036 | SYS-701 |
| BASE-037 | SYS-115 | EVM-037 | SYS-801 |
| BASE-038 | SYS-115 | EVM-038 | SYS-304 |
| BASE-039 | SYS-304 | EVM-039 | SYS-713 |
| BASE-040 | SYS-701 | EVM-040 | SYS-510 |
| BASE-041 | SYS-701 | EVM-041 | SYS-511 |
| BASE-042 | SYS-125 | EVM-042 | SYS-214 |
| BASE-043 | not carried |  |  |
| BASE-044 | SYS-110 |  |  |
| BASE-045 | SYS-119 |  |  |
| BASE-046 | SYS-123 |  |  |
| BASE-047 | SYS-801 |  |  |
| BASE-048 | SYS-802 |  |  |
| BASE-049 | SYS-803 |  |  |
| BASE-050 | SYS-710 |  |  |
| BASE-051 | SYS-120 |  |  |
| BASE-052 | SYS-121 |  |  |
| BASE-053 | SYS-712 |  |  |
| BASE-054 | SYS-304 |  |  |
| BASE-055 | SYS-804 |  |  |
| BASE-056 | SYS-805 |  |  |
| BASE-057 | SYS-124 |  |  |
| BASE-058 | SYS-305 |  |  |
| BASE-059 | SYS-806 |  |  |
| BASE-060 | SYS-118 |  |  |

| Source | Carried by | Source | Carried by | Source | Carried by |
|---|---|---|---|---|---|
| SES-001 | SYS-1307 | SES-049 | SYS-1012 | SES-097 | SYS-1403 |
| SES-002 | SYS-1416 | SES-050 | SYS-1304 | SES-098 | SYS-1404 |
| SES-003 | SYS-1415 | SES-051 | SYS-1305 | SES-099 | SYS-1405 |
| SES-004 | SYS-1004 | SES-052 | SYS-1509 | SES-100 | SYS-1406 |
| SES-005 | SYS-1005 | SES-053 | SYS-1405 | SES-101 | SYS-1407 |
| SES-006 | SYS-203 | SES-054 | SYS-1212 | SES-102 | SYS-1410 |
| SES-007 | SYS-1004 | SES-055 | SYS-1014 | SES-103 | SYS-1411 |
| SES-008 | SYS-1006 | SES-056 | SYS-1306 | SES-104 | SYS-1411 |
| SES-009 | SYS-1004 | SES-057 | SYS-1123 | SES-105 | SYS-1412 |
| SES-010 | SYS-1016 | SES-058 | SYS-1124 | SES-106 | SYS-1413 |
| SES-011 | SYS-1102 | SES-059 | SYS-1124 | SES-107 | SYS-1413 |
| SES-012 | SYS-1121 | SES-060 | SYS-1124 | SES-108 | SYS-1414 |
| SES-013 | SYS-1104 | SES-061 | SYS-1125 | SES-109 | SYS-1412 |
| SES-014 | SYS-1101 | SES-062 | SYS-1125 | SES-110 | SYS-1701 |
| SES-015 | SYS-1120 | SES-063 | SYS-1504 | SES-111 | SYS-1702 |
| SES-016 | SYS-1014 | SES-064 | SYS-301 | SES-112 | SYS-1703 |
| SES-017 | SYS-1103 | SES-065 | SYS-1202 | SES-113 | SYS-1703 |
| SES-018 | SYS-1104 | SES-066 | SYS-303 | SES-114 | SYS-1601 |
| SES-019 | SYS-1121 | SES-067 | SYS-1201 | SES-115 | SYS-1602 |
| SES-020 | SYS-1121 | SES-068 | SYS-1203 | SES-116 | SYS-1603 |
| SES-021 | SYS-1122 | SES-069 | SYS-1204 | SES-117 | SYS-1604 |
| SES-022 | SYS-1105 | SES-070 | SYS-1210 | SES-118 | SYS-1604 |
| SES-023 | SYS-1105 | SES-071 | SYS-1211 | SES-119 | SYS-1308 |
| SES-024 | SYS-1106 | SES-072 | SYS-1211 | SES-120 | SYS-121 |
| SES-025 | SYS-1106 | SES-073 | SYS-1212 | SES-121 | SYS-1606 |
| SES-026 | SYS-1123 | SES-074 | SYS-1212 | SES-122 | SYS-1605 |
| SES-027 | SYS-1123 | SES-075 | SYS-1212 | SES-123 | SYS-1605 |
| SES-028 | SYS-1107 | SES-076 | SYS-1405 | SES-124 | SYS-1504 |
| SES-029 | SYS-1107 | SES-077 | SYS-1212 | SES-125 | SYS-1505 |
| SES-030 | SYS-1108 | SES-078 | SYS-1205 | SES-126 | SYS-1505 |
| SES-031 | SYS-1109 | SES-079 | SYS-1213 | SES-127 | SYS-1505 |
| SES-032 | SYS-1109 | SES-080 | SYS-1213 | SES-128 | SYS-1114 |
| SES-033 | SYS-1112 | SES-081 | SYS-1206 | SES-129 | SYS-1017 |
| SES-034 | SYS-1112 | SES-082 | SYS-1214 | SES-130 | SYS-1114 |
| SES-035 | SYS-1113 | SES-083 | SYS-1214 | SES-131 | SYS-1309 |
| SES-036 | SYS-1112 | SES-084 | SYS-1408 | SES-132 | SYS-1610 |
| SES-037 | SYS-1110 | SES-085 | SYS-1214 | SES-133 | SYS-1610 |
| SES-038 | SYS-1110 | SES-086 | SYS-1207 | SES-134 | SYS-1611 |
| SES-039 | SYS-1111 | SES-087 | SYS-1301 | SES-135 | SYS-1611 |
| SES-040 | SYS-105 | SES-088 | SYS-1301 | SES-136 | SYS-1304 |
| SES-041 | SYS-1010 | SES-089 | SYS-1301 | SES-137 | SYS-1801 |
| SES-042 | SYS-1011 | SES-090 | SYS-1303 | SES-138 | SYS-1801 |
| SES-043 | SYS-1010 | SES-091 | SYS-1413 | SES-139 | SYS-1115 |
| SES-044 | SYS-1011 | SES-092 | SYS-1401 | SES-140 | SYS-1508 |
| SES-045 | SYS-1011 | SES-093 | SYS-503 | SES-141 | SYS-506 |
| SES-046 | SYS-1012 | SES-094 | SYS-503 | SES-142 | SYS-1306 |
| SES-047 | SYS-1013 | SES-095 | SYS-507 | SES-143 | SYS-1310 |
| SES-048 | SYS-1015 | SES-096 | SYS-1402 | SES-144 | SYS-1310 |
