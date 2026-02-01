# EduChain Scholar Hub - Deployment Guide

Complete guide for deploying the ScholarshipHub smart contract to testnet and running the oracle service for an ideathon prototype.

## 🎯 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Frontend (React/Vite)                        │
│              http://localhost:8080 (Go Live)                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│              Backend API (Flask/FastAPI)                        │
│               http://localhost:5000                              │
└──────────────────────────┬──────────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
    ┌──────────┐  ┌──────────────┐  ┌────────────┐
    │ Database │  │ Oracle       │  │ Blockchain │
    │ (SQLite) │  │ Service      │  │ (Sepolia)  │
    │ - PII    │  │ - Verifies   │  │ - Funds    │
    │ - Apps   │  │ - Updates    │  │ - Rules    │
    └──────────┘  │ - Logs       │  │ - Events   │
                  └──────────────┘  └────────────┘
```

---

## 📋 Prerequisites

### Required Software
```bash
# Node.js and npm (for contract deployment)
node --version  # Should be v16+
npm --version

# Python 3.8+
python --version

# Git
git --version
```

### Install Dependencies

**Python dependencies:**
```bash
pip install -r blockchain_requirements.txt
pip install sqlalchemy flask python-dotenv
```

Add to `blockchain_requirements.txt`:
```
sqlalchemy==2.0.0
flask==3.0.0
```

**Node.js dependencies (for contract compilation):**
```bash
npm install --save-dev hardhat @nomiclabs/hardhat-waffle ethereum-waffle chai @nomiclabs/hardhat-ethers ethers
```

---

## 🚀 Step 1: Set Up Environment Variables

Create `.env` file in project root:

```env
# Blockchain Network
NETWORK=sepolia
RPC_URL=https://sepolia.infura.io/v3/YOUR_INFURA_KEY
CHAIN_ID=11155111

# Wallet Configuration (Create a new testnet wallet!)
DEPLOYER_PRIVATE_KEY=your_sepolia_testnet_private_key
ORACLE_PRIVATE_KEY=your_oracle_wallet_private_key
OWNER_ADDRESS=0x...  # Owner wallet address

# Contract Addresses (Fill after deployment)
CONTRACT_ADDRESS=0x...  # Deployed ScholarshipHub address

# Database
DATABASE_URL=sqlite:///scholarship_hub.db

# API Server
FLASK_ENV=development
FLASK_PORT=5000
```

### Getting Testnet ETH

1. **Get Infura API Key:**
   - Visit https://infura.io
   - Sign up and create new project
   - Select Sepolia network
   - Copy Project ID

2. **Get Sepolia Test ETH:**
   - Visit https://sepoliafaucet.com
   - Paste your wallet address
   - Request ETH (free, takes ~1 min)
   - Check balance: https://sepolia.etherscan.io

3. **Fund Oracle Wallet:**
   - Create second wallet for oracle
   - Send some ETH from deployer wallet using Metamask
   - Keep minimum ~0.5 ETH for gas

---

## 🔗 Step 2: Deploy Smart Contract

### Option A: Using Hardhat (Recommended)

**1. Initialize Hardhat project:**
```bash
npx hardhat init
# Select "Create a sample project"
```

**2. Create deployment script (`scripts/deploy.js`):**
```javascript
async function main() {
  const ScholarshipHub = await ethers.getContractFactory("ScholarshipHub");
  const scholarship = await ScholarshipHub.deploy();
  await scholarship.deployed();
  
  console.log("✓ ScholarshipHub deployed to:", scholarship.address);
  console.log("\nAdd this to .env:");
  console.log(`CONTRACT_ADDRESS=${scholarship.address}`);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
```

**3. Deploy:**
```bash
# Copy ScholarshipHub.sol to contracts/
cp ScholarshipHub.sol contracts/

# Deploy to Sepolia
npx hardhat run scripts/deploy.js --network sepolia
```

**4. Verify on Etherscan:**
```bash
npx hardhat verify --network sepolia <CONTRACT_ADDRESS>
```

### Option B: Using Remix (Web Browser)

1. Visit https://remix.ethereum.org
2. Create new file: `ScholarshipHub.sol`
3. Copy contract code from your file
4. Click "Compile" (Solidity Compiler)
5. Click "Deploy" and select "Injected Provider (MetaMask)"
6. Confirm in MetaMask
7. Copy deployed contract address to `.env`

---

## 🗄️ Step 3: Initialize Database

```bash
python -c "from database_models import init_db; init_db()"
```

This creates `scholarship_hub.db` with all tables.

---

## 🤖 Step 4: Deploy Oracle Service

### 4a. Configure Oracle

Edit `oracle_service.py` to connect to your contract:

```python
from blockchain_connector import create_connector
from oracle_service import EligibilityOracle
import os

# Load environment
load_dotenv()

# Initialize blockchain connector
connector = create_connector(
    network=os.getenv("NETWORK", "localhost"),
    private_key=os.getenv("ORACLE_PRIVATE_KEY")
)

# Load contract
contract_abi = [...]  # Load from compiled contract
contract_address = os.getenv("CONTRACT_ADDRESS")
connector.load_contract(contract_address, contract_abi)

# Initialize oracle
oracle = EligibilityOracle(connector, min_gpa=3.0, max_income=50000)
```

### 4b. Run Oracle Service

**Test eligibility checks (no blockchain):**
```bash
python oracle_service.py
```

**Register and verify students (with blockchain):**
```python
# In Python REPL or script
from oracle_service import EligibilityOracle
from blockchain_connector import create_connector

connector = create_connector("sepolia")
oracle = EligibilityOracle(connector)

# Verify all students in database
results = oracle.batch_verify_students()
for result in results:
    print(f"✓ {result['student_id']}: {result['reason']}")
```

---

## 🎓 Step 5: Create Scholarship & Fund It

```python
from blockchain_connector import create_connector
from decimal import Decimal

connector = create_connector("sepolia", private_key=os.getenv("DEPLOYER_PRIVATE_KEY"))
connector.load_contract(
    os.getenv("CONTRACT_ADDRESS"),
    contract_abi  # Load from compiled contract
)

# Create scholarship with 10 ETH for 50 students
# Each student gets 0.2 ETH if eligible
tx = connector.create_scholarship(
    title="Tech Excellence Scholarship 2024",
    beneficiary_count=50,
    description="For outstanding computer science students",
    amount_eth=Decimal("10")
)

print(f"✓ Scholarship created!")
print(f"  TX: {tx['transaction_hash']}")
print(f"  Scholarship ID: 0")
```

---

## ✅ Step 6: Students Claim Scholarships

**Student registration and claiming flow:**

```python
# 1. Student registers with application
student_address = "0x742d35Cc6634C0532925a3b844Bc2e0e42d79e18"
student_id = 1

connector.register_student(
    student_id=student_id,
    application_hash="QmXxxx..."  # IPFS hash of their application
)
print(f"✓ Student registered")

# 2. Oracle verifies (runs separately)
# oracle.verify_student_on_chain(student_data)

# 3. Student claims funds (when marked eligible)
tx = connector.claim_scholarship(scholarship_id=0)
print(f"✓ Claimed! TX: {tx['transaction_hash']}")
```

---

## 🌐 Step 7: Set Up Backend API

Create `app.py`:

```python
from flask import Flask, jsonify, request, send_file
from blockchain_connector import create_connector
from oracle_service import EligibilityOracle
from database_models import *
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
db_session = create_session()
connector = create_connector(os.getenv("NETWORK"))
oracle = EligibilityOracle(connector)

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "EduChain Oracle"})

