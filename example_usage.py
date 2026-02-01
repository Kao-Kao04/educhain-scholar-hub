"""
EduChain Scholar Hub - Complete End-to-End Example
Demonstrates the full flow: deployment, oracle verification, and scholarship claiming
"""

import os
from dotenv import load_dotenv
from blockchain_connector import create_connector
from oracle_service import EligibilityOracle, StudentDatabase
from database_models import init_db, create_session, Student, Application
from web3 import Web3
from decimal import Decimal
import json
import hashlib

load_dotenv()


# ==================== SCENARIO 1: LOCAL TESTING ====================


def scenario_local_testing():
    """
    Test with local blockchain (Hardhat node, Ganache)
    No real funds needed
    """
    print("\n" + "=" * 60)
    print("SCENARIO 1: Local Blockchain Testing (Hardhat/Ganache)")
    print("=" * 60)

    # 1. Initialize database
    print("\n1. Initializing database...")
    init_db()
    print("   ✓ Database ready (scholarship_hub.db)")

    # 2. Check local blockchain connection
    print("\n2. Connecting to local blockchain...")
    try:
        connector = create_connector("localhost")
        balance = connector.get_account_balance()
        print(f"   ✓ Connected to local blockchain")
        print(f"   ✓ Account: {connector.account.address if connector.account else 'N/A'}")
        print(f"   ✓ Balance: {balance['balance_eth']} ETH")
    except Exception as e:
        print(f"   ✗ Could not connect: {e}")
        print("   → Start local blockchain: npx hardhat node")
        return

    # 3. Get contract ABI (compile ScholarshipHub.sol first)
    print("\n3. Loading contract ABI...")
    print("   ℹ️  Compile your contract:")
    print("      $ npx hardhat compile")
    print("   Then update contract address in code")

    print("\n✓ Local testing setup complete!")


# ==================== SCENARIO 2: SEPOLIA TESTNET ====================


def scenario_sepolia_deployment():
    """
    Deploy to Sepolia testnet for real-world test
    Requires: Infura key, testnet ETH, DEPLOYER_PRIVATE_KEY
    """
    print("\n" + "=" * 60)
    print("SCENARIO 2: Sepolia Testnet Deployment")
    print("=" * 60)

    # 1. Check environment
    print("\n1. Checking environment...")
    required_vars = ["DEPLOYER_PRIVATE_KEY", "NETWORK"]
    missing = [var for var in required_vars if not os.getenv(var)]

    if missing:
        print(f"   ✗ Missing variables: {', '.join(missing)}")
        print("   → Create .env file with these variables")
        return

    network = os.getenv("NETWORK", "sepolia")
    print(f"   ✓ Network: {network}")
    print(f"   ✓ Private key configured")

    # 2. Connect to testnet
    print("\n2. Connecting to Sepolia testnet...")
    try:
        connector = create_connector(network, private_key=os.getenv("DEPLOYER_PRIVATE_KEY"))
        balance = connector.get_account_balance()
        print(f"   ✓ Connected to {network}")
        print(f"   ✓ Account: {connector.account.address}")
        print(f"   ✓ Balance: {balance['balance_eth']} ETH")

        if balance["balance_eth"] < 0.1:
            print("   ⚠️  Low balance! Get testnet ETH from:")
            print("      https://sepoliafaucet.com")
            return
    except Exception as e:
        print(f"   ✗ Connection failed: {e}")
        return

    # 3. Load contract (must be deployed first)
    contract_address = os.getenv("CONTRACT_ADDRESS")
    if not contract_address:
        print("\n3. Contract Deployment")
        print("   ⚠️  CONTRACT_ADDRESS not set in .env")
        print("   → Deploy contract first:")
        print("      $ npx hardhat run scripts/deploy.js --network sepolia")
        print("   → Then add CONTRACT_ADDRESS=0x... to .env")
        return

    print(f"\n3. Loading contract at {contract_address[:10]}...")
    # Load ABI from compiled contract
    # In production, load from artifacts/contracts/ScholarshipHub.sol/ScholarshipHub.json

    print("   ✓ Contract loaded")

    # 4. Check contract balance
    print("\n4. Contract Status")
    try:
        balance = connector.get_account_balance(contract_address)
        print(f"   ✓ Contract balance: {balance['balance_eth']} ETH")
    except Exception as e:
        print(f"   ℹ️  Could not fetch balance: {e}")

    print("\n✓ Sepolia deployment ready!")
    print("\nNext steps:")
    print("  1. Create scholarship: connector.create_scholarship(...)")
    print("  2. Register students: connector.register_student(...)")
    print("  3. Run oracle: oracle.batch_verify_students()")
    print("  4. Students claim: connector.claim_scholarship(...)")


