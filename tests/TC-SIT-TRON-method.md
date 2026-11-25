## TC-SIT-001 Server issues challenge for Supported networks (Nile)
Covers: SYS-008, SYS-124
Level: system integration / end-to-end (SIT)
Status: draft
Env: Nile network, local compliance server

**Preconditions**
- Configure the SDK for Nile testnet network (chainId = 3448148188) with a Nile node endpoint
- Server fee payer (spender) and recipient addresses configured

**Steps**
1. Client requests for resource

**Expected result**
- Server responds with 402 and Cache-Control: no-store
- Decoded request has methodDetails.chainId = 3448148188

**Notes**
- None


## TC-SIT-002 Server issues challenge for Supported networks (Shasta)
Covers: SYS-008, SYS-014, SYS-124
Level: system integration / end-to-end (SIT)
Status: draft
Env: Shasta network, local compliance server

**Preconditions**
- Configure the SDK for Shasta testnet network (chainId = 2494104990) with a Shasta node endpoint
- Server fee payer (spender) and recipient addresses configured

**Steps**
1. Client requests for resource

**Expected result**
- Server responds with 402 and Cache-Control: no-store
- Decoded request has methodDetails.chainId = 2494104990
- credentialTypes does not include "permit2"; methodDetails has no permit2Address and the request has no splits (no Permit2 deployment on Shasta)

**Notes**
- None


## TC-SIT-003 Server issues challenges for Supported networks (Mainnet)
Covers: SYS-008, SYS-124
Level: system integration / end-to-end (SIT)
Status: draft
Env: Mainnet network, local compliance server

**Preconditions**
- Configure the SDK for Mainnet network (chainId = 728126428) with a mainnet node endpoint
- Server fee payer (spender) and recipient addresses configured

**Steps**
1. Client requests for resource

**Expected result**
- Server responds with 402 and Cache-Control: no-store
- Decoded request has methodDetails.chainId = 728126428

**Notes**
- No funds are spent; the unpaid request does not touch the chain.


## TC-SIT-004 Server refuses to start for unsupported or mismatched network
Covers: SYS-008
Level: system integration / end-to-end (SIT)
Status: draft
Env: Unsupported network / chainId; Nile and Shasta node endpoints

**Preconditions**
- A Shasta node endpoint (reports chainId 2494104990), for variant B

**Steps**
1. (Variant A) Configure the SDK with an unsupported chainId (3448148189) and start the server
2. (Variant B) Configure the SDK for Nile (chainId = 3448148188) but point the node endpoint to Shasta, and start the server

**Expected result**
1. Server initialization fails with a configuration error; no challenge is ever served
2. Server initialization fails with a chainId mismatch error; no challenge is ever served

**Notes**
- The refusal happens at startup, not as an HTTP status per request. The server must never respond 402 in either variant.


## TC-SIT-005 Server response on unpaid request
Covers: SYS-101, SYS-102, SYS-104
Level: system integration / end-to-end (SIT)
Status: draft
Env: Nile testnet

**Preconditions**
- Configure the SDK for Nile testnet network
- SDK server started with the TRON charge method
- A resource path configured as paid (/resource)

**Steps**
1. Send a plain GET /resource from client with NO Authorization AND NO Payment-Authorization header.
2. Send another plain GET /resource from client with NO Authorization AND NO Payment-Authorization header.
3. Send a GET to a path that does not exist (/does-not-exist)

**Expected result**
1. Server responds with 402 status, WWW-Authenticate holds at least one Payment challenge with method="tron" and intent="charge", and non-empty id, realm, request and expires
2. Server responds with 402 status, the challenge id is fresh (different than step 1 challenge id)
3. Server responds with 404 and no Payment challenge

**Notes**
- An unpaid request does not touch the chain, so this case could also run at ST level with a stub node.


## TC-SIT-006 Unpaid request has no side effects
Covers: SYS-120
Level: system integration / end-to-end (SIT)
Status: draft
Env: Nile testnet + TRC-20 test token (SIT)

**Preconditions**
- Configure the SDK for Nile testnet network
- Server fee payer (spender) address known
- App-side resource handler call counter at 0
- Record the server fee payer account's transaction list (TronGrid or tronscan)

**Steps**
1. Client requests for resource
2. Wait at least 2 blocks, then read the server fee payer account's transaction list again