@app.route("/api/student/<int:student_id>", methods=["GET"])
def get_student(student_id):
    student = db_session.query(Student).filter_by(student_id=student_id).first()
    if not student:
        return {"error": "Student not found"}, 404
    return {
        "student_id": student.student_id,
        "name": student.get_full_name(),
        "gpa": student.gpa,
        "eligibility": oracle.get_student_eligibility_status(student.wallet_address)
    }

@app.route("/api/verify", methods=["POST"])
def verify_student():
    data = request.json
    student_id = data.get("student_id")
    
    student = db_session.query(Student).filter_by(student_id=student_id).first()
    if not student:
        return {"error": "Student not found"}, 404
    
    result = oracle.verify_student_on_chain(student)
    return jsonify(result)

@app.route("/api/claim/<int:scholarship_id>", methods=["POST"])
def claim_scholarship(scholarship_id):
    data = request.json
    wallet = data.get("wallet_address")
    
    tx = connector.claim_scholarship(scholarship_id)
    return jsonify(tx)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
```

**Run the API:**
```bash
python app.py
# API runs at http://localhost:5000
```

---

## 🧪 Step 8: Testing the Full Flow

### Test Script (`test_full_flow.py`):

```python
#!/usr/bin/env python3
"""
Complete end-to-end test of EduChain Scholar Hub
"""
import os
from dotenv import load_dotenv
from blockchain_connector import create_connector
from oracle_service import EligibilityOracle, StudentDatabase
from database_models import init_db
from web3 import Web3

load_dotenv()

