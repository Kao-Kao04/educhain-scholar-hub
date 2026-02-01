"""
Hardhat Deployment Script Template
Copy this as scripts/deploy.js in your Hardhat project
"""

const deploymentScript = `
const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  console.log("\\n========== ScholarshipManager Deployment ==========\\n");

  // Get deployer account
  const [deployer] = await ethers.getSigners();
  console.log("Deploying with account:", deployer.address);
  console.log("Account balance:", (await deployer.getBalance()).toString());

  // Get network info
  const network = await ethers.provider.getNetwork();
  console.log("Network:", network.name, "(Chain ID:", network.chainId + ")");

  // Deploy ScholarshipManager
  console.log("\\nDeploying ScholarshipManager contract...");
  
  const ScholarshipManager = await ethers.getContractFactory("ScholarshipSystem");
  const scholarship = await ScholarshipManager.deploy();
  await scholarship.deployed();

  console.log("\\n✓ ScholarshipManager deployed!");
  console.log("Contract address:", scholarship.address);
  console.log("Deployer address:", deployer.address);

  // Save deployment info
  const deploymentInfo = {
    network: network.name,
    chainId: network.chainId,
    contractAddress: scholarship.address,
    deployerAddress: deployer.address,
    deploymentBlock: await ethers.provider.getBlockNumber(),
    deploymentTime: new Date().toISOString(),
  };

  // Save to file
  const deploymentPath = path.join(__dirname, "../deployments.json");
  if (fs.existsSync(deploymentPath)) {
    const existing = JSON.parse(fs.readFileSync(deploymentPath));
    existing[network.name] = deploymentInfo;
    fs.writeFileSync(deploymentPath, JSON.stringify(existing, null, 2));
  } else {
    fs.writeFileSync(
      deploymentPath,
      JSON.stringify({ [network.name]: deploymentInfo }, null, 2)
    );
  }

  console.log("\\n✓ Deployment info saved to deployments.json");

  // Print .env update instructions
  console.log("\\n========== Update .env File ==========");
  console.log("Add these lines to your .env:");
  console.log("");
  console.log("CONTRACT_ADDRESS=" + scholarship.address);
  console.log("DEPLOYER_ADDRESS=" + deployer.address);
  console.log("");

  // Verify on Etherscan (if not localhost)
  if (network.name !== "hardhat" && network.name !== "localhost") {
    console.log("\\n========== Verification Instructions ==========");
    console.log("Verify contract on Etherscan:");
    console.log(
      \`npx hardhat verify --network \${network.name} \${scholarship.address}\`
    );
  }

  console.log("\\n========== Deployment Complete ==========\\n");

  return scholarship.address;
}

main()
  .then((address) => {
    console.log("Deployment successful!");
    process.exit(0);
  })
  .catch((error) => {
    console.error("Deployment failed:", error);
    process.exit(1);
  });
`;

// Hardhat configuration template
const hardhatConfig = `
require("@nomicfoundation/hardhat-toolbox");
require("@nomiclabs/hardhat-ethers");
require("@nomiclabs/hardhat-etherscan");
require("hardhat-gas-reporter");
require("dotenv").config();

const INFURA_API_KEY = process.env.INFURA_API_KEY || "";
const DEPLOYER_PRIVATE_KEY = process.env.DEPLOYER_PRIVATE_KEY || "0x0000000000000000000000000000000000000000000000000000000000000000";
const ETHERSCAN_API_KEY = process.env.ETHERSCAN_API_KEY || "";

module.exports = {
  solidity: {
    version: "0.8.20",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200,
      },
    },
  },
  networks: {
    hardhat: {
      chainId: 31337,
    },
    localhost: {
      url: "http://127.0.0.1:8545",
    },
    sepolia: {
      url: \`https://sepolia.infura.io/v3/\${INFURA_API_KEY}\`,
      accounts: [DEPLOYER_PRIVATE_KEY],
      chainId: 11155111,
    },
    polygon: {
      url: "https://polygon-rpc.com",
      accounts: [DEPLOYER_PRIVATE_KEY],
      chainId: 137,
    },
    mumbai: {
      url: "https://rpc-mumbai.maticvigil.com",
      accounts: [DEPLOYER_PRIVATE_KEY],
      chainId: 80001,
    },
  },
  etherscan: {
    apiKey: ETHERSCAN_API_KEY,
  },
  gasReporter: {
    enabled: process.env.REPORT_GAS === "true",
    currency: "USD",
  },
  paths: {
    sources: "./contracts",
    tests: "./test",
    cache: "./cache",
    artifacts: "./artifacts",
  },
};
`;

console.log("Hardhat Deployment Script Template\n");
console.log("========================================\n");
console.log("Save as: scripts/deploy.js\n");
console.log(deploymentScript);
console.log("\n========================================\n");
console.log("Hardhat Configuration Template\n");
console.log("========================================\n");
console.log("Save as: hardhat.config.js\n");
console.log(hardhatConfig);
