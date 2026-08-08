import arxiv
import yaml
import os
import calendar
from datetime import datetime
try:
    from collector.filters import is_valid_paper
    from collector.metadata import MetadataStore
except ImportError:
    from filters import is_valid_paper
    from metadata import MetadataStore

def load_config(config_path="collector/config.yaml"):
    if not os.path.exists(config_path):
        alt_path = os.path.join(os.path.dirname(__file__), "config.yaml")
        if os.path.exists(alt_path):
            config_path = alt_path
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def build_category_query(config):
    sources = config.get("sources", [])
    if not sources:
        return "all"
    
    cat_queries = [f"cat:{cat}" for cat in sources]
    return "(" + " OR ".join(cat_queries) + ")"

def collect_papers(max_papers=None):
    config = load_config()
    cat_query = build_category_query(config)
    year_start = config.get("year_start", 2022)
    
    if max_papers is None:
        max_papers = config.get("max_per_year", 2000)
    
    store = MetadataStore(config["paths"]["metadata"])
    client = arxiv.Client()
    
    total_collected = 0
    total_checked = 0
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    print(f"\n{'='*50}")
    print(f"=== Starting arXiv Harvester (Total Batch Limit: {max_papers}) ===")
    print(f"{'='*50}")

    for year in range(current_year, year_start - 1, -1):
        if total_collected >= max_papers:
            print(f"Reached batch limit of {max_papers} papers. Stopping harvester.")
            break
            
        end_month = current_month if year == current_year else 12
        
        for month in range(end_month, 0, -1):
            if total_collected >= max_papers:
                break
                
            start_date = datetime(year, month, 1, 0, 0)
            _, last_day = calendar.monthrange(year, month)
            end_date = datetime(year, month, last_day, 23, 59)
            
            start_str = start_date.strftime("%Y%m%d%H%M")
            end_str = end_date.strftime("%Y%m%d%H%M")
            
            query = f"{cat_query} AND submittedDate:[{start_str} TO {end_str}]"
            print(f"Searching {start_date.strftime('%B %Y')}...")
            
            search = arxiv.Search(
                query=query,
                max_results=max_papers,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending
            )
            
            try:
                for paper in client.results(search):
                    if total_collected >= max_papers:
                        break
                        
                    total_checked += 1
                    
                    if store.has_paper(paper.get_short_id()):
                        continue
                        
                    if is_valid_paper(paper, config):
                        store.add_paper(paper)
                        total_collected += 1
                        print(f"[{total_collected}/{max_papers}] Harvested: {paper.title[:60]}...")
            except Exception as e:
                print(f"Error fetching arXiv month {month}/{year}: {e}")
                
    print(f"\nHarvesting complete! Total new papers collected: {total_collected}")
