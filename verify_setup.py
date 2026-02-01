#!/usr/bin/env python3
"""
EduChain Scholar Hub - Deployment Verification Checklist
Run this script to verify all components are ready for deployment
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def check_files():
    """Verify all required files exist"""
    print("\n📋 Checking Required Files...")
    print("-" * 50)
    
    required_files = {
        "Smart Contract": "ScholarshipHub.sol",
        "Blockchain Connector": "blockchain_connector.py",
        "Oracle Service": "oracle_service.py",
        "Database Models": "database_models.py",
        "Example Usage": "example_usage.py",
        "Deployment Guide": "DEPLOYMENT_GUIDE.md",
        "Blockchain Setup": "BLOCKCHAIN_SETUP.md",
        "README": "README_BLOCKCHAIN.md",
        "Ideathon Guide": "IDEATHON_GUIDE.md",
        "Environment Template": ".env.example",
        "Requirements": "blockchain_requirements.txt",
    }
    
    all_exist = True
    for name, file in required_files.items():
        exists = Path(file).exists()
        status = "✓" if exists else "✗"
        print(f"{status} {name:<25} ({file})")
        if not exists:
            all_exist = False
    
    return all_exist


def check_python_packages():
    """Verify Python packages can be imported"""
    print("\n🐍 Checking Python Packages...")
    print("-" * 50)
    
    packages = {
        "web3": "Web3.py",
        "eth_account": "Eth-Account",
        "sqlalchemy": "SQLAlchemy",
    }
    
    all_installed = True
    for package, name in packages.items():
        try:
            __import__(package)
            print(f"✓ {name:<25} installed")
        except ImportError:
            print(f"✗ {name:<25} NOT installed")
            print(f"  → Install: pip install {package}")
            all_installed = False
    
    return all_installed


def check_env_file():
    """Verify .env file configuration"""
    print("\n⚙️  Checking Environment Configuration...")
    print("-" * 50)
    
    # Check if .env exists
    if not Path(".env").exists():
        print("✗ .env file not found")
        print("  → Copy: cp .env.example .env")
        print("  → Edit: Fill in your private keys and addresses")
        return False
    
    load_dotenv()
    
    required_vars = {
        "NETWORK": "Blockchain network (localhost, sepolia, etc.)",
        "DEPLOYER_PRIVATE_KEY": "Deployer wallet private key",
        "ORACLE_PRIVATE_KEY": "Oracle wallet private key",
        "DATABASE_URL": "Database connection URL",
    }
    
    all_set = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            print(f"✓ {var:<30} configured")
        else:
            print(f"✗ {var:<30} NOT set")
            print(f"  → {description}")
            all_set = False
    
    # Optional variables
    contract_address = os.getenv("CONTRACT_ADDRESS")
    if not contract_address:
        print("ℹ️  CONTRACT_ADDRESS not yet set (fill after deployment)")
    else:
        print(f"✓ CONTRACT_ADDRESS configured ({contract_address[:10]}...)")
    
    return all_set


def check_solidity_syntax():
    """Basic Solidity file validation"""
    print("\n🔗 Checking Smart Contract...")
    print("-" * 50)
    
    try:
        with open("ScholarshipHub.sol", "r") as f:
            content = f.read()
        
        checks = {
            "pragma solidity": "Solidity version declaration",
            "contract ScholarshipHub": "Contract name",
            "function registerStudent": "Student registration",
            "function verifyEligibility": "Oracle verification",
            "function createScholarship": "Scholarship creation",
            "function claimScholarship": "Scholarship claim",
        }
        
        all_present = True
        for keyword, description in checks.items():
            if keyword in content:
                print(f"✓ {description:<30} present")
            else:
                print(f"✗ {description:<30} NOT found")
                all_present = False
        
        return all_present
    except FileNotFoundError:
        print("✗ ScholarshipHub.sol not found")
        return False


def check_python_modules():
    """Verify Python modules are syntactically correct"""
    print("\n✅ Checking Python Modules...")
    print("-" * 50)
    
    modules = {
        "blockchain_connector.py": "Blockchain Connector",
        "oracle_service.py": "Oracle Service",
        "database_models.py": "Database Models",
    }
    
    all_valid = True
    for file, name in modules.items():
        try:
            with open(file, "r") as f:
                compile(f.read(), file, "exec")
            print(f"✓ {name:<30} syntax valid")
        except SyntaxError as e:
            print(f"✗ {name:<30} syntax error: {e}")
            all_valid = False
        except FileNotFoundError:
            print(f"✗ {name:<30} file not found")
            all_valid = False
    
    return all_valid


def main():
    """Run all verification checks"""
    print("\n" + "=" * 60)
    print("EduChain Scholar Hub - Deployment Verification")
    print("=" * 60)
    
    checks = [
        ("Required Files", check_files),
        ("Python Packages", check_python_packages),
        ("Environment Configuration", check_env_file),
        ("Smart Contract", check_solidity_syntax),
        ("Python Modules", check_python_modules),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ Error checking {name}: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nScore: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All checks passed! Ready for deployment!")
        print("\nNext steps:")
        print("1. Deploy smart contract: npx hardhat run scripts/deploy.js --network sepolia")
        print("2. Update CONTRACT_ADDRESS in .env")
        print("3. Initialize database: python -c 'from database_models import init_db; init_db()'")
        print("4. Run oracle: python oracle_service.py")
        print("5. Start backend: python app.py")
        print("6. Run frontend: bun run dev")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("\nFor help, see:")
        print("- DEPLOYMENT_GUIDE.md (setup instructions)")
        print("- IDEATHON_GUIDE.md (quick start)")
        print("- README_BLOCKCHAIN.md (architecture overview)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