**Expected result**
- Server responds with 402
- No new transaction from the server fee payer account on Nile
- Resource handler call counter is still 0
- The 402 body contains no resource content

**Notes**
- None


## TC-SIT-007 Request flow completes (Nile permit2 approved)
Covers: SYS-014, SYS-126, SYS-204, SYS-601
Level: system integration / end-to-end (SIT)
Status: draft
Env: Nile testnet + TRC-20 test token (SIT)

**Preconditions**
- Configure the SDK for Nile testnet network (chainId = 3448148188, permit2 CA=TEetQ5ohtKF5eAF9ec6jbvdTzcLDsB6jTs)
- TRC20 token configured to USDT (Nile, TXYZopYRdj2D9XRtbG411XZZ3kM5VkAeBf)
- Content fee configured to 1.5 USDT
- Payer account activated, holding at least 1.5 USDT, with Permit2 allowance of at least 1.5 USDT; no extra TRX for fees
- Server fee payer (spender) account funded with TRX/Energy for one Permit2 transfer
- App-side resource handler call counter at 0
- Record USDT and TRX balances of payer, recipient and spender

**Steps**
1. Client requests for resource
2. Server responds with 402 (intent "charge" and credentialTypes: "permit2", token and amount are the pre-configured ones)
3. Client signs TIP-712 Permit2 authorization
4. Client sends proof of payment to server (credential with the signed TIP-712 Permit2 authorization)
5. Server executes permitWitnessTransferFrom on-chain txn
6. Server confirms on-chain txn result is SUCCESS
7. Server responds client with 200 OK + Payment-Receipt

**Expected result**
- Decoded request: amount = "1500000", currency = TXYZopYRdj2D9XRtbG411XZZ3kM5VkAeBf; chainId, permit2Address (= Nile canonical CA) and spender are under methodDetails; no TRON fields at the top level
- Payer USDT -1.5, recipient USDT +1.5, in a single transfer
- No Energy, TRX or Bandwidth is deducted from the payer account
- The permitWitnessTransferFrom txn's owner_address equals methodDetails.spender; its Energy and Bandwidth are charged to the spender account
- chainId = 3448148188 in methodDetails.chainId, in the credential source (did:pkh:tron:3448148188:T...), in the TIP-712 domain and in the receipt
- Decoded receipt: method = "tron", challengeId = the challenge id, reference = the settling txID, status = "success", numeric chainId
- Resource handler call counter is exactly 1

**Notes**
- None


## TC-SIT-008 Request flow completes (Mainnet permit2 approved)
Covers: SYS-014, SYS-126, SYS-204, SYS-601
Level: system integration / end-to-end (SIT)
Status: draft
Env: Mainnet + real USDT (SIT, spends real funds)

**Preconditions**
- Configure the SDK for Mainnet network (chainId = 728126428, permit2 CA=TTJxU3P8rHycAyFY4kVtGNfmnMH4ezcuM9)
- TRC20 token configured to USDT (mainnet, TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t)
- Content fee configured to 0.01 USDT
- Payer account activated, holding at least 0.01 USDT, with Permit2 allowance of at least 0.01 USDT; no extra TRX for fees
- Server fee payer (spender) account with a TRX/Energy budget for one Permit2 transfer
- App-side resource handler call counter at 0
- Record USDT and TRX balances of payer, recipient and spender

**Steps**
1. Client requests for resource
2. Server responds with 402 (intent "charge" and credentialTypes: "permit2", token and amount are the pre-configured ones)
3. Client signs TIP-712 Permit2 authorization
4. Client sends proof of payment to server (credential with the signed TIP-712 Permit2 authorization)
5. Server executes permitWitnessTransferFrom on-chain txn
6. Server confirms on-chain txn result is SUCCESS
7. Server responds client with 200 OK + Payment-Receipt

**Expected result**
- Decoded request: amount = "10000", currency = TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t; chainId, permit2Address (= Mainnet canonical CA) and spender are under methodDetails; no TRON fields at the top level
- Payer USDT -0.01, recipient USDT +0.01, in a single transfer
- No Energy, TRX or Bandwidth is deducted from the payer account
- The permitWitnessTransferFrom txn's owner_address equals methodDetails.spender; its Energy and Bandwidth are charged to the spender account
- chainId = 728126428 in methodDetails.chainId, in the credential source (did:pkh:tron:728126428:T...), in the TIP-712 domain and in the receipt
- Decoded receipt: method = "tron", challengeId = the challenge id, reference = the settling txID, status = "success", numeric chainId
- Resource handler call counter is exactly 1

