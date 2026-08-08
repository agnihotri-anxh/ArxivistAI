import React, { useState, useMemo, useEffect } from "react";
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  Search,
  Bell,
  Download,
  User,
  ChevronDown,
  Bot,
  ArrowRight,
  BookOpen,
  TrendingUp,
  Filter,
  X,
  Send,
  RotateCcw,
  ExternalLink,
  Calendar,
  Tag,
  Users,
  Star,
  ChevronRight,
  Menu,
  Sparkles,
  FileText,
  Layers,
} from "lucide-react";
import researchLogoSvg from "@/imports/logo.svg";
import { ImageWithFallback } from "@/app/components/figma/ImageWithFallback";
import { AuthPage } from "@/app/components/AuthPage";
import { AdminPanel } from "@/app/components/AdminPanel";
import { getCategoryBadgeStyle } from "@/app/utils/categories";

type Page = "landing" | "browse" | "chat" | "login" | "signup" | "admin";

const CHAT_HISTORY = [
  {
    role: "assistant" as const,
    content:
      "Hello! I'm Arxvist AI, your research assistant. I can help you find papers, summarize findings, explain concepts, or discuss the latest research trends. What would you like to explore today?",
  },
];

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
    </div>
  );
}

function CategoryBadge({ category }: { category: string }) {
  const badgeStyle = getCategoryBadgeStyle(category);
  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-md text-[11px] font-medium border ${badgeStyle} shadow-2xs transition-colors`}
      style={{ fontFamily: "'Inter', sans-serif" }}
    >
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
  handleLogout
}: {
  currentPage: Page;
  setPage: (p: Page) => void;
  searchQuery: string;
  setSearchQuery: (q: string) => void;
  openAuth: (mode: 'login'|'signup') => void;
  isLoggedIn: boolean;
  handleLogout: () => void;
}) {
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showResearchMenu, setShowResearchMenu] = useState(false);

  return (
    <header className="sticky top-0 z-50 bg-white border-b border-border shadow-sm">
      <div className="flex items-center justify-between h-14 px-4 gap-3 max-w-[1600px] mx-auto">
        {/* Logo */}
        <div className="flex items-center flex-1">
          <button onClick={() => setPage("landing")} className="shrink-0">
            <Logo />
          </button>
        </div>

        {/* Search */}
        <div className="flex-1 max-w-xl w-full">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search papers, authors, topics..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                if (e.target.value && currentPage === "landing") setPage("browse");
              }}
              onKeyDown={(e) => {
                if (e.key === "Enter" && searchQuery) setPage("browse");
              }}
              className="w-full pl-9 pr-4 py-2 text-sm bg-muted rounded-lg border border-transparent focus:border-primary focus:bg-white outline-none transition-all"
              style={{ fontFamily: "'Inter', sans-serif" }}
            />
          </div>
        </div>

        {/* Right side: Nav links & Buttons */}
        <div className="flex items-center justify-end flex-1 gap-4">
          <nav className="hidden md:flex items-center gap-4">
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

          {/* Research dropdown */}
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
                {["Trending", "New Releases", "Top Cited", "Bookmarked"].map((item) => (
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

          {/* AI Chat button */}
          <button
            onClick={() => { if (!isLoggedIn) openAuth('login'); else setPage("chat"); }}
            className={`hidden sm:flex items-center gap-2 px-3 py-1.5 text-sm rounded-lg font-medium transition-all ${
              currentPage === "chat"
                ? "bg-primary text-white shadow-md shadow-primary/30"
                : "bg-gradient-to-r from-primary to-emerald-400 text-white hover:shadow-md hover:shadow-primary/30"
            }`}
            style={{ fontFamily: "'Inter', sans-serif" }}
          >
            <Sparkles className="w-3.5 h-3.5" />
            Arxvist AI
          </button>

          {/* Icons */}
          <button className="relative p-2 rounded-lg hover:bg-muted transition-colors text-muted-foreground hover:text-foreground">
            <Bell className="w-4.5 h-4.5" />
            <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 bg-primary rounded-full" />
          </button>

          {/* User */}
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
                    <button onClick={handleLogout} className="w-full py-1.5 text-xs font-medium border border-red-500 text-red-500 rounded-lg hover:bg-red-50 transition-colors">
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
    </header>
  );
}

function LandingPage({
  setPage,
  isLoggedIn,
  openAuth,
  totalPapers,
  totalCategories,
  categories,
  papers,
}: {
  setPage: (p: Page) => void;
  isLoggedIn: boolean;
  openAuth: (mode: 'login'|'signup') => void;
  totalPapers: number;
  totalCategories: number;
  categories: string[];
  papers: any[];
}) {
  const topPapers = papers.slice(0, 4);

  return (
    <div className="min-h-screen bg-background">
      {/* Hero */}
      <section className="relative bg-secondary overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <div
            className="absolute inset-0"
            style={{
              backgroundImage:
                "radial-gradient(circle at 20% 50%, #16a34a 0%, transparent 50%), radial-gradient(circle at 80% 20%, #0ea5e9 0%, transparent 40%)",
            }}
          />
        </div>
        <div className="relative max-w-[1600px] mx-auto px-6 py-16 md:py-24">
          <div className="max-w-2xl">
            <div
              className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/20 text-primary text-xs font-medium mb-6"
              style={{ fontFamily: "'JetBrains Mono', monospace" }}
            >
              <span className="w-1.5 h-1.5 bg-primary rounded-full animate-pulse" />
              2,847 papers added this week
            </div>
            <h1
              className="text-4xl md:text-5xl font-normal text-white leading-tight mb-4"
              style={{ fontFamily: "'Crimson Text', serif" }}
            >
              The world's research,
              <br />
              <em className="text-primary">intelligently organized.</em>
            </h1>
            <p
              className="text-slate-400 text-lg leading-relaxed mb-8"
              style={{ fontFamily: "'Inter', sans-serif" }}
            >
              Browse, search, and discuss 1.2M+ academic papers across every
              discipline. Powered by Arxvist AI for intelligent discovery.
            </p>
            <div className="flex flex-wrap gap-3">
              <button
                onClick={() => setPage("browse")}
                className="flex items-center gap-2 px-5 py-2.5 bg-primary text-white rounded-lg font-medium hover:bg-primary/90 transition-colors"
              >
                Browse Papers
                <ArrowRight className="w-4 h-4" />
              </button>
              <button
                onClick={() => { if (!isLoggedIn) openAuth('login'); else setPage("chat"); }}
                className="flex items-center gap-2 px-5 py-2.5 bg-white/10 text-white rounded-lg font-medium hover:bg-white/20 transition-colors border border-white/20"
              >
                <Bot className="w-4 h-4" />
                Ask Arxvist AI
              </button>
            </div>
          </div>
        </div>

        {/* Stats bar */}
        <div className="border-t border-white/10">
          <div className="max-w-[1600px] mx-auto px-6 py-4 flex flex-wrap gap-6">
            {[
              { label: "Total Papers Indexed", value: totalPapers > 0 ? totalPapers.toLocaleString() : "..." },
              { label: "Research Categories", value: totalCategories > 0 ? totalCategories.toLocaleString() : "..." },
            ].map((stat) => (
              <div key={stat.label}>
                <span
                  className="text-white font-semibold text-lg"
                  style={{ fontFamily: "'Crimson Text', serif" }}
                >
                  {stat.value}
                </span>
                <span
                  className="text-slate-500 text-xs ml-2"
                  style={{ fontFamily: "'JetBrains Mono', monospace" }}
                >
                  {stat.label}
                </span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Main content: sidebar + papers */}
      <div className="max-w-[1600px] mx-auto px-4 py-8 flex gap-6">
        {/* Sidebar */}
        <aside className="hidden lg:block w-56 shrink-0">
          <div className="sticky top-20 space-y-6">
            <div>
              <p
                className="text-[11px] font-medium uppercase tracking-widest text-muted-foreground mb-2 px-2"
                style={{ fontFamily: "'JetBrains Mono', monospace" }}
              >
                Quick Access
              </p>
              <nav className="space-y-0.5">
                {[
                  { icon: TrendingUp, label: "Trending Now" },
                  { icon: Star, label: "Most Cited" },
                  { icon: BookOpen, label: "New Releases" },
                  { icon: Users, label: "Following" },
                  { icon: Download, label: "My Library" },
                ].map(({ icon: Icon, label }) => (
                  <button
                    key={label}
                    onClick={() => setPage("browse")}
                    className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm text-muted-foreground hover:text-foreground hover:bg-white transition-colors group"
                  >
                    <Icon className="w-4 h-4 group-hover:text-primary transition-colors" />
                    {label}
                  </button>
                ))}
              </nav>
            </div>

            <div>
              <p
                className="text-[11px] font-medium uppercase tracking-widest text-muted-foreground mb-2 px-2"
                style={{ fontFamily: "'JetBrains Mono', monospace" }}
              >
                Categories
              </p>
              <nav className="space-y-0.5">
                {categories.slice(1, 8).map((cat) => (
                  <button
                    key={cat}
                    onClick={() => setPage("browse")}
                    className="w-full flex items-center justify-between px-3 py-1.5 rounded-lg text-sm text-muted-foreground hover:text-foreground hover:bg-white transition-colors group"
                  >
                    <span>{cat}</span>
                    <ChevronRight className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </button>
                ))}
              </nav>
            </div>

            <div className="bg-gradient-to-br from-primary/10 to-emerald-50 rounded-xl p-4 border border-primary/20">
              <Sparkles className="w-5 h-5 text-primary mb-2" />
              <p className="text-sm font-medium text-foreground mb-1">Try Arxvist AI</p>
              <p className="text-xs text-muted-foreground mb-3">
                Ask questions, get summaries, explore trends
              </p>
              <button
                onClick={() => setPage("chat")}
                className="w-full py-1.5 text-sm bg-primary text-white rounded-lg font-medium hover:bg-primary/90 transition-colors"
              >
                Start Chat
              </button>
            </div>
          </div>
        </aside>

        {/* Content */}
        <main className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-5">
            <h2
              className="text-2xl text-foreground font-normal"
              style={{ fontFamily: "'Crimson Text', serif" }}
            >
              Latest Stories
            </h2>
            <button
              onClick={() => setPage("browse")}
              className="flex items-center gap-1 text-sm text-primary hover:text-primary/80 transition-colors font-medium"
            >
              View all <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          {topPapers.length > 0 && (
            <>
              {/* Featured paper */}
              <div
                className="relative bg-white rounded-xl overflow-hidden border border-border mb-5 hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => setPage("browse")}
              >
                <div className="flex flex-col md:flex-row">
                  <div className="p-5 flex-1">
                    <div className="flex items-center gap-2 mb-3">
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-primary text-white text-[11px] font-medium rounded">
                        <TrendingUp className="w-3 h-3" />
                        Featured
                      </span>
                      <CategoryBadge category={topPapers[0].category} />
                      <span
                        className="text-[11px] text-muted-foreground"
                        style={{ fontFamily: "'JetBrains Mono', monospace" }}
                      >
                        {topPapers[0].venue || "Arxvist"}
                      </span>
                    </div>
                    <h3
                      className="text-xl font-normal text-foreground mb-2 leading-snug"
                      style={{ fontFamily: "'Crimson Text', serif" }}
                    >
                      {topPapers[0].title}
                    </h3>
                    <p className="text-sm text-muted-foreground leading-relaxed mb-3 line-clamp-2">
                      {topPapers[0].abstract || "No abstract available."}
                    </p>
                    <div className="flex items-center gap-4 text-xs text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <Users className="w-3.5 h-3.5" />
                        {topPapers[0].authors.join(", ")}
                      </span>
                      <span className="flex items-center gap-1">
                        <Calendar className="w-3.5 h-3.5" />
                        {topPapers[0].year}
                      </span>
                    </div>
                  </div>
                  <div className="w-full md:w-52 bg-gradient-to-br from-secondary to-slate-800 flex items-center justify-center p-8 shrink-0">
                    <FileText className="w-16 h-16 text-white/20" />
                  </div>
                </div>
              </div>

              {/* Paper cards grid */}
              <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {topPapers.slice(1).map((paper) => (
                  <article
                    key={paper.id}
                    className="bg-white rounded-xl border border-border p-4 hover:shadow-md transition-all cursor-pointer hover:border-primary/30 group"
                    onClick={() => setPage("browse")}
                  >
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <CategoryBadge category={paper.category} />
                      <ExternalLink className="w-3.5 h-3.5 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity shrink-0 mt-0.5" />
                    </div>
                    <h4
                      className="text-base font-normal text-foreground leading-snug mb-2 group-hover:text-primary transition-colors"
                      style={{ fontFamily: "'Crimson Text', serif" }}
                    >
                      {paper.title}
                    </h4>
                    <p className="text-xs text-muted-foreground leading-relaxed mb-3 line-clamp-2">
                      {paper.abstract || "No abstract available."}
                    </p>
                    <div className="flex items-center justify-between text-xs text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <Users className="w-3.5 h-3.5" />
                        {paper.authors[0]} {paper.authors.length > 1 && "et al."}
                      </span>
                      <span style={{ fontFamily: "'JetBrains Mono', monospace" }}>{paper.year}</span>
                    </div>
                  </article>
                ))}
              </div>
            </>
          )}

          {/* Section: More papers */}
          <div className="mt-8">
            <h2
              className="text-2xl text-foreground font-normal mb-5"
              style={{ fontFamily: "'Crimson Text', serif" }}
            >
              From the Archives
            </h2>
            <div className="space-y-3">
              {papers.slice(4, 10).map((paper) => (
                <article
                  key={paper.id}
                  className="bg-white rounded-xl border border-border p-4 hover:shadow-sm transition-all cursor-pointer flex gap-4 group"
                  onClick={() => setPage("browse")}
                >
                  <div className="w-1 bg-primary/20 rounded-full shrink-0 group-hover:bg-primary transition-colors" />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1.5">
                      <CategoryBadge category={paper.category} />
                      <span
                        className="text-[11px] text-muted-foreground"
                        style={{ fontFamily: "'JetBrains Mono', monospace" }}
                      >
                        {paper.venue || "Arxvist"}
                      </span>
                    </div>
                    <h4
                      className="text-base font-normal text-foreground leading-snug mb-1 group-hover:text-primary transition-colors"
                      style={{ fontFamily: "'Crimson Text', serif" }}
                    >
                      {paper.title}
                    </h4>
                    <p className="text-xs text-muted-foreground line-clamp-1">{paper.abstract || "No abstract available."}</p>
                    <div className="flex items-center gap-4 mt-1.5 text-xs text-muted-foreground">
                      <span>{paper.authors[0]}{paper.authors.length > 1 ? ` + ${paper.authors.length - 1}` : ""}</span>
                      <span>{paper.year}</span>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          </div>
        </main>

        {/* Right sidebar */}
        <aside className="hidden xl:block w-60 shrink-0">
          <div className="sticky top-20 space-y-5">
            <div className="bg-secondary text-white rounded-xl p-5">
              <p
                className="text-xs font-medium text-slate-400 uppercase tracking-widest mb-2"
                style={{ fontFamily: "'JetBrains Mono', monospace" }}
              >
                Arxvist AI
              </p>
              <p
                className="text-lg font-normal mb-3 leading-snug"
                style={{ fontFamily: "'Crimson Text', serif" }}
              >
                The trust you know. The tech you need.
              </p>
              <p className="text-xs text-slate-400 mb-4">
                10+ years of academic research access, now with AI-powered discovery.
              </p>
              <button
                onClick={() => setPage("chat")}
                className="w-full py-2 bg-primary text-white text-sm font-medium rounded-lg hover:bg-primary/90 transition-colors"
              >
                Know more →
              </button>
            </div>

            <div className="bg-white rounded-xl border border-border p-4">
              <p
                className="text-[11px] font-medium uppercase tracking-widest text-muted-foreground mb-3"
                style={{ fontFamily: "'JetBrains Mono', monospace" }}
              >
                Tools
              </p>
              <div className="grid grid-cols-3 gap-2">
                {[
                  { icon: Search, label: "Search" },
                  { icon: Layers, label: "Compare" },
                  { icon: Download, label: "Export" },
                  { icon: Users, label: "Collab" },
                  { icon: Tag, label: "Tags" },
                  { icon: BookOpen, label: "Read" },
                ].map(({ icon: Icon, label }) => (
                  <button
                    key={label}
                    className="flex flex-col items-center gap-1 p-2 rounded-lg hover:bg-muted transition-colors group"
                  >
                    <Icon className="w-4 h-4 text-muted-foreground group-hover:text-primary transition-colors" />
                    <span className="text-[10px] text-muted-foreground">{label}</span>
                  </button>
                ))}
              </div>
            </div>

            <div className="bg-white rounded-xl border border-border p-4">
              <p
                className="text-[11px] font-medium uppercase tracking-widest text-muted-foreground mb-3"
                style={{ fontFamily: "'JetBrains Mono', monospace" }}
              >
                Trending Tags
              </p>
              <div className="flex flex-wrap gap-1.5">
                {["LLM", "diffusion", "alignment", "RLHF", "scaling", "transformers", "RAG", "agents"].map(
                  (tag) => (
                    <button
                      key={tag}
                      className="px-2 py-0.5 text-[11px] bg-muted hover:bg-accent text-muted-foreground hover:text-primary rounded transition-colors"
                      style={{ fontFamily: "'JetBrains Mono', monospace" }}
                    >
                      #{tag}
                    </button>
                  )
                )}
              </div>
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}

function BrowsePage({ papers, categories, years }: { papers: any[], categories: string[], years: string[] }) {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [selectedYear, setSelectedYear] = useState("All");
  const [showFilters, setShowFilters] = useState(false);

  const categoryCounts = useMemo(() => {
    const counts: Record<string, number> = {};
    papers.forEach((p) => {
      if (p.category) {
        counts[p.category] = (counts[p.category] || 0) + 1;
      }
    });
    return counts;
  }, [papers]);

  const filtered = useMemo(() => {
    return papers.filter((p) => {
      const matchesSearch =
        !searchQuery ||
        p.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        p.authors.some((a: string) => a.toLowerCase().includes(searchQuery.toLowerCase())) ||
        p.abstract.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (p.tags && p.tags.some((t: string) => t.toLowerCase().includes(searchQuery.toLowerCase())));
      const matchesCat = selectedCategory === "All" || p.category === selectedCategory;
      const matchesYear = selectedYear === "All" || p.year === selectedYear;
      return matchesSearch && matchesCat && matchesYear;
    });
  }, [papers, searchQuery, selectedCategory, selectedYear]);

  return (
    <div className="flex min-h-[calc(100vh-56px)]">
      {/* Filter sidebar */}
      <aside
        className={`${showFilters ? "block" : "hidden"} md:block w-64 shrink-0 bg-sidebar border-r border-sidebar-border`}
      >
        <div className="sticky top-14 max-h-[calc(100vh-56px)] overflow-y-auto p-4 space-y-6">
          <div className="flex items-center justify-between">
            <p
              className="text-[11px] font-medium uppercase tracking-widest text-sidebar-accent-foreground"
              style={{ fontFamily: "'JetBrains Mono', monospace" }}
            >
              Filters
            </p>
            <button
              onClick={() => {
                setSelectedCategory("All");
                setSelectedYear("All");
              }}
              className="text-[11px] text-primary hover:underline"
            >
              Reset
            </button>
          </div>

          <div>
            <p
              className="text-[11px] font-medium uppercase tracking-widest text-sidebar-accent-foreground mb-2"
              style={{ fontFamily: "'JetBrains Mono', monospace" }}
            >
              Category
            </p>
            <div className="space-y-0.5">
              {categories.map((cat) => {
                const count = cat === "All" ? papers.length : (categoryCounts[cat] || 0);
                return (
                  <button
                    key={cat}
                    onClick={() => setSelectedCategory(cat)}
                    className={`w-full flex items-center justify-between px-3 py-1.5 rounded-lg text-xs transition-colors ${
                      selectedCategory === cat
                        ? "bg-primary text-white font-medium shadow-xs"
                        : "text-sidebar-foreground hover:bg-sidebar-accent"
                    }`}
                  >
                    <span className="truncate pr-2 text-left">{cat}</span>
                    <span
                      className={`text-[10px] px-1.5 py-0.2 rounded-full shrink-0 ${
                        selectedCategory === cat
                          ? "bg-white/20 text-white"
                          : "bg-sidebar-accent text-sidebar-accent-foreground"
                      }`}
                    >
                      {count}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>

          <div>
            <p
              className="text-[11px] font-medium uppercase tracking-widest text-sidebar-accent-foreground mb-2"
              style={{ fontFamily: "'JetBrains Mono', monospace" }}
            >
              Year
            </p>
            <div className="space-y-0.5">
              {years.map((year) => (
                <button
                  key={year}
                  onClick={() => setSelectedYear(year)}
                  className={`w-full text-left px-3 py-1.5 rounded-lg text-sm transition-colors ${
                    selectedYear === year
                      ? "bg-primary text-white"
                      : "text-sidebar-foreground hover:bg-sidebar-accent"
                  }`}
                >
                  {year}
                </button>
              ))}
            </div>
          </div>

        </div>
      </aside>

      {/* Main table area */}
      <div className="flex-1 min-w-0 bg-background">
        {/* Table header / search bar */}
        <div className="sticky top-14 z-40 bg-white border-b border-border px-5 py-3 flex items-center gap-3">
          <button
            className="md:hidden p-1.5 rounded-lg hover:bg-muted transition-colors"
            onClick={() => setShowFilters(!showFilters)}
          >
            <Filter className="w-4 h-4 text-muted-foreground" />
          </button>
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search within results..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-1.5 text-sm bg-muted rounded-lg border border-transparent focus:border-primary focus:bg-white outline-none transition-all"
            />
          </div>
          <span
            className="text-sm text-muted-foreground ml-auto"
            style={{ fontFamily: "'JetBrains Mono', monospace" }}
          >
            {filtered.length} results
          </span>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr className="border-b border-border bg-muted/50">
                <th className="text-left px-5 py-3 text-[11px] font-medium uppercase tracking-widest text-muted-foreground w-[45%]"
                  style={{ fontFamily: "'JetBrains Mono', monospace" }}>
                  Paper
                </th>
                <th className="text-left px-4 py-3 text-[11px] font-medium uppercase tracking-widest text-muted-foreground hidden lg:table-cell"
                  style={{ fontFamily: "'JetBrains Mono', monospace" }}>
                  Venue
                </th>
                <th className="text-left px-4 py-3 text-[11px] font-medium uppercase tracking-widest text-muted-foreground"
                  style={{ fontFamily: "'JetBrains Mono', monospace" }}>
                  Category
                </th>
                <th className="text-right px-5 py-3 text-[11px] font-medium uppercase tracking-widest text-muted-foreground hidden sm:table-cell"
                  style={{ fontFamily: "'JetBrains Mono', monospace" }}>
                  Year
                </th>
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={4} className="text-center py-16 text-muted-foreground text-sm">
                    No papers match your filters.
                  </td>
                </tr>
              ) : (
                filtered.map((paper, i) => (
                  <tr
                    key={paper.id}
                    className="border-b border-border hover:bg-white transition-colors cursor-pointer group"
                    onClick={() => window.open(`/api/pdfs/${paper.id}.pdf`, '_blank')}
                  >
                    <td className="px-5 py-4">
                      <div className="flex items-start gap-3">
                        <span
                          className="text-muted-foreground text-[11px] tabular-nums mt-0.5 shrink-0"
                          style={{ fontFamily: "'JetBrains Mono', monospace" }}
                        >
                          {String(i + 1).padStart(2, "0")}
                        </span>
                        <div className="min-w-0">
                          <p
                            className="font-normal text-foreground text-[15px] leading-snug mb-1 group-hover:text-primary transition-colors"
                            style={{ fontFamily: "'Crimson Text', serif" }}
                          >
                            {paper.title}
                          </p>
                          <p className="text-xs text-muted-foreground truncate">
                            {paper.authors.join(", ")}
                          </p>
                          <div className="flex flex-wrap gap-1 mt-1.5">
                            {paper.tags.map((tag) => (
                              <span
                                key={tag}
                                className="px-1.5 py-0.5 text-[10px] bg-muted text-muted-foreground rounded"
                                style={{ fontFamily: "'JetBrains Mono', monospace" }}
                              >
                                #{tag}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-4 hidden lg:table-cell">
                      <span className="text-xs text-muted-foreground">{paper.venue}</span>
                    </td>
                    <td className="px-4 py-4">
                      <CategoryBadge category={paper.category} />
                    </td>
                    <td className="px-5 py-4 text-right hidden sm:table-cell">
                      <div className="flex flex-col items-end gap-2">
                        <span
                          className="text-xs text-muted-foreground"
                          style={{ fontFamily: "'JetBrains Mono', monospace" }}
                        >
                          {paper.year}
                        </span>
                        <button 
                          className="opacity-0 group-hover:opacity-100 transition-opacity text-xs bg-primary/10 text-primary px-2 py-1 rounded-md font-medium flex items-center gap-1"
                          onClick={(e) => { e.stopPropagation(); window.open(`/api/pdfs/${paper.id}.pdf`, '_blank'); }}
                        >
                          <FileText className="w-3 h-3" /> Read PDF
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function ChatPage({ token }: { token: string | null }) {
  const [messages, setMessages] = useState(CHAT_HISTORY);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);

  const SAMPLE_QUESTIONS = [
    "What are the latest breakthroughs in LLM alignment?",
    "Summarize the key findings in scaling law research",
    "Find papers on diffusion models for 3D generation",
    "Compare RLHF vs Constitutional AI approaches",
  ];

  async function sendMessage(text?: string) {
    const msg = text || input;
    if (!msg.trim()) return;
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
        body: JSON.stringify({ question: userQuestion })
      });
      const text = await response.text();
      let data: any = {};
      if (text && text.trim()) {
        try { data = JSON.parse(text); } catch {}
      }
      setMessages((prev) => [...prev, { role: "assistant" as const, content: data.answer || data.detail || "No response received." }]);
    } catch (e) {
      setMessages((prev) => [...prev, { role: "assistant" as const, content: "Error connecting to AI backend." }]);
    } finally {
      setIsTyping(false);
    }
  }

  return (
    <div className="flex min-h-[calc(100vh-56px)] bg-background">
      {/* Chat sidebar */}
      <aside className="hidden md:flex flex-col w-60 bg-sidebar border-r border-sidebar-border">
        <div className="p-4 border-b border-sidebar-border">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-full bg-primary/20 flex items-center justify-center">
              <Sparkles className="w-3.5 h-3.5 text-primary" />
            </div>
            <div>
              <p className="text-sm font-medium text-sidebar-foreground">Arxvist AI</p>
              <p
                className="text-[10px] text-sidebar-accent-foreground"
                style={{ fontFamily: "'JetBrains Mono', monospace" }}
              >
                Research Assistant
              </p>
            </div>
          </div>
        </div>
        <div className="flex-1 p-3 space-y-1 overflow-y-auto">
          <p
            className="text-[10px] font-medium uppercase tracking-widest text-sidebar-accent-foreground px-2 mb-2"
            style={{ fontFamily: "'JetBrains Mono', monospace" }}
          >
            Recent Chats
          </p>
          {[
            "Scaling laws for LLMs",
            "Diffusion model survey",
            "Post-quantum crypto",
            "Protein folding review",
          ].map((chat) => (
            <button
              key={chat}
              className="w-full text-left px-3 py-2 rounded-lg text-sm text-sidebar-foreground hover:bg-sidebar-accent transition-colors truncate"
            >
              {chat}
            </button>
          ))}
        </div>
        <div className="p-3 border-t border-sidebar-border">
          <button
            onClick={() => setMessages(CHAT_HISTORY)}
            className="w-full flex items-center gap-2 px-3 py-2 text-sm text-sidebar-foreground hover:bg-sidebar-accent rounded-lg transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            New Chat
          </button>
        </div>
      </aside>

      {/* Chat main */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Chat header */}
        <div className="bg-white border-b border-border px-5 py-3 flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-emerald-400 flex items-center justify-center shrink-0">
            <Bot className="w-4 h-4 text-white" />
          </div>
          <div>
            <p className="text-sm font-semibold text-foreground">Arxvist AI</p>
            <p
              className="text-[11px] text-primary"
              style={{ fontFamily: "'JetBrains Mono', monospace" }}
            >
              ● Online · 1.2M papers indexed
            </p>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-5 space-y-4">
          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              {msg.role === "assistant" && (
                <div className="w-7 h-7 rounded-full bg-gradient-to-br from-primary to-emerald-400 flex items-center justify-center shrink-0 mr-2 mt-0.5">
                  <Bot className="w-3.5 h-3.5 text-white" />
                </div>
              )}
              <div
                className={`max-w-[70%] px-4 py-3 rounded-2xl text-sm leading-relaxed ${
                  msg.role === "user"
                    ? "bg-primary text-white rounded-tr-sm"
                    : "bg-white border border-border text-foreground rounded-tl-sm shadow-sm"
                }`}
                style={{ fontFamily: "'Inter', sans-serif" }}
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
                      className="w-1.5 h-1.5 bg-muted-foreground rounded-full animate-bounce"
                      style={{ animationDelay: `${i * 0.15}s` }}
                    />
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Suggested questions */}
        {messages.length <= 1 && (
          <div className="px-5 pb-3 flex flex-wrap gap-2">
            {SAMPLE_QUESTIONS.map((q) => (
              <button
                key={q}
                onClick={() => sendMessage(q)}
                className="px-3 py-1.5 text-xs border border-border rounded-full text-muted-foreground hover:border-primary hover:text-primary hover:bg-accent transition-colors"
              >
                {q}
              </button>
            ))}
          </div>
        )}

        {/* Input */}
        <div className="bg-white border-t border-border p-4">
          <div className="flex items-center gap-3 bg-muted rounded-xl px-4 py-2.5 focus-within:ring-2 focus-within:ring-primary/30 transition-shadow">
            <input
              type="text"
              placeholder="Ask about any paper, topic, or research area..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
              className="flex-1 bg-transparent text-sm outline-none text-foreground placeholder:text-muted-foreground"
              style={{ fontFamily: "'Inter', sans-serif" }}
            />
            <button
              onClick={() => sendMessage()}
              disabled={!input.trim()}
              className="p-1.5 rounded-lg bg-primary text-white hover:bg-primary/90 transition-colors disabled:opacity-40 disabled:cursor-not-allowed shrink-0"
            >
              <Send className="w-3.5 h-3.5" />
            </button>
          </div>
          <p
            className="text-[10px] text-muted-foreground text-center mt-2"
            style={{ fontFamily: "'JetBrains Mono', monospace" }}
          >
            Arxvist AI can make mistakes. Verify critical information.
          </p>
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
      return <div style={{padding: '2rem', color: 'red'}}><h1>Something went wrong.</h1><pre>{this.state.error?.toString()}</pre><pre>{this.state.error?.stack}</pre></div>;
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

  const [papers, setPapers] = useState<any[]>([]);
  useEffect(() => {
    fetch('/api/papers')
      .then(async (res) => {
        if (!res.ok) return [];
        const text = await res.text();
        return text && text.trim() ? JSON.parse(text) : [];
      })
      .then(data => {
        if (Array.isArray(data) && data.length > 0) setPapers(data);
      })
      .catch(err => console.error("Failed to fetch papers:", err));
  }, []);

  const categories = useMemo(() => ["All", ...new Set(papers.map((p) => p.category))], [papers]);
  const years = useMemo(() => ["All", ...new Set(papers.map((p) => p.year))], [papers]);

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

  return (
    <div className="min-h-screen bg-background" style={{ fontFamily: "'Inter', sans-serif" }}>
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
      {page === "landing" && <LandingPage setPage={setPage} isLoggedIn={!!token} openAuth={(mode) => setPage(mode)} totalPapers={papers.length} totalCategories={categories.length - 1} categories={categories} papers={papers} />}
      {page === "browse" && <BrowsePage papers={papers} categories={categories} years={years} />}
      {page === "chat" && <ChatPage token={token} />}
      {page === "admin" && <AdminPanel />}
      {page === "login" && <AuthPage initialMode="login" onLoginSuccess={handleLogin} />}
      {page === "signup" && <AuthPage initialMode="signup" onLoginSuccess={handleLogin} />}
    </div>
  );
}
