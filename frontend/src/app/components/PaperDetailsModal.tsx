import React, { useState } from 'react';
import { 
  X, 
  FileText, 
  Sparkles, 
  Copy, 
  Check, 
  ExternalLink, 
  Calendar, 
  Users, 
  Tag, 
  BookOpen 
} from 'lucide-react';
import { getCategoryBadgeStyle } from '../utils/categories';

interface PaperDetailsModalProps {
  paper: any | null;
  onClose: () => void;
  onAskAI: (paper: any) => void;
}

export function PaperDetailsModal({ paper, onClose, onAskAI }: PaperDetailsModalProps) {
  const [copied, setCopied] = useState(false);

  if (!paper) return null;

  const authorsList = Array.isArray(paper.authors) 
    ? paper.authors.join(", ") 
    : (paper.authors || "Unknown Authors");

  const categoryStyle = getCategoryBadgeStyle(paper.category);

  const generateBibtex = () => {
    const paperId = paper.paper_id || paper.id || "paper";
    const cleanAuthors = authorsList.replace(/, /g, " and ");
    return `@article{${paperId.replace(/[^a-zA-Z0-9]/g, "")},\n  title={${paper.title}},\n  author={${cleanAuthors}},\n  journal={arXiv preprint arXiv:${paperId}},\n  year={${paper.year || 2024}}\n}`;
  };

  const handleCopyCitation = () => {
    const bibtex = generateBibtex();
    navigator.clipboard.writeText(bibtex);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div 
        className="relative w-full max-w-3xl bg-white rounded-2xl shadow-2xl border border-slate-200/80 overflow-hidden flex flex-col max-h-[90vh]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="p-6 bg-slate-50 border-b border-slate-200/80 flex items-start justify-between gap-4">
          <div className="space-y-2">
            <div className="flex flex-wrap items-center gap-2">
              <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border ${categoryStyle.bg} ${categoryStyle.text} ${categoryStyle.border}`}>
                <Tag className="w-3 h-3" />
                {paper.category || "Research"}
              </span>
              {paper.year && (
                <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-200/70 text-slate-700">
                  <Calendar className="w-3 h-3" />
                  {paper.year}
                </span>
              )}
            </div>
            <h2 className="text-xl font-black text-slate-900 leading-snug tracking-tight">
              {paper.title}
            </h2>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-slate-200/60 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1 custom-scrollbar">
          {/* Authors */}
          <div className="flex items-start gap-3 p-3.5 bg-slate-50/80 rounded-xl border border-slate-200/60">
            <Users className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
            <div>
              <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Authors</p>
              <p className="text-sm font-semibold text-slate-800 mt-0.5">{authorsList}</p>
            </div>
          </div>

          {/* Abstract */}
          <div className="space-y-2">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
              <BookOpen className="w-3.5 h-3.5 text-emerald-600" />
              Full Abstract
            </h3>
            <div className="p-4 bg-slate-50/50 rounded-xl border border-slate-200/50 text-sm text-slate-700 leading-relaxed font-normal">
              {paper.full_abstract || paper.abstract || "No abstract details available."}
            </div>
          </div>

          {/* BibTeX Code Snippet Preview */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">BibTeX Citation</h3>
              <button
                onClick={handleCopyCitation}
                className="text-xs text-emerald-600 hover:text-emerald-700 font-semibold flex items-center gap-1 transition-colors"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                {copied ? "Copied!" : "Copy BibTeX"}
              </button>
            </div>
            <pre className="p-3 bg-slate-900 text-slate-300 rounded-xl font-mono text-xs overflow-x-auto border border-slate-800">
              {generateBibtex()}
            </pre>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="p-4 bg-slate-50 border-t border-slate-200/80 flex flex-wrap items-center justify-between gap-3">
          <button
            onClick={() => {
              onClose();
              onAskAI(paper);
            }}
            className="flex-1 min-w-[200px] py-2.5 px-4 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white font-bold text-xs rounded-xl shadow-md shadow-emerald-600/20 hover:shadow-lg transition-all flex items-center justify-center gap-2"
          >
            <Sparkles className="w-4 h-4 fill-white" />
            Ask AI Assistant About This Paper
          </button>

          <a
            href={paper.pdf_url || `/api/pdfs/${paper.paper_id || paper.id}.pdf`}
            target="_blank"
            rel="noopener noreferrer"
            className="py-2.5 px-4 bg-white hover:bg-slate-100 text-slate-700 border border-slate-200 rounded-xl font-bold text-xs transition-colors flex items-center justify-center gap-2"
          >
            <FileText className="w-4 h-4 text-emerald-600" />
            View Source PDF
            <ExternalLink className="w-3 h-3 text-slate-400" />
          </a>
        </div>
      </div>
    </div>
  );
}
