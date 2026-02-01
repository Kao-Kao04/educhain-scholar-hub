# EduChain Scholar Hub - Blockchain Implementation

> Decentralized scholarship management system powered by Ethereum smart contracts and Python oracle verification.

## 🎯 Project Vision

EduChain Scholar Hub solves the **transparency and fraud problems** in traditional scholarship systems by:

- **Immutable Rules**: Smart contract logic cannot be changed after deployment
- **Public Transactions**: Every scholarship distribution is recorded on blockchain
- **Privacy-First**: Student PII stays off-chain; only verification status is on-chain
- **Sybil Resistance**: Each student mapped to unique university ID
- **Oracle Integration**: Python backend verifies eligibility using configurable rules

## 📐 Architecture

### Hybrid Model

```
┌─────────────────────────────────────────────────────────────┐
│                     Off-Chain (Python)                       │
│  Database, Student Data, Application Essays, Document PDFs   │
│  - Sensitive PII protected                                   │
│  - Flexible database backend                                 │
│  - Student verification logic                                │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────┤ Oracle Service (Verifier)
        │                  │ - Queries student data
        │                  │ - Checks eligibility rules
        ▼                  │ - Updates blockchain
┌──────────────────────────▼──────────────────────────────────┐
│                   On-Chain (Solidity)                         │
│  ScholarshipManager.sol - Smart Contract                      │
│  - Scholarship funds (ETH)                                   │
│  - Verification status (boolean)                             │
│  - Distribution rules                                        │
│  - Event logs (immutable history)                            │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
1. Student Submits Application
   ├─ Application data → Database
   └─ Eligibility status → Blockchain

2. Oracle Verification
   ├─ Check GPA, Income, Documents (off-chain)
   ├─ Sign verification transaction
   └─ Update blockchain eligibility status

3. Student Claims Scholarship
   ├─ Check: isEligible && !hasClaimedAlready
   ├─ Transfer ETH
   └─ Emit event (public record)

4. Immutable History
   └─ All transactions visible on Etherscan forever
```

## 🔧 Core Components

### 1. Solidity Smart Contract (`ScholarshipManager.sol`)

**Key Functions:**
- `verifySponsor(address)` - Admin verifies sponsor
- `verifyStudent(address, assignedSponsor, amount, initialGpa)` - Admin verifies student
- `fundStudent(address)` - Sponsor funds student (payable)
- `claimScholarship()` - Student claims funds

**Safety Features:**
- `onlyOracle` modifier: Only trusted oracle can verify
- `studentIsEligible` modifier: Only eligible students can claim
- Prevents double-claiming with `hasClaimedScholarship` flag
- Sybil resistance: Wallet mapped to unique student ID

### 2. Python Oracle Service (`oracle_service.py`)

```python
from oracle_service import EligibilityOracle

oracle = EligibilityOracle(connector, min_gpa=3.0, max_income=50000)

# Check eligibility
is_eligible, reason = oracle.check_eligibility(student_data)

# Verify on-chain (admin)
result = oracle.verify_student_on_chain(
   student_data,
   sponsor_address="0xSponsorAddress...",
   amount_wei=Web3.to_wei(0.1, "ether")
)
```

**Features:**
- Configurable eligibility rules
- Batch verification
- Integration with student database
- Blockchain transaction handling

### 3. Blockchain Connector (`blockchain_connector.py`)

```python
from blockchain_connector import create_connector

connector = create_connector("sepolia", private_key=os.getenv("DEPLOYER_PRIVATE_KEY"))

# Verify sponsor (admin)
connector.verify_sponsor("0xSponsorAddress...")

# Verify student (admin)
connector.verify_student(
   student_address="0xStudentAddress...",
   assigned_sponsor="0xSponsorAddress...",
   amount_wei=Web3.to_wei(0.1, "ether"),
   initial_gpa=350
)

# Sponsor funds student
connector.fund_student("0xStudentAddress...", Web3.to_wei(0.1, "ether"))

# Student claims funds
connector.claim_scholarship()
```

### 4. Database Models (`database_models.py`)

