
# MPP SW System Requirements 

Baseline: `draft-evm-charge-00` (2 Nov 2026, expires 6 May 2027).

Field guide
- Level: MUST / SHOULD as in the spec (RFC 2119)
- Layer: V = framing vector, M = method-level, E = end-to-end testnet
- TRON: same = applies as written, adapt = needs adaptation, review = unsure if TRON supports it
- Status: open | n/a (give reason) -- n/a requirements are excluded from coverage gaps, doc once requirement is covered by at least 1 Test Case

Rules: IDs are permanent. Never renumber or reuse; mark deprecated instead.
Parser contract: each requirement starts with `## <ID> <title>` and uses `- Key: value` lines.

## Table of Contents

   1.  Introduction
   2.  Terminology
   3.  Protocol Overview
     3.1. Request Flow
     3.2. HTTP Status Codes & Responses

   4.  Request Schema
     4.1.  Shared Fields
     4.2.  Method Details
       4.2.1.  Chain Identification
       4.2.2.  Credential Type Negotiation
       4.2.3.  Payment Splits
   5.  Credential Schema
     5.1.  Credential Structure
     5.2.  Permit2 Payload (type="permit2")
       5.2.1.  Permit Object
       5.2.2.  Transfer Details
       5.2.3.  Witness Data (Challenge Binding)
       5.2.4.  Server Behavior
       5.2.5.  Example: Single Transfer
       5.2.6.  Example: Batch Transfer with Splits
     5.3.  Authorization Payload (type="authorization")
       5.3.1.  Challenge Binding
       5.3.2.  Constraints
       5.3.3.  Example
     5.4.  Transaction Payload (type="transaction")
     5.5.  Hash Payload (type="hash")
     5.6.  Gas Sponsorship Model
   6.  Verification Procedure
     6.1.  Permit2 Verification
     6.2.  Authorization Verification
     6.3.  Transaction Verification
     6.4.  Hash Verification
   7.  Settlement Procedure
     7.1.  Permit2 Settlement
     7.2.  Authorization Settlement
     7.3.  Transaction Settlement
     7.4.  Hash Settlement
     7.5.  Confirmation Requirements
     7.6.  Receipt Generation
   8.  Replay Protection
   9.  Error Responses
   10. Security Considerations
     10.1.  Transport Security
     10.2.  Transaction Replay
     10.3.  Amount Verification
     10.4.  Hash Credential Binding
     10.5.  Permit2-Specific Risks
     10.6.  Fee Payer Risks
     10.7.  Split Payment Risks
     10.8.  RPC Trust
   11. IANA Considerations
     11.1.  Payment Method Registration
     11.2.  Payment Intent Registration
   12. References
     12.1.  Normative References
     12.2.  Informative References

## 1. Introduction

   This document defines the "charge" intent for the "TRON" payment method in the Payment. It specifies how clients and servers exchange one-time TRC-20 token transfers.

   Four credential types are supported: type="permit2" (RECOMMENDED), where the client signs an off-chain Permit2 authorization and the
   server submits the transfer; type="authorization" (opt-in for TIP-3009 tokens), where the client signs an off-chain transfer
   authorization and the server submits it directly to the token contract; type="transaction", where the client signs and the server
   broadcasts a standard TRC-20 transfer transaction; and type="hash" (optional fallback), where the client broadcasts the transaction
   itself and presents the on-chain transaction hash for server verification.

   This specification covers TRC-20 token transfers only.  Native token transfers (TRX, TRC10) are currently out of scope.
  
   HTTP Payment Authentication [I-D.httpauth-payment] defines a challenge-response mechanism that gates access to resources behind
   payment.

   The TRON Virtual Machine (TVM) is the execution environment for the payment layer. A common smart contract interface (TRC-20), transaction format (TIP-1559), address encoding (TIP-55), Fullnode HTTP API and JSON-RPC API make it possible to define this payment method

   ### Charge flow

           Client                  Server               TRON Chain
            |                        |                      |
            | (1) GET /resource      |                      |
            |----------------------->|                      |
            |                        |                      |
            | (2) 402 Payment Req    |                      |
            |     intent="charge"    |                      |
            |<-----------------------|                      |
            |                        |                      |
            | (3) Sign TIP-712       |                      |
            |     Permit2 authz      |                      |
            |                        |                      |
            | (4) Authorization:     |                      |
            |     Payment <cred>     |                      |
            |----------------------->|                      |
            |                        | (5) Submit permit-   |
            |                        |  [Batch]Witness-     |
            |                        |  TransferFrom()      |
            |                        |--------------------->|
            |                        | (6) Receipt          |
            |                        |<---------------------|
            | (7) 200 OK + Receipt   |                      |
            |<-----------------------|                      |
            |                        |                      |

### 2 Terminology

   - Payment Challenge  A WWW-Authenticate header with scheme "Payment"
      indicating the payment requirements for accessing a resource.

   - Payment Credential  An HTTP header field with scheme "Payment"
      containing payment authorization data.  The default field name is
      Authorization.  A Payment challenge MAY select Payment-
      Authorization with the header parameter (see Section 5.2).

   - Payment Method  A mechanism for transferring value, identified by a
      registered identifier.

   - Payment Intent  The type of payment request, identified by a
      registered value in the IANA "HTTP Payment Intents" registry.
      Intents are defined by separate intent specifications.

   - Request  Method-specific data in the challenge enabling payment
      completion.  Encoded as base64url JSON in the request parameter.

   - Payload  Method-specific data in the credential proving payment.

   - Permit2  Uniswap's universal token approval contract [PERMIT2],
      deployed at the canonical address
      0x000000000022D473030F116dDEE9F6B43aC78BA3 on all supported
      chains.  Enables off-chain signed approvals for any TRC-20 token
      via PermitWitnessTransferFrom and PermitBatchWitnessTransferFrom.

   - TIP-712  A standard for typed structured data hashing and signing
      [TIP-712], used by Permit2 to produce human-readable, replay-
      protected authorization signatures.

   - Base Units  The smallest transferable unit of a token, determined by
      the token's decimal precision.  For example, USDT (6 decimals)
      uses 1,000,000 base units per 1 USDT; USDD (18 decimals) uses
      10^18 base units per 1 USDD.



      
## SSR