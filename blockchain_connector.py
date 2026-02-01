"""
EduChain Scholar Hub - Blockchain Connector
Communicates with Solidity smart contracts for scholarship management
Supports Ethereum-compatible blockchains
"""

from web3 import Web3
from eth_account import Account
from typing import Dict, List, Any, Optional
import json
from decimal import Decimal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScholarshipBlockchainConnector:
    """
    Manages interaction with Solidity smart contracts for scholarship management.
    Supports contract deployment, fund management, and scholarship distribution.
    """

    def __init__(
        self,
        provider_url: str,
        contract_address: Optional[str] = None,
        contract_abi: Optional[List[Dict]] = None,
        private_key: Optional[str] = None,
    ):
        """
        Initialize blockchain connector.

        Args:
            provider_url: RPC provider URL (e.g., Infura, Alchemy, local node)
            contract_address: Deployed contract address
            contract_abi: Contract ABI JSON
            private_key: Private key for transaction signing (without '0x' prefix)
        """
        self.w3 = Web3(Web3.HTTPProvider(provider_url))

        if not self.w3.is_connected():
            raise ConnectionError(f"Failed to connect to {provider_url}")

        self.contract_address = contract_address
        self.contract_abi = contract_abi
        self.account = None

        if private_key:
            self.account = Account.from_key(private_key)
            self.w3.eth.default_account = self.account.address

        logger.info(
            f"Connected to blockchain at {provider_url}. Chain ID: {self.w3.eth.chain_id}"
        )

    def load_contract(self, contract_address: str, contract_abi: List[Dict]) -> Any:
        """
        Load a smart contract instance.

        Args:
            contract_address: Contract address
            contract_abi: Contract ABI

        Returns:
            Contract instance
        """
        self.contract_address = Web3.to_checksum_address(contract_address)
        self.contract_abi = contract_abi
        return self.w3.eth.contract(
            address=self.contract_address, abi=self.contract_abi
        )

    def deploy_contract(
        self,
        contract_bytecode: str,
        contract_abi: List[Dict],
        constructor_args: Optional[List[Any]] = None,
        gas_limit: int = 3000000,
    ) -> Dict[str, Any]:
        """
        Deploy a new scholarship contract.

        Args:
            contract_bytecode: Compiled contract bytecode
            contract_abi: Contract ABI
            constructor_args: Constructor arguments
            gas_limit: Gas limit for deployment

        Returns:
            Transaction receipt and contract address
        """
        if not self.account:
            raise ValueError("Private key required for contract deployment")

        contract = self.w3.eth.contract(abi=contract_abi, bytecode=contract_bytecode)

        # Build transaction
        constructor_args = constructor_args or []
        tx = contract.constructor(*constructor_args).build_transaction(
            {
                "from": self.account.address,
                "nonce": self.w3.eth.get_transaction_count(self.account.address),
                "gas": gas_limit,
                "gasPrice": self.w3.eth.gas_price,
            }
        )

        # Sign and send transaction
        signed_tx = self.w3.eth.account.sign_transaction(tx, self.account.key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

        # Wait for receipt
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        logger.info(
            f"Contract deployed at {receipt.contractAddress} (Tx: {tx_hash.hex()})"
        )

        return {
            "contract_address": receipt.contractAddress,
            "transaction_hash": tx_hash.hex(),
            "block_number": receipt.blockNumber,
            "gas_used": receipt.gasUsed,
        }

    def call_read_function(
        self, function_name: str, *args, **kwargs
    ) -> Any:
        """
        Call a read-only contract function (no state change).

        Args:
            function_name: Function name
            *args: Function arguments

        Returns:
            Function result
        """
        if not self.contract_address or not self.contract_abi:
            raise ValueError("Contract not loaded. Use load_contract() first.")

        contract = self.w3.eth.contract(
            address=self.contract_address, abi=self.contract_abi
        )

        function = getattr(contract.functions, function_name)
        return function(*args).call()

    def call_write_function(
        self,
        function_name: str,
        *args,
        value: int = 0,
        gas_limit: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Call a contract function that modifies state.

        Args:
            function_name: Function name
            *args: Function arguments
            value: ETH value to send (in wei)
            gas_limit: Gas limit for transaction

        Returns:
            Transaction receipt
        """
        if not self.contract_address or not self.contract_abi or not self.account:
            raise ValueError(
                "Contract not loaded or private key not set. Use load_contract() and set private_key first."
            )

        contract = self.w3.eth.contract(
            address=self.contract_address, abi=self.contract_abi
        )

        function = getattr(contract.functions, function_name)

        # Estimate gas if not provided
        if gas_limit is None:
            gas_limit = function(*args).estimate_gas(
                {"from": self.account.address, "value": value}
            )

        # Build transaction
        tx = function(*args).build_transaction(
            {
                "from": self.account.address,
                "value": value,
                "gas": gas_limit,
                "gasPrice": self.w3.eth.gas_price,
                "nonce": self.w3.eth.get_transaction_count(self.account.address),
            }
        )

        # Sign and send
        signed_tx = self.w3.eth.account.sign_transaction(tx, self.account.key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

        # Wait for receipt
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        logger.info(
            f"Transaction {tx_hash.hex()} completed. Gas used: {receipt.gasUsed}"
        )

        return {
            "transaction_hash": tx_hash.hex(),
            "block_number": receipt.blockNumber,
            "gas_used": receipt.gasUsed,
            "status": receipt.status,  # 1 = success, 0 = failed
        }

    def get_scholarship_balance(self, scholarship_id: int) -> Dict[str, Any]:
        """
        Get balance information for a scholarship.

        Args:
            scholarship_id: Scholarship ID

        Returns:
            Balance information
        """
        balance = self.call_read_function("getScholarshipBalance", scholarship_id)
        return {
            "scholarship_id": scholarship_id,
            "balance_wei": balance,
            "balance_eth": Web3.from_wei(balance, "ether"),
        }

    def distribute_scholarship(
        self, student_address: str, amount_wei: int, scholarship_id: int
    ) -> Dict[str, Any]:
        """
        Distribute funds to a student.

        Args:
            student_address: Student's wallet address
            amount_wei: Amount in wei
            scholarship_id: Scholarship ID

        Returns:
            Transaction receipt
        """
        student_address = Web3.to_checksum_address(student_address)
        return self.call_write_function(
            "distributeScholarship", student_address, amount_wei, scholarship_id
        )

    def add_scholarship(
        self,
        title: str,
        amount_wei: int,
        beneficiary_count: int,
        description: str = "",
    ) -> Dict[str, Any]:
        """
        Create a new scholarship.

        Args:
            title: Scholarship title
            amount_wei: Total amount in wei
            beneficiary_count: Expected number of beneficiaries
            description: Scholarship description

        Returns:
            Transaction receipt
        """
        return self.call_write_function(
            "addScholarship", title, amount_wei, beneficiary_count, description
        )

    def withdraw_funds(self, amount_wei: int) -> Dict[str, Any]:
        """
        Withdraw unclaimed funds from contract (owner only).

        Args:
            amount_wei: Amount to withdraw in wei

        Returns:
            Transaction receipt
        """
        return self.call_write_function("withdrawUnclaimedFunds", amount_wei)

    # ==================== ORACLE FUNCTIONS ====================

    def register_student(self, student_id: int, application_hash: str) -> Dict[str, Any]:
        """
        Register a student with application hash (Sybil resistance).

        Args:
            student_id: Unique university student ID
            application_hash: IPFS hash or keccak256 of application data

        Returns:
            Transaction receipt
        """
        return self.call_write_function("registerStudent", student_id, application_hash)

    def verify_eligibility(
        self,
        student_address: str,
        student_id: int,
        is_eligible: bool,
        reason: str,
    ) -> Dict[str, Any]:
        """
        Oracle function: Verify student eligibility on-chain.

        Args:
            student_address: Student's wallet address
            student_id: Student's university ID
            is_eligible: Eligibility status
            reason: Eligibility reason (e.g., "GPA: 3.8")

        Returns:
            Transaction receipt
        """
        student_address = Web3.to_checksum_address(student_address)
        return self.call_write_function(
            "verifyEligibility", student_address, student_id, is_eligible, reason
        )

    def create_scholarship(
        self,
        title: str,
        beneficiary_count: int,
        description: str = "",
        amount_eth: Decimal = Decimal("1"),
    ) -> Dict[str, Any]:
        """
        Create a new scholarship with funding.

        Args:
            title: Scholarship title
            beneficiary_count: Number of eligible beneficiaries
            description: Scholarship description
            amount_eth: Total amount in ETH (default: 1 ETH)

        Returns:
            Transaction receipt
        """
        amount_wei = Web3.to_wei(amount_eth, "ether")
        return self.call_write_function(
            "createScholarship", title, beneficiary_count, description, value=amount_wei
        )

    def claim_scholarship(self, scholarship_id: int) -> Dict[str, Any]:
        """
        Claim scholarship funds (student only, must be eligible).

        Args:
            scholarship_id: ID of scholarship to claim

        Returns:
            Transaction receipt
        """
        return self.call_write_function("claimScholarship", scholarship_id)

    def get_student_info(self, student_address: str) -> Dict[str, Any]:
        """
        Get student information from contract.

        Args:
            student_address: Student's wallet address

        Returns:
            Student data
        """
        student_address = Web3.to_checksum_address(student_address)
        return self.call_read_function("getStudent", student_address)

    def get_student_eligibility(self, student_address: str) -> bool:
        """
        Check if student is marked as eligible.

        Args:
            student_address: Student's wallet address

        Returns:
            True if eligible, False otherwise
        """
        student_address = Web3.to_checksum_address(student_address)
        return self.call_read_function("getStudentEligibilityStatus", student_address)

    def get_verification_history(self, student_address: str) -> List[Dict]:
        """
        Get student's verification history.

        Args:
            student_address: Student's wallet address

        Returns:
            List of verification records
        """
        student_address = Web3.to_checksum_address(student_address)
        return self.call_read_function("getVerificationHistory", student_address)

    def set_oracle_address(self, oracle_address: str) -> Dict[str, Any]:
        """
        Update oracle address (owner only).

        Args:
            oracle_address: New oracle wallet address

        Returns:
            Transaction receipt
        """
        oracle_address = Web3.to_checksum_address(oracle_address)
        return self.call_write_function("setOracleAddress", oracle_address)

    def get_account_balance(self, address: Optional[str] = None) -> Dict[str, Any]:
        """
        Get account balance.

        Args:
            address: Account address (uses connected account if not provided)

        Returns:
            Balance information
        """
        if address is None:
            if not self.account:
                raise ValueError("Address not provided and no account connected")
            address = self.account.address
        else:
            address = Web3.to_checksum_address(address)

        balance_wei = self.w3.eth.get_balance(address)
        return {
            "address": address,
            "balance_wei": balance_wei,
            "balance_eth": Web3.from_wei(balance_wei, "ether"),
        }

    def get_transaction_status(self, tx_hash: str) -> Dict[str, Any]:
        """
        Get transaction status.

        Args:
            tx_hash: Transaction hash

        Returns:
            Transaction details
        """
        receipt = self.w3.eth.get_transaction_receipt(tx_hash)
        return {
            "transaction_hash": tx_hash,
            "block_number": receipt.blockNumber,
            "gas_used": receipt.gasUsed,
            "status": "Success" if receipt.status == 1 else "Failed",
            "from": receipt["from"],
            "to": receipt.to,
        }


# Example usage and helper functions
def load_contract_from_file(filepath: str) -> Dict[str, Any]:
    """Load contract ABI from JSON file."""
    with open(filepath, "r") as f:
        return json.load(f)


def create_connector(
    network: str = "localhost",
    private_key: Optional[str] = None,
) -> ScholarshipBlockchainConnector:
    """
    Create a connector for common networks.

    Args:
        network: 'localhost', 'sepolia', 'mainnet', or custom RPC URL
        private_key: Optional private key for transactions

    Returns:
        Configured ScholarshipBlockchainConnector instance
    """
    network_urls = {
        "localhost": "http://localhost:8545",
        "sepolia": "https://sepolia.infura.io/v3/YOUR_INFURA_KEY",
        "mainnet": "https://mainnet.infura.io/v3/YOUR_INFURA_KEY",
        "polygon": "https://polygon-rpc.com",
        "mumbai": "https://rpc-mumbai.maticvigil.com",
    }

    provider_url = network_urls.get(network, network)
    return ScholarshipBlockchainConnector(provider_url, private_key=private_key)


if __name__ == "__main__":
    # Example: Connect to local blockchain (Ganache, Hardhat, etc.)
    try:
        connector = create_connector("localhost")
        print("✓ Connected to blockchain!")

        # Example: Check account balance
        balance = connector.get_account_balance()
        print(f"Account balance: {balance['balance_eth']} ETH")

    except Exception as e:
        print(f"Error: {e}")
