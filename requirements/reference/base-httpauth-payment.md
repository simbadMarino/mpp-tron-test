# Requirements: "Payment" HTTP Authentication Scheme (base)

Baseline: `draft-httpauth-payment-01` (9 Sep 2026, expires 13 Mar 2027, Standards Track, individual draft).
Chain-agnostic: applies to any payment method, including a TRON method.
Method-specific drafts (e.g. EVM charge) add to these; see `evm-charge.md`.

Field guide
- Level: MUST / SHOULD / MAY as in the spec (RFC 2119). Combined values (e.g. SHOULD/MUST) mean the clause has several parts.
- Role: Server, Client, Both, Method (payment method infrastructure), Method spec (a requirement on spec authors)
- Layer: V = framing vector, M = method/behavioral test with a mock or compliance server, E = end-to-end or deployment check
- Vector: candidate mpp-tools vector file (www-authenticate, authorization, receipt, base64url, challenge-id), taken from the
  README descriptions of those files. NOT verified against the actual vector contents.
- Status: open | n/a (give reason) -- n/a requirements are excluded from coverage gaps

Rules: IDs are permanent; never renumber or reuse; mark deprecated instead.
Parser contract: each requirement starts with `## <ID> <title>` and uses `- Key: value` lines.

## BASE-001 No credential -> 402 with fresh challenge
- Spec: §4.2
- Level: MUST
- Role: Server
- Layer: M/E
- Status: open
- Text: Resource requires payment and no credential is provided: respond 402 with a fresh Payment challenge in WWW-Authenticate.

## BASE-002 Malformed credential -> malformed-credential
- Spec: §4.2, 8.2
- Level: MUST
- Role: Server
- Layer: M
- Vector: authorization
- Status: open
- Text: Invalid base64url or bad JSON in the credential: respond 402 with a fresh challenge and a malformed-credential problem.

## BASE-003 Unknown or used challenge id -> invalid-challenge
- Spec: §4.2, 8.2
- Level: MUST
- Role: Server
- Layer: M
- Status: open
- Text: Unknown or already-used challenge id: respond 402 with a fresh challenge and an invalid-challenge problem.

## BASE-004 Expired challenge -> payment-expired
- Spec: §4.2, 8.2
- Level: MUST
- Role: Server
- Layer: M
- Status: open
- Text: Expired challenge id: respond 402 with a fresh challenge and a payment-expired problem.

## BASE-005 Failed verification -> verification-failed
- Spec: §4.2, 5.3.1, 8.2
- Level: MUST
- Role: Server
- Layer: M
- Status: open
- Text: Invalid proof or failed verification: respond 402 with a fresh challenge and a verification-failed problem.

## BASE-006 Valid payment but policy denial -> 403
- Spec: §4.2, 4.3
- Level: MUST
- Role: Server
- Layer: M
- Status: open
- Text: Payment verified but policy denies access: respond 403 with no challenge. 401 is reserved for authentication failures unrelated to payment.

## BASE-007 Error details in Problem Details body
- Spec: §4.2
- Level: MUST (implied)
- Role: Server
- Layer: M
- Status: open
- Text: Error details go in the response body as Problem Details (RFC 9457), not in WWW-Authenticate parameters.

## BASE-008 402 must carry a Payment challenge
- Spec: §4.2, 4.4.2
- Level: MUST
- Role: Server
- Layer: M
- Vector: www-authenticate
- Status: open
- Text: Servers never return 402 without a WWW-Authenticate header containing at least one Payment challenge.

## BASE-009 When to return 402 (and when not)
- Spec: §4.4.1, 4.4.2
- Level: SHOULD
- Role: Server
- Layer: M
- Status: open
- Text: Return 402 when payment is the primary barrier and a challenge can be built; do not return it for missing authentication (401), missing authorization (403), nonexistent resources (404), or when no challenge can be constructed.

## BASE-010 Authenticate before challenging for payment
- Spec: §4.4.3
- Level: SHOULD
- Role: Server
- Layer: M/E
- Status: open
- Text: When both authentication and payment are required: verify authentication first, return 401 on failure, and issue a 402 Payment challenge only after authentication succeeds.

## BASE-011 Challenge syntax
- Spec: §5.1, App. A
- Level: MUST
- Role: Both
- Layer: V
- Vector: www-authenticate
- Status: open
- Text: Challenge is the scheme Payment followed by auth-params per RFC 9110 / ABNF in Appendix A.