SQLAlchemy ORM models for:
- **Student**: Personal info, GPA, income, verification status
- **Application**: Essays, documents, application hash
- **Verification**: Eligibility record, verification history
- **ScholarshipProgram**: Scholarship details
- **ClaimRecord**: Track scholarship claims

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r blockchain_requirements.txt
pip install sqlalchemy flask python-dotenv
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your values
```

### 3. Deploy Smart Contract

```bash
# Use Hardhat (recommended)
npx hardhat init
cp ScholarshipManager.sol contracts/
npx hardhat run scripts/deploy.js --network sepolia

# Add CONTRACT_ADDRESS to .env
```

### 4. Initialize Database

```bash
python -c "from database_models import init_db; init_db()"
```

### 5. Run Oracle Service

```bash
python oracle_service.py
```

### 6. Start Backend API

```bash
python app.py
# API available at http://localhost:5000
```

### 7. Run Frontend

```bash
bun run dev
# Frontend available at http://localhost:8080
```

## 📊 Workflow Example

### Step 1: Verify Sponsor (Admin)

```python
from blockchain_connector import create_connector
from decimal import Decimal

connector = create_connector("sepolia", 
    private_key=os.getenv("DEPLOYER_PRIVATE_KEY"))

tx = connector.verify_sponsor("0xSponsorAddress...")
print(f"Sponsor verified: {tx['transaction_hash']}")
```

### Step 2: Verify Student (Admin)

```python
# Student creates wallet (Metamask)
# Student submits application with essay, documents

app_data = {
    "student_id": 123,
    "name": "Alice Chen",
    "gpa": 3.8,
    "essay": "Why I deserve this scholarship..."
}

# Verify student on blockchain
connector.verify_student(
   student_address="0xStudentAddress...",
   assigned_sponsor="0xSponsorAddress...",
   amount_wei=Web3.to_wei(0.5, "ether"),
   initial_gpa=380
)
```

### Step 3: Oracle Verifies

```python
from oracle_service import EligibilityOracle, StudentDatabase

db = StudentDatabase()
oracle = EligibilityOracle(connector)

# Get student from database
student = db.get_student(123)

# Check eligibility (GPA >= 3.0, Income <= $50k, etc.)
is_eligible, reason = oracle.check_eligibility(student)

# Update blockchain (admin)
result = oracle.verify_student_on_chain(
   student,
   sponsor_address="0xSponsorAddress...",
   amount_wei=Web3.to_wei(0.5, "ether")
)
```

### Step 4: Sponsor Funds & Student Claims

```python
# Sponsor funds student
connector.fund_student("0xStudentAddress...", Web3.to_wei(0.5, "ether"))

# Student (with wallet) calls claim function
tx = connector.claim_scholarship()

# Smart contract:
# 1. Checks: isEligible == True
# 2. Checks: hasClaimedScholarship == False
# 3. Transfers scholarship amount to student's wallet
# 4. Emits ScholarshipGranted event
```

### Step 5: Verify on Etherscan

```
https://sepolia.etherscan.io/address/0xCONTRACT_ADDRESS

View:
- All transactions
- Scholarship creation events
- Verification events
- Claim events
- Immutable history forever
```

## 🔐 Security & Privacy

### Privacy Design

```
❌ DON'T store on-chain:
- Student names
- Email addresses
- Income amounts
- GPA scores
- Essay content

✓ DO store on-chain:
- Student address (wallet)
- Student ID (anonymous)
- Eligibility status (boolean)
- Sponsor assignment and eligibility status
- Events (transparent history)
```

### Sybil Resistance

```solidity
// One wallet per student ID
mapping(uint256 => address) public studentIdToWallet;

// One student per wallet
mapping(address => Student) public students;

// Prevents: Multiple wallets → Same student ID
require(studentIdToWallet[_studentId] == address(0), 
    "Student ID already registered");
```

### Oracle Security

```solidity
modifier onlyOracle() {
    require(msg.sender == oracleAddress, "Only oracle can verify");
    _;
}

