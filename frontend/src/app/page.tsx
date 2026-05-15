"use client";

import { useState, useEffect } from "react";
import { Search, Plane } from "lucide-react";
import DisclaimerModal from "@/components/DisclaimerModal";
import ResultCard from "@/components/ResultCard";

const ATA_CHAPTERS = [
  "All Chapters",
  "72-00-00",
  "72-21-00",
  "72-21-03",
  "72-22-00",
  "72-23-00",
  "72-31-00",
  "72-41-00",
  "72-51-00",
  "72-61-00"
];

export default function Home() {
  const [hasAccepted, setHasAccepted] = useState(false);
  const [query, setQuery] = useState("");
  const [ataFilter, setAtaFilter] = useState("All Chapters");
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [healthStatus, setHealthStatus] = useState<any>(null);

  useEffect(() => {
    // Check health on load
    fetch("http://localhost:8001/health")
      .then(res => res.json())
      .then(data => setHealthStatus(data))
      .catch(err => console.error("Health check failed", err));
  }, []);

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError("");

    try {
      let url = `http://localhost:8001/search?q=${encodeURIComponent(query)}`;
      if (ataFilter !== "All Chapters") {
        url += `&ata=${encodeURIComponent(ataFilter)}`;
      }

      const res = await fetch(url);
      if (!res.ok) {
        throw new Error(res.status === 429 ? "Rate limit exceeded. Please try again in a minute." : "Search failed. Backend might be down.");
      }
      
      const data = await res.json();
      setResults(data.results || []);
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-950 text-slate-200">
      {!hasAccepted && <DisclaimerModal onAccept={() => setHasAccepted(true)} />}

      <div className="max-w-5xl mx-auto p-4 sm:p-6 lg:p-8">
        <header className="mb-8 border-b border-slate-800 pb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="bg-blue-600 p-2 rounded-lg">
                <Plane className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-extrabold tracking-tight text-white">AMM Retriever</h1>
                <p className="text-sm text-slate-400 font-medium">737 MAX Verbatim Search Index</p>
              </div>
            </div>
            {healthStatus && (
              <div className="hidden sm:flex items-center gap-2 text-xs">
                <div className={`w-2 h-2 rounded-full ${healthStatus.search_engine_ready ? 'bg-emerald-500' : 'bg-amber-500 animate-pulse'}`}></div>
                <span className="text-slate-400">
                  {healthStatus.search_engine_ready ? `${healthStatus.chunks_loaded} Pages Indexed` : 'Initializing...'}
                </span>
              </div>
            )}
          </div>
        </header>

        <form onSubmit={handleSearch} className="mb-8 relative z-10">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <Search className="h-5 w-5 text-slate-500" />
              </div>
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Enter damage description or part name (e.g. 'fan disk', 'FOD')"
                className="block w-full pl-11 pr-4 py-4 bg-slate-900 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all shadow-inner"
              />
            </div>
            <div className="sm:w-48">
              <select
                value={ataFilter}
                onChange={(e) => setAtaFilter(e.target.value)}
                className="block w-full px-4 py-4 bg-slate-900 border border-slate-700 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all cursor-pointer appearance-none"
              >
                {ATA_CHAPTERS.map(chapter => (
                  <option key={chapter} value={chapter}>{chapter}</option>
                ))}
              </select>
            </div>
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="px-8 py-4 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-800 disabled:text-slate-500 text-white font-bold rounded-lg transition-colors shadow-lg shadow-blue-900/20"
            >
              {loading ? "Searching..." : "Search"}
            </button>
          </div>
        </form>

        {error && (
          <div className="bg-red-900/50 border border-red-500/50 text-red-200 p-4 rounded-lg mb-8">
            {error}
          </div>
        )}

        <div>
          {results.length > 0 && (
            <h3 className="text-sm font-semibold text-slate-400 mb-4 uppercase tracking-wider">
              Top Verbatim Matches ({results.length})
            </h3>
          )}
          
          {results.length === 0 && !loading && query && !error && (
            <div className="text-center py-12 text-slate-500 bg-slate-900/50 rounded-xl border border-slate-800 border-dashed">
              <Search className="w-12 h-12 mx-auto mb-3 opacity-20" />
              <p>No matches found for "{query}"</p>
              <p className="text-sm mt-1">Try adjusting your keywords or ATA filter.</p>
            </div>
          )}

          <div className="space-y-6">
            {results.map((res) => (
              <ResultCard key={res.chunk_id} result={res} />
            ))}
          </div>
        </div>
      </div>
    </main>
  );
}