## BASE-012 id parameter
- Spec: §5.1.1
- Level: MUST
- Role: Both
- Layer: V/M
- Vector: www-authenticate
- Status: open
- Text: id is present and non-empty after parsing and unescaping; servers never emit a missing or empty id; clients and parsers reject challenges with a missing or empty id; clients echo id unchanged.

## BASE-013 realm parameter
- Spec: §5.1.1
- Level: MUST
- Role: Server
- Layer: V
- Vector: www-authenticate
- Status: open
- Text: Servers include realm to define the scope of the payment requirement.

## BASE-014 method parameter format
- Spec: §5.1.1, 6.1
- Level: MUST
- Role: Both
- Layer: V
- Vector: www-authenticate
- Status: open
- Text: method is a lowercase ASCII string (1*LOWERALPHA), case-sensitive.

## BASE-015 intent parameter
- Spec: §5.1.1, 7.1
- Level: MUST
- Role: Both
- Layer: V
- Vector: www-authenticate
- Status: open
- Text: intent is a registered entry in the IANA HTTP Payment Intents registry; syntax is 1*(ALPHA/DIGIT/-).

## BASE-016 request parameter encoding
- Spec: §5.1.1
- Level: MUST
- Role: Both
- Layer: V
- Vector: base64url
- Status: open
- Text: request is base64url (RFC 4648) JSON (RFC 8259) with no '=' padding, serialized with JCS (RFC 8785) before encoding.

## BASE-017 digest parameter
- Spec: §5.1.2
- Level: SHOULD/MUST
- Role: Both
- Layer: V/M
- Vector: www-authenticate
- Status: open
- Text: Servers include digest (RFC 9530 format) when the challenge applies to a request with a body; when present, clients submit the credential with a body matching that digest.

## BASE-018 expires parameter
- Spec: §5.1.2
- Level: SHOULD/MUST
- Role: Both
- Layer: V/M
- Vector: www-authenticate
- Status: open
- Text: expires is an RFC 3339 date-time; servers include it; clients never submit credentials for expired challenges.

## BASE-019 description is display-only
- Spec: §5.1.2, 11.6
- Level: MUST
- Role: Both
- Layer: M
- Status: open
- Text: description is never relied on for payment verification.

## BASE-020 Client credential field selection (header parameter)
- Spec: §5.1.2, 5.2
- Level: MUST
- Role: Client
- Layer: M
- Vector: authorization
- Status: open
- Text: Without header the client sends the credential in Authorization; with header=Payment-Authorization it sends it in that field only; clients that do not support Payment-Authorization do not send a credential for that challenge.

## BASE-021 Server accepts credential only from selected field
- Spec: §5.2
- Level: MUST
- Role: Server
- Layer: M
- Status: open
- Text: A credential received in any field other than the one selected by the challenge does not satisfy the challenge.

## BASE-022 header parameter value restriction
- Spec: §5.1.2, 5.2
- Level: MUST
- Role: Both
- Layer: V/M
- Vector: www-authenticate
- Status: open
- Text: Only the value Payment-Authorization is allowed; servers never emit other values; clients treat other values as an unrecognized challenge and send no credential.

## BASE-023 opaque parameter
- Spec: §5.1.2
- Level: MUST
- Role: Both
- Layer: V/M
- Vector: www-authenticate
- Status: open
- Text: opaque is base64url JSON (JCS-serialized) forming a flat string-to-string map; clients return it unchanged; servers include it in the challenge binding.

## BASE-024 Unknown parameters ignored
- Spec: §5.1.2, 9.2.1, 9.3
- Level: MUST
- Role: Client
- Layer: V/M
- Vector: www-authenticate
- Status: open
- Text: Clients ignore unknown challenge parameters (and unknown fields); custom parameters use lowercase names.

## BASE-025 Challenge binding: coverage
- Spec: §5.1.2.1
- Level: MUST
- Role: Server
- Layer: M
- Vector: challenge-id
- Status: open
- Text: Servers bind id to realm, method, intent and request, plus expires, digest, opaque and header when present; description is excluded.

## BASE-026 Challenge binding: verification
- Spec: §5.1.2.1
- Level: MUST
- Role: Server
- Layer: M
- Status: open
- Text: Servers verify the binding on every credential and reject credentials whose echoed challenge parameters do not match the expected binding.

