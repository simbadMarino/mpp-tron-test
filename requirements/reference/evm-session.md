# Requirements: EVM session method (spec-derived baseline)

Baseline: `draft-evm-session-00` (11 Nov 2026, expires 15 May 2027).
Base scheme requirements: see `base-httpauth-payment.md` (BASE-xxx).
Scope: sections 4 to 15 of the draft (session flow, escrow contract, request and credential schemas, voucher signing, verification, accounting, settlement, security considerations).
Not yet extracted: `draft-payment-intent-session` (session intent) -> separate ID range.

Field guide
- Spec: section number(s) of the draft
- Level: MUST / SHOULD / MAY as in the spec (RFC 2119); "MUST (implied)" = stated normatively without a keyword; RECOMMENDED is recorded as SHOULD
- Role: Server | Client | Both | Contract (the escrow contract itself)
- Layer: V = framing/encoding vector, M = method-level (mocked chain), E = end-to-end on a real chain, C = escrow contract behavior
- TRON: same = applies as written, adapt = needs adaptation, review = unsure if TRON supports it
- Status: open | n/a (give reason) -- n/a requirements are excluded from coverage gaps

Rules: IDs are permanent. Never renumber or reuse; mark deprecated instead.
Parser contract: each requirement starts with `## <ID> <title>` and uses `- Key: value` lines.

## SES-001 Voucher and close use the paid resource URI
- Spec: §4, 14.5
- Level: SHOULD
- Role: Both
- Layer: M
- TRON: same
- Status: open
- Text: Voucher updates and close requests are sent to the same resource URI that requires payment (there is no separate session endpoint); servers SHOULD accept voucher updates via any HTTP method; clients MAY use HEAD for voucher-only updates that need no response body.

## SES-002 New stream replaces the active session
- Spec: §5
- Level: SHOULD
- Role: Server
- Layer: M
- TRON: same
- Status: open
- Text: A channel supports one active session at a time; when a new streaming request arrives on a channel that already has an active session, the server SHOULD terminate the previous session and start a new one.

## SES-003 Voucher processing is atomic and serialized per channel
- Spec: §5
- Level: MUST
- Role: Server
- Layer: M
- TRON: same
- Status: open
- Text: Voucher updates MAY arrive on separate HTTP connections (including HTTP/2 streams) and MUST be processed atomically with respect to balance updates; voucher acceptance and balance deduction are serialized per channel to prevent race conditions.

## SES-004 Lowercase 0x hex for byte arrays
- Spec: §6.1
- Level: MUST
- Role: Both
- Layer: V
- TRON: adapt
- Status: open
- Text: channelId, signatures and hashes use lowercase hexadecimal with 0x prefix and no padding or truncation (bytes32 = 66 chars, signature = 132 chars, address = 42 chars). TRON: transaction IDs are conventionally shown without 0x and addresses are Base58Check; decide the wire form for each.

## SES-005 Signatures are 65-byte r||s||v, never EIP-2098
- Spec: §6.1
- Level: MUST
- Role: Both
- Layer: V/M
- TRON: same
- Status: open
- Text: All signatures are 65 bytes encoded r (32) || s (32) || v (1) as a single bytes value; implementations MUST NOT produce EIP-2098 compact 64-byte signatures, MAY accept them, and MUST NOT require clients to produce them.

## SES-006 Address display form and comparison
- Spec: §6.1
- Level: MUST/SHOULD
- Role: Both
- Layer: V/M
- TRON: adapt
- Status: open
- Text: Address fields in the request (currency, recipient, escrowContract) SHOULD use EIP-55 mixed-case for display and MUST be compared by decoded 20-byte value, not string form. TRON: Base58Check T-addresses (21 bytes with 0x41) must be mapped to the 20-byte form before comparison; EIP-55 does not apply.

## SES-007 Integers are decimal strings
- Spec: §6.2
- Level: MUST (implied)
- Role: Both
- Layer: V
- TRON: same
- Status: open
- Text: Integer values such as amounts (cumulativeAmount, deposits) and signed-data timestamps (validAfter, validBefore, deadline) are encoded as decimal strings in JSON.

## SES-008 chainId is a JSON number converted to uint256
- Spec: §6.2
- Level: MUST
- Role: Both
- Layer: V/M
- TRON: adapt
- Status: open
- Text: chainId is encoded as a JSON number; implementations MUST convert it to uint256 when constructing the EIP-712 domain separator. TRON: the chain identifier used in TIP-712 domains and returned by block.chainid in the TVM needs to be pinned down and may not match the EVM chain-ID convention.

## SES-009 Timestamp formats
- Spec: §6.3
- Level: MUST (implied)
- Role: Both
- Layer: V
- TRON: same
- Status: open
- Text: HTTP headers and receipt fields use RFC 3339 timestamps; timestamps inside EIP-712 signed data use Unix seconds as decimal strings.

## SES-010 Escrow restricted to well-behaved tokens
- Spec: §7
- Level: MUST
- Role: Server
- Layer: M/C
- TRON: adapt
- Status: open
- Text: The escrow is used only with well-behaved ERC-20 tokens that transfer exactly the requested amount; it MUST NOT be used with fee-on-transfer or rebasing tokens. TRON: TRC-20 tokens; check candidate tokens (e.g. USDT) for latent fee parameters and non-standard transfer return values.

## SES-011 Deterministic channelId computation
- Spec: §7.1
- Level: MUST
- Role: Contract
- Layer: C/V
- TRON: adapt
- Status: open
- Text: channelId = keccak256(abi.encode(payer, payee, token, salt, authorizedSigner, address(this), block.chainid)), computed by the contract's computeChannelId() or equivalent logic, binding the channel to one escrow deployment and chain. TRON: addresses enter abi.encode in their 20-byte form and block.chainid has TVM-specific semantics; off-chain computation must match.

## SES-012 Payer of a relayed open is the from argument
- Spec: §7.1, 7.4
- Level: MUST (implied)
- Role: Contract
- Layer: C
- TRON: review
- Status: open
- Text: For openWithAuthorization and openWithPermit2 the payer used in the channelId computation and stored in the channel is the from argument (the depositor), not the relayer that submits the transaction. TRON: only relevant if a relayed open path exists (EIP-3009 or Permit2 availability unknown).

## SES-013 Channels and vouchers have no expiry
- Spec: §7.2, 15.11
- Level: MUST (implied)
- Role: Contract
- Layer: C
- TRON: same
- Status: open
- Text: Channels have no expiry and remain open until explicitly closed (cooperative close or forced close); vouchers have no validUntil and remain valid until the channel closes.

## SES-014 Mandatory core functions
- Spec: §7.3
- Level: MUST
- Role: Contract
- Layer: C
- TRON: same
- Status: open
- Text: Every compliant escrow implements open, settle, topUp, close, requestClose and withdraw.

## SES-015 Relayed profile is optional and may be partial
- Spec: §7.3, 9.3, 9.4
- Level: MAY
- Role: Contract
- Layer: C
- TRON: review
- Status: open
- Text: The Relayed / Gasless Operations profile (openWithAuthorization, topUpWithAuthorization, openWithPermit2, topUpWithPermit2, settleWithAuthorization, closeWithAuthorization) MAY be omitted entirely or implemented as any subset; the EIP-3009 and Permit2 payer-funded paths are alternatives. TRON: payer-funded paths depend on EIP-3009 or Permit2, which may not be available; the payee-side functions only need typed-data signatures.

