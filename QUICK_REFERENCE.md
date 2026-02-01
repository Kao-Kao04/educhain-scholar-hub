# EduChain Scholar Hub - Quick Reference Card

## 🚀 One-Minute Summary

**What is this?** A blockchain scholarship system where:
- Students apply → Oracle verifies eligibility → Smart contract distributes funds
- Everything transparent, impossible to manipulate, no fraud

**Why blockchain?** Immutable rules + public audit trail + no single gatekeeper

**Tech stack:** Solidity (smart contracts) + Python (oracle) + React (frontend)

---

## ⚡ Quick Commands

### Setup (First Time)
```bash
# 1. Copy environment
cp .env.example .env

# 2. Install Python packages
pip install web3 eth-account sqlalchemy flask python-dotenv

# 3. Get testnet ETH
# → https://sepoliafaucet.com (paste your wallet address, wait 1 min)

# 4. Deploy contract
npx hardhat run scripts/deploy.js --network sepolia

# 5. Copy returned address to .env as CONTRACT_ADDRESS

# 6. Initialize database
python database_models.py

# 7. Run oracle
python oracle_service.py
```

### Daily Usage
```bash
# Start oracle service
python oracle_service.py

# In new terminal, start API
python app.py

# In another terminal, start frontend
bun run dev

# Open http://localhost:8080
```

---

## 📁 What Each File Does

| File | Purpose | Key Function |
|------|---------|--------------|
| **ScholarshipHub.sol** | Smart contract | `registerStudent()`, `verifyEligibility()`, `claimScholarship()` |
| **blockchain_connector.py** | Web3 wrapper | `create_scholarship()`, `register_student()`, `claim_scholarship()` |
| **oracle_service.py** | Verification engine | `check_eligibility()`, `verify_student_on_chain()` |
| **database_models.py** | Student database | Student, Application, Verification records |
| **example_usage.py** | Code examples | Complete workflow demonstrations |

---

## 🔄 Workflow Steps

```
1️⃣  Student submits application
    └─ Creates wallet (Metamask)
    └─ Submits essay, documents, personal info
    └─ System creates hash of application

2️⃣  Oracle verifies
    └─ Checks: GPA >= 3.0
    └─ Checks: Income <= $50k
    └─ Checks: Documents verified
    └─ Updates blockchain: isEligible = true

3️⃣  Student claims scholarship
    └─ Clicks "Claim" button
    └─ Smart contract checks: isEligible?
    └─ Smart contract checks: Already claimed?
    └─ Transfers ETH to wallet
    └─ Emits event (proof of distribution)

4️⃣  Verify on Etherscan
    └─ View all transactions
    └─ Check fund transfers
    └─ Confirm events logged
    └─ Proof of transparency
```

---

## 🔑 Key Concepts

### Oracle Pattern
```
Off-Chain (Secret)          On-Chain (Public)
─────────────────          ─────────────────
GPA: 3.8            →      isEligible: true
Income: $30k        →      ✓ Can claim funds
Documents: ✓        →      Event logged forever
```

### Sybil Resistance
```
❌ One student could register 10 times with 10 wallets
✓ Solution: Map each wallet to unique Student ID
   - Can't register same Student ID twice
   - Can't register same wallet twice
```

### Privacy
```
❌ DON'T put on blockchain:
   - Names, emails (huge privacy issue)
   - Exact GPA/income scores
   - Personal essays

✓ DO put on blockchain:
   - Only verification status (true/false)
   - Application hash (proves data integrity)
   - Events (audit trail)
```

---

## 🧪 Testing Sequence

### Option 1: Local (No Real ETH Needed)
```bash
# Terminal 1: Start local blockchain
npx hardhat node

# Terminal 2: Deploy contract
npx hardhat run scripts/deploy.js --network localhost

# Terminal 3: Test oracle
python example_usage.py

# ✓ All functions work, no real money spent
```

### Option 2: Testnet (Free ETH from Faucet)
```bash
# 1. Get testnet ETH: https://sepoliafaucet.com
# 2. Update .env: NETWORK=sepolia
# 3. Deploy: npx hardhat run scripts/deploy.js --network sepolia
# 4. Update .env: CONTRACT_ADDRESS=0x...
# 5. Test: python example_usage.py
# ✓ Transactions visible on Etherscan!
```

---

## ⚙️ Configuration Checklist

Before running, ensure:

- [ ] `.env` file created (copy from `.env.example`)
- [ ] `NETWORK` set (use `sepolia` for demo)
- [ ] `DEPLOYER_PRIVATE_KEY` filled in (from Metamask)
- [ ] `ORACLE_PRIVATE_KEY` filled in (new wallet)
- [ ] Testnet ETH in deployer wallet (get from faucet)
- [ ] `CONTRACT_ADDRESS` filled in (after deployment)
- [ ] Python packages installed (`pip install -r blockchain_requirements.txt`)
- [ ] Database initialized (`python database_models.py`)

---

## 🐛 Troubleshooting

| Error | Fix |
|-------|-----|
| "Connection refused" | Start blockchain: `npx hardhat node` |
| "Insufficient funds" | Get testnet ETH: https://sepoliafaucet.com |
| "Only oracle can verify" | Check ORACLE_PRIVATE_KEY in .env |
| "Student not found" | Register student first: `connector.register_student()` |
| "Already claimed" | Each student can only claim once |

---

## 📊 Architecture in One Picture

```
┌─────────────────┐
│     Frontend    │ React/Vite on localhost:8080
│  (student app)  │ - Registration form
└────────┬────────┘ - Claim button
         │
    HTTP │ JSON
         │
┌────────▼────────┐
│   Python API    │ Flask on localhost:5000
│ (backend logic) │ - Student endpoints
└────────┬────────┘ - Verification triggers
         │
         ├──────────┬──────────┐
         ▼          ▼          ▼
    Database    Oracle     Blockchain
    (SQLite)    Service    (Sepolia)
    - PII       - Verify   - Funds
    - Apps      - Sign TX  - Rules
    - History   - Log      - Events
```

---

## 🎯 For Ideathon Judges

**Show them:**
1. ✅ Smart contract deployed on Sepolia
2. ✅ All transactions visible on Etherscan
3. ✅ Oracle verified students automatically
4. ✅ Students received real ETH
5. ✅ Immutable history (can't be changed)

**Key value prop:**
> "Unlike traditional systems, every decision is recorded on blockchain. Impossible to deny, manipulate, or lose. Perfect for government scholarships where accountability is critical."

---

## 📚 Documentation Files

- **IDEATHON_GUIDE.md** ← Start here! (5 min read)
- **DEPLOYMENT_GUIDE.md** ← Step-by-step setup (30 min)
- **README_BLOCKCHAIN.md** ← Full architecture (deep dive)
- **example_usage.py** ← Code examples (learn by doing)

---

## ✨ You Have:

✅ Smart contract (fully functional)
✅ Python oracle service (ready to verify)
✅ Database models (for student tracking)
✅ Full documentation (setup to deployment)
✅ Example code (copy-paste ready)
✅ Verification script (check everything works)

**→ You're ready to deploy! Follow IDEATHON_GUIDE.md next**

---

## 🎓 This Teaches:

- Smart contract development (Solidity)
- Blockchain integration (Web3.py)
- Oracle patterns (off-chain verification)
- Database design (SQLAlchemy)
- Security (Sybil resistance, privacy)
- Full-stack development (frontend to blockchain)

Perfect for an ideathon! 🚀