## BASE-027 HMAC-SHA256 binding layout
- Spec: §5.1.2.1.1
- Level: SHOULD
- Role: Server
- Layer: V
- Vector: challenge-id
- Status: open
- Text: If HMAC-SHA256 is used: seven positional slots (realm, method, intent, request, expires, digest, opaque) with empty strings for absent optionals, an eighth header slot only when present, joined with '|', HMAC-SHA256 with a server secret, base64url without padding.

## BASE-028 Digest verification
- Spec: §5.1.3
- Level: MUST
- Role: Server
- Layer: M
- Status: open
- Text: When the challenge has a digest, compute the digest of the current request body, compare, and reject the credential on mismatch.

## BASE-029 Credential encoding
- Spec: §5.2
- Level: MUST
- Role: Both
- Layer: V
- Vector: authorization
- Status: open
- Text: Field value is the scheme Payment, one or more spaces, then base64url (no padding) of a JSON object.

## BASE-030 Credential fields
- Spec: §5.2
- Level: MUST
- Role: Both
- Layer: V
- Vector: authorization
- Status: open
- Text: JSON object has challenge (required object), payload (required object), and source (optional string, DID recommended).

## BASE-031 Credential challenge object
- Spec: §5.2
- Level: MUST
- Role: Client
- Layer: V/M
- Vector: authorization
- Status: open
- Text: The echoed challenge object carries id, realm, method, intent, request, plus description, opaque, digest, expires and header when present in the challenge; if the challenge had no header, the client does not include header.

## BASE-032 Payment-Receipt on success
- Spec: §5.3
- Level: SHOULD
- Role: Server
- Layer: V/M
- Vector: receipt
- Status: open
- Text: Successful responses include Payment-Receipt (base64url JSON) with status, method, timestamp (RFC 3339) and reference.

## BASE-033 Receipt status semantics
- Spec: §5.3.1
- Level: MUST
- Role: Server
- Layer: V/M
- Vector: receipt
- Status: open
- Text: Receipt status is always success, and receipts appear only on 2xx responses.

## BASE-034 No receipt on error responses
- Spec: §5.3.1
- Level: MUST
- Role: Server
- Layer: M/E
- Status: open
- Text: Payment-Receipt is never returned on error responses; failures use status codes and Problem Details.

## BASE-035 Multiple challenges
- Spec: §7.3, B.4
- Level: MAY/SHOULD
- Role: Both
- Layer: M
- Vector: www-authenticate
- Status: open
- Text: Servers MAY issue several Payment challenges; clients choose one; clients treat unrecognized intents as unsupported.

## BASE-036 Accept-Payment syntax
- Spec: §7.4, App. A
- Level: MAY
- Role: Client
- Layer: V
- Status: open
- Text: Header lists method/intent ranges with wildcards and optional q weights (default q=1, q=0 means do not use).

## BASE-037 Accept-Payment server behavior
- Spec: §7.4
- Level: SHOULD
- Role: Server
- Layer: M
- Status: open
- Text: Filter to challenges matching a range with q>0, order by descending q, keep server order for ties, prefer the most specific matching range.

## BASE-038 Accept-Payment absent, malformed or unmatched
- Spec: §7.4
- Level: MUST/MAY
- Role: Server
- Layer: M
- Status: open
- Text: Absent header: behave as if any method/intent is accepted. Malformed header or no match: server MAY ignore it.

## BASE-039 Challenge is authoritative
- Spec: §7.4
- Level: MUST
- Role: Client
- Layer: M
- Status: open
- Text: Clients validate the returned challenge before authorizing payment, even when Accept-Payment was used.

## BASE-040 Problem Details format
- Spec: §8.1
- Level: SHOULD
- Role: Server
- Layer: M
- Status: open
- Text: 402 responses carry RFC 9457 bodies; the type URI corresponds to a defined problem type under https://paymentauth.org/problems/.

## BASE-041 Problem types and statuses
- Spec: §8.2
- Level: SHOULD
- Role: Server
- Layer: M
- Status: open
- Text: Types: payment-required, payment-insufficient, payment-expired, verification-failed, malformed-credential, invalid-challenge (402) and method-unsupported (400).

## BASE-042 Retry-After
- Spec: §8.3
- Level: SHOULD
- Role: Server
- Layer: M
- Status: open
- Text: Servers use Retry-After to indicate when clients may retry.

## BASE-043 Method specification content
- Spec: §9.1
- Level: MUST
- Role: Method spec
- Layer: -
- Status: open
- Text: A payment method specification defines: method identifier, request schema, payload schema, verification procedure, settlement procedure, and security considerations.