## SES-016 No advertising of unimplemented capabilities
- Spec: §7.3, 9.4
- Level: MUST
- Role: Server
- Layer: M
- TRON: same
- Status: open
- Text: A server MUST NOT advertise a capability (feePayer: true, or relayed settle/close) whose backing function its escrow does not implement; feePayer: true requires at least one payer-funded function for the offered type and relayed settlement requires the corresponding payee-side function.

## SES-017 open creates the channel and rejects an existing channelId
- Spec: §7.3.1, 7.4
- Level: MUST
- Role: Contract
- Layer: C
- TRON: adapt
- Status: open
- Text: open(payee, token, deposit, salt, authorizedSigner) is callable by anyone, makes the caller the payer, pulls deposit via transferFrom after a prior approve, returns the channelId, and MUST revert if a channel with the computed channelId already exists. TRON: TRC-20 transferFrom on some tokens does not return a standard bool; the contract needs tolerant transfer handling.

## SES-018 Channel records are retained permanently
- Spec: §7.3.1, 15.2
- Level: MUST
- Role: Contract
- Layer: C
- TRON: same
- Status: open
- Text: The finalized flag is sticky (set once at close/withdraw, never cleared) and the channel record MUST NOT be deleted, so that the already-exists check rejects every re-open of a used channelId, including a finalized one.

## SES-019 openWithAuthorization pulls via receiveWithAuthorization
- Spec: §7.3.2, 15.13
- Level: MUST
- Role: Contract
- Layer: C
- TRON: review
- Status: open
- Text: openWithAuthorization (callable by anyone) MUST pull funds with the token's receiveWithAuthorization (not transferWithAuthorization), using the bytes-signature overload with the packed 65-byte signature; tokens exposing only the (v, r, s) interface are not supported. TRON: unknown whether target TRC-20 tokens implement receiveWithAuthorization at all.

## SES-020 openWithAuthorization validates the derived nonce
- Spec: §7.3.2, 15.13
- Level: MUST/SHOULD
- Role: Contract
- Layer: C
- TRON: review
- Status: open
- Text: The contract MUST recompute the expected EIP-3009 nonce as keccak256(abi.encode(from, payee, token, salt, authorizedSigner)), revert before invoking the token if the supplied nonce differs (SHOULD use a dedicated error such as NonceMismatch()), pass the validated nonce to receiveWithAuthorization, and MUST NOT skip the check or fall back to the caller-supplied value. TRON: depends on EIP-3009 support in the token.

## SES-021 openWithPermit2 uses a witness transfer
- Spec: §7.3.3, 15.13
- Level: MUST
- Role: Contract
- Layer: C
- TRON: review
- Status: open
- Text: openWithPermit2 (callable by anyone) MUST use permitWitnessTransferFrom (not permitTransferFrom), constructing the permit with permitted.token = token, permitted.amount = deposit, transferDetails.to = address(this), requestedAmount = deposit and witnessHash = keccak256(abi.encode(CHANNEL_OPEN_WITNESS_TYPEHASH, payee, salt, authorizedSigner)), so that a signature over a different payee, salt or authorizedSigner reverts. TRON: no canonical Permit2 deployment exists.

## SES-022 settle is payee-only
- Spec: §7.3.4, 7.4
- Level: MUST
- Role: Contract
- Layer: C
- TRON: same
- Status: open
- Text: settle(channelId, cumulativeAmount, signature) MUST revert if msg.sender != channel.payee.

## SES-023 settle requires a strictly increasing amount within the deposit
- Spec: §7.3.4, 15.5
- Level: MUST
- Role: Contract
- Layer: C
- TRON: same
- Status: open
- Text: settle MUST revert if cumulativeAmount <= channel.settled (e.g. AmountNotIncreasing()) and if cumulativeAmount > channel.deposit (e.g. AmountExceedsDeposit()); otherwise it computes delta = cumulativeAmount - channel.settled, sets channel.settled = cumulativeAmount and transfers delta to the payee without closing the channel.

## SES-024 topUp is payer-only
- Spec: §7.3.5, 7.4
- Level: MUST
- Role: Contract
- Layer: C
- TRON: same
- Status: open
- Text: topUp(channelId, additionalDeposit) pulls the additional deposit after a prior approve and MUST revert if msg.sender != channel.payer.

## SES-025 topUp cancels a pending close
- Spec: §7.3.5, 10.2.3
- Level: MUST
- Role: Contract
- Layer: C
- TRON: same
- Status: open
- Text: If a close request is pending (channel.closeRequestedAt != 0), topUp MUST reset closeRequestedAt to 0, cancelling the pending close.

## SES-026 topUpWithAuthorization validates the derived nonce
- Spec: §7.3.6, 15.13
- Level: MUST
- Role: Contract
- Layer: C
- TRON: review
- Status: open
- Text: topUpWithAuthorization (callable by anyone) MUST recompute the expected EIP-3009 nonce as keccak256(abi.encode(channelId, additionalDeposit, from, topUpSalt)) and revert (e.g. NonceMismatch()) before invoking the token if the supplied nonce does not match; funds are pulled via receiveWithAuthorization. TRON: depends on EIP-3009 support in the token.

## SES-027 topUpWithPermit2 binds the channelId as witness
- Spec: §7.3.7
- Level: MUST
- Role: Contract
- Layer: C
- TRON: review
- Status: open
- Text: topUpWithPermit2 (callable by anyone) MUST call permitWitnessTransferFrom with a ChannelTopUpWitness binding channelId, using permitted.token = channel.token from the existing channel record; no topUpSalt is used. TRON: no canonical Permit2 deployment exists.

## SES-028 close is payee-only, settles and refunds atomically
- Spec: §7.3.8, 7.4, 15.16
- Level: MUST
- Role: Contract
- Layer: C
- TRON: same
- Status: open
- Text: close(channelId, cumulativeAmount, signature) MUST revert if msg.sender != channel.payee; on success it settles the outstanding voucher delta to the payee, refunds the remainder to the payer and finalizes the channel in a single transaction.

## SES-029 close forfeit path may skip the voucher signature
- Spec: §7.3.8, 9.4.2
- Level: MAY
- Role: Contract
- Layer: C
- TRON: same
- Status: open
- Text: If cumulativeAmount <= channel.settled on close (payee forfeits any uncollected amount), the contract MAY skip voucher signature verification and the signature MAY be empty; the same applies to voucherSignature in closeWithAuthorization.

## SES-030 requestClose is payer-only and starts the grace period
- Spec: §7.3.9, 7.4
- Level: MUST
- Role: Contract
- Layer: C
- TRON: same
- Status: open
- Text: requestClose(channelId) records the close request time (closeRequestedAt) and MUST revert if msg.sender != channel.payer, if no channel exists for channelId, or if the channel is already finalized.

## SES-031 withdraw revert conditions
- Spec: §7.3.10, 7.4
- Level: MUST
- Role: Contract
- Layer: C
- TRON: same
- Status: open
- Text: withdraw(channelId) MUST revert if msg.sender != channel.payer, if the channel is already finalized, if no close has been requested (closeRequestedAt == 0), or if block.timestamp < closeRequestedAt + CLOSE_GRACE_PERIOD.

