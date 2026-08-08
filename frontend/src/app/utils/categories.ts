export const CATEGORY_COLORS: Record<string, string> = {
  "Artificial Intelligence": "bg-emerald-100 text-emerald-800 border-emerald-200",
  "Natural Language Processing": "bg-blue-100 text-blue-800 border-blue-200",
  "Machine Learning": "bg-violet-100 text-violet-800 border-violet-200",
  "Machine Learning (Stats)": "bg-purple-100 text-purple-800 border-purple-200",
  "Computer Vision": "bg-indigo-100 text-indigo-800 border-indigo-200",
  "Information Retrieval": "bg-teal-100 text-teal-800 border-teal-200",
  "Robotics": "bg-orange-100 text-orange-800 border-orange-200",
  "Software Engineering": "bg-cyan-100 text-cyan-800 border-cyan-200",
  "Cryptography & Security": "bg-slate-100 text-slate-800 border-slate-200",
  "Neural & Evolutionary Computing": "bg-amber-100 text-amber-800 border-amber-200",
  "Databases & Data Management": "bg-rose-100 text-rose-800 border-rose-200",
  "Human-Computer Interaction": "bg-pink-100 text-pink-800 border-pink-200",
  "Quantum Physics": "bg-sky-100 text-sky-800 border-sky-200",
  "Image & Video Processing": "bg-indigo-100 text-indigo-800 border-indigo-200",
  "Optimization & Control": "bg-emerald-100 text-emerald-800 border-emerald-200",
  "Numerical Analysis": "bg-amber-100 text-amber-800 border-amber-200",
  "Applied Statistics": "bg-yellow-100 text-yellow-800 border-yellow-200",
};

export function getCategoryBadgeStyle(category: string): string {
  if (CATEGORY_COLORS[category]) {
    return CATEGORY_COLORS[category];
  }
  
  // Dynamic color selection based on string hash for missing explicitly defined categories
  const colorPool = [
    "bg-emerald-100 text-emerald-800 border-emerald-200",
    "bg-blue-100 text-blue-800 border-blue-200",
    "bg-violet-100 text-violet-800 border-violet-200",
    "bg-amber-100 text-amber-800 border-amber-200",
    "bg-teal-100 text-teal-800 border-teal-200",
    "bg-indigo-100 text-indigo-800 border-indigo-200",
    "bg-rose-100 text-rose-800 border-rose-200",
    "bg-sky-100 text-sky-800 border-sky-200",
  ];
  
  let hash = 0;
  for (let i = 0; i < category.length; i++) {
    hash = category.charCodeAt(i) + ((hash << 5) - hash);
  }
  const index = Math.abs(hash) % colorPool.length;
  return colorPool[index];
}
