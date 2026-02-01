"""
EduChain Scholar Hub - Database Models
SQLAlchemy ORM models for student, application, and scholarship tracking.
Replace with actual database configuration in production.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class AcademicStanding(enum.Enum):
    """Student academic standing status"""
    GOOD = "good"
    PROBATION = "probation"
    DISMISSED = "dismissed"


class VerificationStatus(enum.Enum):
    """Verification status of application documents"""
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class Student(Base):
    """Student profile stored off-chain for privacy"""
    __tablename__ = "students"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, unique=True, nullable=False, index=True)
    wallet_address = Column(String(42), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False, index=True)
    phone = Column(String(20))
    
    # Academic information
    gpa = Column(Float, nullable=False)
    academic_standing = Column(Enum(AcademicStanding), default=AcademicStanding.GOOD)
    major = Column(String(100))
    year_of_study = Column(Integer)  # 1-4 for undergrad, 1-6 for grad
    
    # Financial information
    annual_income = Column(Float)  # Household income
    income_verified = Column(Boolean, default=False)
    
    # Blockchain information
    on_chain_registration = Column(Boolean, default=False)
    blockchain_tx_hash = Column(String(66))  # 0x + 64 hex chars
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    applications = relationship("Application", back_populates="student")
    verifications = relationship("Verification", back_populates="student")
    
    def __repr__(self):
        return f"<Student {self.student_id}: {self.first_name} {self.last_name}>"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class Application(Base):
    """Student scholarship application"""
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=False, index=True)
    scholarship_id = Column(Integer, nullable=False, index=True)
    
    # Application content
    essay = Column(Text)  # Scholarship essay
    motivation = Column(Text)  # Why student needs scholarship
    documents_hash = Column(String(66), nullable=False)  # Hash of uploaded documents (IPFS)
    
    # Application status
    verification_status = Column(Enum(VerificationStatus), default=VerificationStatus.PENDING)
    
    # Blockchain reference
    application_hash = Column(String(66))  # Hash recorded on blockchain
    
    # Timestamps
    submitted_at = Column(DateTime, default=datetime.utcnow)
    verified_at = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = relationship("Student", back_populates="applications")
    
    def __repr__(self):
        return f"<Application {self.id}: Student {self.student_id} for Scholarship {self.scholarship_id}>"


class Verification(Base):
    """Eligibility verification record"""
    __tablename__ = "verifications"
    
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=False, index=True)
    
    # Verification details
    is_eligible = Column(Boolean, nullable=False)
    reason = Column(String(500))  # Why eligible/ineligible
    
    # Verification metadata
    gpa_check = Column(Boolean)
    income_check = Column(Boolean)
    documents_check = Column(Boolean)
    academic_standing_check = Column(Boolean)
    
    # Blockchain reference
    blockchain_tx_hash = Column(String(66))  # Transaction hash on blockchain
    oracle_address = Column(String(42))  # Oracle wallet that performed verification
    
    # Timestamps
    verified_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    student = relationship("Student", back_populates="verifications")
    
    def __repr__(self):
        status = "Eligible" if self.is_eligible else "Ineligible"
        return f"<Verification {self.id}: Student {self.student_id} - {status}>"


class ScholarshipProgram(Base):
    """Scholarship program information"""
    __tablename__ = "scholarship_programs"
    
    id = Column(Integer, primary_key=True)
    blockchain_scholarship_id = Column(Integer, unique=True, nullable=False, index=True)
    
    title = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Funding
    total_amount_eth = Column(Float, nullable=False)  # Total ETH allocated
    amount_per_student_eth = Column(Float, nullable=False)
    max_recipients = Column(Integer, nullable=False)
    
    # Eligibility criteria
    min_gpa = Column(Float, default=3.0)
    max_annual_income = Column(Float)
    required_major = Column(String(100))
    required_year = Column(Integer)  # Year of study requirement
    
    # Status
    is_active = Column(Boolean, default=True)
    applications_open = Column(Boolean, default=True)
    
    # Blockchain reference
    contract_address = Column(String(42))
    creator_address = Column(String(42))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    deadline = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<ScholarshipProgram {self.id}: {self.title}>"


class ClaimRecord(Base):
    """Track scholarship claims"""
    __tablename__ = "claim_records"
    
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=False, index=True)
    scholarship_id = Column(Integer, ForeignKey("scholarship_programs.blockchain_scholarship_id"), 
                           nullable=False, index=True)
    
    # Claim details
    amount_claimed_eth = Column(Float, nullable=False)
    claim_timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Blockchain reference
    blockchain_tx_hash = Column(String(66))  # Transaction hash on blockchain
    
    def __repr__(self):
        return f"<ClaimRecord {self.id}: Student {self.student_id} claimed {self.amount_claimed_eth} ETH>"


# ==================== DATABASE INITIALIZATION ====================

def init_db(db_url: str = "sqlite:///scholarship_hub.db"):
    """
    Initialize database with all tables.
    
    Args:
        db_url: SQLAlchemy database URL
                Default: SQLite file
                Production: postgresql://user:password@host/dbname
    """
    from sqlalchemy import create_engine
    
    engine = create_engine(db_url, echo=False)
    Base.metadata.create_all(engine)
    print(f"✓ Database initialized at {db_url}")
    return engine


def create_session(db_url: str = "sqlite:///scholarship_hub.db"):
    """
    Create a database session.
    
    Args:
        db_url: SQLAlchemy database URL
    
    Returns:
        SQLAlchemy session
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    engine = create_engine(db_url, echo=False)
    Session = sessionmaker(bind=engine)
    return Session()


# ==================== EXAMPLE USAGE ====================

if __name__ == "__main__":
    print("\n=== EduChain Scholar Hub - Database Schema ===\n")
    
    # Initialize database
    engine = init_db()
    
    # Create a session
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print("\nDatabase Tables:")
    print("  - students: Student profiles and personal information")
    print("  - applications: Scholarship applications with essays and documents")
    print("  - verifications: Eligibility verification records")
    print("  - scholarship_programs: Scholarship program details")
    print("  - claim_records: Track scholarship claims")
    
    print("\nKey Features:")
    print("  ✓ Sybil Resistance: Wallet mapped to unique Student ID")
    print("  ✓ Privacy: Sensitive data stored off-chain")
    print("  ✓ Integrity: Application hash recorded on blockchain")
    print("  ✓ Auditability: All verifications and claims tracked")
    
    print("\nSchema Design Benefits:")
    print("  - PII (personal data) stays off-chain")
    print("  - Only boolean eligibility status goes on-chain")
    print("  - Application hashes ensure data wasn't swapped")
    print("  - Verification history is immutable on blockchain")
    
    session.close()
