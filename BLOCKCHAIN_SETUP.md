# EduChain Scholar Hub - Blockchain Integration Setup

This guide helps you set up the Python-Solidity blockchain integration for the EduChain Scholar Hub scholarship management application.

## 📋 Files Created

1. **blockchain_connector.py** - Main Python module for blockchain interaction
2. **ScholarshipHub.sol** - Solidity smart contract for scholarship management
3. **blockchain_requirements.txt** - Python dependencies
4. **example_usage.py** - Integration examples and usage patterns

---

## 🚀 Quick Start

### 1. Open Homepage with Go Live

In VS Code:
- Your Vite server runs on **http://localhost:8080**
- **Method 1:** Click the "Go Live" button in the status bar (bottom-right corner)
- **Method 2:** Run in terminal:
  ```bash
  npm run dev
  # or with bun
  bun run dev
  ```
- Open browser to: **http://localhost:8080**

### 2. Set Up Python Environment

```bash
# Install dependencies
pip install -r blockchain_requirements.txt

# Or install individually
pip install web3 eth-account python-dotenv
```

### 3. Create Environment File

Create `.env` file in project root:
```env
PRIVATE_KEY=your_ethereum_private_key_here
CONTRACT_ADDRESS=deployed_contract_address_here
NETWORK=localhost
```

---

## 🔗 Blockchain Integration

### ScholarshipHub Smart Contract Features

The Solidity contract (`ScholarshipHub.sol`) provides:

- **Scholarship Management**: Create and manage scholarships
- **Fund Distribution**: Distribute funds to eligible students
- **Balance Tracking**: Monitor scholarship and student balances
- **Admin Controls**: Multi-admin scholarship management
- **Event Logging**: Track all blockchain transactions

### Key Functions

```solidity
// Create scholarship
addScholarship(string title, uint256 amount, uint256 beneficiaryCount, string description)

// Distribute funds
distributeScholarship(uint256 scholarshipId, address student, uint256 amount)

// Check balance
getScholarshipBalance(uint256 scholarshipId)

// Withdraw funds
withdrawStudentFunds(uint256 amount)
```

### Python Integration

```python
from blockchain_connector import create_connector

# Connect to blockchain
connector = create_connector("localhost")

# Create scholarship
tx = connector.add_scholarship(
    title="Tech Excellence Award",
    amount_wei=1000000000000000000,  # 1 ETH
    beneficiary_count=10,
    description="For outstanding tech students"
)

# Distribute to student
distribution = connector.distribute_scholarship(
    student_address="0x742d35Cc6634C0532925a3b844Bc2e0e42d79e18",
    amount_wei=100000000000000000,  # 0.1 ETH
    scholarship_id=0
)

# Check balance
balance = connector.get_scholarship_balance(0)
print(f"Remaining: {balance['balance_eth']} ETH")
```

---

## 🔧 Setup for Testing

### Option A: Local Blockchain (Recommended for Development)

1. **Install Hardhat:**
   ```bash
   npm install --save-dev hardhat
   npx hardhat
   ```

2. **Start local node:**
   ```bash
   npx hardhat node
   ```

3. **In another terminal, run Python script:**
   ```bash
   python example_usage.py
   ```

### Option B: Public Testnet

Update `.env`:
```env
NETWORK=sepolia
PRIVATE_KEY=your_testnet_private_key
```

Requires testnet ETH from faucet (https://sepoliafaucet.com)

### Option C: Public Testnet with Infura

1. Create account at https://infura.io
2. Add to `.env`:
   ```env
   INFURA_KEY=your_infura_key
   NETWORK=sepolia
   ```

3. Update blockchain_connector.py network URLs

---

## 📱 Web Application Integration

To connect your React frontend with Python backend:

### Backend API Server

Create `api_server.py`:
```python
from flask import Flask, jsonify, request
from blockchain_connector import create_connector
import os

app = Flask(__name__)
connector = create_connector(os.getenv("NETWORK", "localhost"))

@app.route("/api/scholarship/<int:id>", methods=["GET"])
def get_scholarship(id):
    return jsonify(connector.get_scholarship_balance(id))

@app.route("/api/distribute", methods=["POST"])
def distribute():
    data = request.json
    result = connector.distribute_scholarship(
        student_address=data["address"],
        amount_wei=data["amount"],
        scholarship_id=data["scholarship_id"]
    )
    return jsonify(result)

if __name__ == "__main__":
    app.run(port=5000)
```

### Frontend Integration (React)

```typescript
// src/services/blockchain.ts
export async function getScholarshipBalance(id: number) {
  const response = await fetch(`http://localhost:5000/api/scholarship/${id}`);
  return response.json();
}

export async function distributeScholarship(
  studentAddress: string,
  amount: bigint,
  scholarshipId: number
) {
  const response = await fetch("http://localhost:5000/api/distribute", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      address: studentAddress,
      amount: amount.toString(),
      scholarship_id: scholarshipId,
    }),
  });
  return response.json();
}
```

---

## 🧪 Testing

Run tests with:
```bash
# Python tests
pytest blockchain_connector.py

# React/Vite tests
npm test
bun run test
```

---

## 📚 Additional Resources

- **Web3.py Docs**: https://web3py.readthedocs.io/
- **Solidity Docs**: https://docs.soliditylang.org/
- **Hardhat**: https://hardhat.org/
- **Ethereum Testnet Faucets**: https://sepoliafaucet.com

---

## ⚠️ Security Notes

- **Never commit `.env` file** to version control
- **Use testnet** for development/testing
- **Validate all inputs** before blockchain transactions
- **Use hardware wallet** for mainnet deployments
- **Audit smart contracts** before production use

---

## 🐛 Troubleshooting

**Connection Error:**
```
ConnectionError: Failed to connect to http://localhost:8545
```
→ Make sure local blockchain is running (`npx hardhat node`)

**Transaction Failed:**
```
ValueError: Insufficient contract balance
```
→ Check account balance with `connector.get_account_balance()`

**Contract Not Found:**
```
ValueError: Contract not loaded
```
→ Load contract with `connector.load_contract(address, abi)`

---

## 📞 Support

For issues or questions about integration:
1. Check the example_usage.py file
2. Review ScholarshipHub.sol documentation
3. Test with blockchain_connector.py directly

Happy coding! 🚀
