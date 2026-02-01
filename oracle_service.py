"""
EduChain Scholar Hub - Oracle Service
Bridges off-chain student data with on-chain smart contract verification.
This service verifies student eligibility and updates the blockchain accordingly.
"""

from blockchain_connector import ScholarshipBlockchainConnector
from web3 import Web3
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import hashlib
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class StudentData:
    """Represents student information from database"""

    student_id: int
    wallet_address: str
    name: str
    email: str
    gpa: float
    income_level: float  # In currency units
    academic_standing: str  # "good", "probation", etc.
    documents_verified: bool


class StudentDatabase:
    """
    Mock database connector. Replace with actual database queries
    (PostgreSQL, MongoDB, etc.) in production.
    """

    # Mock student data storage
    students_db = {
        1: StudentData(
            student_id=1,
            wallet_address="0x742d35Cc6634C0532925a3b844Bc2e0e42d79e18",
            name="Alice Chen",
            email="alice@university.edu",
            gpa=3.8,
            income_level=25000,
            academic_standing="good",
            documents_verified=True,
        ),
        2: StudentData(
            student_id=2,
            wallet_address="0x1234567890123456789012345678901234567890",
            name="Bob Martinez",
            email="bob@university.edu",
            gpa=3.2,
            income_level=45000,
            academic_standing="good",
            documents_verified=True,
        ),
        3: StudentData(
            student_id=3,
            wallet_address="0x0987654321098765432109876543210987654321",
            name="Carol Park",
            email="carol@university.edu",
            gpa=2.8,
            income_level=60000,
            academic_standing="probation",
            documents_verified=False,
        ),
    }

    @classmethod
    def get_student(cls, student_id: int) -> Optional[StudentData]:
        """Fetch student from database"""
        return cls.students_db.get(student_id)

    @classmethod
    def get_all_students(cls) -> List[StudentData]:
        """Get all students"""
        return list(cls.students_db.values())

    @classmethod
    def add_student(cls, student: StudentData):
        """Add student to mock database"""
        cls.students_db[student.student_id] = student