// Owner can update oracle address if needed
function setOracleAddress(address _newOracle) public onlyOwner { }
```

## 🌐 Network Options

### Development
```
Network: localhost
Provider: Hardhat node or Ganache
Cost: Free
Speed: Instant
```

### Testing
```
Network: Sepolia
Provider: Infura or Alchemy
Cost: Free test ETH from faucet
Speed: ~15 seconds per transaction
Visibility: https://sepolia.etherscan.io
```

### Production
```
Network: Ethereum Mainnet or Polygon
Provider: Infura or Alchemy
Cost: Real ETH (~$0.50-$10 per transaction)
Speed: Mainnet 15s, Polygon 2s
```

## 📚 Key Files

```
├── ScholarshipManager.sol       # Smart contract
├── blockchain_connector.py      # Web3 wrapper
├── oracle_service.py            # Eligibility verification
├── database_models.py           # SQLAlchemy ORM
├── example_usage.py             # Complete examples
├── DEPLOYMENT_GUIDE.md          # Step-by-step setup
├── BLOCKCHAIN_SETUP.md          # Architecture overview
├── .env.example                 # Configuration template
└── blockchain_requirements.txt  # Python dependencies
```

## 🧪 Testing

### Local Testing (No Funds Required)

```bash
# 1. Start Hardhat node
npx hardhat node

# 2. Deploy contract
npx hardhat run scripts/deploy.js --network localhost

# 3. Run tests
python example_usage.py
```

### Testnet Testing (Free ETH)

```bash
# 1. Get Sepolia test ETH
# https://sepoliafaucet.com

# 2. Update .env with NETWORK=sepolia

# 3. Deploy and test
npx hardhat run scripts/deploy.js --network sepolia
python example_usage.py
```

## 🐛 Common Issues

**Problem**: "Connection refused"
```
→ Make sure Hardhat node is running: npx hardhat node
```

**Problem**: "Insufficient funds for gas"
```
→ Get testnet ETH from https://sepoliafaucet.com
```

**Problem**: "Only oracle can verify"
```
→ Set DEPLOYER_PRIVATE_KEY correctly
→ Oracle address must match contract's oracleAddress
```

**Problem**: "Already claimed scholarship"
```
→ Each student can only claim once per scholarship
→ Check hasClaimedScholarship flag
```

## 📈 Deployment Checklist

- [ ] Install Node.js and Python dependencies
- [ ] Create `.env` file with wallet keys
- [ ] Get testnet ETH from faucet
- [ ] Compile ScholarshipManager.sol
- [ ] Deploy to Sepolia testnet
- [ ] Update CONTRACT_ADDRESS in .env
- [ ] Initialize database
- [ ] Test oracle service
- [ ] Configure API endpoints
- [ ] Connect frontend to backend
- [ ] Test full workflow
- [ ] Verify on Etherscan

## 🚀 For Ideathon Submission

### Deliverables

1. **Smart Contract**
   - Deployed to Sepolia testnet
   - Verified on Etherscan
   - Function documentation

2. **Oracle Service**
   - Verifies students based on database
   - Updates blockchain
   - Handles batch verification

3. **Backend API**
   - REST endpoints for student info
   - Verification triggers
   - Claim processing

4. **Frontend Integration**
   - Student registration form
   - Eligibility status display
   - Claim button

5. **Documentation**
   - Complete setup guide
   - Architecture diagrams
   - Security analysis

### Demo Flow

```bash
# Terminal 1: Start blockchain
npx hardhat node

# Terminal 2: Deploy contract
npx hardhat run scripts/deploy.js --network localhost

# Terminal 3: Run oracle
python oracle_service.py

# Terminal 4: Start API
python app.py

# Terminal 5: Start frontend
bun run dev

# Browser: http://localhost:8080
# 1. Connect wallet
# 2. Submit application
# 3. Wait for oracle verification
# 4. Claim scholarship
# 5. Check Etherscan
```

## 📖 Resources

- **Solidity Docs**: https://docs.soliditylang.org/
- **Web3.py**: https://web3py.readthedocs.io/
- **Hardhat**: https://hardhat.org/docs
- **Ethereum Dev**: https://ethereum.org/en/developers/
- **OpenZeppelin**: https://docs.openzeppelin.com/

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m "Add amazing feature"`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

## 📄 License

MIT License - see LICENSE file

## 🎓 Educational Value

This project demonstrates:

✓ Smart contract development (Solidity)
✓ Blockchain integration (Web3.py)
✓ Oracle pattern implementation
✓ Privacy-first design
✓ Sybil resistance techniques
✓ Full-stack blockchain development
✓ Real-world use case (scholarships)

Perfect for learning blockchain technology through a meaningful application!

---

**Built with ❤️ for the EduChain initiative**