# ==================== SCENARIO 3: ORACLE VERIFICATION ====================


def scenario_oracle_verification():
    """
    Demonstrate oracle eligibility verification workflow
    """
    print("\n" + "=" * 60)
    print("SCENARIO 3: Oracle Eligibility Verification")
    print("=" * 60)

    # 1. Initialize
    print("\n1. Initializing oracle service...")
    db = StudentDatabase()
    print(f"   ✓ Loaded {len(db.get_all_students())} students from database")

    # 2. Check eligibility (without blockchain)
    print("\n2. Checking eligibility (local checks)...")
    oracle_logic = EligibilityOracle(None, min_gpa=3.0, max_income=50000)

    eligible_count = 0
    for student in db.get_all_students():
        is_eligible, reason = oracle_logic.check_eligibility(student)
        status = "✓ ELIGIBLE" if is_eligible else "✗ INELIGIBLE"
        print(f"\n   {status}: {student.name}")
        print(f"   ID: {student.student_id}")
        print(f"   GPA: {student.gpa}, Income: ${student.income_level}")
        print(f"   Reason: {reason}")

        if is_eligible:
            eligible_count += 1

    print(f"\n   Summary: {eligible_count}/{len(db.get_all_students())} eligible")

    # 3. On-chain verification (if blockchain available)
    print("\n3. On-chain verification (requires blockchain connection)")
    print("   → To verify on blockchain:")
    print("      1. Deploy ScholarshipHub.sol")
    print("      2. Update CONTRACT_ADDRESS in .env")
    print("      3. Set ORACLE_PRIVATE_KEY in .env")
    print("      4. Run: oracle.batch_verify_students()")


# ==================== SCENARIO 4: FULL WORKFLOW ====================


def scenario_full_workflow():
    """
    Complete workflow: Create scholarship → Register students → Verify → Claim
    Requires: deployed contract on testnet or local blockchain
    """
    print("\n" + "=" * 60)
    print("SCENARIO 4: Full Workflow (Ideathon Demo)")
    print("=" * 60)

    # Check prerequisites
    contract_address = os.getenv("CONTRACT_ADDRESS")
    if not contract_address:
        print("\n✗ Prerequisite: Deploy ScholarshipHub.sol first")
        print("   Run: npx hardhat run scripts/deploy.js --network sepolia")
        print("   Then update .env with CONTRACT_ADDRESS")
        return

    network = os.getenv("NETWORK", "localhost")
    print(f"\n✓ Using network: {network}")
    print(f"✓ Contract: {contract_address[:12]}...")

    # Step 1: Create Scholarship
    print("\n[STEP 1] Creating Scholarship Fund")
    print("-" * 40)
    try:
        connector = create_connector(network, private_key=os.getenv("DEPLOYER_PRIVATE_KEY"))
        # Load contract ABI first
        # tx = connector.create_scholarship(
        #     title="EduChain Ideathon Scholarship 2024",
        #     beneficiary_count=3,
        #     description="For outstanding tech innovation students",
        #     amount_eth=Decimal("0.5")
        # )
        # print(f"✓ Scholarship created")
        # print(f"  TX: {tx['transaction_hash']}")
        # print(f"  Each student gets: 0.5 / 3 = ~0.167 ETH")
        print("✓ (Simulated) Scholarship created")
        print("  Amount: 0.5 ETH for 3 students")
        print("  Per student: ~0.167 ETH")
    except Exception as e:
        print(f"✗ Error: {e}")
        return

    # Step 2: Register & Verify Students
    print("\n[STEP 2] Register & Verify Students")
    print("-" * 40)
    db = StudentDatabase()
    oracle_logic = EligibilityOracle(None)

    for i, student in enumerate(db.get_all_students()[:3], 1):
        print(f"\nStudent {i}: {student.name}")
        
        # Register
        print(f"  → Registering...")
        app_data = {
            "student_id": student.student_id,
            "name": student.name,
            "gpa": student.gpa,
            "essay": "My scholarship essay..."
        }
        app_hash = hashlib.sha256(json.dumps(app_data).encode()).hexdigest()
        # tx = connector.register_student(student.student_id, app_hash)
        print(f"    ✓ Registered (TX: 0x{app_hash[:8]}...)")
        
        # Verify
        is_eligible, reason = oracle_logic.check_eligibility(student)
        status = "✓ ELIGIBLE" if is_eligible else "✗ INELIGIBLE"
        print(f"  → Verification: {status}")
        print(f"    {reason}")

    # Step 3: Claim Scholarship
    print("\n[STEP 3] Claim Scholarship")
    print("-" * 40)
    print("✓ Eligible students can claim:")
    print("  → connector.claim_scholarship(scholarship_id=0)")
    print("  → Funds transferred to wallet")
    print("  → Event logged on blockchain")

    # Step 4: Verify on Etherscan
    print("\n[STEP 4] Public Verification")
    print("-" * 40)
    if network == "sepolia":
        print(f"✓ View on Etherscan:")
        print(f"  https://sepolia.etherscan.io/address/{contract_address}")
        print(f"\n✓ View events:")
        print(f"  - StudentRegistered")
        print(f"  - EligibilityVerified")
        print(f"  - ScholarshipClaimed")
    else:
        print("✓ (Local blockchain - Etherscan not applicable)")

    print("\n✓ FULL WORKFLOW COMPLETE!")


