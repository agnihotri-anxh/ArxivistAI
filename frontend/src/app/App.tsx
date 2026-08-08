import React, { useState, useEffect, useMemo } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  Search,
  BookOpen,
  Users,
  Sparkles,
  ChevronDown,
  Bell,
  User,
  Filter,
  ArrowRight,
  ExternalLink,
  Bot,
  RotateCcw,
  Tag,
  Calendar,
  Layers,
  Download,
  Trash2,
  Plus,
  ChevronLeft,
  ChevronRight
} from "lucide-react";
import researchLogoSvg from "@/imports/logo.svg";
import { ImageWithFallback } from "@/app/components/figma/ImageWithFallback";
import { AuthPage } from "@/app/components/AuthPage";
import { AdminPanel } from "@/app/components/AdminPanel";
import { PaperDetailsModal } from "@/app/components/PaperDetailsModal";
import { getCategoryBadgeStyle } from "@/app/utils/categories";

type Page = "landing" | "browse" | "chat" | "login" | "signup" | "admin";

const CATEGORIES_LIST = [
  "All",
  "Artificial Intelligence",
  "Natural Language Processing",
  "Computer Vision",
  "Machine Learning",
  "Robotics",
  "Data Mining"
];

const YEARS_LIST = ["All", "2026", "2025", "2024", "2023", "2022"];

function Logo({ compact = false }: { compact?: boolean }) {
  return (
    <div className="flex items-center">
      <div className="h-10 shrink-0">
        <img
          src={researchLogoSvg}
          alt="Research AI Logo"
          className="h-full w-auto object-contain"
        />
      </div>
      {!compact && (
        <span className="font-semibold text-lg text-foreground tracking-tight ml-2">
          ArXivist AI
        </span>
      )}
    </div>
  );
}

