import { FileText, Image as ImageIcon } from "lucide-react";

interface ChunkResult {
  chunk_id: string;
  page_no: number;
  ata_chapter: string;
  content: string;
  figure_ids: string[];
  score?: number;
}

interface ResultCardProps {
  result: ChunkResult;
}

export default function ResultCard({ result }: ResultCardProps) {
  // Truncate content for display if it's too long
  const displayContent = result.content.length > 800 
    ? result.content.substring(0, 800) + "..."
    : result.content;

  return (
    <div className="bg-slate-800 border border-slate-700 rounded-lg p-5 mb-4 shadow-lg hover:border-blue-500/50 transition-colors">
      <div className="flex justify-between items-start mb-3">
        <div className="flex items-center gap-2">
          <span className="bg-blue-600 text-white px-3 py-1 rounded-full text-sm font-bold flex items-center gap-1 shadow-sm">
            <FileText className="w-4 h-4" />
            Page {result.page_no}
          </span>
          <span className="bg-slate-700 text-slate-300 px-3 py-1 rounded-full text-sm font-medium border border-slate-600">
            ATA {result.ata_chapter}
          </span>
        </div>
      </div>
      
      <div className="bg-slate-900 rounded p-4 mb-4 overflow-x-auto text-slate-300 font-mono text-sm border border-slate-800 leading-relaxed whitespace-pre-wrap">
        {displayContent}
      </div>

      {result.figure_ids && result.figure_ids.length > 0 && (
        <div className="mt-4">
          <h4 className="text-sm font-bold text-slate-400 mb-2 flex items-center gap-1 uppercase tracking-wider">
            <ImageIcon className="w-4 h-4" />
            Related Schematics ({result.figure_ids.length})
          </h4>
          <div className="flex overflow-x-auto gap-4 pb-2 snap-x">
            {result.figure_ids.map((figId) => (
              <div key={figId} className="flex-none snap-center relative group">
                <a 
                  href={`http://localhost:8001/figure/${result.page_no}/${figId.split('_')[1]}`} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="block"
                >
                  <div className="h-40 w-56 bg-slate-200 rounded overflow-hidden relative border border-slate-600 group-hover:border-blue-400 transition-colors">
                    <img 
                      src={`http://localhost:8001/figure/${result.page_no}/${figId.split('_')[1]}`}
                      alt={`Figure ${figId}`}
                      className="w-full h-full object-contain p-2"
                      loading="lazy"
                    />
                    <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity">
                      <span className="bg-blue-600 text-white px-2 py-1 rounded text-xs font-bold shadow">
                        View Full Size
                      </span>
                    </div>
                  </div>
                </a>
              </div>
            ))}
          </div>
        </div>
      )}
      
      <div className="mt-4 pt-3 border-t border-slate-700/50">
        <p className="text-xs text-amber-500/80 font-medium">
          ⚠️ Note: This is an extracted reference. You must verify this information on Page {result.page_no} of the DGCA-approved manual.
        </p>
      </div>
    </div>
  );
}