def main():
    print("\n=== EduChain Scholar Hub - Full Flow Test ===\n")
    
    # 1. Initialize
    print("1️⃣  Initializing...")
    init_db()
    connector = create_connector(os.getenv("NETWORK"))
    oracle = EligibilityOracle(connector)
    db = StudentDatabase()
    print("   ✓ Connected to blockchain")
    print(f"   ✓ Chain ID: {connector.w3.eth.chain_id}")
    
    # 2. Create scholarship
    print("\n2️⃣  Creating scholarship...")
    tx = connector.create_scholarship(
        title="Ideathon Proof of Concept",
        beneficiary_count=3,
        description="For ideathon participants",
        amount_eth=0.5
    )
    print(f"   ✓ Scholarship created")
    print(f"   ✓ TX: {tx['transaction_hash']}")
    
    # 3. Register students
    print("\n3️⃣  Registering students...")
    for student in db.get_all_students()[:3]:
        try:
            connector.register_student(
                student_id=student.student_id,
                application_hash="QmExample123456"
            )
            print(f"   ✓ Registered: {student.name}")
        except Exception as e:
            print(f"   ✗ Registration failed: {e}")
    
    # 4. Verify eligibility
    print("\n4️⃣  Verifying eligibility...")
    results = oracle.batch_verify_students([1, 2, 3])
    for result in results:
        status = "✓" if result["is_eligible"] else "✗"
        print(f"   {status} Student {result['student_id']}: {result['reason']}")
    
    # 5. Test claim
    print("\n5️⃣  Testing scholarship claim...")
    eligible_student = next((s for s in db.get_all_students() if s.student_id == 1), None)
    if eligible_student:
        try:
            tx = connector.claim_scholarship(0)
            print(f"   ✓ Claimed scholarship")
            print(f"   ✓ TX: {tx['transaction_hash']}")
        except Exception as e:
            print(f"   ℹ️  Claim test (expected if not eligible): {e}")
    
    print("\n✓ Full flow test complete!")

if __name__ == "__main__":
    main()
```

**Run test:**
```bash
python test_full_flow.py
```

---

## 📊 Monitoring & Verification

### Check Contract Status

```python
# Get total scholarships
total = connector.call_read_function("getTotalScholarships")
print(f"Total scholarships: {total}")

# Get contract balance
balance = connector.call_read_function("getContractBalance")
print(f"Contract balance: {Web3.from_wei(balance, 'ether')} ETH")

# Get scholarship details
scholarship = connector.call_read_function("getScholarship", 0)
print(f"Scholarship 0: {scholarship}")
```

### View on Etherscan

```
https://sepolia.etherscan.io/address/YOUR_CONTRACT_ADDRESS
```

---

## 🎨 Integration with Frontend

**Update `src/services/blockchain.ts`:**

```typescript
const API_URL = "http://localhost:5000";

export async function getStudentInfo(studentId: number) {
  const res = await fetch(`${API_URL}/api/student/${studentId}`);
  return res.json();
}

export async function verifyStudent(studentId: number) {
  const res = await fetch(`${API_URL}/api/verify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ student_id: studentId }),
  });
  return res.json();
}

export async function claimScholarship(scholarshipId: number, wallet: string) {
  const res = await fetch(`${API_URL}/api/claim/${scholarshipId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ wallet_address: wallet }),
  });
  return res.json();
}
```

---

## 🐛 Troubleshooting

**Problem: "Failed to connect to RPC"**
```bash
# Check RPC URL is valid
curl https://sepolia.infura.io/v3/YOUR_KEY

# Verify network in code
echo $NETWORK  # Should be 'sepolia'
```

**Problem: "Insufficient funds for gas"**
```bash
# Get more testnet ETH
# https://sepoliafaucet.com
# Wait 1-2 minutes before retrying
```

**Problem: "verifyEligibility only callable by oracle"**
```python
# Make sure ORACLE_PRIVATE_KEY is set
# And oracle address matches contract's oracleAddress

connector = create_connector("sepolia", private_key=os.getenv("ORACLE_PRIVATE_KEY"))
print(connector.account.address)  # Should match contract oracle
```

---

## ✨ For Ideathon Submission

### Deliverables Checklist

- [ ] Smart contract deployed to Sepolia
- [ ] Contract address in `.env`
- [ ] Oracle service running and verifying students
- [ ] Database initialized with sample students
- [ ] Backend API running on port 5000
- [ ] Frontend connects to API
- [ ] Test flow: Register → Verify → Claim working
- [ ] Etherscan verification of contract
- [ ] README with setup instructions

### Demo Script

```bash
# 1. Start blockchain connector
python oracle_service.py

# 2. Start backend API (new terminal)
python app.py

# 3. Start frontend
bun run dev

# 4. Open http://localhost:8080
# 5. Connect wallet (MetaMask on Sepolia)
# 6. Submit application
# 7. Wait for oracle verification
# 8. Claim scholarship
```

---

## 📚 Resources

- **Sepolia Faucet**: https://sepoliafaucet.com
- **Etherscan Sepolia**: https://sepolia.etherscan.io
- **Hardhat Docs**: https://hardhat.org
- **Web3.py Docs**: https://web3py.readthedocs.io
- **Solidity Docs**: https://docs.soliditylang.org
- **Infura**: https://infura.io

---

## 🚀 Next Steps (Post-Ideathon)

1. **Mainnet Deployment**: Deploy to Ethereum mainnet
2. **Frontend Completion**: Full UI for student portal
3. **Multi-signature Oracle**: Multiple verifiers for security
4. **IPFS Integration**: Store documents on IPFS
5. **Zero-Knowledge Proofs**: Privacy-preserving verification
6. **DAO Governance**: Decentralized scholarship decisions

---

Happy building! 🎓🔗
