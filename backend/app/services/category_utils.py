from typing import Dict

# Comprehensive mapping of arXiv taxonomy codes to clean, human-readable labels
ARXIV_CATEGORY_MAP: Dict[str, str] = {
    # Computer Science
    "cs.AI": "Artificial Intelligence",
    "cs.CL": "Natural Language Processing",
    "cs.CV": "Computer Vision",
    "cs.LG": "Machine Learning",
    "cs.NE": "Neural & Evolutionary Computing",
    "cs.RO": "Robotics",
    "cs.IR": "Information Retrieval",
    "cs.SE": "Software Engineering",
    "cs.CR": "Cryptography & Security",
    "cs.DB": "Databases & Data Management",
    "cs.HC": "Human-Computer Interaction",
    "cs.DC": "Distributed & Parallel Computing",
    "cs.NI": "Networking & Internet Architecture",
    "cs.CY": "Computers & Society",
    "cs.SI": "Social & Information Networks",
    "cs.SD": "Sound & Audio Processing",
    "cs.AR": "Computer Architecture",
    "cs.GT": "Computer Science & Game Theory",
    "cs.IT": "Information Theory",
    "cs.DS": "Data Structures & Algorithms",
    "cs.PL": "Programming Languages",
    "cs.CE": "Computational Engineering",
    "cs.MS": "Mathematical Software",
    "cs.ET": "Emerging Technologies",
    
    # Statistics & Mathematics
    "stat.ML": "Machine Learning (Stats)",
    "stat.AP": "Applied Statistics",
    "stat.TH": "Statistical Theory",
    "stat.ME": "Methodology",
    "stat.CO": "Computation Statistics",
    "math.OC": "Optimization & Control",
    "math.NA": "Numerical Analysis",
    "math.PR": "Probability Theory",
    "math.DS": "Dynamical Systems",
    "math.ST": "Mathematical Statistics",
    
    # Electrical Engineering & Systems
    "eess.IV": "Image & Video Processing",
    "eess.SP": "Signal Processing",
    "eess.SY": "Systems & Control",
    "eess.AS": "Audio & Speech Processing",
    
    # Physics & Quantum
    "quant-ph": "Quantum Physics",
    "gr-qc": "General Relativity & Quantum Cosmology",
    "hep-ph": "High Energy Physics",
    "nlin.PS": "Nonlinear Sciences",
    "physics.optics": "Optics & Photonics",
    "physics.med-ph": "Medical Physics",
    "physics.data-an": "Data Analysis & Physics",
    "physics.flu-dyn": "Fluid Dynamics",
    "physics.ao-ph": "Atmospheric & Oceanic Physics",
    "cond-mat.mtrl-sci": "Materials Science",
    "cond-mat.dis-nn": "Disordered Systems & Neural Networks",
    "astro-ph.CO": "Cosmology & Astrophysics",
    "astro-ph.EP": "Earth & Planetary Astrophysics",
    "astro-ph.GA": "Galactic Astrophysics",
    "astro-ph.IM": "Instrumentation & Methods",
    
    # Quantitative Biology & Finance
    "q-bio.QM": "Quantitative Methods",
    "q-bio.GN": "Genomics & Bioinformatics",
    "q-bio.NC": "Neuron & Cognition",
    "q-fin.ST": "Statistical Finance",
    "q-fin.TR": "Trading & Market Microstructure",
    "q-fin.PM": "Portfolio Management"
}

def format_category_name(raw_code: str) -> str:
    """
    Transforms a raw arXiv category code (e.g. 'cs.AI') into a human-readable label.
    Includes smart fallback formatting for unmapped codes.
    """
    if not raw_code:
        return "General Research"
    
    cleaned = raw_code.strip()
    
    # Check exact match
    if cleaned in ARXIV_CATEGORY_MAP:
        return ARXIV_CATEGORY_MAP[cleaned]
    
    # Smart Fallback Formatting for unknown codes (e.g. "physics.comp-ph" -> "Physics: Comp Ph")
    if "." in cleaned:
        prefix, suffix = cleaned.split(".", 1)
        prefix_title = {
            "cs": "Computer Science",
            "stat": "Statistics",
            "math": "Mathematics",
            "physics": "Physics",
            "eess": "Engineering",
            "astro-ph": "Astrophysics",
            "cond-mat": "Condensed Matter",
            "q-bio": "Quantitative Biology",
            "q-fin": "Quantitative Finance"
        }.get(prefix.lower(), prefix.capitalize())
        
        suffix_formatted = suffix.replace("-", " ").replace("_", " ").title()
        return f"{prefix_title}: {suffix_formatted}"
    
    return cleaned.replace("-", " ").replace("_", " ").title()