## SES-032 withdraw pays the unsettled remainder and finalizes
- Spec: §7.3.10
- Level: MUST (implied)
- Role: Contract
- Layer: C
- TRON: same
- Status: open
- Text: On success withdraw transfers channel.deposit - channel.settled to the payer and sets finalized atomically with the payout, so no second payout is possible.

## SES-033 Voucher signatures must be canonical low-s
- Spec: §7.5, 15.9
- Level: MUST
- Role: Contract
- Layer: C
- TRON: same
- Status: open
- Text: For all functions accepting voucher signatures the contract MUST reject ECDSA signatures with s > secp256k1_order / 2 (half-order 0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF5D576E7357A4501DDFE92F46681B20A0).

## SES-034 Voucher signer must be the authorized signer
- Spec: §7.5
- Level: MUST
- Role: Contract
- Layer: C
- TRON: same
- Status: open
- Text: The contract MUST recover the signer from the EIP-712 voucher signature and verify it equals channel.authorizedSigner if non-zero, otherwise channel.payer.

## SES-035 Contract-wallet signers verified via ERC-1271
- Spec: §7.5, 3
- Level: MUST (implied)
- Role: Contract
- Layer: C
- TRON: adapt
- Status: open
- Text: The signer may be an EOA (verified via ECDSA) or an ERC-1271 contract wallet (verified via isValidSignature). TRON: isValidSignature is a plain TVM contract call, but TRON-native multi-signature (account permissions) is not a contract wallet and cannot sign vouchers this way.

## SES-036 Voucher domain bound to the escrow address
- Spec: §7.5, 15.1
- Level: MUST
- Role: Contract
- Layer: C
- TRON: adapt
- Status: open
- Text: The contract MUST use its own address as verifyingContract in the EIP-712 domain separator so vouchers cannot be replayed across escrow deployments. TRON: TIP-712 encodes the contract address in its 20-byte form (0x41 prefix stripped).

## SES-037 Revert on unknown or finalized channel
- Spec: §7.6
- Level: MUST
- Role: Contract
- Layer: C
- TRON: same
- Status: open
- Text: settle, topUp, close (each including WithAuthorization and WithPermit2 variants where they exist), requestClose and withdraw revert when no channel exists for the channelId or the channel is already finalized.

## SES-038 Revert on zero deposit and deposit overflow
- Spec: §7.6
- Level: MUST
- Role: Contract
- Layer: C
- TRON: same
- Status: open
- Text: open and topUp (including their WithAuthorization and WithPermit2 variants) revert when the deposit amount is 0 or when the deposit would exceed the uint128 bound.

## SES-039 Recommended revert vocabulary
- Spec: §7.6
- Level: SHOULD
- Role: Contract
- Layer: C
- TRON: same
- Status: open
- Text: The error names ChannelAlreadyExists, ChannelNotFound, ChannelFinalized, NotPayee, NotPayer, AmountNotIncreasing, AmountExceedsDeposit, InvalidSignature, NonceMismatch, NonceAlreadyUsed, AuthorizationExpired, CloseNotReady, ZeroDeposit and DepositOverflow are RECOMMENDED; implementations MAY use different names or revert representations.

## SES-040 Request is JCS-serialized and base64url-encoded
- Spec: §8
- Level: MUST (implied)
- Role: Server
- Layer: V
- TRON: same
- Status: open
- Text: The request parameter of the WWW-Authenticate challenge is a JSON object serialized with JCS (RFC 8785) and then base64url-encoded.

## SES-041 Required request fields
- Spec: §8.1
- Level: MUST
- Role: Server
- Layer: V/M
- TRON: adapt
- Status: open
- Text: amount (string, price per unit of service in base units, not a total charge), currency (token contract address) and recipient (payee address) are REQUIRED. TRON: currency is a TRC-20 contract and both addresses need a Base58Check or hex format decision.

## SES-042 Optional request fields
- Spec: §8.1
- Level: MAY
- Role: Server
- Layer: V
- TRON: same
- Status: open
- Text: unitType (string, unit being priced), suggestedDeposit (string, base units), description (string) and externalId (string) are OPTIONAL.

## SES-043 Required methodDetails
- Spec: §8.2
- Level: MUST
- Role: Server
- Layer: V/M
- TRON: adapt
- Status: open
- Text: methodDetails.chainId (number) and methodDetails.escrowContract (address string) are REQUIRED. TRON: chain identifier convention and escrow address format need a decision.

## SES-044 minVoucherDelta default
- Spec: §8.2
- Level: MAY
- Role: Server
- Layer: V/M
- TRON: same
- Status: open
- Text: methodDetails.minVoucherDelta (string, base units) is OPTIONAL and defaults to "0", meaning any positive increment is accepted.

## SES-045 feePayer default
- Spec: §8.2
- Level: MAY
- Role: Server
- Layer: V/M
- TRON: adapt
- Status: open
- Text: methodDetails.feePayer (boolean) is OPTIONAL and defaults to false; if true the server pays gas for open/topUp. TRON: fees are Energy/Bandwidth; what server-paid fees mean without a relayed deposit path needs a decision.

## SES-046 credentialTypes values, order and default
- Spec: §8.2, 9.1
- Level: MAY
- Role: Server
- Layer: V/M
- TRON: review
- Status: open
- Text: Servers MAY advertise methodDetails.credentialTypes as an ordered preference list of every accepted payload.type, drawn from "permit2", "authorization" and "hash" (no full signed-transaction type); if omitted it defaults to ["hash"]. TRON: only "hash" is certain to be usable.

## SES-047 Client honors credentialTypes
- Spec: §8.2, 9.1, 9.2
- Level: MUST
- Role: Client
- Layer: M
- TRON: same
- Status: open
- Text: Clients select the first listed type they can produce unless local policy chooses otherwise and MUST NOT submit a format absent from the list; in particular type="hash" MUST NOT be submitted when credentialTypes is present and omits "hash".

## SES-048 permit2Contract advertisement and use
- Spec: §8.2, 10.2.2
- Level: MUST
- Role: Both
- Layer: M
- TRON: review
- Status: open
- Text: methodDetails.permit2Contract is OPTIONAL and defaults to the canonical Permit2 address; servers MUST advertise it on any chain whose Permit2 is not at the canonical address; the client MUST use it (or the canonical default) as verifyingContract when signing; it MUST match the escrow's configured Permit2 address. TRON: there is no canonical Permit2 address, so the field would always be required if Permit2 is used at all.

## SES-049 feePayer true lists a server-submitted type
- Spec: §8.2
- Level: MUST
- Role: Server
- Layer: M
- TRON: review
- Status: open
- Text: When feePayer is true, servers that want clients to use a server-submitted open/topUp format MUST include at least one such type backed by the escrow in credentialTypes ("authorization" if openWithAuthorization is deployed, "permit2" if openWithPermit2 is deployed) and MAY also include "hash" as a client-broadcast fallback. TRON: depends on EIP-3009 or Permit2 availability.

## SES-050 New channel: client derives salt and channelId
- Spec: §8.2
- Level: MUST (implied)
- Role: Client
- Layer: M/E
- TRON: adapt
- Status: open
- Text: Channel reuse is OPTIONAL; when the challenge carries no channelId the client generates a random salt, computes channelId with the section 7.1 formula, opens the channel on-chain and returns the channelId in the credential. TRON: off-chain channelId computation must use the 20-byte address forms and the TVM chain identifier.

