function SecurityBadge({ status, riskScore }) {
  const normalizedStatus = status || "UNKNOWN";
  const colors = {
    SAFE: "bg-green-100 text-green-800",
    SUSPICIOUS: "bg-yellow-100 text-yellow-800",
    DANGEROUS: "bg-red-100 text-red-800",
    "AI OFFLINE": "bg-gray-100 text-gray-800",
  };

  return (
    <div className={`inline-flex items-center gap-2 rounded px-2 py-1 text-sm font-semibold ${colors[normalizedStatus] || "bg-gray-100 text-gray-800"}`}>
      <span>{normalizedStatus}</span>
      {riskScore !== undefined && riskScore !== null && <span>({riskScore})</span>}
    </div>
  );
}

export default SecurityBadge;
