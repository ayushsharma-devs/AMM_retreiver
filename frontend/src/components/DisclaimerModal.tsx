"use client";

import { useState } from "react";
import { AlertTriangle } from "lucide-react";

interface DisclaimerModalProps {
  onAccept: () => void;
}

export default function DisclaimerModal({ onAccept }: DisclaimerModalProps) {
  const [loading, setLoading] = useState(false);

  const handleAccept = async () => {
    setLoading(true);
    try {
      const response = await fetch("http://localhost:8001/audit/accept", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_agent: navigator.userAgent }),
      });
      if (response.ok) {
        onAccept();
      } else {
        console.error("Failed to log acceptance");
        setLoading(false);
      }
    } catch (e) {
      console.error(e);
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
      <div className="bg-slate-900 border border-slate-700 rounded-xl p-6 max-w-lg w-full shadow-2xl text-slate-100">
        <div className="flex items-center gap-4 mb-4 text-amber-500">
          <AlertTriangle className="w-8 h-8" />
          <h2 className="text-xl font-bold text-white">Regulatory Warning</h2>
        </div>
        
        <div className="space-y-4 mb-8 text-slate-300">
          <p>
            <strong>AMM Retriever</strong> is a supplementary search tool designed to aid discovery. It is <strong>NOT</strong> the official source of truth for aircraft maintenance.
          </p>
          <p>
            Every result must be verified against the official DGCA-approved Aircraft Maintenance Manual (AMM) PDF before any airworthiness sign-off or maintenance action is performed.
          </p>
          <p className="text-sm border-l-2 border-slate-600 pl-3">
            By proceeding, you acknowledge that you will verify all page references in the official documentation. Your acceptance will be logged for compliance auditing.
          </p>
        </div>
        
        <button
          onClick={handleAccept}
          disabled={loading}
          className="w-full bg-amber-600 hover:bg-amber-500 text-white font-bold py-3 px-4 rounded transition-colors disabled:opacity-50"
        >
          {loading ? "Logging acceptance..." : "I Understand & Accept"}
        </button>
      </div>
    </div>
  );
}