**Notes**
- Spends real USDT and the spender's TRX (a Permit2 transfer needs roughly 100k Energy unless staked).


## TC-SIT-009 Only TRC-20 tokens as supported currency
Covers: SYS-202, SYS-203
Level: system integration / end-to-end (SIT)
Status: draft
Env: Nile testnet + TRC-20 test token (SIT)

**Preconditions**
- Configure the SDK for Nile testnet network with a reachable Nile node endpoint
- A valid Base58Check Nile address with no contract deployed (ordinary account)

**Steps**
1. Configure currency as TRC-20 token USDT (TXYZopYRdj2D9XRtbG411XZZ3kM5VkAeBf)
2. Initialize Server service (Server checks contract validity on-chain), request the resource, then deinit Server
3. Configure currency as TRX (Id:0)
4. Initialize Server service
5. Configure currency as a TRC-10 (Id:1005416)
6. Initialize Server service
7. Configure currency as the address with no contract
8. Initialize Server service (Server checks contract validity on-chain)

**Expected result**
2. Server initializes and the challenge's currency = TXYZopYRdj2D9XRtbG411XZZ3kM5VkAeBf
4. Initialization throws or returns a configuration error (not a Base58Check address)
6. Initialization throws or returns a configuration error (not a Base58Check address)
8. Initialization throws or returns a configuration error (no contract at the address)

**Notes**
- Steps 3–6 are format checks (SYS-203); only step 8 exercises the on-chain check of SYS-202, which is a SHOULD.


## TC-SIT-010 Splits challenge rejects transaction credential
Covers: SYS-212, SYS-701
Level: system integration / end-to-end (SIT)
Status: draft
Env: Nile testnet + TRC-20 test token (SIT)

**Preconditions**
- Configure the SDK for Nile testnet network (chainId = 3448148188, permit2 CA=TEetQ5ohtKF5eAF9ec6jbvdTzcLDsB6jTs)
- TRC20 token configured to USDT (test token)
- Content fee (amount) configured to 1.5 USDT
- Splits configured: one split recipient (account B) with 0.5 USDT; primary recipient receives the remaining 1.0 USDT
- Payer account activated and funded with at least 1.5 USDT plus TRX/Energy for one transfer
- Test client able to send a transaction credential regardless of credentialTypes
- Record USDT balances of payer, primary recipient and account B

**Steps**
1. Client requests resource
2. Server responds with 402 (intent "charge", methodDetails.splits contains account B / 0.5 USDT); record credentialTypes
3. Client signs a TRC-20 transfer of 1.5 USDT to the primary recipient, does not broadcast it, and sends it as a transaction credential echoing the challenge from step 2 unchanged

**Expected result**
- Server responds 402 with problem type invalid-payload
- Response carries a fresh Payment challenge in WWW-Authenticate (new id, still with splits) and no Payment-Receipt
- The signed transaction is not broadcast (its txID is not found on Nile)
- Payer, primary recipient and account B USDT balances are unchanged

**Notes**
- Splits are set by the server in the challenge and bound by its HMAC; the client cannot add them. A credential that alters splits fails earlier with invalid-challenge (SYS-104) and does not test SYS-212.


## TC-SIT-011 Splits challenge rejects authorization credential
Covers: SYS-212, SYS-701
Level: system integration / end-to-end (SIT)
Status: draft
Env: Nile testnet + TRC-3009 test token (USDC clone) (SIT)

**Preconditions**
- Configure the SDK for Nile testnet network (chainId = 3448148188, permit2 CA=TEetQ5ohtKF5eAF9ec6jbvdTzcLDsB6jTs)
- TRC20 token configured to the USDC clone (implements transferWithAuthorization); confirm its address and that the challenge still offers permit2 with permit2Address for it
- Content fee (amount) configured to 1.5 USDC
- Splits configured: one split recipient (account B) with 0.5 USDC; primary recipient receives the remaining 1.0 USDC
- Payer account activated and funded with at least 1.5 USDC
- Test client able to send an authorization credential regardless of credentialTypes
- Record USDC balances of payer, primary recipient and account B

