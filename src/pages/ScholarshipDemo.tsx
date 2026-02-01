import { useMemo, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Shield, Users, DollarSign, CheckCircle, FileText, Wallet } from "lucide-react";
import { Link } from "react-router-dom";
import { createWalletClient, custom, parseEther } from "viem";

const ScholarshipDemo = () => {
  const [walletAddress, setWalletAddress] = useState<string>("");
  const [contractAddress, setContractAddress] = useState<string>("");
  const [sponsorAddress, setSponsorAddress] = useState<string>("");
  const [studentAddress, setStudentAddress] = useState<string>("");
  const [amountEth, setAmountEth] = useState<string>("0.1");
  const [gpaScaled, setGpaScaled] = useState<string>("350");
  const [logs, setLogs] = useState<string[]>([]);

  const contractAbi = useMemo(
    () => [
      {
        type: "function",
        name: "verifySponsor",
        stateMutability: "nonpayable",
        inputs: [{ name: "_sponsorAddr", type: "address" }],
        outputs: [],
      },
      {
        type: "function",
        name: "verifyStudent",
        stateMutability: "nonpayable",
        inputs: [
          { name: "_studentAddr", type: "address" },
          { name: "_assignedSponsor", type: "address" },
          { name: "_amount", type: "uint256" },
          { name: "_initialGpa", type: "uint256" },
        ],
        outputs: [],
      },
      {
        type: "function",
        name: "updateStudentGPA",
        stateMutability: "nonpayable",
        inputs: [
          { name: "_studentAddr", type: "address" },
          { name: "_newGpa", type: "uint256" },
        ],
        outputs: [],
      },
      {
        type: "function",
        name: "fundStudent",
        stateMutability: "payable",
        inputs: [{ name: "_studentAddr", type: "address" }],
        outputs: [],
      },
      {
        type: "function",
        name: "withdrawSponsorFunds",
        stateMutability: "nonpayable",
        inputs: [{ name: "_studentAddr", type: "address" }],
        outputs: [],
      },
      {
        type: "function",
        name: "claimScholarship",
        stateMutability: "nonpayable",
        inputs: [],
        outputs: [],
      },
    ],
    []
  );

  const walletClient = useMemo(() => {
    if (!window.ethereum) {
      return null;
    }
    return createWalletClient({
      transport: custom(window.ethereum),
    });
  }, []);

  const pushLog = (message: string) => {
    setLogs((prev) => [`${new Date().toLocaleTimeString()} • ${message}`, ...prev]);
  };

  const connectWallet = async () => {
    if (!walletClient) {
      pushLog("MetaMask not found. Install it to continue.");
      return;
    }
    const accounts = await walletClient.requestAddresses();
    setWalletAddress(accounts[0] ?? "");
    pushLog(`Connected wallet: ${accounts[0] ?? ""}`);
  };

  const ensureReady = () => {
    if (!walletClient) {
      pushLog("MetaMask not found.");
      return false;
    }
    if (!contractAddress) {
      pushLog("Contract address is required.");
      return false;
    }
    if (!walletAddress) {
      pushLog("Connect wallet first.");
      return false;
    }
    return true;
  };

  const verifySponsor = async () => {
    if (!ensureReady() || !sponsorAddress) {
      pushLog("Sponsor address is required.");
      return;
    }
    const hash = await walletClient!.writeContract({
      account: walletAddress as `0x${string}`,
      address: contractAddress as `0x${string}`,
      abi: contractAbi,
      functionName: "verifySponsor",
      args: [sponsorAddress as `0x${string}`],
    });
    pushLog(`verifySponsor sent: ${hash}`);
  };

  const verifyStudent = async () => {
    if (!ensureReady() || !studentAddress || !sponsorAddress) {
      pushLog("Student and sponsor addresses are required.");
      return;
    }
    const amountWei = parseEther(amountEth || "0");
    const hash = await walletClient!.writeContract({
      account: walletAddress as `0x${string}`,
      address: contractAddress as `0x${string}`,
      abi: contractAbi,
      functionName: "verifyStudent",
      args: [
        studentAddress as `0x${string}`,
        sponsorAddress as `0x${string}`,
        amountWei,
        BigInt(gpaScaled || "0"),
      ],
    });
    pushLog(`verifyStudent sent: ${hash}`);
  };

  const fundStudent = async () => {
    if (!ensureReady() || !studentAddress) {
      pushLog("Student address is required.");
      return;
    }
    const amountWei = parseEther(amountEth || "0");
    const hash = await walletClient!.writeContract({
      account: walletAddress as `0x${string}`,
      address: contractAddress as `0x${string}`,
      abi: contractAbi,
      functionName: "fundStudent",
      args: [studentAddress as `0x${string}`],
      value: amountWei,
    });
    pushLog(`fundStudent sent: ${hash}`);
  };

  const claimScholarship = async () => {
    if (!ensureReady()) {
      return;
    }
    const hash = await walletClient!.writeContract({
      account: walletAddress as `0x${string}`,
      address: contractAddress as `0x${string}`,
      abi: contractAbi,
      functionName: "claimScholarship",
      args: [],
    });
    pushLog(`claimScholarship sent: ${hash}`);
  };
  const steps = [
    {
      title: "Admin verifies sponsor",
      description: "Call verifySponsor(sponsorAddress) to approve a sponsor.",
      action: "verifySponsor(0xSponsor...)",
      status: "Required",
      onClick: verifySponsor,
    },
    {
      title: "Admin verifies student",
      description: "Assign sponsor, set scholarship amount, and initial GPA.",
      action: "verifyStudent(0xStudent..., 0xSponsor..., 0.1 ETH, 3.50)",
      status: "Required",
      onClick: verifyStudent,
    },
    {
      title: "Sponsor funds student",
      description: "Sponsor sends the exact scholarship amount to fundStudent().",
      action: "fundStudent(0xStudent...) payable",
      status: "Required",
      onClick: fundStudent,
    },
    {
      title: "Student claims scholarship",
      description: "Student calls claimScholarship() once funded and eligible.",
      action: "claimScholarship()",
      status: "Final",
      onClick: claimScholarship,
    },
  ];

  const demoState = [
    { label: "Admin", value: "0xA1b2...cD3E", icon: Shield },
    { label: "Sponsor", value: "0xF4e5...bA67", icon: Wallet },
    { label: "Student", value: "0x9C8d...12EF", icon: Users },
    { label: "Scholarship Amount", value: "0.10 ETH", icon: DollarSign },
  ];

  const contractActions = [
    {
      role: "Admin",
      items: ["verifySponsor", "verifyStudent", "updateStudentGPA"],
      icon: Shield,
    },
    {
      role: "Sponsor",
      items: ["fundStudent", "withdrawSponsorFunds"],
      icon: Wallet,
    },
    {
      role: "Student",
      items: ["claimScholarship"],
      icon: Users,
    },
  ];

  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="border-b border-border bg-card/50">
        <div className="container mx-auto px-6 py-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
              <Shield className="w-6 h-6 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-xl font-bold">ScholarshipManager Demo</h1>
              <p className="text-xs text-muted-foreground">Contract walkthrough for ideathon</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline" onClick={connectWallet}>
              {walletAddress ? "Wallet Connected" : "Connect Wallet"}
            </Button>
            <Button variant="outline" asChild>
              <Link to="/">Back to Home</Link>
            </Button>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-10 space-y-10">
        <section className="grid md:grid-cols-2 gap-4">
          <div className="bg-card border border-border rounded-xl p-5 space-y-3">
            <h2 className="text-sm font-semibold text-muted-foreground">Connection</h2>
            <div className="space-y-2">
              <label className="text-xs text-muted-foreground">Contract Address</label>
              <Input
                placeholder="0x..."
                value={contractAddress}
                onChange={(event) => setContractAddress(event.target.value)}
              />
            </div>
            <div className="text-xs text-muted-foreground">Connected Wallet: {walletAddress || "Not connected"}</div>
          </div>
          <div className="bg-card border border-border rounded-xl p-5 space-y-3">
            <h2 className="text-sm font-semibold text-muted-foreground">Demo Inputs</h2>
            <div className="grid md:grid-cols-2 gap-3">
              <div>
                <label className="text-xs text-muted-foreground">Sponsor Address</label>
                <Input
                  placeholder="0xSponsor..."
                  value={sponsorAddress}
                  onChange={(event) => setSponsorAddress(event.target.value)}
                />
              </div>
              <div>
                <label className="text-xs text-muted-foreground">Student Address</label>
                <Input
                  placeholder="0xStudent..."
                  value={studentAddress}
                  onChange={(event) => setStudentAddress(event.target.value)}
                />
              </div>
              <div>
                <label className="text-xs text-muted-foreground">Amount (ETH)</label>
                <Input
                  value={amountEth}
                  onChange={(event) => setAmountEth(event.target.value)}
                />
              </div>
              <div>
                <label className="text-xs text-muted-foreground">Initial GPA (x100)</label>
                <Input
                  value={gpaScaled}
                  onChange={(event) => setGpaScaled(event.target.value)}
                />
              </div>
            </div>
          </div>
        </section>
        <section className="grid md:grid-cols-4 gap-4">
          {demoState.map((item) => (
            <div key={item.label} className="bg-card border border-border rounded-xl p-4">
              <item.icon className="w-5 h-5 text-primary mb-2" />
              <p className="text-xs text-muted-foreground">{item.label}</p>
              <p className="font-semibold text-foreground mt-1">{item.value}</p>
            </div>
          ))}
        </section>

        <section className="bg-card border border-border rounded-xl p-6">
          <div className="flex items-center gap-2 mb-4">
            <FileText className="w-5 h-5 text-primary" />
            <h2 className="text-lg font-semibold">Contract Roles & Permissions</h2>
          </div>
          <div className="grid md:grid-cols-3 gap-4">
            {contractActions.map((role) => (
              <div key={role.role} className="border border-border rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <role.icon className="w-4 h-4 text-primary" />
                  <span className="font-medium">{role.role}</span>
                </div>
                <ul className="text-sm text-muted-foreground space-y-1">
                  {role.items.map((item) => (
                    <li key={item}>• {item}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </section>

        <section className="bg-card border border-border rounded-xl p-6">
          <div className="flex items-center gap-2 mb-6">
            <CheckCircle className="w-5 h-5 text-green-400" />
            <h2 className="text-lg font-semibold">End-to-End Demo Flow</h2>
          </div>
          <div className="space-y-4">
            {steps.map((step, index) => (
              <div key={step.title} className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border border-border rounded-lg p-4">
                <div>
                  <p className="text-sm text-muted-foreground">Step {index + 1}</p>
                  <h3 className="font-semibold text-foreground">{step.title}</h3>
                  <p className="text-sm text-muted-foreground mt-1">{step.description}</p>
                  <p className="text-xs font-mono text-primary mt-2">{step.action}</p>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-xs bg-primary/10 text-primary px-2 py-1 rounded-full">{step.status}</span>
                  <Button variant="outline" onClick={step.onClick}>
                    Run
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="bg-card border border-border rounded-xl p-6">
          <div className="flex items-center gap-2 mb-4">
            <FileText className="w-5 h-5 text-primary" />
            <h2 className="text-lg font-semibold">Transaction Log</h2>
          </div>
          {logs.length === 0 ? (
            <p className="text-sm text-muted-foreground">No transactions yet.</p>
          ) : (
            <ul className="space-y-2 text-sm text-muted-foreground">
              {logs.map((entry, index) => (
                <li key={index} className="border border-border rounded-md px-3 py-2 bg-accent/10">
                  {entry}
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="bg-gradient-to-br from-primary/10 to-background border border-primary/20 rounded-xl p-6 flex flex-col md:flex-row md:items-center md:justify-between gap-6">
          <div>
            <h2 className="text-lg font-semibold">Ready to test on-chain?</h2>
            <p className="text-sm text-muted-foreground mt-1">
              Deploy ScholarshipManager.sol and wire the demo actions to real transactions when ready.
            </p>
          </div>
          <Button asChild>
            <Link to="/">Return to Dashboard</Link>
          </Button>
        </section>
      </main>
    </div>
  );
};

export default ScholarshipDemo;