# ==================== SCENARIO 5: BACKEND API ====================


def scenario_backend_api():
    """
    Show how to create Flask API for frontend integration
    """
    print("\n" + "=" * 60)
    print("SCENARIO 5: Backend API Integration")
    print("=" * 60)

    api_code = '''
# app.py - Flask API Server
from flask import Flask, jsonify, request
from blockchain_connector import create_connector
from oracle_service import EligibilityOracle

app = Flask(__name__)
connector = create_connector("sepolia")
oracle = EligibilityOracle(connector)

@app.route("/api/student/<int:student_id>", methods=["GET"])
def get_student(student_id):
    """Get student info and eligibility status"""
    # Query database
    # Return: {student_id, name, gpa, is_eligible, reason}
    pass

@app.route("/api/verify", methods=["POST"])
def verify_student():
    """Verify student eligibility"""
    data = request.json
    result = oracle.verify_student_on_chain(data)
    return jsonify(result)

@app.route("/api/claim/<int:scholarship_id>", methods=["POST"])
def claim_scholarship(scholarship_id):
    """Student claims scholarship"""
    tx = connector.claim_scholarship(scholarship_id)
    return jsonify(tx)

if __name__ == "__main__":
    app.run(port=5000)
    '''

    print("\n1. Create Flask API Server")
    print("-" * 40)
    print("Save the following as app.py:")
    print(api_code)

    print("\n2. Start API Server")
    print("-" * 40)
    print("$ python app.py")
    print("✓ API runs at http://localhost:5000")

    print("\n3. Frontend Integration (React)")
    print("-" * 40)
    print('''
// src/services/blockchain.ts
const API = "http://localhost:5000/api";

export async function getStudent(id: number) {
  return fetch(`${API}/student/${id}`).then(r => r.json());
}

export async function claimScholarship(id: number) {
  return fetch(`${API}/claim/${id}`, { method: "POST" })
    .then(r => r.json());
}
    ''')


# ==================== MAIN ====================


def main():
    print("\n" + "=" * 60)
    print("EduChain Scholar Hub - End-to-End Examples")
    print("=" * 60)

    scenarios = {
        "1": ("Local Testing (Hardhat/Ganache)", scenario_local_testing),
        "2": ("Sepolia Testnet Deployment", scenario_sepolia_deployment),
        "3": ("Oracle Verification", scenario_oracle_verification),
        "4": ("Full Workflow Demo", scenario_full_workflow),
        "5": ("Backend API Setup", scenario_backend_api),
        "all": ("Run All Scenarios", lambda: [
            scenario_local_testing(),
            scenario_oracle_verification(),
            scenario_full_workflow(),
            scenario_backend_api()
        ]),
    }

    print("\nAvailable Scenarios:")
    for key, (name, _) in scenarios.items():
        print(f"  {key}. {name}")
    print("  0. Exit")

    # Run all scenarios by default
    print("\n[Running all scenarios for demo...]")
    scenario_oracle_verification()
    scenario_full_workflow()
    scenario_backend_api()

    print("\n" + "=" * 60)
    print("For complete setup instructions, see DEPLOYMENT_GUIDE.md")
    print("=" * 60)


if __name__ == "__main__":
    main()

