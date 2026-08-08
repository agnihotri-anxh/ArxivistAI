import React, { useState, useEffect } from 'react';
import { 
  Database, 
  BookOpen, 
  Users, 
  Layers, 
  Play, 
  RotateCcw, 
  Activity, 
  CheckCircle2, 
  AlertCircle, 
  Terminal,
  Sparkles,
  Download,
  FileText,
  Cpu
} from 'lucide-react';

interface SystemStatus {
  raw_staging_count: number;
  website_papers_count: number;
  users_count: number;
  milvus_vectors_count: number;
  is_running: boolean;
  current_step: string;
  last_run: string;
  status: string;
  logs: string[];
}

export function AdminPanel() {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [actionMessage, setActionMessage] = useState('');
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [batchLimit, setBatchLimit] = useState<number>(50);

  const fetchStatus = async () => {
    try {
      const res = await fetch('/api/admin/status');
      if (res.ok) {
        const text = await res.text();
        if (text && text.trim()) {
          const data = JSON.parse(text);
          setStatus(data);
        }
      }
    } catch (e) {
      console.error("Failed to fetch admin status:", e);
    }
  };

  useEffect(() => {
    fetchStatus();
    let interval: any;
    if (autoRefresh) {
      interval = setInterval(fetchStatus, 3000);
    }
    return () => clearInterval(interval);
  }, [autoRefresh]);

  const triggerAction = async (action: string) => {
    setLoading(true);
    setActionMessage('');
    try {
      const res = await fetch(`/api/admin/pipeline/${action}?limit=${batchLimit}`, {
        method: 'POST'
      });
      const text = await res.text();
      let data: any = {};
      if (text && text.trim()) {
        try { data = JSON.parse(text); } catch {}
      }
      if (!res.ok) {
        throw new Error(data.detail || 'Action failed');
      }
      setActionMessage(`Task '${action}' (Limit: ${batchLimit} records) started successfully!`);
      fetchStatus();
    } catch (err: any) {
      setActionMessage(`Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-56px)] bg-[#f8fafc] py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Header Banner */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200/80 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <div className="w-8 h-8 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold text-sm">
                ⚙️
              </div>
              <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Admin Control Panel</h1>
            </div>
            <p className="text-sm text-slate-500">
              Orchestrate arXiv harvesting, PDF extraction, BGE-M3 vector embeddings, and MongoDB catalog pipelines.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={`px-3 py-1.5 text-xs font-semibold rounded-lg border transition-all flex items-center gap-1.5 ${
                autoRefresh 
                  ? 'bg-emerald-50 text-emerald-700 border-emerald-300' 
                  : 'bg-slate-50 text-slate-600 border-slate-200'
              }`}
            >
              <Activity className={`w-3.5 h-3.5 ${autoRefresh ? 'animate-pulse text-emerald-600' : ''}`} />
              {autoRefresh ? 'Live Refresh ON (3s)' : 'Live Refresh OFF'}
            </button>
            <button
              onClick={fetchStatus}
              className="p-2 rounded-lg bg-slate-100 text-slate-600 hover:bg-slate-200 transition-colors"
              title="Refresh Stats"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Action Alert Banner */}
        {actionMessage && (
          <div className={`p-4 rounded-xl text-sm font-medium border flex items-center gap-2 ${
            actionMessage.startsWith('Error') 
              ? 'bg-rose-50 text-rose-700 border-rose-200' 
              : 'bg-emerald-50 text-emerald-700 border-emerald-200'
          }`}>
            {actionMessage.startsWith('Error') ? <AlertCircle className="w-4 h-4" /> : <CheckCircle2 className="w-4 h-4" />}
            {actionMessage}
          </div>
        )}

        {/* Live Metrics Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {/* Card 1: Staging Papers */}
          <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-sm flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Staging Metadata</p>
              <p className="text-2xl font-black text-slate-900 mt-1">
                {status ? status.raw_staging_count.toLocaleString() : '...'}
              </p>
              <p className="text-[11px] text-slate-400 mt-1">MongoDB `raw_arxiv_metadata`</p>
            </div>
            <div className="w-12 h-12 rounded-2xl bg-amber-50 text-amber-600 flex items-center justify-center">
              <Database className="w-6 h-6" />
            </div>
          </div>

          {/* Card 2: Website Catalog Papers */}
          <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-sm flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Website Catalog</p>
              <p className="text-2xl font-black text-slate-900 mt-1">
                {status ? status.website_papers_count.toLocaleString() : '...'}
              </p>
              <p className="text-[11px] text-slate-400 mt-1">MongoDB `papers` collection</p>
            </div>
            <div className="w-12 h-12 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <BookOpen className="w-6 h-6" />
            </div>
          </div>

          {/* Card 3: Milvus Chunks */}
          <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-sm flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Milvus Vector Index</p>
              <p className="text-2xl font-black text-slate-900 mt-1">
                {status ? status.milvus_vectors_count.toLocaleString() : '...'}
              </p>
              <p className="text-[11px] text-slate-400 mt-1">Zilliz Cloud BGE-M3 Embeddings</p>
            </div>
            <div className="w-12 h-12 rounded-2xl bg-purple-50 text-purple-600 flex items-center justify-center">
              <Layers className="w-6 h-6" />
            </div>
          </div>

          {/* Card 4: Registered Users */}
          <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-sm flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Active Users</p>
              <p className="text-2xl font-black text-slate-900 mt-1">
                {status ? status.users_count.toLocaleString() : '...'}
              </p>
              <p className="text-[11px] text-slate-400 mt-1">MongoDB `users` collection</p>
            </div>
            <div className="w-12 h-12 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center">
              <Users className="w-6 h-6" />
            </div>
          </div>
        </div>

        {/* Pipeline Control Hub & Execution Status */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Controls Column */}
          <div className="lg:col-span-1 bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <h2 className="font-bold text-slate-800 text-lg">Pipeline Execution Hub</h2>
              <div className={`px-2.5 py-1 rounded-full text-xs font-bold uppercase tracking-wider flex items-center gap-1.5 ${
                status?.is_running 
                  ? 'bg-amber-100 text-amber-800 animate-pulse' 
                  : 'bg-emerald-100 text-emerald-800'
              }`}>
                <span className={`w-2 h-2 rounded-full ${status?.is_running ? 'bg-amber-600' : 'bg-emerald-600'}`} />
                {status?.is_running ? 'RUNNING' : 'IDLE'}
              </div>
            </div>

            {status?.is_running && (
              <div className="p-3 bg-amber-50 rounded-xl border border-amber-200 text-xs text-amber-900">
                <span className="font-semibold">Active Step:</span> {status.current_step}
              </div>
            )}

            <div className="flex items-center justify-between bg-slate-50/80 p-3 rounded-xl border border-slate-200/80">
              <label className="text-xs font-semibold text-slate-700">Records Batch Limit:</label>
              <select
                value={batchLimit}
                onChange={(e) => setBatchLimit(Number(e.target.value))}
                className="px-2.5 py-1 text-xs font-semibold bg-white border border-slate-300 rounded-lg text-slate-800 outline-none focus:border-emerald-500 shadow-2xs"
              >
                <option value={10}>10 records</option>
                <option value={25}>25 records</option>
                <option value={50}>50 records</option>
                <option value={100}>100 records</option>
                <option value={250}>250 records</option>
                <option value={500}>500 records</option>
                <option value={1000}>1000 records</option>
              </select>
            </div>

            <div className="space-y-3 pt-2">
              <button
                onClick={() => triggerAction('harvest')}
                disabled={status?.is_running || loading}
                className="w-full flex items-center justify-between p-3.5 bg-slate-50 hover:bg-emerald-50 hover:border-emerald-300 border border-slate-200 rounded-xl text-slate-800 font-semibold text-xs transition-all disabled:opacity-50 group"
              >
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center">
                    <Sparkles className="w-4 h-4" />
                  </div>
                  <span>1. Harvest arXiv Metadata</span>
                </div>
                <Play className="w-4 h-4 text-slate-400 group-hover:text-emerald-600 transition-colors" />
              </button>

              <button
                onClick={() => triggerAction('download')}
                disabled={status?.is_running || loading}
                className="w-full flex items-center justify-between p-3.5 bg-slate-50 hover:bg-blue-50 hover:border-blue-300 border border-slate-200 rounded-xl text-slate-800 font-semibold text-xs transition-all disabled:opacity-50 group"
              >
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-lg bg-blue-100 text-blue-700 flex items-center justify-center">
                    <Download className="w-4 h-4" />
                  </div>
                  <span>2. Download Paper PDFs</span>
                </div>
                <Play className="w-4 h-4 text-slate-400 group-hover:text-blue-600 transition-colors" />
              </button>

              <button
                onClick={() => triggerAction('extract')}
                disabled={status?.is_running || loading}
                className="w-full flex items-center justify-between p-3.5 bg-slate-50 hover:bg-violet-50 hover:border-violet-300 border border-slate-200 rounded-xl text-slate-800 font-semibold text-xs transition-all disabled:opacity-50 group"
              >
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-lg bg-violet-100 text-violet-700 flex items-center justify-center">
                    <FileText className="w-4 h-4" />
                  </div>
                  <span>3. Extract Text & Figures</span>
                </div>
                <Play className="w-4 h-4 text-slate-400 group-hover:text-violet-600 transition-colors" />
              </button>

              <button
                onClick={() => triggerAction('embed')}
                disabled={status?.is_running || loading}
                className="w-full flex items-center justify-between p-3.5 bg-slate-50 hover:bg-purple-50 hover:border-purple-300 border border-slate-200 rounded-xl text-slate-800 font-semibold text-xs transition-all disabled:opacity-50 group"
              >
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-lg bg-purple-100 text-purple-700 flex items-center justify-center">
                    <Cpu className="w-4 h-4" />
                  </div>
                  <span>4. Embed Vectors & Index Milvus</span>
                </div>
                <Play className="w-4 h-4 text-slate-400 group-hover:text-purple-600 transition-colors" />
              </button>

              <div className="pt-2">
                <button
                  onClick={() => triggerAction('full')}
                  disabled={status?.is_running || loading}
                  className="w-full py-3 px-4 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white font-bold text-xs tracking-wider rounded-xl shadow-md shadow-emerald-600/20 hover:shadow-lg transition-all uppercase flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  <Play className="w-4 h-4 fill-white" />
                  Run Full Automated Ingestion
                </button>
              </div>

            </div>
          </div>

          {/* Execution Log Terminal */}
          <div className="lg:col-span-2 bg-slate-900 rounded-2xl border border-slate-800 shadow-xl p-5 flex flex-col justify-between overflow-hidden min-h-[420px]">
            <div>
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <div className="flex items-center gap-2 text-slate-200">
                  <Terminal className="w-4 h-4 text-emerald-400" />
                  <h3 className="font-semibold text-sm">Background Execution Terminal</h3>
                </div>
                <span className="text-[11px] text-slate-500 font-mono">
                  Last Run: {status?.last_run || 'Never'}
                </span>
              </div>

              <div className="mt-4 font-mono text-xs text-slate-300 space-y-1.5 max-h-[340px] overflow-y-auto pr-2 custom-scrollbar">
                {status?.logs && status.logs.length > 0 ? (
                  status.logs.map((line, idx) => (
                    <div key={idx} className="leading-relaxed hover:bg-slate-800/50 px-1 py-0.5 rounded">
                      <span className="text-slate-500 mr-2">$</span>
                      <span className={
                        line.includes('Error') || line.includes('error') 
                          ? 'text-rose-400 font-semibold' 
                          : line.includes('Started') 
                            ? 'text-amber-300 font-semibold' 
                            : line.includes('finished') 
                              ? 'text-emerald-400 font-semibold' 
                              : 'text-slate-300'
                      }>
                        {line}
                      </span>
                    </div>
                  ))
                ) : (
                  <p className="text-slate-600 italic">No log entries available.</p>
                )}
              </div>
            </div>

            <div className="pt-3 border-t border-slate-800 text-[10px] text-slate-500 flex justify-between items-center font-mono">
              <span>ArXivist AI Background Orchestrator v1.0</span>
              <span>Status: {status?.status || 'idle'}</span>
            </div>
          </div>

        </div>

      </div>
    </div>
  );
}
