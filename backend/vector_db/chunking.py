import re
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

def get_splitters():
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    recursive_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=120,
        separators=["\n\n", "\n", " ", ""]
    )
    return markdown_splitter, recursive_splitter

def extract_conclusion_and_strip_references(markdown_text: str):
    conclusion_text = ""
    
    # 1. Strip References
    ref_match = re.search(r"(?m)^#\s+References?\s*$", markdown_text, re.IGNORECASE)
    if ref_match:
        markdown_text = markdown_text[:ref_match.start()]
        
    # 2. Extract Conclusion
    conc_match = re.search(r"(?m)^#\s+(?:Conclusion|Conclusions|Discussion)\s*$(.*?)(?=(?:^#\s+)|\Z)", markdown_text, re.IGNORECASE | re.DOTALL)
    if conc_match:
        conclusion_text = conc_match.group(1).strip()
        
    return markdown_text, conclusion_text
