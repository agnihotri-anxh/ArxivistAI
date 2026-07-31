import re

def is_valid_paper(paper, config):
    """
    Checks if a paper meets our quality and keyword filters.
    """
    # Check if English/has abstract (arxiv results usually do, but let's be safe)
    if not paper.summary or len(paper.summary.strip()) < 50:
        return False
        
    if not paper.pdf_url:
        return False
        
    # Check year
    year_start = config.get("year_start", 2022)
    if paper.published.year < year_start:
        return False
        
    # Check keywords in abstract or title
    keywords = config.get("keywords", [])
    if not keywords:
        return True
        
    text_to_search = (paper.title + " " + paper.summary).lower()
    
    for keyword in keywords:
        pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
        if re.search(pattern, text_to_search):
            return True
            
    return False