## SES-051 Existing channel: client checks remaining balance
- Spec: §8.2
- Level: MUST
- Role: Client
- Layer: E
- TRON: same
- Status: open
- Text: When the server suggests an existing channel via methodDetails.channelId, the client MUST verify channel.deposit - channel.settled >= amount before resuming.

## SES-052 feePayer affects only open and topUp
- Spec: §9, 9.3
- Level: MUST (implied)
- Role: Server
- Layer: E
- TRON: adapt
- Status: open
- Text: feePayer affects only the client-originated funding transactions (open, topUp); settle and close are always server-initiated and the server pays for them regardless of feePayer, either directly or via the relayed payee-side functions. TRON: the server needs Energy/Bandwidth (or TRX with fee_limit) for settle and close.

## SES-053 Server-paid funding uses a token-pull authorization
- Spec: §9.1
- Level: MUST (implied)
- Role: Both
- Layer: E
- TRON: review
- Status: open
- Text: When feePayer is true the client submits a token-pull authorization signature (type="authorization" for EIP-3009 or type="permit2") instead of broadcasting a transaction, and the server submits openWith.../topUpWith... and pays the fee. TRON: both authorization formats may be unavailable.

## SES-054 Permit2 path requires prior approval
- Spec: §9.1, 15.14
- Level: MUST
- Role: Client
- Layer: E
- TRON: review
- Status: open
- Text: On the Permit2 path the payer MUST have previously approved the Permit2 contract for the token. TRON: no canonical Permit2 deployment exists.

## SES-055 feePayer true only for serviceable tokens
- Spec: §9.1
- Level: MUST
- Role: Server
- Layer: M
- TRON: review
- Status: open
- Text: When feePayer is true the currency token MUST support at least one of the advertised server-submitted paths; servers MUST NOT advertise feePayer: true for tokens whose authorization paths they cannot service. TRON: EIP-3009 support of target TRC-20 tokens is unknown.

## SES-056 Client-paid open
- Spec: §9.2, 10.2.1
- Level: MUST (implied)
- Role: Client
- Layer: E
- TRON: adapt
- Status: open
- Text: When feePayer is false or omitted the client calls approve(escrow, deposit) and open() itself and pays the fee; smart wallets MAY batch approve + open in an ERC-4337 UserOperation and a Paymaster MAY sponsor it. TRON: fees are Energy/Bandwidth with fee_limit and there is no ERC-4337 EntryPoint path.

## SES-057 Third-party top-ups credit the channel only
- Spec: §9.4.1
- Level: MUST (implied)
- Role: Contract
- Layer: C
- TRON: review
- Status: open
- Text: On the relayed top-up paths the funding from need not equal channel.payer; the contract credits the existing channel and any refund on close or withdraw is still paid to channel.payer. TRON: only relevant if a relayed top-up path exists.

## SES-058 Payee authorization must be signed by channel.payee
- Spec: §9.4.2
- Level: MUST
- Role: Contract
- Layer: C
- TRON: adapt
- Status: open
- Text: settleWithAuthorization and closeWithAuthorization require a voucher signature plus an EIP-712 authorization for this specific call; the contract MUST recover the payeeSignature signer and verify it equals channel.payee (EOA via ECDSA, contract wallet via ERC-1271); any caller may submit. TRON: TIP-712 typed data.

## SES-059 Payee authorization typed data
- Spec: §9.4.2
- Level: MUST (implied)
- Role: Both
- Layer: V/C
- TRON: adapt
- Status: open
- Text: The payee authorization uses SettleAuthorization(bytes32 channelId,uint128 cumulativeAmount,uint256 nonce,uint256 deadline) and CloseAuthorization(bytes32 channelId,uint128 cumulativeAmount,uint256 nonce,uint256 deadline) under the same domain separator as the Voucher. TRON: TIP-712 domain.

## SES-060 Relayed settle/close verify the voucher like settle/close
- Spec: §9.4.2
- Level: MUST
- Role: Contract
- Layer: C
- TRON: same
- Status: open
- Text: settleWithAuthorization and closeWithAuthorization MUST verify the voucher signature exactly as settle/close do (section 7.5), including the strictly increasing rule; only the close forfeit path may omit voucherSignature.

## SES-061 Payee authorization nonce replay protection
- Spec: §9.4.2
- Level: MUST
- Role: Contract
- Layer: C
- TRON: same
- Status: open
- Text: The contract MUST maintain a used-set keyed by (channel.payee, channelId, nonce) and revert (e.g. NonceAlreadyUsed()) if the nonce was already consumed; settle and close authorizations MUST share the same used-set; nonces are arbitrary unused uint256 values with no ordering requirement.

## SES-062 Payee authorization deadline
- Spec: §9.4.2
- Level: MUST
- Role: Contract
- Layer: C
- TRON: same
- Status: open
- Text: settleWithAuthorization and closeWithAuthorization MUST revert (e.g. AuthorizationExpired()) when block.timestamp > deadline.

## SES-063 Payees set short authorization deadlines
- Spec: §9.4.2
- Level: SHOULD
- Role: Server
- Layer: M
- TRON: same
- Status: open
- Text: Payees SHOULD set a short deadline to bound the lifetime of an unsubmitted settle/close authorization.

## SES-064 Credential structure
- Spec: §10, 10.1
- Level: MUST
- Role: Client
- Layer: V
- TRON: same
- Status: open
- Text: The credential is a base64url-encoded JSON object with REQUIRED challenge (echo of the challenge parameters) and payload (session-specific object).

## SES-065 source required for hash credentials
- Spec: §10.1, 10.2.1, 10.2.3, 10.2.4
- Level: MUST
- Role: Client
- Layer: V/M
- TRON: same
- Status: open
- Text: The credential-level source field is REQUIRED when payload type="hash" (open and topUp); it is not required for type="authorization" or "permit2" (payer identified via authorization.from) and is OPTIONAL for action="voucher" and "close" (payer identified from channel state).

## SES-066 source uses did:pkh
- Spec: §10.1
- Level: SHOULD
- Role: Client
- Layer: V
- TRON: adapt
- Status: open
- Text: source SHOULD use the did:pkh method with the chain ID from the challenge and the payer's address (e.g. did:pkh:eip155:196:0x...). TRON: the eip155 namespace does not apply; a TRON chain namespace and address form need a decision.

## SES-067 payload.action discriminator
- Spec: §10.2
- Level: MUST
- Role: Client
- Layer: V
- TRON: same
- Status: open
- Text: payload.action is REQUIRED and is one of "open", "topUp", "voucher", "close".

## SES-068 Open payload with type hash
- Spec: §10.2.1
- Level: MUST
- Role: Client
- Layer: V
- TRON: adapt
- Status: open
- Text: For a client-broadcast open the payload carries REQUIRED action="open", type="hash", channelId (hex bytes32), hash (tx hash of the on-chain open, direct or via ERC-4337 EntryPoint), cumulativeAmount, signature (voucher signature for the initial amount) and salt (bytes32 hex), plus OPTIONAL authorizedSigner (defaults to payer if omitted). TRON: hash is a 32-byte transaction ID; no EntryPoint path; authorizedSigner address format.

## SES-069 Initial voucher is required at open
- Spec: §10.2.1, 10.2.2
- Level: MUST
- Role: Client
- Layer: M
- TRON: same
- Status: open
- Text: Every open payload includes a signed initial voucher (cumulativeAmount typically "0"; field signature for type="hash", voucherSignature for server-submitted types) so the server can settle or close at any time.

