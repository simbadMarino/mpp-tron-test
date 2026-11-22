<!-- Copy this file to tests/TC-XXX-short-name.md. Files starting with "_" are ignored by the tracer. -->

## TC-SIT-001 Server issues challenge for Supported networks (Nile)
Covers: SYS-008, SYS-102
Level: system integration / end-to-end (SIT)
Status: draft
Env:Nile network, local compliance server

**Preconditions**
- Configure the SDK for Nile testnet network

**Steps**
1. Client requests for resource

**Expected result**
- Server responds with 402.

**Notes**
- None


## TC-SIT-002 Server issues challenge for Supported networks (Shasta)
Covers: SYS-008, SYS-102
Level: system integration / end-to-end (SIT)
Status: draft
Env:Shasta network, local compliance server

**Preconditions**
- Configure the SDK for Shasta testnet network

**Steps**
1. Client requests for resource

**Expected result**
- Server responds with 402.

**Notes**
- None


## TC-SIT-003 Server issues challenges for Supported networks (Mainnet)
Covers: SYS-008, SYS-102
Level: system integration / end-to-end (SIT)
Status: draft
Env:Mainnet network, local compliance server

**Preconditions**
- Configure the SDK for Mainnet network

**Steps**
1. Client requests for resource

**Expected result**
- Server responds with 402.

**Notes**
- None


## TC-SIT-004 Server refuses to issue challenge for unsupported network
Covers: SYS-008, SYS-102
Level: system integration / end-to-end (SIT)
Status: draft
Env: Unsupported network / chainId

**Preconditions**
- Configure the SDK with an unsupported network (chainId = 3448148189)

**Steps**
1. Client requests for resource

**Expected result**
- Server refuses to construct challenge and returns 401.

**Notes**
- Confirm whether SDK must return 401 or 403. It must never respond 402


## TC-SIT-005 Server response on unpaid request 
Covers: SYS-101
Level: system integration / end-to-end (SIT)
Status: draft
Env:e.g. stub TRON node (ST) OR Nile testnet

**Preconditions**
- Configure the SDK for Nile testnet network

**Steps**
1. Start the SDK server with the TRON charge method
2. Send a plain GET /resource from client with NO Authorization AND NO Payment-Authorization header.
3. Send another plain GET / resource from client with NO Authorization AND NO Payment-Authorization header.

**Expected result**
2. Server responds with 402 status, WWW-Authenticate holds at least one Payment challenge with method="tron" and intent="charge"
3. Server responds with 402 status, the challenge id is fresh (different than step 2 result challenge Id).

**Notes**
- We need to confirm challenge id does involve a random nonce to calculate the HAMAC sha256 hash (challenge id)


## TC-SIT-006 Unpaid request does not broadcast transactions to network
Covers: SYS-120
Level: system integration / end-to-end (SIT)
Status: draft
Env: Nile testnet + TRC-20 test token (SIT)

**Preconditions**
- Configure the SDK for Nile testnet network
- Check Server Account Bandwidth and store in memory

**Steps**
1. Client requests for resource
2. Check server account bandwidth and compare with initial value

**Expected result**
- Server responds with 402, No transaction is broadcasted in Nile testnet (final bandwidth >= initial bandwidth)

**Notes**
- TRON account in server should not present any bandwidth deduction


## TC-SIT-007 Request flow completes (Nile permit2 approved)
Covers: SYS-014, SYS-126, SYS-204
Level: system integration / end-to-end (SIT)
Status: draft
Env: Nile testnet + TRC-20 test token (SIT)

**Preconditions**
- Configure the SDK for Nile testnet network (chainId = 3448148188, permit2 CA=TEetQ5ohtKF5eAF9ec6jbvdTzcLDsB6jTs)
- Use a permit2-pre-approved EOA as payee
- TRC20 token configured to USDT
- Content fee configured to 1.5 USDT

**Steps**
1. Client requests for resource
2. Server responds with 402 (intent "charge" and credentialType: "permit2", token and content fee is displayed as the pre-configured one)
3. Client signs EIP-712 permit2 authorization
4. Client sends proof of payment to server (including off-chain signed TIP-712 Permit2 authorization)
5. Server executes permitWitnessTransferFrom on-chain txn
6. Server confirms on-chain txn Receipt indicates success and re
7. Server responds client with 200 OK + Receipt

**Expected result**
- Client (payee) account TRC20 token balance is deducted exactly by the preconfigured fee
- No energy, TRX or bandwidth is deducted from client account
- A single TRC20 token transfer is executed from Client to Server account succesfully
- Server TRX, Bandwidthand and energy balance is deducted depending on current chain network parameter fees.
- Both Server and Client implement All TRON-specicif fields are nested under methodDetails.
- chainId is ALWAYS 3448148188 through ALL Client-Server-Network interactions
- permit2 contract address corresponds to Nile canonical CA

**Notes**
- None

## TC-SIT-008 Request flow completes (Mainnet permit2 approved)
Covers: SYS-014, SYS-126, SYS-204
Level: system integration / end-to-end (SIT)
Status: draft
Env: Mainnet testnet + TRC-20 test token (SIT)

**Preconditions**
- Configure the SDK for Mainnet testnet network (chainId = 728126428, permit2 CA=TTJxU3P8rHycAyFY4kVtGNfmnMH4ezcuM9)
- Use a permit2-pre-approved EOA as payee
- TRC20 token configured to USDT
- Content fee configured to 1.5 USDT

**Steps**
1. Client requests for resource
2. Server responds with 402 (intent "charge" and credentialType: "permit2", token and content fee is displayed as the pre-configured one)
3. Client signs EIP-712 permit2 authorization
4. Client sends proof of payment to server (including off-chain signed TIP-712 Permit2 authorization)
5. Server executes permitWitnessTransferFrom on-chain txn
6. Server confirms on-chain txn Receipt indicates success and re
7. Server responds client with 200 OK + Receipt

**Expected result**
- Client (payee) account TRC20 token balance is deducted exactly by the preconfigured fee
- No energy, TRX or bandwidth is deducted from client account
- A single TRC20 token transfer is executed from Client to Server account succesfully
- Server TRX, Bandwidthand and energy balance is deducted depending on current chain network parameter fees.
- Both Server and Client implement All TRON-specicif fields are nested under methodDetails.
- chainId is ALWAYS 728126428 through ALL Client-Server-Network interactions
- permit2 contract address corresponds to Mainnet canonical CA

**Notes**
- None

