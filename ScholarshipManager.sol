// SPDX-License-Identifier: MIT
pragma solidity ^0.8.30;

contract ScholarshipSystem {
    
    // 1. Define the Student Object
    struct Student {
        uint256 id;
        uint256 gpa;
        bool isEligible;        // Determined by ADMIN
        address assignedSponsor;
        uint256 scholarshipAmount;
        bool hasReceivedFunds;
    }

    struct Sponsor {
        uint256 id;
        bool isVerified;
    }

    address public admin; 
    uint256 private nextStudentId = 1;
    uint256 private nextSponsorId = 1001;

    mapping(address => Student) public students;
    mapping(address => Sponsor) public sponsors;
    mapping(address => uint256) public studentBalances;

    // Event for transparency (This is what the public sees)
    event ScholarshipGranted(address indexed student, address indexed sponsor, uint256 amount);
    event EligibilityChanged(address indexed student, bool status, uint256 newGpa);
    event FundsWithdrawn(address indexed sponsor, uint256 amount);
    event SponsorVerified(address indexed sponsor, uint256 sponsorId);

    modifier onlyAdmin() {
        require(msg.sender == admin, "Only the ADMIN can perform this action.");
        _;
    }

    constructor() {
        admin = msg.sender;
    }

// --- ADMIN ACTIONS ---

    function verifySponsor(address _sponsorAddr) external onlyAdmin {
        require(!sponsors[_sponsorAddr].isVerified, "Already verified");
        sponsors[_sponsorAddr] = Sponsor(nextSponsorId++, true);
        emit SponsorVerified(_sponsorAddr, sponsors[_sponsorAddr].id);
    }

    function verifyStudent(address _studentAddr, address _assignedSponsor, uint256 _amount, uint256 _initialGpa) external onlyAdmin {
        require(sponsors[_assignedSponsor].isVerified, "Sponsor not verified");
        
        students[_studentAddr] = Student({
            id: nextStudentId++,
            gpa: _initialGpa,
            isEligible: (_initialGpa >= 300),
            assignedSponsor: _assignedSponsor,
            scholarshipAmount: _amount,
            hasReceivedFunds: false
        });
    }

    function updateStudentGPA(address _studentAddr, uint256 _newGpa) external onlyAdmin {
        Student storage s = students[_studentAddr];
        require(s.id != 0, "Student does not exist");
        
        s.gpa = _newGpa;
        s.isEligible = (_newGpa >= 300); 
        
        emit EligibilityChanged(_studentAddr, s.isEligible, _newGpa);
    }

    // --- SPONSOR ACTIONS ---

    function fundStudent(address _studentAddr) external payable {
        require(sponsors[msg.sender].isVerified, "Not a verified sponsor");
        require(students[_studentAddr].assignedSponsor == msg.sender, "Not your assigned student");
        require(msg.value == students[_studentAddr].scholarshipAmount, "Incorrect amount sent");

        studentBalances[_studentAddr] += msg.value;
    }

    function withdrawSponsorFunds(address _studentAddr) external {
        uint256 amount = studentBalances[_studentAddr];
        require(amount > 0, "No funds to withdraw");
        require(students[_studentAddr].assignedSponsor == msg.sender, "Not your student");
        require(!students[_studentAddr].hasReceivedFunds, "Student already claimed");

        studentBalances[_studentAddr] = 0;
        
        (bool success, ) = payable(msg.sender).call{value: amount}("");
        require(success, "Transfer failed");

        emit FundsWithdrawn(msg.sender, amount);
    }

    // --- STUDENT ACTIONS ---

    function claimScholarship() external {
        Student storage s = students[msg.sender];
        uint256 availableAmount = studentBalances[msg.sender];
        
        require(s.isEligible, "GPA below 3.0 or ineligible");
        require(!s.hasReceivedFunds, "Already claimed");
        require(availableAmount >= s.scholarshipAmount, "Sponsor has not funded yet");

        s.hasReceivedFunds = true;
        studentBalances[msg.sender] = 0;
        
        (bool success, ) = payable(msg.sender).call{value: availableAmount}("");
        require(success, "Transfer failed");

        emit ScholarshipGranted(msg.sender, s.assignedSponsor, availableAmount);
    }
}