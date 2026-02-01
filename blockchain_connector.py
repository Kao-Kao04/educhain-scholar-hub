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

    # ==================== SCHOLARSHIP MANAGER FUNCTIONS ====================

    def verify_sponsor(self, sponsor_address: str) -> Dict[str, Any]:
        """
        Admin action: verify a sponsor.

        Args:
            sponsor_address: Sponsor wallet address

        Returns:
            Transaction receipt
        """
        sponsor_address = Web3.to_checksum_address(sponsor_address)
        return self.call_write_function("verifySponsor", sponsor_address)

    def verify_student(
        self,
        student_address: str,
        assigned_sponsor: str,
        amount_wei: int,
        initial_gpa: int,
    ) -> Dict[str, Any]:
        """
        Admin action: verify a student and assign sponsor.

        Args:
            student_address: Student wallet address
            assigned_sponsor: Verified sponsor address
            amount_wei: Scholarship amount in wei
            initial_gpa: GPA in contract scale (e.g., 300 = 3.00)

        Returns:
            Transaction receipt
        """
        student_address = Web3.to_checksum_address(student_address)
        assigned_sponsor = Web3.to_checksum_address(assigned_sponsor)
        return self.call_write_function(
            "verifyStudent", student_address, assigned_sponsor, amount_wei, initial_gpa
        )

    def update_student_gpa(self, student_address: str, new_gpa: int) -> Dict[str, Any]:
        """
        Admin action: update student GPA.

        Args:
            student_address: Student wallet address
            new_gpa: GPA in contract scale (e.g., 300 = 3.00)

        Returns:
            Transaction receipt
        """
        student_address = Web3.to_checksum_address(student_address)
        return self.call_write_function("updateStudentGPA", student_address, new_gpa)

    def fund_student(self, student_address: str, amount_wei: int) -> Dict[str, Any]:
        """
        Sponsor action: fund assigned student (payable).

        Args:
            student_address: Student wallet address
            amount_wei: Amount to fund in wei

        Returns:
            Transaction receipt
        """
        student_address = Web3.to_checksum_address(student_address)
        return self.call_write_function(
            "fundStudent", student_address, value=amount_wei
        )

    def withdraw_sponsor_funds(self, student_address: str) -> Dict[str, Any]:
        """
        Sponsor action: withdraw funds for a student (if not claimed).

        Args:
            student_address: Student wallet address

        Returns:
            Transaction receipt
        """
        student_address = Web3.to_checksum_address(student_address)
        return self.call_write_function("withdrawSponsorFunds", student_address)

    def claim_scholarship(self) -> Dict[str, Any]:
        """
        Student action: claim scholarship funds.

        Returns:
            Transaction receipt
        """
        return self.call_write_function("claimScholarship")

    def get_student(self, student_address: str) -> Dict[str, Any]:
        """
        Get student data from public mapping.

        Args:
            student_address: Student wallet address

        Returns:
            Student struct tuple
        """
        student_address = Web3.to_checksum_address(student_address)
        return self.call_read_function("students", student_address)

    def get_sponsor(self, sponsor_address: str) -> Dict[str, Any]:
        """
        Get sponsor data from public mapping.

        Args:
            sponsor_address: Sponsor wallet address

        Returns:
            Sponsor struct tuple
        """
        sponsor_address = Web3.to_checksum_address(sponsor_address)
        return self.call_read_function("sponsors", sponsor_address)

    def get_student_balance(self, student_address: str) -> Dict[str, Any]:
        """
        Get student balance from public mapping.

        Args:
            student_address: Student wallet address

        Returns:
            Balance information
        """
        student_address = Web3.to_checksum_address(student_address)
        balance = self.call_read_function("studentBalances", student_address)
        return {
            "student": student_address,
            "balance_wei": balance,
            "balance_eth": Web3.from_wei(balance, "ether"),
        }

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