## SES-070 Open payload with server-submitted type
- Spec: §10.2.2
- Level: MUST
- Role: Client
- Layer: V
- TRON: review
- Status: open
- Text: For a server-submitted open the payload carries REQUIRED action="open", type ("authorization" or "permit2"), channelId, authorization (object shaped by type), signature (65-byte authorization signature), cumulativeAmount, voucherSignature and salt, plus OPTIONAL authorizedSigner. TRON: both authorization formats may be unavailable.

## SES-071 EIP-3009 authorization object
- Spec: §10.2.2, 15.13
- Level: MUST
- Role: Client
- Layer: V/M
- TRON: review
- Status: open
- Text: For type="authorization" the authorization object carries REQUIRED from (payer), to (MUST be the escrow contract address = methodDetails.escrowContract), value (deposit in base units), validAfter and validBefore (Unix-seconds decimal strings; "0" = immediately) and nonce (bytes32 hex). TRON: EIP-3009 support of target TRC-20 tokens is unknown.

## SES-072 Client derives the EIP-3009 nonce from channel parameters
- Spec: §10.2.2, 7.3.6, 15.13
- Level: MUST
- Role: Client
- Layer: M
- TRON: review
- Status: open
- Text: The EIP-3009 nonce MUST be keccak256(abi.encode(from, payee, token, salt, authorizedSigner)) for open and keccak256(abi.encode(channelId, additionalDeposit, from, topUpSalt)) for topUp; the client MUST sign the EIP-3009 typed data with this derived nonce and MUST transmit it in the credential. TRON: depends on EIP-3009 support in the token.

## SES-073 Permit2 authorization object
- Spec: §10.2.2
- Level: MUST
- Role: Client
- Layer: V
- TRON: review
- Status: open
- Text: For type="permit2" the authorization object carries REQUIRED from (Permit2 owner), permitted {token = request.currency, amount = deposit in base units}, nonce (decimal string, any unused uint256), deadline (decimal string, Unix seconds) and witness. TRON: no canonical Permit2 deployment exists.

## SES-074 Permit2 spender is the escrow
- Spec: §10.2.2
- Level: MUST
- Role: Client
- Layer: M
- TRON: review
- Status: open
- Text: spender is omitted from the authorization object; clients MUST set spender = methodDetails.escrowContract when constructing the Permit2 EIP-712 hash. TRON: no canonical Permit2 deployment exists.

## SES-075 Permit2 witness carries the channel parameters
- Spec: §10.2.2
- Level: MUST
- Role: Client
- Layer: M
- TRON: review
- Status: open
- Text: The witness MUST carry, for open, payee (equal to request.recipient), salt and authorizedSigner (equal to the open-payload fields; an omitted authorizedSigner is the zero address) and, for topUp, channelId (equal to the payload channelId). TRON: no canonical Permit2 deployment exists.

## SES-076 Server rejects a mismatching Permit2 witness
- Spec: §10.2.2
- Level: MUST
- Role: Server
- Layer: M
- TRON: review
- Status: open
- Text: The channel parameters the server passes to the escrow are authoritative; a server MUST reject the credential if authorization.witness disagrees with them rather than forwarding a signature that will revert on-chain. TRON: no canonical Permit2 deployment exists.

## SES-077 Permit2 domain and type strings
- Spec: §10.2.2
- Level: MUST (implied)
- Role: Both
- Layer: V
- TRON: review
- Status: open
- Text: The Permit2 domain is EIP712Domain(string name,uint256 chainId,address verifyingContract) with name "Permit2" and no version; the signed type is PermitWitnessTransferFrom(TokenPermissions permitted,address spender,uint256 nonce,uint256 deadline,<Witness> witness) with ChannelOpenWitness(address payee,bytes32 salt,address authorizedSigner) for open or ChannelTopUpWitness(bytes32 channelId) for topUp, and TokenPermissions(address token,uint256 amount); the witnessTypeString is the suffix from the witness member onward. TRON: no canonical Permit2 deployment exists.

## SES-078 TopUp payload with type hash
- Spec: §10.2.3
- Level: MUST
- Role: Client
- Layer: V
- TRON: adapt
- Status: open
- Text: For a client-broadcast top-up the payload carries REQUIRED action="topUp", type="hash", channelId, hash (tx hash of the on-chain topUp) and additionalDeposit. TRON: hash is a 32-byte transaction ID; no EntryPoint path.

## SES-079 TopUp payload with server-submitted type
- Spec: §10.2.3
- Level: MUST
- Role: Client
- Layer: V
- TRON: review
- Status: open
- Text: For a server-submitted top-up the payload carries REQUIRED action="topUp", type ("authorization" or "permit2"), channelId, authorization (same shapes as for open), signature and additionalDeposit; salt (passed as topUpSalt) is REQUIRED for type="authorization" and omitted for "permit2". TRON: both authorization formats may be unavailable.

## SES-080 additionalDeposit equals the authorization amount
- Spec: §10.2.3
- Level: MUST
- Role: Both
- Layer: M
- TRON: review
- Status: open
- Text: The top-level additionalDeposit MUST equal the authorization amount (authorization.value for "authorization", authorization.permitted.amount for "permit2"); a server MUST reject the credential if the two disagree. TRON: both authorization formats may be unavailable.

## SES-081 Voucher payload
- Spec: §10.2.4
- Level: MUST
- Role: Client
- Layer: V
- TRON: same
- Status: open
- Text: The voucher payload carries REQUIRED action="voucher", channelId, cumulativeAmount (cumulative amount authorized) and signature (EIP-712 voucher signature).

## SES-082 Voucher deposit extension fields
- Spec: §10.2.4
- Level: MAY/MUST
- Role: Client
- Layer: V
- TRON: review
- Status: open
- Text: A voucher payload MAY carry a deposit object; if present, deposit.action ("open" or "topUp"), deposit.type ("authorization" or "permit2"), deposit.authorization (shape per type) and deposit.signature (65 bytes hex) are REQUIRED; deposit.salt is REQUIRED when deposit.action is "open" and, for "topUp", REQUIRED for type="authorization" (as topUpSalt) and unused for "permit2"; deposit.authorizedSigner is OPTIONAL and applies only to "open". TRON: both authorization formats may be unavailable.

## SES-083 Omitted deposit.authorizedSigner means the zero address
- Spec: §10.2.4
- Level: MUST
- Role: Client
- Layer: M
- TRON: review
- Status: open
- Text: When deposit.authorizedSigner is omitted, clients MUST use the zero address (not authorization.from) when deriving the EIP-3009 nonce or constructing the Permit2 witness. TRON: both authorization formats may be unavailable.

## SES-084 Deposit is processed before the voucher
- Spec: §10.2.4, 12.5
- Level: MUST
- Role: Server
- Layer: M/E
- TRON: review
- Status: open
- Text: When deposit is present the server MUST process it first by calling the matching escrow function (openWithAuthorization/topUpWithAuthorization or openWithPermit2/topUpWithPermit2), verify the updated channel state, then validate the voucher against the (possibly newly created) channel; if the deposit fails the server MUST reject the entire credential. TRON: both authorization formats may be unavailable.