## BASE-044 Versioning rules
- Spec: §9.2
- Level: MUST/MAY
- Role: Both
- Layer: M
- Status: open
- Text: No wire version in the core protocol; unknown parameters and fields are ignored; methods MAY add a version in methodDetails (absent means 1); intents are not versioned.

## BASE-045 Size limits
- Spec: §9.4
- Level: SHOULD/MUST
- Role: Both
- Layer: M
- Status: open
- Text: Servers keep challenges under 8KB; clients handle challenges of at least 4KB; servers handle credentials of at least 4KB.

## BASE-046 Character encoding and locale
- Spec: §10
- Level: SHOULD
- Role: Both
- Layer: M
- Status: open
- Text: Strings are UTF-8; realm should be ASCII; description should follow Accept-Language.

## BASE-047 TLS required
- Spec: §11.2
- Level: MUST
- Role: Both
- Layer: E
- Status: open
- Text: TLS 1.2 or later (1.3 recommended); servers never issue challenges over plain HTTP; clients never send credentials over plain HTTP; non-TLS messages should be rejected.

## BASE-048 Credential handling and logging
- Spec: §11.2.1, 11.7, 11.8
- Level: MUST/SHOULD
- Role: Both
- Layer: E
- Status: open
- Text: Credentials and Payment-Receipt are treated as sensitive: not logged or included in errors, debug output or analytics; stored only in memory and cleared after use.

## BASE-049 Challenge-binding secret management
- Spec: §11.2.2
- Level: MUST/SHOULD
- Role: Server
- Layer: E
- Status: open
- Text: The binding secret stays server-side, is never disclosed or logged; on rotation, challenges issued under the previous secret keep verifying until they expire.

## BASE-050 Single-use proof semantics
- Spec: §11.3
- Level: MUST
- Role: Method
- Layer: M/E
- Status: open
- Text: A payment proof is usable exactly once; reuse is rejected.

## BASE-051 No side effects for unpaid requests
- Spec: §11.4
- Level: MUST
- Role: Server
- Layer: M/E
- Status: open
- Text: Unpaid requests that trigger a 402 do not modify server state beyond recording the challenge.

## BASE-052 Idempotency-Key support
- Spec: §11.4
- Level: SHOULD
- Role: Server
- Layer: M/E
- Status: open
- Text: For POST/PUT/DELETE accept Idempotency-Key; a retry with the same key and a valid credential returns the original response without re-executing.

## BASE-053 Concurrent credential use
- Spec: §11.5
- Level: MUST/SHOULD
- Role: Server
- Layer: E
- Status: open
- Text: Concurrent requests with the same credential produce at most one settlement and one resource delivery; use atomic operations or locks.

## BASE-054 Client amount verification
- Spec: §11.6
- Level: MUST
- Role: Client
- Layer: M
- Status: open
- Text: Before authorizing, clients verify the amount is reasonable, the recipient is expected, the currency is expected, and the validity window is appropriate.

## BASE-055 No account requirement; privacy
- Spec: §11.7
- Level: MUST/SHOULD
- Role: Server
- Layer: E
- Status: open
- Text: Servers never require user accounts for payment; methods should offer pseudonymous options.

## BASE-056 Intermediary handling of 402
- Spec: §11.9
- Level: SHOULD/MUST
- Role: Both
- Layer: E
- Status: open
- Text: Servers do not rely on intermediary-specific 402 handling; clients handle 402 through any intermediary.

## BASE-057 Caching headers
- Spec: §11.10
- Level: MUST
- Role: Server
- Layer: V/M
- Status: open
- Text: 402 responses carry Cache-Control: no-store; responses with Payment-Receipt carry Cache-Control: private; when the credential is in a non-Authorization field every response carries private or no-store.

## BASE-058 Cross-origin and user consent
- Spec: §11.11
- Level: SHOULD
- Role: Client
- Layer: E
- Status: open
- Text: Clients display the requesting origin, require explicit user confirmation, and do not auto-respond to challenges.

## BASE-059 Rate limiting
- Spec: §11.12
- Level: SHOULD
- Role: Server
- Layer: E
- Status: open
- Text: Rate limit challenge issuance and credential verification attempts.

## BASE-060 Single credential per request
- Spec: §B.4
- Level: MUST/SHOULD
- Role: Both
- Layer: M
- Status: open
- Text: Clients send exactly one Payment credential, in the field selected by the chosen challenge; servers SHOULD reject requests with multiple Payment credentials with 400.