**Steps**
1. Client requests resource
2. Server responds with 402 (intent "charge", methodDetails.splits contains account B / 0.5 USDC); record credentialTypes
3. Client signs transferWithAuthorization for 1.5 USDC to the primary recipient (validAfter in the past, validBefore in the future, fresh nonce) and sends it as an authorization credential echoing the challenge from step 2 unchanged

**Expected result**
- Server responds 402 with problem type invalid-payload
- Response carries a fresh Payment challenge in WWW-Authenticate (new id, still with splits) and no Payment-Receipt
- No transferWithAuthorization call is submitted; authorizationState for the nonce stays unused
- Payer, primary recipient and account B USDC balances are unchanged

**Notes**
- Uses the USDC clone so that the only reason for rejection is the splits rule, not a token without EIP-3009 support.


## TC-SIT-012 Splits challenge rejects hash credential
Covers: SYS-212, SYS-701
Level: system integration / end-to-end (SIT)
Status: draft
Env: Nile testnet + TRC-20 test token (SIT)

**Preconditions**
- Configure the SDK for Nile testnet network (chainId = 3448148188, permit2 CA=TEetQ5ohtKF5eAF9ec6jbvdTzcLDsB6jTs)
- TRC20 token configured to USDT (test token)
- Content fee (amount) configured to 1.5 USDT
- Splits configured: one split recipient (account B) with 0.5 USDT; primary recipient receives the remaining 1.0 USDT
- Test client able to send a hash credential regardless of credentialTypes
- Payer account activated and funded with at least 1.5 USDT plus TRX/Energy for one transfer
- Record USDT balances of payer, primary recipient and account B

**Steps**
1. Client requests resource
2. Server responds with 402 (intent "charge", methodDetails.splits contains account B / 0.5 USDT); record credentialTypes
3. Client broadcasts a 1.5 USDT transfer to the primary recipient and waits for SUCCESS
4. Client sends the txID as a hash credential echoing the challenge from step 2 unchanged

**Expected result**
- Server responds 402 with problem type invalid-payload
- Response carries a fresh Payment challenge in WWW-Authenticate (new id, still with splits) and no Payment-Receipt
- The only on-chain transfer is the client's own from step 3: payer -1.5 USDT, primary recipient +1.5 USDT
- Account B balance is unchanged; the server sends no transfer of its own

**Notes**
- The step 3 transfer is lost to the payer; it is not credited as payment.


## TC-SIT-013 Splits challenge settles with permit2 credential
Covers: SYS-212, SYS-213, SYS-601
Level: system integration / end-to-end (SIT)
Status: draft
Env: Nile testnet + TRC-20 test token (SIT)

**Preconditions**
- Configure the SDK for Nile testnet network (chainId = 3448148188, permit2 CA=TEetQ5ohtKF5eAF9ec6jbvdTzcLDsB6jTs)
- TRC20 token configured to USDT (test token)
- Content fee (amount) configured to 1.5 USDT
- Splits configured: one split recipient (account B) with 0.5 USDT; primary recipient receives the remaining 1.0 USDT
- Payer account activated, with Permit2 allowance of at least 1.5 USDT
- Server fee payer (spender) account funded with TRX/Energy for one Permit2 batch transfer
- Record USDT balances of payer, primary recipient and account B

**Steps**
1. Client requests resource
2. Server responds with 402 (intent "charge", credentialTypes includes "permit2", methodDetails.splits contains account B / 0.5 USDT)
3. Client signs a TIP-712 Permit2 batch authorization (primary + split) and sends it as a permit2 credential
4. Server executes permitWitnessTransferFrom on-chain
5. Server responds 200 OK + Payment-Receipt

**Expected result**
- A single on-chain transaction carries both transfers
- Transfer events in order: first to the primary recipient (1.0 USDT), then to account B (0.5 USDT)
- Payer -1.5 USDT, primary recipient +1.0 USDT, account B +0.5 USDT
- No TRX, Energy or Bandwidth is deducted from the payer account
- Decoded receipt: method = "tron", challengeId = the challenge id, reference = the settling txID, status = "success", numeric chainId

**Notes**
- Control case: shows that rejections in TC-SIT-010..012 are specific to the credential type, not to the splits configuration.