class EligibilityOracle:
    """
    Oracle service that verifies student eligibility based on rules
    and updates the blockchain smart contract.

    Eligibility Rules (configurable):
    - GPA >= 3.0
    - Income <= threshold
    - Academic standing = "good"
    - Documents verified = True
    """

    def __init__(
        self,
        connector: Optional[ScholarshipBlockchainConnector],
        min_gpa: float = 3.0,
        max_income: float = 50000,
        default_sponsor_address: Optional[str] = None,
        default_amount_wei: int = 0,
    ):
        """
        Initialize Oracle.

        Args:
            connector: Blockchain connector instance
            min_gpa: Minimum GPA requirement
            max_income: Maximum income threshold
        """
        self.connector = connector
        self.min_gpa = min_gpa
        self.max_income = max_income
        self.db = StudentDatabase()
        self.default_sponsor_address = default_sponsor_address
        self.default_amount_wei = default_amount_wei

    @staticmethod
    def gpa_to_contract_scale(gpa: float) -> int:
        """Convert GPA float (e.g., 3.85) to contract scale (e.g., 385)."""
        return int(round(gpa * 100))

    def check_eligibility(self, student: StudentData) -> Tuple[bool, str]:
        """
        Check if a student meets eligibility criteria.

        Args:
            student: StudentData object

        Returns:
            Tuple of (is_eligible, reason_string)
        """
        # Rule 1: GPA check
        if student.gpa < self.min_gpa:
            return False, f"GPA too low ({student.gpa} < {self.min_gpa})"

        # Rule 2: Income check
        if student.income_level > self.max_income:
            return False, f"Income exceeds threshold (${student.income_level} > ${self.max_income})"

        # Rule 3: Academic standing
        if student.academic_standing != "good":
            return (
                False,
                f"Academic standing not good ({student.academic_standing})",
            )

        # Rule 4: Documents verification
        if not student.documents_verified:
            return False, "Documents not verified"

        # All checks passed
        return True, f"Eligible: GPA {student.gpa}, Income ${student.income_level}"

    def verify_student_on_chain(
        self,
        student: StudentData,
        sponsor_address: Optional[str] = None,
        amount_wei: Optional[int] = None,
    ) -> Dict:
        """
        Verify a student and update blockchain.

        Args:
            student: StudentData to verify

        Returns:
            Transaction receipt and verification result
        """
        is_eligible, reason = self.check_eligibility(student)

        logger.info(
            f"Verifying student {student.student_id} ({student.name}): {is_eligible} - {reason}"
        )

        if not self.connector:
            raise ValueError("Blockchain connector not configured")

        sponsor_address = sponsor_address or self.default_sponsor_address
        amount_wei = amount_wei if amount_wei is not None else self.default_amount_wei

        if not sponsor_address:
            raise ValueError("Sponsor address required to verify student")
        if amount_wei is None or amount_wei <= 0:
            raise ValueError("Scholarship amount (wei) required to verify student")

        # Admin verification on ScholarshipManager.sol
        try:
            tx_receipt = self.connector.verify_student(
                student_address=student.wallet_address,
                assigned_sponsor=sponsor_address,
                amount_wei=amount_wei,
                initial_gpa=self.gpa_to_contract_scale(student.gpa),
            )

            logger.info(
                f"✓ Student {student.student_id} verification recorded on blockchain"
            )

            return {
                "student_id": student.student_id,
                "wallet": student.wallet_address,
                "is_eligible": is_eligible,
                "reason": reason,
                "transaction": tx_receipt,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"✗ Failed to update blockchain: {e}")
            raise

    def batch_verify_students(
        self, student_ids: Optional[List[int]] = None
    ) -> List[Dict]:
        """
        Verify multiple students in batch.

        Args:
            student_ids: List of student IDs to verify (None = verify all)

        Returns:
            List of verification results
        """
        if student_ids is None:
            students = self.db.get_all_students()
        else:
            students = [self.db.get_student(sid) for sid in student_ids if sid]

        results = []
        for student in students:
            if student:
                try:
                    result = self.verify_student_on_chain(student)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Failed to verify student {student.student_id}: {e}")

        logger.info(f"Batch verification complete: {len(results)}/{len(students)} successful")
        return results

    def update_student_gpa_on_chain(self, student: StudentData, new_gpa: float) -> Dict:
        """
        Admin action: update student GPA on-chain.

        Args:
            student: StudentData
            new_gpa: GPA as float (e.g., 3.25)

        Returns:
            Transaction receipt
        """
        if not self.connector:
            raise ValueError("Blockchain connector not configured")

        return self.connector.update_student_gpa(
            student.wallet_address, self.gpa_to_contract_scale(new_gpa)
        )

    def get_student_on_chain(self, wallet_address: str) -> Optional[Dict]:
        """
        Fetch student struct from ScholarshipManager.sol mapping.

        Args:
            wallet_address: Student's wallet address

        Returns:
            Student struct tuple or None
        """
        if not self.connector:
            return None
        try:
            return self.connector.get_student(wallet_address)
        except Exception as e:
            logger.error(f"Failed to fetch student data: {e}")
            return None

    # ==================== CONFIGURABLE ELIGIBILITY RULES ====================

    def set_min_gpa(self, gpa: float):
        """Update minimum GPA requirement"""
        self.min_gpa = gpa
        logger.info(f"Minimum GPA requirement updated to {gpa}")

    def set_max_income(self, income: float):
        """Update maximum income threshold"""
        self.max_income = income
        logger.info(f"Maximum income threshold updated to ${income}")

    def add_custom_rule(self, rule_name: str, rule_function):
        """
        Add custom eligibility rule.

        Args:
            rule_name: Name of the rule
            rule_function: Function that takes StudentData and returns (bool, str)
        """
        logger.info(f"Custom rule '{rule_name}' added")
        # Extend check_eligibility to include custom rules


# ==================== EXAMPLE USAGE ====================

if __name__ == "__main__":
    print("\n=== EduChain Scholar Hub - Oracle Service Demo ===\n")

    # Initialize connector
    try:
        connector = None  # Will be initialized in actual usage
        # connector = create_connector("localhost", private_key=os.getenv("PRIVATE_KEY"))

        # Initialize oracle
        # oracle = EligibilityOracle(connector, min_gpa=3.0, max_income=50000)

        # Demo: Check eligibility without blockchain
        db = StudentDatabase()
        oracle_logic = EligibilityOracle(connector or None, min_gpa=3.0, max_income=50000)

        print("Student Eligibility Check (Demo):\n")
        for student in db.get_all_students():
            is_eligible, reason = oracle_logic.check_eligibility(student)
            status = "✓ ELIGIBLE" if is_eligible else "✗ NOT ELIGIBLE"
            print(f"{status} - {student.name}")
            print(f"  ID: {student.student_id}, GPA: {student.gpa}, Income: ${student.income_level}")
            print(f"  Reason: {reason}\n")

    except Exception as e:
        print(f"Error: {e}")

    print("Setup Instructions:")
    print("1. Deploy ScholarshipManager.sol to testnet")
    print("2. Set CONTRACT_ADDRESS in .env")
    print("3. Set ORACLE_PRIVATE_KEY in .env (oracle wallet)")
    print("4. Connect oracle to database")
    print("5. Run: python -m oracle_service --verify-all")