## SES-085 deposit.action is topUp for existing channels
- Spec: §10.2.4
- Level: MUST
- Role: Client
- Layer: M
- TRON: review
- Status: open
- Text: For already-existing channels deposit.action MUST be "topUp"; "open" is only for bundling channel creation with the initial voucher. TRON: both authorization formats may be unavailable.

## SES-086 Close payload
- Spec: §10.2.5
- Level: MUST
- Role: Client
- Layer: V
- TRON: same
- Status: open
- Text: The close payload carries REQUIRED action="close", channelId, cumulativeAmount (final cumulative amount) and signature (EIP-712 voucher signature).

## SES-087 Voucher typed-data struct
- Spec: §11.1, 11.3
- Level: MUST (implied)
- Role: Both
- Layer: V
- TRON: same
- Status: open
- Text: The voucher struct is Voucher(bytes32 channelId,uint128 cumulativeAmount); structHash = keccak256(abi.encode(keccak256("Voucher(bytes32 channelId,uint128 cumulativeAmount)"), channelId, cumulativeAmount)).

## SES-088 Voucher domain separator
- Spec: §11.2, 11.3, 15.3
- Level: MUST (implied)
- Role: Both
- Layer: V
- TRON: adapt
- Status: open
- Text: The domain is EIP712Domain(string name,string version,uint256 chainId,address verifyingContract) with name "EVM Payment Channel", version "1", the chain ID and the escrow contract address. TRON: TIP-712 encodes verifyingContract in 20-byte form and uses a TRON chain identifier; whether to keep the domain name is a method decision.

## SES-089 Voucher signing hash and signature encoding
- Spec: §11.3
- Level: MUST (implied)
- Role: Client
- Layer: V
- TRON: same
- Status: open
- Text: signingHash = keccak256("\x19\x01" || domainSeparator || structHash), signed with ECDSA over secp256k1 and encoded as 65 bytes r || s || v with v = 27 or 28.

## SES-090 Vouchers are cumulative totals
- Spec: §11.4, 14.4
- Level: MUST (implied)
- Role: Both
- Layer: M
- TRON: same
- Status: open
- Text: cumulativeAmount is a cumulative total, not an incremental delta; sequential sessions on one channel share the same cumulative counter and the channel's highest accepted voucher amount is the floor for the next voucher.

## SES-091 cumulativeAmount within uint128
- Spec: §11.4, 15.6
- Level: MUST
- Role: Server
- Layer: M
- TRON: same
- Status: open
- Text: The server MUST verify cumulativeAmount <= 2^128 - 1 and reject vouchers exceeding it.

## SES-092 Common credential verification
- Spec: §12.1
- Level: MUST
- Role: Server
- Layer: M
- TRON: same
- Status: open
- Text: Before action-specific verification the server MUST decode the base64url credential and parse the JSON, verify payload.action is recognized, look up the stored challenge by credential.challenge.id, verify all credential.challenge fields exactly match the stored challenge, and verify the challenge has not expired.

## SES-093 Receipt status is always checked
- Spec: §12.2
- Level: MUST
- Role: Server
- Layer: E
- TRON: adapt
- Status: open
- Text: Whenever the server relies on an on-chain transaction (a client-submitted hash, or one it submits for authorization, permit2, settle or close) it MUST read the receipt status and MUST NOT treat the transaction as effective merely because a receipt exists; on success it proceeds to verify channel state. TRON: an included transaction can still have failed, so the execution result (contract result in the transaction info) must be checked.

## SES-094 Reverted transaction fails fast
- Spec: §12.2, 12.3, 12.4
- Level: MUST
- Role: Server
- Layer: E
- TRON: adapt
- Status: open
- Text: A reverted transaction (status 0x0) is a definitive negative outcome: the server MUST fail fast with a typed error, reject it immediately and MUST NOT keep polling for a state change. TRON: failure results include revert and out-of-energy style outcomes; all non-success results count.

## SES-095 Unmined transaction may be awaited with a bound
- Spec: §12.2
- Level: MAY
- Role: Server
- Layer: E
- TRON: adapt
- Status: open
- Text: When no receipt exists yet (not mined) the server MAY await or retry up to a bounded timeout; this is distinct from a revert. TRON: the transaction expiration gives a natural upper bound for the wait.

## SES-096 Open (hash): transaction verification
- Spec: §12.3
- Level: MUST
- Role: Server
- Layer: E
- TRON: adapt
- Status: open
- Text: For action="open" with type="hash" the server MUST verify the transaction via its receipt, verify it successfully caused open() to execute on the expected escrow (directly or through an ERC-4337 EntryPoint UserOperation) and verify that this execution created the specific payload.channelId. TRON: lookup is by transaction ID via TRON APIs (no eth_getTransactionReceipt), no EntryPoint path, and a solidified block should be considered.

## SES-097 Open: channel state checks
- Spec: §12.3
- Level: MUST
- Role: Server
- Layer: E
- TRON: same
- Status: open
- Text: On open (all types) the server MUST query the escrow and verify the channel exists with the provided channelId, channel.payee is the server's address, channel.token matches request.currency, channel.deposit - channel.settled >= amount, the channel is not finalized and channel.closeRequestedAt == 0.

## SES-098 Open: initial voucher verified and accounting initialized
- Spec: §12.3
- Level: MUST
- Role: Server
- Layer: M
- TRON: same
- Status: open
- Text: On open (all types) the server MUST verify the initial voucher signature per the voucher verification rules and then initialize server-side accounting state.

## SES-099 Open (authorization/permit2): validate then submit
- Spec: §12.3
- Level: MUST
- Role: Server
- Layer: E
- TRON: review
- Status: open
- Text: For action="open" with type="authorization" or "permit2" the server MUST validate the EIP-3009 or Permit2 fields and signature, call the matching escrow function (openWithAuthorization or openWithPermit2), then verify channel state. TRON: both authorization formats may be unavailable.

## SES-100 TopUp (hash) verification
- Spec: §12.4
- Level: MUST
- Role: Server
- Layer: E
- TRON: adapt
- Status: open
- Text: For action="topUp" with type="hash" the server MUST verify the transaction shows a successful topUp() on the expected escrow (directly or via ERC-4337 EntryPoint), verify it affected the specific payload.channelId, query the updated channel state, verify the channel deposit increased by exactly payload.additionalDeposit, and update the server-side balance. TRON: lookup by transaction ID with execution-result check; no EntryPoint path.

## SES-101 TopUp (authorization/permit2) verification
- Spec: §12.4
- Level: MUST
- Role: Server
- Layer: E
- TRON: review
- Status: open
- Text: For action="topUp" with type="authorization" or "permit2" the server MUST validate the EIP-3009 or Permit2 fields and signature, call topUpWithAuthorization or topUpWithPermit2, verify the updated channel state and update the server-side balance. TRON: both authorization formats may be unavailable.

## SES-102 Vouchers rejected while a close is pending
- Spec: §12.5
- Level: MUST
- Role: Server
- Layer: M/E
- TRON: same
- Status: open
- Text: On action="voucher" the server MUST verify channel.closeRequestedAt == 0 and reject vouchers on channels with a pending forced close.

## SES-103 Voucher signature and signer verification
- Spec: §12.5
- Level: MUST
- Role: Server
- Layer: M
- TRON: adapt
- Status: open
- Text: The server MUST verify the voucher signature by EIP-712 recovery, verify it uses a canonical low-s value, and verify the recovered signer matches the expected signer from on-chain state (channel.authorizedSigner if non-zero, otherwise channel.payer), using isValidSignature for ERC-1271 contract wallets. TRON: the digest is TIP-712 and the ERC-1271 check is a constant contract call on the TVM.

