import { useState } from "react";
import { Shield, Lock, Eye, CheckCircle, AlertTriangle, FileText, Users, DollarSign, Database, Clock, Hash } from "lucide-react";

const Index = () => {
  const [activeRole, setActiveRole] = useState<"public" | "committee" | "admin">("public");

  // Mock data for applicants
  const applicants = [
    { id: "APL-2024-001", name: "Maria Santos", academicScore: 92, financialStatus: "Low Income", eligibility: "Eligible", status: "Selected", reason: "High academic performance with demonstrated financial need" },
    { id: "APL-2024-002", name: "Juan Dela Cruz", academicScore: 88, financialStatus: "Middle Income", eligibility: "Eligible", status: "Selected", reason: "Outstanding extracurricular achievements and academic excellence" },
    { id: "APL-2024-003", name: "Ana Reyes", academicScore: 75, financialStatus: "Low Income", eligibility: "Not Eligible", status: "Rejected", reason: "Academic score below minimum threshold (80)" },
    { id: "APL-2024-004", name: "Pedro Garcia", academicScore: 95, financialStatus: "Low Income", eligibility: "Eligible", status: "Selected", reason: "Top academic performer with verified financial hardship" },
    { id: "APL-2024-005", name: "Elena Cruz", academicScore: 85, financialStatus: "Low Income", eligibility: "Eligible", status: "Pending", reason: "Under review - awaiting document verification" },
  ];

  // Mock data for fund distributions
  const fundDistributions = [
    { txHash: "0x7a8f...3d2e", beneficiaryId: "BEN-001", amount: "₱25,000", timestamp: "2024-01-15 09:32:41", status: "Released" },
    { txHash: "0x9c4b...1a7f", beneficiaryId: "BEN-002", amount: "₱25,000", timestamp: "2024-01-15 10:15:22", status: "Released" },
    { txHash: "0x2e6d...8b4c", beneficiaryId: "BEN-004", amount: "₱25,000", timestamp: "2024-01-16 14:45:33", status: "Pending" },
  ];

  // Mock data for beneficiaries
  const beneficiaries = [
    { id: "BEN-001", blockchainId: "0xABCD...1234", name: "Maria Santos", verificationStatus: "verified" },
    { id: "BEN-002", blockchainId: "0xEFGH...5678", name: "Juan Dela Cruz", verificationStatus: "verified" },
    { id: "BEN-003", blockchainId: "0xIJKL...9012", name: "Unknown", verificationStatus: "duplicate" },
    { id: "BEN-004", blockchainId: "0xMNOP...3456", name: "Pedro Garcia", verificationStatus: "verified" },
  ];

  // Mock audit logs
  const auditLogs = [
    { action: "Fund Release Approved", timestamp: "2024-01-15 09:30:00", refId: "BLK-REF-001" },
    { action: "Applicant Verified", timestamp: "2024-01-14 14:22:15", refId: "BLK-REF-002" },
    { action: "Selection Criteria Updated", timestamp: "2024-01-13 11:05:33", refId: "BLK-REF-003" },
    { action: "New Beneficiary Registered", timestamp: "2024-01-12 16:48:21", refId: "BLK-REF-004" },
  ];

  const getRoleAccessLabel = () => {
    switch (activeRole) {
      case "public":
        return "Access Level: Public — No Blockchain Credentials Required";
      case "committee":
        return "Access Level: Committee — Blockchain Credential Verified";
      case "admin":
        return "Access Level: Administrator — Smart Contract Authority Verified";
    }
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
                <Shield className="w-6 h-6 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-foreground">Edu-Chain</h1>
                <p className="text-xs text-muted-foreground">Blockchain Scholarship System</p>
              </div>
            </div>
            <div className="flex items-center gap-2 text-sm bg-accent/50 px-4 py-2 rounded-full">
              <Lock className="w-4 h-4 text-green-400" />
              <span className="text-muted-foreground">{getRoleAccessLabel()}</span>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 px-6 bg-gradient-to-b from-primary/5 to-background">
        <div className="container mx-auto text-center max-w-4xl">
          <div className="inline-flex items-center gap-2 bg-accent/50 px-4 py-2 rounded-full mb-6">
            <Shield className="w-4 h-4 text-primary" />
            <span className="text-sm text-muted-foreground">Blockchain-Powered Transparency</span>
          </div>
          <h2 className="text-4xl md:text-5xl font-bold text-foreground mb-6">
            Transparent Scholarship Selection & Fund Management
          </h2>
          <p className="text-lg text-muted-foreground mb-10 max-w-2xl mx-auto">
            Edu-Chain ensures accountability in scholarship distribution through immutable records, 
            credential-based access, and transparent selection criteria — all powered by blockchain technology.
          </p>
          
          {/* Feature Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-12">
            {[
              { icon: Eye, title: "Transparent Selection", desc: "Public visibility of criteria" },
              { icon: Lock, title: "Immutable Records", desc: "Tamper-proof documentation" },
              { icon: Shield, title: "Fraud Prevention", desc: "Duplicate detection system" },
              { icon: Users, title: "Credential Access", desc: "Role-based permissions" },
            ].map((feature, idx) => (
              <div key={idx} className="bg-card border border-border rounded-xl p-5 hover:border-primary/50 transition-colors">
                <feature.icon className="w-8 h-8 text-primary mb-3 mx-auto" />
                <h3 className="font-semibold text-foreground mb-1">{feature.title}</h3>
                <p className="text-xs text-muted-foreground">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Role Selection Section */}
      <section className="py-16 px-6 bg-card/30">
        <div className="container mx-auto max-w-5xl">
          <h2 className="text-2xl font-bold text-center mb-2">Credential-Based Access</h2>
          <p className="text-center text-muted-foreground mb-10">
            Roles are assigned via blockchain credentials — select a role to view available data
          </p>
          
          <div className="grid md:grid-cols-3 gap-6">
            {[
              { 
                role: "public" as const, 
                icon: Eye, 
                title: "Public Viewer", 
                desc: "View selected scholars, criteria, and fund summaries",
                access: "No credentials required"
              },
              { 
                role: "committee" as const, 
                icon: Users, 
                title: "Scholarship Committee", 
                desc: "Access full applicant list and eligibility details",
                access: "Blockchain credential verified"
              },
              { 
                role: "admin" as const, 
                icon: Shield, 
                title: "Administrator", 
                desc: "Fund distribution logs and audit trails",
                access: "Smart contract authority"
              },
            ].map((item) => (
              <button
                key={item.role}
                onClick={() => setActiveRole(item.role)}
                className={`p-6 rounded-xl border text-left transition-all ${
                  activeRole === item.role 
                    ? "bg-primary/10 border-primary" 
                    : "bg-card border-border hover:border-primary/50"
                }`}
              >
                <item.icon className={`w-10 h-10 mb-4 ${activeRole === item.role ? "text-primary" : "text-muted-foreground"}`} />
                <h3 className="font-semibold text-foreground mb-2">{item.title}</h3>
                <p className="text-sm text-muted-foreground mb-3">{item.desc}</p>
                <span className="text-xs text-primary bg-primary/10 px-2 py-1 rounded-full">
                  {item.access}
                </span>
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Scholarship Selection Transparency */}
      <section className="py-16 px-6">
        <div className="container mx-auto max-w-6xl">
          <div className="flex items-center gap-3 mb-6">
            <FileText className="w-6 h-6 text-primary" />
            <h2 className="text-2xl font-bold">Scholarship Selection Transparency</h2>
          </div>
          <p className="text-muted-foreground mb-8">
            All applicant records are stored on the blockchain and cannot be altered
          </p>

          <div className="bg-card border border-border rounded-xl overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-accent/50">
                  <tr>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-foreground">Applicant ID</th>
                    {(activeRole === "committee" || activeRole === "admin") && (
                      <th className="px-4 py-3 text-left text-sm font-semibold text-foreground">Name</th>
                    )}
                    <th className="px-4 py-3 text-left text-sm font-semibold text-foreground">Academic Score</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-foreground">Financial Status</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-foreground">Eligibility</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-foreground">Status</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-foreground">Reason</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {applicants
                    .filter(a => activeRole === "public" ? a.status === "Selected" : true)
                    .map((applicant) => (
                    <tr key={applicant.id} className="hover:bg-accent/20 transition-colors">
                      <td className="px-4 py-3 text-sm font-mono text-muted-foreground">{applicant.id}</td>
                      {(activeRole === "committee" || activeRole === "admin") && (
                        <td className="px-4 py-3 text-sm text-foreground">{applicant.name}</td>
                      )}
                      <td className="px-4 py-3 text-sm text-foreground">{applicant.academicScore}%</td>
                      <td className="px-4 py-3 text-sm text-muted-foreground">{applicant.financialStatus}</td>
                      <td className="px-4 py-3">
                        <span className={`text-xs px-2 py-1 rounded-full ${
                          applicant.eligibility === "Eligible" 
                            ? "bg-green-500/20 text-green-400" 
                            : "bg-red-500/20 text-red-400"
                        }`}>
                          {applicant.eligibility}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`text-xs px-2 py-1 rounded-full ${
                          applicant.status === "Selected" ? "bg-green-500/20 text-green-400" :
                          applicant.status === "Rejected" ? "bg-red-500/20 text-red-400" :
                          "bg-yellow-500/20 text-yellow-400"
                        }`}>
                          {applicant.status}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-muted-foreground max-w-xs truncate" title={applicant.reason}>
                        {applicant.reason}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="bg-accent/30 px-4 py-3 flex items-center gap-2 text-sm text-muted-foreground">
              <Lock className="w-4 h-4 text-green-400" />
              This record is immutable and stored on the blockchain.
            </div>
          </div>
        </div>
      </section>

      {/* Fund Distribution Tracking */}
      {(activeRole === "admin" || activeRole === "public") && (
        <section className="py-16 px-6 bg-card/30">
          <div className="container mx-auto max-w-6xl">
            <div className="flex items-center gap-3 mb-6">
              <DollarSign className="w-6 h-6 text-primary" />
              <h2 className="text-2xl font-bold">Fund Distribution Tracking</h2>
            </div>

            {/* Timeline */}
            <div className="flex items-center justify-between max-w-2xl mx-auto mb-12">
              {["Applied", "Verified", "Approved", "Released"].map((step, idx) => (
                <div key={step} className="flex items-center">
                  <div className="flex flex-col items-center">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                      idx < 3 ? "bg-green-500/20 text-green-400" : "bg-primary/20 text-primary"
                    }`}>
                      <CheckCircle className="w-5 h-5" />
                    </div>
                    <span className="text-xs text-muted-foreground mt-2">{step}</span>
                  </div>
                  {idx < 3 && <div className="w-16 md:w-24 h-0.5 bg-green-500/30 mx-2" />}
                </div>
              ))}
            </div>

            {/* Transaction Cards */}
            <div className="grid md:grid-cols-3 gap-4">
              {fundDistributions.map((tx) => (
                <div key={tx.txHash} className="bg-card border border-border rounded-xl p-5">
                  <div className="flex items-center gap-2 mb-4">
                    <Hash className="w-4 h-4 text-primary" />
                    <span className="font-mono text-sm text-muted-foreground">{tx.txHash}</span>
                  </div>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Beneficiary:</span>
                      <span className="text-foreground font-mono">{tx.beneficiaryId}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Amount:</span>
                      <span className="text-foreground font-semibold">{tx.amount}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Timestamp:</span>
                      <span className="text-foreground text-xs">{tx.timestamp}</span>
                    </div>
                    <div className="flex justify-between items-center pt-2">
                      <span className="text-muted-foreground">Status:</span>
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        tx.status === "Released" ? "bg-green-500/20 text-green-400" : "bg-yellow-500/20 text-yellow-400"
                      }`}>
                        {tx.status}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            
            <div className="bg-accent/30 rounded-lg px-4 py-3 mt-6 flex items-center gap-2 text-sm text-muted-foreground">
              <AlertTriangle className="w-4 h-4 text-yellow-400" />
              Fund releases are executed via smart contracts.
            </div>
          </div>
        </section>
      )}

      {/* Beneficiary Verification */}
      <section className="py-16 px-6">
        <div className="container mx-auto max-w-6xl">
          <div className="flex items-center gap-3 mb-6">
            <Database className="w-6 h-6 text-primary" />
            <h2 className="text-2xl font-bold">Beneficiary Verification & Anti-Duplication</h2>
          </div>
          <p className="text-muted-foreground mb-8">
            Each beneficiary is assigned a unique blockchain ID to prevent duplicate registrations
          </p>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            {beneficiaries.map((ben) => (
              <div key={ben.id} className="bg-card border border-border rounded-xl p-5">
                <div className="flex items-center justify-between mb-4">
                  <span className="font-mono text-sm text-muted-foreground">{ben.id}</span>
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    ben.verificationStatus === "verified" ? "bg-green-500/20 text-green-400" :
                    ben.verificationStatus === "duplicate" ? "bg-red-500/20 text-red-400" :
                    "bg-yellow-500/20 text-yellow-400"
                  }`}>
                    {ben.verificationStatus === "verified" ? "✓ Verified" :
                     ben.verificationStatus === "duplicate" ? "⚠ Duplicate" : "Invalid"}
                  </span>
                </div>
                <p className="text-foreground font-medium mb-2">
                  {(activeRole === "committee" || activeRole === "admin") ? ben.name : "••••••••"}
                </p>
                <p className="font-mono text-xs text-muted-foreground">{ben.blockchainId}</p>
              </div>
            ))}
          </div>

          <div className="bg-card border border-border rounded-xl p-6 mt-8">
            <h3 className="font-semibold text-foreground mb-3">How Blockchain Prevents Duplicates</h3>
            <div className="grid md:grid-cols-3 gap-4 text-sm">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-primary font-bold">1</span>
                </div>
                <p className="text-muted-foreground">Each applicant receives a unique cryptographic hash based on their verified identity</p>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-primary font-bold">2</span>
                </div>
                <p className="text-muted-foreground">Smart contracts automatically check for existing hashes before registration</p>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-primary font-bold">3</span>
                </div>
                <p className="text-muted-foreground">Duplicate attempts are flagged and rejected automatically</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Admin Audit Dashboard */}
      {activeRole === "admin" && (
        <section className="py-16 px-6 bg-card/30">
          <div className="container mx-auto max-w-6xl">
            <div className="flex items-center gap-3 mb-6">
              <Clock className="w-6 h-6 text-primary" />
              <h2 className="text-2xl font-bold">Admin Audit & Oversight Dashboard</h2>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
              {[
                { label: "Total Applicants", value: "156", icon: Users },
                { label: "Verified Beneficiaries", value: "42", icon: CheckCircle },
                { label: "Funds Released", value: "₱1.05M", icon: DollarSign },
                { label: "Pending Reviews", value: "8", icon: Clock },
              ].map((stat, idx) => (
                <div key={idx} className="bg-card border border-border rounded-xl p-5">
                  <stat.icon className="w-6 h-6 text-primary mb-2" />
                  <p className="text-2xl font-bold text-foreground">{stat.value}</p>
                  <p className="text-sm text-muted-foreground">{stat.label}</p>
                </div>
              ))}
            </div>

            {/* Audit Logs */}
            <div className="bg-card border border-border rounded-xl overflow-hidden">
              <div className="px-4 py-3 bg-accent/50 border-b border-border">
                <h3 className="font-semibold text-foreground">Audit Log (Read-Only)</h3>
              </div>
              <div className="divide-y divide-border">
                {auditLogs.map((log, idx) => (
                  <div key={idx} className="px-4 py-3 flex items-center justify-between hover:bg-accent/20 transition-colors">
                    <div className="flex items-center gap-4">
                      <FileText className="w-4 h-4 text-muted-foreground" />
                      <span className="text-foreground">{log.action}</span>
                    </div>
                    <div className="flex items-center gap-6 text-sm">
                      <span className="text-muted-foreground">{log.timestamp}</span>
                      <span className="font-mono text-primary bg-primary/10 px-2 py-1 rounded text-xs">{log.refId}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-red-500/10 border border-red-500/30 rounded-lg px-4 py-3 mt-6 flex items-center gap-2 text-sm text-red-400">
              <AlertTriangle className="w-4 h-4" />
              All administrative actions are permanently recorded on the blockchain.
            </div>
          </div>
        </section>
      )}

      {/* Footer */}
      <footer className="py-8 px-6 border-t border-border bg-card/50">
        <div className="container mx-auto text-center">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Shield className="w-5 h-5 text-primary" />
            <span className="font-semibold text-foreground">Edu-Chain</span>
          </div>
          <p className="text-sm text-muted-foreground mb-2">
            Blockchain-Based Scholarship Transparency and Credential-Based Management System
          </p>
          <p className="text-xs text-muted-foreground">
            All records are immutable • Blockchain Verified • Smart Contract Secured
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Index;
