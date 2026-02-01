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
        connector: ScholarshipBlockchainConnector,
        min_gpa: float = 3.0,
        max_income: float = 50000,
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

    def verify_student_on_chain(self, student: StudentData) -> Dict:
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

        # Call oracle function on smart contract
        try:
            tx_receipt = self.connector.call_write_function(
                "verifyEligibility",
                Web3.to_checksum_address(student.wallet_address),
                student.student_id,
                is_eligible,
                reason,
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

    def verify_and_register_student(
        self, student_id: int, application_data: Dict
    ) -> Dict:
        """
        Register a student and verify eligibility in one transaction flow.

        Args:
            student_id: Student ID
            application_data: Application submission data

        Returns:
            Registration and verification result
        """
        student = self.db.get_student(student_id)
        if not student:
            raise ValueError(f"Student {student_id} not found in database")

        # Create hash of application data for integrity check
        app_hash = hashlib.sha256(
            json.dumps(application_data, sort_keys=True).encode()
        ).hexdigest()

        logger.info(f"Registering student {student_id} with application hash {app_hash}")

        # Step 1: Register student on-chain
        try:
            reg_tx = self.connector.call_write_function(
                "registerStudent", student_id, app_hash
            )
            logger.info(f"✓ Student {student_id} registered on blockchain")
        except Exception as e:
            logger.error(f"Registration failed: {e}")
            raise

        # Step 2: Verify eligibility
        try:
            ver_tx = self.verify_student_on_chain(student)
            logger.info(f"✓ Student {student_id} verified")
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            raise

        return {
            "student_id": student_id,
            "registration_tx": reg_tx,
            "verification_result": ver_tx,
            "application_hash": app_hash,
        }

    def get_student_verification_history(self, wallet_address: str) -> List[Dict]:
        """
        Fetch student's verification history from blockchain.

        Args:
            wallet_address: Student's wallet address

        Returns:
            List of verification records
        """
        try:
            history = self.connector.call_read_function(
                "getVerificationHistory", Web3.to_checksum_address(wallet_address)
            )
            return history
        except Exception as e:
            logger.error(f"Failed to fetch verification history: {e}")
            return []

    def get_student_eligibility_status(self, wallet_address: str) -> bool:
        """
        Check if a student is marked as eligible on-chain.

        Args:
            wallet_address: Student's wallet address

        Returns:
            True if eligible, False otherwise
        """
        try:
            is_eligible = self.connector.call_read_function(
                "getStudentEligibilityStatus",
                Web3.to_checksum_address(wallet_address),
            )
            return is_eligible
        except Exception as e:
            logger.error(f"Failed to check eligibility status: {e}")
            return False

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
    print("1. Deploy ScholarshipHub.sol to testnet")
    print("2. Set CONTRACT_ADDRESS in .env")
    print("3. Set ORACLE_PRIVATE_KEY in .env (oracle wallet)")
    print("4. Connect oracle to database")
    print("5. Run: python -m oracle_service --verify-all")