function CategoryBadge({ category }: { category: string }) {
  const style = getCategoryBadgeStyle(category);
  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold border ${style.bg} ${style.text} ${style.border}`}
    >
      <Tag className="w-3 h-3" />
      {category}
    </span>
  );
}

function TopNav({
  currentPage,
  setPage,
  searchQuery,
  setSearchQuery,
  openAuth,
  isLoggedIn,
  handleLogout,
}: {
  currentPage: Page;
  setPage: (page: Page) => void;
  searchQuery: string;
  setSearchQuery: (q: string) => void;
  openAuth: (mode: 'login' | 'signup') => void;
  isLoggedIn: boolean;
  handleLogout: () => void;
}) {
  const [showResearchMenu, setShowResearchMenu] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);

  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-md border-b border-border shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-14">
          <div className="flex items-center gap-6">
            <button onClick={() => setPage("landing")} className="flex items-center">
              <Logo />
            </button>
            <div className="relative hidden md:block w-72">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search 17,000+ research papers..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => { if (e.key === 'Enter') setPage("browse"); }}
                className="w-full pl-9 pr-4 py-1.5 text-xs bg-muted rounded-full border border-transparent focus:border-primary focus:bg-white outline-none transition-all"
              />
            </div>
          </div>

          <div className="flex items-center gap-3">
            <nav className="hidden md:flex items-center gap-1">
              <button
                onClick={() => setPage("landing")}
                className={`px-3 py-1.5 text-sm rounded-md transition-colors ${currentPage === "landing" ? "text-primary font-medium" : "text-muted-foreground hover:text-foreground"}`}
              >
                Home
              </button>
              <button
                onClick={() => setPage("browse")}
                className={`px-3 py-1.5 text-sm rounded-md transition-colors ${currentPage === "browse" ? "text-primary font-medium" : "text-muted-foreground hover:text-foreground"}`}
              >
                Browse
              </button>
              <button
                onClick={() => setPage("admin")}
                className={`px-3 py-1.5 text-sm rounded-md transition-colors ${currentPage === "admin" ? "text-primary font-medium" : "text-muted-foreground hover:text-foreground"}`}
              >
                Admin
              </button>

              <div className="relative">
                <button
                  onClick={() => setShowResearchMenu(!showResearchMenu)}
                  className="flex items-center gap-1 px-3 py-1.5 text-sm rounded-md bg-primary text-white hover:bg-primary/90 transition-colors"
                >
                  Research
                  <ChevronDown className="w-3.5 h-3.5" />
                </button>
                {showResearchMenu && (
                  <div className="absolute top-full left-0 mt-1.5 w-44 bg-white rounded-lg shadow-lg border border-border py-1 z-50">
                    {["Trending", "New Releases", "Top Cited"].map((item) => (
                      <button
                        key={item}
                        className="w-full text-left px-3 py-2 text-sm hover:bg-muted text-foreground transition-colors"
                        onClick={() => {
                          setShowResearchMenu(false);
                          setPage("browse");
                        }}
                      >
                        {item}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </nav>

            <button
              onClick={() => { if (!isLoggedIn) openAuth('login'); else setPage("chat"); }}
              className={`hidden sm:flex items-center gap-2 px-3.5 py-1.5 text-sm rounded-lg font-medium transition-all ${
                currentPage === "chat"
                  ? "bg-primary text-white shadow-md shadow-primary/30"
                  : "bg-gradient-to-r from-primary to-emerald-400 text-white hover:shadow-md hover:shadow-primary/30"
              }`}
            >
              <Sparkles className="w-3.5 h-3.5" />
              ArXivist AI
            </button>

            <button className="relative p-2 rounded-lg hover:bg-muted transition-colors text-muted-foreground hover:text-foreground">
              <Bell className="w-4.5 h-4.5" />
              <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 bg-primary rounded-full" />
            </button>

            <div className="relative">
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 border-2 border-primary/30 hover:border-primary transition-colors"
              >
                <User className="w-4 h-4 text-primary" />
              </button>
              {showUserMenu && (
                <div className="absolute right-0 top-full mt-2 w-56 bg-white rounded-xl shadow-xl border border-border p-4 z-50">
                  <p className="font-semibold text-sm text-foreground">{isLoggedIn ? 'Welcome Back!' : 'Welcome'}</p>
                  <p className="text-xs text-muted-foreground mt-0.5 mb-3">
                    {isLoggedIn ? 'You are logged in' : 'To access AI features and chat'}
                  </p>
                  <div className="flex flex-col gap-2">
                    <button onClick={() => { setShowUserMenu(false); setPage("admin"); }} className="w-full py-1.5 text-xs font-medium bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 transition-colors">
                      ⚙️ Admin Control Panel
                    </button>
                    {isLoggedIn ? (
                      <button onClick={() => { setShowUserMenu(false); handleLogout(); }} className="w-full py-1.5 text-xs font-medium border border-red-500 text-red-500 rounded-lg hover:bg-red-50 transition-colors">
                        Log Out
                      </button>
                    ) : (
                      <div className="flex gap-2">
                        <button onClick={() => { setShowUserMenu(false); openAuth('signup'); }} className="flex-1 py-1.5 text-sm font-medium border border-primary text-primary rounded-lg hover:bg-accent transition-colors">
                          Sign Up
                        </button>
                        <button onClick={() => { setShowUserMenu(false); openAuth('login'); }} className="flex-1 py-1.5 text-sm font-medium border border-primary text-primary rounded-lg hover:bg-accent transition-colors">
                          Log In
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}

function LandingPage({
  setPage,
  isLoggedIn,
  openAuth,
  totalPapers,
  onCategorySelect,
  onPaperSelect
}: {
  setPage: (p: Page) => void;
  isLoggedIn: boolean;
  openAuth: (mode: 'login' | 'signup') => void;
  totalPapers: number;
  onCategorySelect: (cat: string) => void;
  onPaperSelect: (paper: any) => void;
}) {
  const [featuredPapers, setFeaturedPapers] = useState<any[]>([]);

  useEffect(() => {
    fetch('/api/papers?limit=6')
      .then(async (res) => {
        if (!res.ok) return [];
        const text = await res.text();
        return text && text.trim() ? JSON.parse(text) : [];
      })
      .then(data => {
        const list = data.papers || data;
        if (Array.isArray(list)) setFeaturedPapers(list.slice(0, 6));
      })
      .catch(() => {});
  }, []);

  return (
    <div className="min-h-screen bg-background">
      <section className="relative overflow-hidden bg-gradient-to-b from-emerald-50/50 via-background to-background py-16 lg:py-24 border-b border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
            <div className="lg:col-span-7 space-y-6">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20 text-xs font-semibold text-primary">
                <Sparkles className="w-3.5 h-3.5" />
                Next-Gen Agentic RAG Assistant
              </div>
              <h1 className="text-4xl sm:text-5xl font-black text-foreground tracking-tight leading-tight">
                Empowering Research with <span className="text-primary">Intelligence & Speed</span>
              </h1>
              <p className="text-base text-muted-foreground leading-relaxed max-w-2xl">
                Instant access to 17,000+ arXiv papers, dual-stage vector indexing with BGE-M3, and a citation-grounded AI assistant.
              </p>
              <div className="flex flex-wrap items-center gap-4 pt-2">
                <button
                  onClick={() => setPage("browse")}
                  className="px-6 py-3 bg-primary text-white font-bold text-sm rounded-xl shadow-lg shadow-primary/20 hover:bg-primary/90 transition-all flex items-center gap-2"
                >
                  Explore Catalog
                  <ArrowRight className="w-4 h-4" />
                </button>
                <button
                  onClick={() => { if (!isLoggedIn) openAuth('login'); else setPage("chat"); }}
                  className="px-6 py-3 bg-white text-slate-700 font-bold text-sm border border-border rounded-xl hover:bg-slate-50 transition-colors flex items-center gap-2"
                >
                  <Sparkles className="w-4 h-4 text-primary" />
                  Ask AI Assistant
                </button>
              </div>

              <div className="grid grid-cols-3 gap-6 pt-6 border-t border-border/60">
                <div>
                  <p className="text-2xl font-black text-foreground">{totalPapers ? totalPapers.toLocaleString() : '17,909+'}</p>
                  <p className="text-xs text-muted-foreground">Indexed Papers</p>
                </div>
                <div>
                  <p className="text-2xl font-black text-foreground">47,353</p>
                  <p className="text-xs text-muted-foreground">Milvus Vector Chunks</p>
                </div>
                <div>
                  <p className="text-2xl font-black text-foreground">6 Categories</p>
                  <p className="text-xs text-muted-foreground">CS Subfields</p>
                </div>
              </div>
            </div>

            <div className="lg:col-span-5 bg-white rounded-2xl p-6 border border-border shadow-xl space-y-4">
              <h3 className="text-sm font-bold text-foreground uppercase tracking-wider flex items-center gap-2">
                <Tag className="w-4 h-4 text-primary" />
                Browse by Category
              </h3>
              <div className="grid grid-cols-1 gap-2">
                {CATEGORIES_LIST.filter(c => c !== "All").map((cat) => (
                  <button
                    key={cat}
                    onClick={() => {
                      onCategorySelect(cat);
                      setPage("browse");
                    }}
                    className="flex items-center justify-between p-3 rounded-xl bg-slate-50 hover:bg-emerald-50 hover:border-emerald-200 border border-slate-200/60 text-slate-800 text-xs font-semibold transition-all group"
                  >
                    <span>{cat}</span>
                    <ArrowRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-primary transition-colors" />
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Papers */}
      <section className="py-12 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-foreground tracking-tight">Recent Featured Research</h2>
            <p className="text-xs text-muted-foreground">Latest papers indexed in MongoDB Atlas and Milvus Cloud.</p>
          </div>
          <button onClick={() => setPage("browse")} className="text-xs font-bold text-primary hover:underline flex items-center gap-1">
            View All Papers →
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {featuredPapers.map((paper, idx) => (
            <div
              key={idx}
              onClick={() => onPaperSelect(paper)}
              className="bg-white rounded-2xl p-5 border border-border shadow-xs hover:shadow-md hover:border-primary/40 transition-all cursor-pointer flex flex-col justify-between space-y-4 group"
            >
              <div className="space-y-2">
                <CategoryBadge category={paper.category} />
                <h3 className="text-base font-bold text-foreground group-hover:text-primary transition-colors line-clamp-2">
                  {paper.title}
                </h3>
                <p className="text-xs text-muted-foreground line-clamp-3">
                  {paper.abstract}
                </p>
              </div>

              <div className="flex items-center justify-between pt-3 border-t border-border text-[11px] text-muted-foreground">
                <span className="truncate max-w-[180px]">{Array.isArray(paper.authors) ? paper.authors[0] : paper.authors}</span>
                <span className="font-semibold text-primary">Read More →</span>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

function BrowsePage({
  category,
  onCategorySelect,
  year,
  onYearSelect,
  onPaperSelect
}: {
  category: string;
  onCategorySelect: (cat: string) => void;
  year: string;
  onYearSelect: (y: string) => void;
  onPaperSelect: (paper: any) => void;
}) {
  const [searchQuery, setSearchQuery] = useState("");
  const [page, setPageNum] = useState(1);
  const [papersData, setPapersData] = useState<{ papers: any[]; total: number; page: number; total_pages: number }>({
    papers: [],
    total: 0,
    page: 1,
    total_pages: 1
  });
  const [loading, setLoading] = useState(false);

  const fetchPapers = async () => {
    setLoading(true);
    try {
      const queryParams = new URLSearchParams({
        page: String(page),
        limit: "24"
      });
      if (category && category !== "All") queryParams.append("category", category);
      if (year && year !== "All") queryParams.append("year", year);
      if (searchQuery.trim()) queryParams.append("search", searchQuery.trim());

      const res = await fetch(`/api/papers?${queryParams.toString()}`);
      if (res.ok) {
        const text = await res.text();
        if (text && text.trim()) {
          const data = JSON.parse(text);
          if (data.papers) {
            setPapersData(data);
          } else if (Array.isArray(data)) {
            setPapersData({ papers: data, total: data.length, page: 1, total_pages: 1 });
          }
        }
      }
    } catch (e) {
      console.error("Failed to fetch papers:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPapers();
  }, [category, year, searchQuery, page]);

  return (
    <div className="flex min-h-[calc(100vh-56px)]">
      {/* Sidebar Filter */}
      <aside className="hidden md:block w-64 shrink-0 bg-sidebar border-r border-sidebar-border p-4 space-y-6">
        <div className="flex items-center justify-between">
          <p className="text-[11px] font-medium uppercase tracking-widest text-sidebar-accent-foreground">
            Filters
          </p>
          <button
            onClick={() => {
              onCategorySelect("All");
              onYearSelect("All");
              setSearchQuery("");
              setPageNum(1);
            }}
            className="text-[11px] text-primary hover:underline font-semibold"
          >
            Reset All
          </button>
        </div>

        <div>
          <p className="text-[11px] font-medium uppercase tracking-widest text-sidebar-accent-foreground mb-2">
            Categories
          </p>
          <div className="space-y-1">
            {CATEGORIES_LIST.map((cat) => (
              <button
                key={cat}
                onClick={() => {
                  onCategorySelect(cat);
                  setPageNum(1);
                }}
                className={`w-full flex items-center justify-between px-3 py-1.5 rounded-lg text-xs transition-colors ${
                  category === cat
                    ? "bg-primary text-white font-medium shadow-xs"
                    : "text-sidebar-foreground hover:bg-sidebar-accent"
                }`}
              >
                <span className="truncate pr-2 text-left">{cat}</span>
              </button>
            ))}
          </div>
        </div>

        <div>
          <p className="text-[11px] font-medium uppercase tracking-widest text-sidebar-accent-foreground mb-2">
            Publication Year
          </p>
          <div className="space-y-1">
            {YEARS_LIST.map((y) => (
              <button
                key={y}
                onClick={() => {
                  onYearSelect(y);
                  setPageNum(1);
                }}
                className={`w-full text-left px-3 py-1.5 rounded-lg text-xs transition-colors ${
                  year === y
                    ? "bg-primary text-white font-medium"
                    : "text-sidebar-foreground hover:bg-sidebar-accent"
                }`}
              >
                {y}
              </button>
            ))}
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 min-w-0 bg-background flex flex-col justify-between">
        <div className="p-6 space-y-6">
          <div className="bg-white rounded-2xl p-4 border border-border shadow-xs flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="relative flex-1 w-full max-w-md">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search titles, authors, abstracts..."
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  setPageNum(1);
                }}
                className="w-full pl-10 pr-4 py-2 text-xs bg-slate-50 rounded-xl border border-slate-200 focus:border-primary focus:bg-white outline-none transition-all"
              />
            </div>

            <div className="flex items-center gap-2 text-xs font-semibold text-slate-500">
              <span>Found <strong className="text-slate-900">{papersData.total.toLocaleString()}</strong> papers</span>
            </div>
          </div>

          {/* Paper Cards List */}
          {loading ? (
            <div className="py-16 text-center text-slate-400 text-xs italic">Loading papers catalog...</div>
          ) : papersData.papers.length === 0 ? (
            <div className="py-16 text-center text-slate-400 text-xs italic">No research papers match your filter criteria.</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {papersData.papers.map((paper, idx) => (
                <div
                  key={idx}
                  onClick={() => onPaperSelect(paper)}
                  className="bg-white rounded-2xl p-5 border border-border shadow-xs hover:shadow-md hover:border-primary/40 transition-all cursor-pointer flex flex-col justify-between space-y-4 group"
                >
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <CategoryBadge category={paper.category} />
                      <span className="text-[11px] font-mono text-slate-400">{paper.year}</span>
                    </div>
                    <h3 className="text-sm font-bold text-foreground group-hover:text-primary transition-colors line-clamp-2">
                      {paper.title}
                    </h3>
                    <p className="text-xs text-muted-foreground line-clamp-3">
                      {paper.abstract}
                    </p>
                  </div>

                  <div className="flex items-center justify-between pt-3 border-t border-border text-[11px]">
                    <span className="text-muted-foreground truncate max-w-[150px]">
                      {Array.isArray(paper.authors) ? paper.authors.join(", ") : paper.authors}
                    </span>
                    <span className="font-bold text-primary">Read More →</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Server-Side Pagination Bar */}
        <div className="p-4 bg-white border-t border-border flex items-center justify-between">
          <button
            onClick={() => setPageNum(Math.max(1, page - 1))}
            disabled={page <= 1}
            className="px-3.5 py-1.5 text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg transition-colors disabled:opacity-40 flex items-center gap-1"
          >
            <ChevronLeft className="w-3.5 h-3.5" />
            Previous
          </button>

          <span className="text-xs font-semibold text-slate-600 font-mono">
            Page {papersData.page} of {papersData.total_pages}
          </span>

          <button
            onClick={() => setPageNum(Math.min(papersData.total_pages, page + 1))}
            disabled={page >= papersData.total_pages}
            className="px-3.5 py-1.5 text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg transition-colors disabled:opacity-40 flex items-center gap-1"
          >
            Next
            <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
}

function ChatPage({
  token,
  initialQuestion,
  onQuestionHandled
}: {
  token: string | null;
  initialQuestion?: string;
  onQuestionHandled?: () => void;
}) {
  const [sessions, setSessions] = useState<any[]>([]);
  const [activeChatId, setActiveChatId] = useState<string | null>(null);
  const [messages, setMessages] = useState<any[]>([
    {
      role: "assistant",
      content: "Hello! I'm ArXivist AI, your research assistant. How can I assist you with academic papers today?"
    }
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);

  const fetchSessions = async () => {
    if (!token) return;
    try {
      const res = await fetch('/api/chat/sessions', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const text = await res.text();
        if (text && text.trim()) {
          const data = JSON.parse(text);
          setSessions(data);
          if (data.length > 0 && !activeChatId) {
            loadSession(data[0].chat_id);
          }
        }
      }
    } catch (e) {
      console.error("Failed to load chat sessions:", e);
    }
  };

  const loadSession = async (chatId: string) => {
    if (!token) return;
    setActiveChatId(chatId);
    try {
      const res = await fetch(`/api/chat/sessions/${chatId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const text = await res.text();
        if (text && text.trim()) {
          const data = JSON.parse(text);
          setMessages(data.messages || []);
        }
      }
    } catch (e) {
      console.error("Failed to load session history:", e);
    }
  };

  const createNewSession = async () => {
    if (!token) return;
    try {
      const res = await fetch('/api/chat/sessions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ title: "New Research Chat" })
      });
      if (res.ok) {
        const text = await res.text();
        if (text && text.trim()) {
          const data = JSON.parse(text);
          setActiveChatId(data.chat_id);
          setMessages(data.messages || []);
          fetchSessions();
        }
      }
    } catch (e) {
      console.error("Failed to create new chat session:", e);
    }
  };

  const deleteSession = async (chatId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!token) return;
    try {
      const res = await fetch(`/api/chat/sessions/${chatId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        if (activeChatId === chatId) {
          setActiveChatId(null);
          setMessages([]);
        }
        fetchSessions();
      }
    } catch (err) {
      console.error("Failed to delete session:", err);
    }
  };

  useEffect(() => {
    fetchSessions();
  }, [token]);

  useEffect(() => {
    if (initialQuestion && initialQuestion.trim()) {
      sendMessage(initialQuestion);
      if (onQuestionHandled) onQuestionHandled();
    }
  }, [initialQuestion]);

  async function sendMessage(text?: string) {
    const userQuestion = text || input;
    if (!userQuestion.trim()) return;

    setMessages((prev) => [...prev, { role: "user" as const, content: userQuestion }]);
    setInput("");
    setIsTyping(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          chat_id: activeChatId,
          question: userQuestion
        })
      });
      const textRes = await response.text();
      let data: any = {};
      if (textRes && textRes.trim()) {
        try { data = JSON.parse(textRes); } catch {}
      }
      if (data.chat_id && data.chat_id !== activeChatId) {
        setActiveChatId(data.chat_id);
      }
      setMessages((prev) => [...prev, { role: "assistant" as const, content: data.answer || data.detail || "No response received." }]);
      fetchSessions();
    } catch (e) {
      setMessages((prev) => [...prev, { role: "assistant" as const, content: "Error connecting to AI backend." }]);
    } finally {
      setIsTyping(false);
    }
  }

  return (
    <div className="flex min-h-[calc(100vh-56px)] bg-background">
      {/* Chat Sessions Sidebar */}
      <aside className="hidden md:flex flex-col w-64 bg-sidebar border-r border-sidebar-border justify-between">
        <div className="flex-1 flex flex-col min-h-0">
          <div className="p-4 border-b border-sidebar-border flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-full bg-primary/20 flex items-center justify-center">
                <Sparkles className="w-3.5 h-3.5 text-primary" />
              </div>
              <p className="text-xs font-bold text-sidebar-foreground">ArXivist AI Chat</p>
            </div>
            <button
              onClick={createNewSession}
              className="p-1.5 rounded-lg bg-primary text-white hover:bg-primary/90 transition-colors"
              title="New Chat"
            >
              <Plus className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="flex-1 p-3 space-y-1 overflow-y-auto custom-scrollbar">
            <p className="text-[10px] font-bold uppercase tracking-widest text-sidebar-accent-foreground px-2 mb-2 font-mono">
              Conversations
            </p>
            {sessions.map((s) => (
              <div
                key={s.chat_id}
                onClick={() => loadSession(s.chat_id)}
                className={`group flex items-center justify-between px-3 py-2 rounded-xl text-xs cursor-pointer transition-all ${
                  activeChatId === s.chat_id
                    ? "bg-primary text-white font-semibold shadow-xs"
                    : "text-sidebar-foreground hover:bg-sidebar-accent"
                }`}
              >
                <span className="truncate pr-2">{s.title}</span>
                <button
                  onClick={(e) => deleteSession(s.chat_id, e)}
                  className="opacity-0 group-hover:opacity-100 p-1 hover:text-rose-400 transition-opacity"
                  title="Delete Chat"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              </div>
            ))}
          </div>
        </div>

        <div className="p-3 border-t border-sidebar-border">
          <button
            onClick={createNewSession}
            className="w-full flex items-center justify-center gap-2 py-2 text-xs font-bold text-primary border border-primary/30 rounded-xl hover:bg-primary/10 transition-colors"
          >
            <Plus className="w-3.5 h-3.5" />
            New Research Thread
          </button>
        </div>
      </aside>

      {/* Main Chat Conversation Window */}
      <div className="flex-1 flex flex-col min-w-0">
        <div className="bg-white border-b border-border px-5 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-emerald-400 flex items-center justify-center shrink-0">
              <Bot className="w-4 h-4 text-white" />
            </div>
            <div>
              <p className="text-sm font-bold text-foreground">ArXivist AI Assistant</p>
              <p className="text-[11px] text-emerald-600 font-mono">● Conversational Memory Active · Milvus BGE-M3</p>
            </div>
          </div>
        </div>

        {/* Message Stream */}
        <div className="flex-1 overflow-y-auto p-5 space-y-4 custom-scrollbar">
          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              {msg.role === "assistant" && (
                <div className="w-7 h-7 rounded-full bg-gradient-to-br from-primary to-emerald-400 flex items-center justify-center shrink-0 mr-2 mt-0.5">
                  <Bot className="w-3.5 h-3.5 text-white" />
                </div>
              )}
              <div
                className={`max-w-[75%] px-4 py-3 rounded-2xl text-xs leading-relaxed ${
                  msg.role === "user"
                    ? "bg-primary text-white rounded-tr-sm font-medium"
                    : "bg-white border border-border text-foreground rounded-tl-sm shadow-sm"
                }`}
              >
                {msg.role === "assistant" ? (
                  <div className="markdown-body space-y-2">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
                  </div>
                ) : (
                  msg.content
                )}
              </div>
            </div>
          ))}

          {isTyping && (
            <div className="flex justify-start">
              <div className="w-7 h-7 rounded-full bg-gradient-to-br from-primary to-emerald-400 flex items-center justify-center shrink-0 mr-2">
                <Bot className="w-3.5 h-3.5 text-white" />
              </div>
              <div className="bg-white border border-border rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm">
                <div className="flex gap-1 items-center h-4">
                  {[0, 1, 2].map((i) => (
                    <span
                      key={i}
                      className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce"
                      style={{ animationDelay: `${i * 0.15}s` }}
                    />
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Input Box */}
        <div className="p-4 bg-white border-t border-border">
          <div className="flex items-center gap-2 max-w-4xl mx-auto">
            <input
              type="text"
              placeholder="Ask a question about research papers..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter') sendMessage(); }}
              className="flex-1 px-4 py-2.5 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:border-primary focus:bg-white outline-none transition-all"
            />
            <button
              onClick={() => sendMessage()}
              disabled={isTyping || !input.trim()}
              className="px-4 py-2.5 bg-primary hover:bg-primary/90 text-white font-bold text-xs rounded-xl shadow-md transition-all disabled:opacity-50 flex items-center gap-1.5"
            >
              <Sparkles className="w-3.5 h-3.5" />
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

class ErrorBoundary extends React.Component<{children: React.ReactNode}, {hasError: boolean, error: any}> {
  constructor(props: {children: React.ReactNode}) { super(props); this.state = { hasError: false, error: null }; }
  static getDerivedStateFromError(error: any) { return { hasError: true, error }; }
  componentDidCatch(error: any, errorInfo: any) { console.error("ErrorBoundary caught an error", error, errorInfo); }
  render() {
    if (this.state.hasError) {
      return <div style={{padding: '2rem', color: 'red'}}><h1>Something went wrong.</h1><pre>{this.state.error?.toString()}</pre></div>;
    }
    return this.props.children;
  }
}

export default function App() {
  return (
    <ErrorBoundary>
      <AppContent />
    </ErrorBoundary>
  );
}

function AppContent() {
  const [page, setPage] = useState<Page>("landing");
  const [navSearch, setNavSearch] = useState("");
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [activeCategory, setActiveCategory] = useState("All");
  const [activeYear, setActiveYear] = useState("All");
  const [selectedPaperModal, setSelectedPaperModal] = useState<any | null>(null);
  const [promptPaperContext, setPromptPaperContext] = useState<string>("");

  const handleLogin = (newToken: string) => {
    localStorage.setItem('token', newToken);
    setToken(newToken);
    setPage("landing");
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
    if (page === "chat") setPage("landing");
  };

  const handleAskAIAboutPaper = (paper: any) => {
    const question = `Can you explain the main findings and methodology of the paper "${paper.title}"?`;
    setPromptPaperContext(question);
    if (!token) {
      setPage("login");
    } else {
      setPage("chat");
    }
  };

  return (
    <div className="min-h-screen bg-background font-sans">
      {page !== "login" && page !== "signup" && (
        <TopNav
          currentPage={page}
          setPage={(p) => { if (p === "chat" && !token) setPage("login"); else setPage(p); }}
          searchQuery={navSearch}
          setSearchQuery={setNavSearch}
          openAuth={(mode) => setPage(mode)}
          isLoggedIn={!!token}
          handleLogout={handleLogout}
        />
      )}

      {page === "landing" && (
        <LandingPage
          setPage={setPage}
          isLoggedIn={!!token}
          openAuth={(mode) => setPage(mode)}
          totalPapers={17909}
          onCategorySelect={(cat) => setActiveCategory(cat)}
          onPaperSelect={(paper) => setSelectedPaperModal(paper)}
        />
      )}

      {page === "browse" && (
        <BrowsePage
          category={activeCategory}
          onCategorySelect={(cat) => setActiveCategory(cat)}
          year={activeYear}
          onYearSelect={(y) => setActiveYear(y)}
          onPaperSelect={(paper) => setSelectedPaperModal(paper)}
        />
      )}

      {page === "chat" && (
        <ChatPage
          token={token}
          initialQuestion={promptPaperContext}
          onQuestionHandled={() => setPromptPaperContext("")}
        />
      )}

      {page === "admin" && <AdminPanel />}
      {page === "login" && <AuthPage initialMode="login" onLoginSuccess={handleLogin} />}
      {page === "signup" && <AuthPage initialMode="signup" onLoginSuccess={handleLogin} />}

      <PaperDetailsModal
        paper={selectedPaperModal}
        onClose={() => setSelectedPaperModal(null)}
        onAskAI={handleAskAIAboutPaper}
      />
    </div>
  );
}