## SES-104 Signature verified before any idempotent short-circuit
- Spec: §12.5, 12.6
- Level: MUST
- Role: Server
- Layer: M
- TRON: same
- Status: open
- Text: Signature and signer verification MUST be performed before the idempotency short-circuit; if signature verification fails the server MUST return an error response regardless of how cumulativeAmount compares to the highest accepted voucher amount.

## SES-105 Idempotent replay of old or equal vouchers
- Spec: §12.5, 12.6
- Level: MUST
- Role: Server
- Layer: M
- TRON: same
- Status: open
- Text: After successful signature and signer verification, a voucher with cumulativeAmount equal to or lower than highestVoucherAmount MUST get 200 OK without any state change; only higher amounts proceed to the monotonicity and balance checks.

## SES-106 Strictly increasing vouchers and minVoucherDelta
- Spec: §12.5, 15.5
- Level: MUST
- Role: Server
- Layer: M
- TRON: same
- Status: open
- Text: The server MUST only accept (advance state on) strictly increasing cumulativeAmount and MUST verify (cumulativeAmount - highestVoucherAmount) >= minVoucherDelta.

## SES-107 Voucher capped by channel deposit
- Spec: §12.5, 15.7
- Level: MUST
- Role: Server
- Layer: M
- TRON: same
- Status: open
- Text: The server MUST verify cumulativeAmount <= channel.deposit.

## SES-108 Voucher persisted before service
- Spec: §12.5
- Level: MUST
- Role: Server
- Layer: M
- TRON: same
- Status: open
- Text: The server MUST persist an accepted voucher to durable storage before providing service and then update highestVoucherAmount = cumulativeAmount.

## SES-109 Verified-signature cache
- Spec: §12.5
- Level: MAY
- Role: Server
- Layer: M
- TRON: same
- Status: open
- Text: Implementations MAY cache successfully verified voucher signatures keyed by (channelId, cumulativeAmount, signature) and short-circuit on an exact bit-for-bit replay before re-running recovery.

## SES-110 HTTP status mapping for errors
- Spec: §12.7
- Level: MUST (implied)
- Role: Server
- Layer: M
- TRON: same
- Status: open
- Text: 400 for malformed payload or missing fields; 402 for invalid signature or signer mismatch; 409 when a submitted or verified on-chain transaction reverted; 410 when the channel is finalized or not found.

## SES-111 Problem Details with uniform session problem types
- Spec: §12.7
- Level: MUST
- Role: Server
- Layer: V/M
- TRON: same
- Status: open
- Text: Error responses use Problem Details (RFC 9457) with type URIs https://paymentauth.org/problems/session/{invalid-signature, signer-mismatch, amount-exceeds-deposit, delta-too-small, channel-not-found, channel-finalized, challenge-not-found, insufficient-balance, transaction-reverted}; these problem types MUST be uniform across deployments regardless of how each escrow names its internal reverts.

## SES-112 Most specific problem type, never a raw revert
- Spec: §12.7, 7.6
- Level: MUST
- Role: Server
- Layer: M
- TRON: same
- Status: open
- Text: When a server-submitted transaction reverts or an action fails server-side validation, the server MUST report the most specific applicable problem type, falling back to transaction-reverted; servers MUST NOT surface a raw on-chain revert selector or implementation-specific error string as the problem type.

## SES-113 Recommended revert-to-problem mapping
- Spec: §12.7
- Level: SHOULD
- Role: Server
- Layer: M
- TRON: same
- Status: open
- Text: Recommended mapping: AmountExceedsDeposit -> amount-exceeds-deposit; ChannelNotFound -> channel-not-found; ChannelFinalized -> channel-finalized; InvalidSignature -> invalid-signature; insufficient on-chain balance or failed token pull -> insufficient-balance; NonceMismatch, NonceAlreadyUsed, AuthorizationExpired, AmountNotIncreasing, ChannelAlreadyExists or any other -> transaction-reverted.

## SES-114 Per-session accounting state
- Spec: §13
- Level: MUST
- Role: Server
- Layer: M
- TRON: same
- Status: open
- Text: Servers MUST maintain per-session acceptedCumulative (highest valid voucher amount accepted, monotonically increasing, same as highestVoucherAmount), spent (cumulative amount charged, monotonically increasing) and settledOnChain (last cumulative amount settled on-chain); available = acceptedCumulative - spent.

## SES-115 402 when available balance is below cost
- Spec: §13.1
- Level: MUST (implied)
- Role: Server
- Layer: M
- TRON: same
- Status: open
- Text: Per request the server verifies and persists any new acceptedCumulative, then returns 402 if available < cost.

## SES-116 Crash-safe persistence order
- Spec: §13.1, 13.2
- Level: MUST (implied)
- Role: Server
- Layer: M
- TRON: same
- Status: open
- Text: The server persists spent := spent + cost BEFORE delivering service and persists acceptedCumulative BEFORE relying on the new balance, using transactional storage or write-ahead logging.

## SES-117 Stop and signal when balance runs out mid-stream
- Spec: §13.3
- Level: MUST
- Role: Server
- Layer: M
- TRON: same
- Status: open
- Text: When balance is exhausted during a streaming response the server MUST stop delivering additional metered content and MUST emit a payment-need-voucher SSE event.

## SES-118 payment-need-voucher event data
- Spec: §13.3
- Level: MUST
- Role: Server
- Layer: V
- TRON: same
- Status: open
- Text: The payment-need-voucher event data carries REQUIRED string fields channelId, requiredCumulative (minimum next voucher amount), acceptedCumulative (current highest accepted) and deposit (current on-chain deposit).

## SES-119 Client tops up when the required amount exceeds the deposit
- Spec: §13.3
- Level: MUST
- Role: Client
- Layer: M
- TRON: same
- Status: open
- Text: When requiredCumulative > deposit the client MUST submit a topUp before sending a new voucher.

## SES-120 Idempotency-Key support
- Spec: §13.4
- Level: SHOULD
- Role: Both
- Layer: M
- TRON: same
- Status: open
- Text: Clients SHOULD include an Idempotency-Key header on paid requests; servers SHOULD track (challengeId, idempotencyKey) pairs and return cached responses for duplicates.

## SES-121 No double charge on duplicate requests
- Spec: §13.4
- Level: MUST
- Role: Server
- Layer: M
- TRON: same
- Status: open
- Text: Servers MUST NOT increment spent for duplicate idempotent requests.

## SES-122 Supported cost models
- Spec: §13.5
- Level: MUST
- Role: Server
- Layer: M
- TRON: same
- Status: open
- Text: Servers MUST support at least one of fixed cost (a predetermined amount per request) or usage-based cost (proportional to resource consumption).

## SES-123 Streaming cost handling
- Spec: §13.5
- Level: SHOULD
- Role: Server
- Layer: M
- TRON: same
- Status: open
- Text: For streaming (SSE) responses servers SHOULD reserve an estimated cost before starting delivery, adjust spent as actual consumption is measured, and pause delivery if available is exhausted.

