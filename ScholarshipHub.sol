// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title ScholarshipHub
 * @dev Decentralized scholarship management system with oracle-based eligibility verification
 * Architecture:
 *   - Off-chain: Python backend manages student data, applications, GPA verification
 *   - On-chain: Solidity enforces rules, stores verification status, and manages funds
 *   - Oracle: Python script bridges the gap by verifying eligibility
 */

contract ScholarshipHub {
    // ==================== DATA STRUCTURES ====================

    struct Student {
        uint256 studentId;           // Unique university/system ID (for Sybil resistance)
        address walletAddress;        // Ethereum wallet address
        string applicationHash;       // IPFS or hash of application data (integrity check)
        bool isEligible;              // Oracle-verified eligibility status
        bool hasClaimedScholarship;   // Prevent double-claiming
        uint256 verificationTimestamp;
    }

    struct Scholarship {
        uint256 id;
        string title;
        string description;
        uint256 totalAmount;
        uint256 remainingAmount;
        uint256 claimAmount;          // Amount per eligible student
        uint256 beneficiaryCount;
        uint256 claimsProcessed;
        address creator;
        uint256 createdAt;
        bool active;
    }

    struct VerificationRecord {
        address student;
        uint256 studentId;
        bool isEligible;
        string reason;                // e.g., "GPA: 3.8", "Income: Below threshold"
        uint256 timestamp;
        address verifier;             // The oracle that verified
    }

    // ==================== STATE VARIABLES ====================

    address public owner;
    address public oracleAddress;     // Trusted oracle for eligibility verification
    
    uint256 public scholarshipCounter = 0;
    uint256 public totalFunds = 0;
    
    // Mappings for data integrity
    mapping(address => Student) public students;                    // Wallet -> Student info
    mapping(uint256 => address) public studentIdToWallet;          // Student ID -> Wallet (Sybil resistance)
    mapping(uint256 => Scholarship) public scholarships;
    mapping(address => VerificationRecord[]) public verificationHistory;
    mapping(address => uint256) public claimedAmounts;              // Track total claimed per student

    // ==================== EVENTS ====================

    event StudentRegistered(
        uint256 indexed studentId,
        address indexed walletAddress,
        string applicationHash
    );
    event EligibilityVerified(
        address indexed student,
        uint256 indexed studentId,
        bool isEligible,
        string reason,
        uint256 timestamp
    );
    event ScholarshipCreated(
        uint256 indexed scholarshipId,
        string title,
        uint256 totalAmount,
        uint256 claimAmount,
        address indexed creator
    );
    event ScholarshipClaimed(
        address indexed student,
        uint256 indexed scholarshipId,
        uint256 amount,
        uint256 timestamp
    );
    event FundsDeposited(address indexed donor, uint256 amount);
    event FundsWithdrawn(address indexed recipient, uint256 amount);
    event OracleAddressUpdated(address indexed newOracle);
    event AdminAdded(address indexed admin);
    event AdminRemoved(address indexed admin);

    // ==================== MODIFIERS ====================

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }

    modifier onlyOracle() {
        require(msg.sender == oracleAddress, "Only oracle can call this function");
        _;
    }

    modifier scholarshipExists(uint256 _id) {
        require(
            _id < scholarshipCounter && scholarships[_id].active,
            "Scholarship does not exist"
        );
        _;
    }

    modifier studentIsEligible(address _student) {
        require(students[_student].isEligible, "Student is not verified as eligible");
        _;
    }

    // ==================== CONSTRUCTOR ====================

    constructor() {
        owner = msg.sender;
        oracleAddress = msg.sender;  // Owner is oracle by default
    }

    // ==================== ORACLE MANAGEMENT ====================

    function setOracleAddress(address _newOracle) public onlyOwner {
        require(_newOracle != address(0), "Invalid oracle address");
        oracleAddress = _newOracle;
        emit OracleAddressUpdated(_newOracle);
    }

    // ==================== STUDENT REGISTRATION ====================

    /**
     * @dev Register a student with their application hash (integrity check)
     * @param _studentId Unique university ID (for Sybil resistance)
     * @param _applicationHash IPFS hash or keccak256 of application data
     */
    function registerStudent(uint256 _studentId, string calldata _applicationHash)
        public
    {
        require(_studentId > 0, "Invalid student ID");
        require(studentIdToWallet[_studentId] == address(0), "Student ID already registered");
        require(students[msg.sender].studentId == 0, "Wallet already registered");
        require(bytes(_applicationHash).length > 0, "Application hash cannot be empty");

        students[msg.sender] = Student({
            studentId: _studentId,
            walletAddress: msg.sender,
            applicationHash: _applicationHash,
            isEligible: false,
            hasClaimedScholarship: false,
            verificationTimestamp: 0
        });

        studentIdToWallet[_studentId] = msg.sender;

        emit StudentRegistered(_studentId, msg.sender, _applicationHash);
    }

    // ==================== ORACLE VERIFICATION ====================

    /**
     * @dev Oracle function: Verify student eligibility based on off-chain data
     * Only callable by the trusted oracle (Python backend)
     * @param _studentAddress Student's wallet address
     * @param _studentId Student's university ID
     * @param _isEligible Eligibility status (true/false)
     * @param _reason Reason string (e.g., "GPA: 3.8", "Income verified")
     */
    function verifyEligibility(
        address _studentAddress,
        uint256 _studentId,
        bool _isEligible,
        string calldata _reason
    ) public onlyOracle {
        require(_studentAddress != address(0), "Invalid student address");
        require(students[_studentAddress].studentId == _studentId, "Student ID mismatch");

        // Update student eligibility
        students[_studentAddress].isEligible = _isEligible;
        students[_studentAddress].verificationTimestamp = block.timestamp;

        // Record verification in history
        verificationHistory[_studentAddress].push(
            VerificationRecord({
                student: _studentAddress,
                studentId: _studentId,
                isEligible: _isEligible,
                reason: _reason,
                timestamp: block.timestamp,
                verifier: msg.sender
            })
        );

        emit EligibilityVerified(
            _studentAddress,
            _studentId,
            _isEligible,
            _reason,
            block.timestamp
        );
    }

    // ==================== SCHOLARSHIP MANAGEMENT ====================

    /**
     * @dev Create a new scholarship (funded on creation)
     * @param _title Scholarship name
     * @param _beneficiaryCount Expected number of eligible students
     * @param _description Scholarship description
     */
    function createScholarship(
        string calldata _title,
        uint256 _beneficiaryCount,
        string calldata _description
    ) public payable onlyOwner {
        require(msg.value > 0, "Must deposit funds");
        require(_beneficiaryCount > 0, "Beneficiary count must be greater than 0");
        require(bytes(_title).length > 0, "Title cannot be empty");

        uint256 claimAmount = msg.value / _beneficiaryCount;
        require(claimAmount > 0, "Insufficient funds for beneficiary count");

        scholarships[scholarshipCounter] = Scholarship({
            id: scholarshipCounter,
            title: _title,
            description: _description,
            totalAmount: msg.value,
            remainingAmount: msg.value,
            claimAmount: claimAmount,
            beneficiaryCount: _beneficiaryCount,
            claimsProcessed: 0,
            creator: msg.sender,
            createdAt: block.timestamp,
            active: true
        });

        totalFunds += msg.value;

        emit ScholarshipCreated(
            scholarshipCounter,
            _title,
            msg.value,
            claimAmount,
            msg.sender
        );

        scholarshipCounter++;
    }

    // ==================== FUND CLAIMING ====================

    /**
     * @dev Eligible student claims their scholarship funds
     * Prevents double-claiming through hasClaimedScholarship flag
     * @param _scholarshipId ID of the scholarship to claim
     */
    function claimScholarship(uint256 _scholarshipId)
        public
        scholarshipExists(_scholarshipId)
        studentIsEligible(msg.sender)
    {
        Student storage student = students[msg.sender];
        Scholarship storage scholarship = scholarships[_scholarshipId];

        require(!student.hasClaimedScholarship, "Student has already claimed scholarship");
        require(
            scholarship.claimsProcessed < scholarship.beneficiaryCount,
            "All funds have been distributed"
        );
        require(
            scholarship.remainingAmount >= scholarship.claimAmount,
            "Insufficient scholarship funds"
        );

        // Prevent double-claiming
        student.hasClaimedScholarship = true;
        scholarship.claimsProcessed++;
        scholarship.remainingAmount -= scholarship.claimAmount;
        claimedAmounts[msg.sender] += scholarship.claimAmount;

        // Transfer funds
        (bool success, ) = payable(msg.sender).call{value: scholarship.claimAmount}("");
        require(success, "Transfer failed");

        totalFunds -= scholarship.claimAmount;

        emit ScholarshipClaimed(
            msg.sender,
            _scholarshipId,
            scholarship.claimAmount,
            block.timestamp
        );
    }

    // ==================== VIEW FUNCTIONS ====================

    function getStudent(address _studentAddress)
        public
        view
        returns (Student memory)
    {
        return students[_studentAddress];
    }

    function getScholarship(uint256 _id)
        public
        view
        scholarshipExists(_id)
        returns (Scholarship memory)
    {
        return scholarships[_id];
    }

    function getScholarshipBalance(uint256 _id)
        public
        view
        scholarshipExists(_id)
        returns (uint256)
    {
        return scholarships[_id].remainingAmount;
    }

    function getVerificationHistory(address _student)
        public
        view
        returns (VerificationRecord[] memory)
    {
        return verificationHistory[_student];
    }

    function getStudentEligibilityStatus(address _student) public view returns (bool) {
        return students[_student].isEligible;
    }

    function getTotalScholarships() public view returns (uint256) {
        return scholarshipCounter;
    }

    function getContractBalance() public view returns (uint256) {
        return address(this).balance;
    }

    // ==================== ADMIN WITHDRAWAL ====================

    function withdrawUnclaimedFunds(uint256 _amount) public onlyOwner {
        require(address(this).balance >= _amount, "Insufficient balance");
        (bool success, ) = payable(owner).call{value: _amount}("");
        require(success, "Withdrawal failed");
        emit FundsWithdrawn(owner, _amount);
    }

    // ==================== RECEIVE FUNCTION ====================

    receive() external payable {
        totalFunds += msg.value;
        emit FundsDeposited(msg.sender, msg.value);
    }
}