## SES-124 Settlement outcome check
- Spec: §14.1
- Level: MUST
- Role: Server
- Layer: E
- TRON: adapt
- Status: open
- Text: Servers MAY settle at any time; for every server-submitted settle() or close() the server MUST check the receipt status and treat a revert as a definitive failure to settle (surface a typed error and retry as appropriate), never as a pending result polled to timeout. TRON: check the execution result of the included transaction, not just inclusion.

## SES-125 Close voucher must cover delivered service
- Spec: §14.2
- Level: MUST/SHOULD
- Role: Server
- Layer: M
- TRON: same
- Status: open
- Text: On action="close" the server MUST verify cumulativeAmount >= spent; if the client's close voucher is insufficient the server SHOULD settle using the highest previously accepted voucher instead.

## SES-126 Cooperative close execution and failure handling
- Spec: §14.2, 10.2.5
- Level: MUST
- Role: Server
- Layer: E
- TRON: adapt
- Status: open
- Text: The server calls close(channelId, cumulativeAmount, signature) on the escrow and MUST check the resulting receipt status; on a revert it MUST NOT report the channel as closed or leave the client waiting, MUST surface a typed error and MAY retry (e.g. with the highest accepted voucher). TRON: check the execution result; fee is Energy/Bandwidth under fee_limit.

## SES-127 Close success returns a receipt with the transaction hash
- Spec: §14.2
- Level: MUST (implied)
- Role: Server
- Layer: E
- TRON: adapt
- Status: open
- Text: On a successful close (delta settled, remainder refunded to the payer) the server returns a receipt that includes the transaction hash. TRON: the 32-byte transaction ID.

## SES-128 Grace period of at least 10 minutes
- Spec: §14.3
- Level: MUST
- Role: Contract
- Layer: C
- TRON: same
- Status: open
- Text: The forced-close grace period is the contract's CLOSE_GRACE_PERIOD constant (reference value 15 minutes); compliant implementations MUST NOT use a grace period shorter than 10 minutes.

## SES-129 Server checks the contract's grace period
- Spec: §14.3
- Level: MUST
- Role: Server
- Layer: E
- TRON: same
- Status: open
- Text: Servers MUST verify that the escrow contract's grace period meets the 10-minute minimum before accepting channels on that contract.

## SES-130 Payee can settle or close during the grace period
- Spec: §14.3, 15.16
- Level: MUST (implied)
- Role: Contract
- Layer: C
- TRON: same
- Status: open
- Text: After requestClose the payee can still call settle() or close() during the grace period; only after it elapses can the payer withdraw the remaining unsettled funds.

## SES-131 Voucher transport concurrency
- Spec: §14.5
- Level: SHOULD
- Role: Client
- Layer: M
- TRON: same
- Status: open
- Text: Clients SHOULD use HTTP/2 multiplexing or maintain separate connections for voucher updates and content streaming.

## SES-132 Payment-Receipt on every successful paid request
- Spec: §14.6
- Level: MUST
- Role: Server
- Layer: M
- TRON: same
- Status: open
- Text: Servers MUST return a Payment-Receipt header on every successful paid request.

## SES-133 Streaming receipts
- Spec: §14.6
- Level: MUST
- Role: Server
- Layer: M
- TRON: same
- Status: open
- Text: For streaming (SSE) responses servers MUST include the receipt in the initial response headers AND as a final payment-receipt SSE event; for chunked responses the final receipt MAY be delivered as an HTTP trailer if the client advertises TE: trailers.

## SES-134 Receipt fields
- Spec: §14.6
- Level: MUST
- Role: Server
- Layer: V
- TRON: adapt
- Status: open
- Text: The receipt carries REQUIRED method ("evm"), intent ("session"), status ("success"), timestamp (RFC 3339), reference, challengeId, channelId, acceptedCumulative (string), spent (string) and chainId (number), plus OPTIONAL units (number), txHash (present on settlement/close) and confirmations (number). TRON: method name, chain identifier and transaction ID format differ.

## SES-135 Receipt reference equals channelId
- Spec: §14.6
- Level: MUST
- Role: Server
- Layer: V
- TRON: same
- Status: open
- Text: The receipt reference field MUST equal channelId.

## SES-136 Fresh channel after close needs a new salt
- Spec: §15.2
- Level: MUST
- Role: Client
- Layer: M
- TRON: same
- Status: open
- Text: Clients that want a fresh channel after close MUST choose a new salt, because a used channelId can never be re-opened.

## SES-137 Denial-of-service limits
- Spec: §15.8
- Level: SHOULD
- Role: Server
- Layer: M
- TRON: same
- Status: open
- Text: Servers rate limit voucher submissions (SHOULD limit to 10 per second per session), enforce minVoucherDelta, enforce minimum deposit thresholds and perform format validation before signature recovery.

## SES-138 Minimum deposit when the server pays fees
- Spec: §15.8
- Level: SHOULD
- Role: Server
- Layer: M
- TRON: adapt
- Status: open
- Text: When feePayer is true servers SHOULD enforce minimum deposit amounts to prevent gas griefing through many small authorizations. TRON: the griefing cost is Energy/Bandwidth (or burned TRX).

## SES-139 Checks-effects-interactions and reentrancy protection
- Spec: §15.10
- Level: MUST
- Role: Contract
- Layer: C
- TRON: same
- Status: open
- Text: settle, close, withdraw and their relayed variants MUST commit all state changes (channel.settled, channel.finalized, the payee-relayed nonce used-set) before the external token transfer; settleWithAuthorization and closeWithAuthorization MUST apply a reentrancy guard or rely strictly on checks-effects-interactions.

## SES-140 Idle channels are settled and closed
- Spec: §15.11, 15.17
- Level: SHOULD
- Role: Server
- Layer: M/E
- TRON: same
- Status: open
- Text: Servers SHOULD settle and close channels that have been inactive for extended periods (e.g. 30+ days).

## SES-141 Confirmation depth before accepting open/topUp
- Spec: §15.12
- Level: SHOULD
- Role: Server
- Layer: E
- TRON: adapt
- Status: open
- Text: Servers SHOULD use sufficient confirmation depth before accepting open/topUp transactions (e.g. 1 block on fast-finality L2s, 12+ blocks on Ethereum mainnet). TRON: the equivalent is waiting for the block to be solidified.

## SES-142 Client batches approve and open
- Spec: §15.14
- Level: SHOULD
- Role: Client
- Layer: E
- TRON: adapt
- Status: open
- Text: Clients SHOULD batch approve and open in a single transaction when possible (e.g. via ERC-4337 UserOperations or multicall). TRON: a transaction carries a single contract call and a helper contract would change msg.sender (and thus the payer), so batching may not be achievable.

## SES-143 Contract-wallet signer mutability mitigations
- Spec: §15.15
- Level: SHOULD
- Role: Both
- Layer: M
- TRON: same
- Status: open
- Text: Payers using a contract wallet as authorizedSigner SHOULD avoid key rotation during active sessions or coordinate it with settlement; payees SHOULD settle more frequently when the authorizedSigner is a contract wallet and MAY detect this by inspecting the signer's code size.

## SES-144 Session-key delegation for contract-wallet payers
- Spec: §15.15
- Level: SHOULD
- Role: Client
- Layer: M
- TRON: same
- Status: open
- Text: When the payer is a contract wallet it SHOULD delegate voucher signing to an ephemeral EOA session key via authorizedSigner; the session key SHOULD be scoped to the lifetime of the channel and discarded after close.
