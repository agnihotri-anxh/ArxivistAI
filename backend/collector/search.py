import arxiv
import yaml
import os
import calendar
from datetime import datetime
from filters import is_valid_paper
from metadata import MetadataStore

def load_config(config_path="collector/config.yaml"):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def build_category_query(config):
    # Constructing query like: (cat:cs.AI OR cat:cs.CL)
    sources = config.get("sources", [])
    if not sources:
        return "all"
    
    cat_queries = [f"cat:{cat}" for cat in sources]
    return "(" + " OR ".join(cat_queries) + ")"

def collect_papers():
    config = load_config()
    cat_query = build_category_query(config)
    year_start = config.get("year_start", 2022)
    max_per_year = config.get("max_per_year", 2000)
    
    store = MetadataStore(config["paths"]["metadata"])
    client = arxiv.Client()
    
    # Pre-calculate how many papers we already have for each year in the database
    existing_per_year = {}
    for paper in store.get_all():
        try:
            # Handle ISO format strings like '2026-07-09T17:59:32+00:00'
            year = datetime.fromisoformat(paper["published"]).year
            existing_per_year[year] = existing_per_year.get(year, 0) + 1/
        except Exception:
            pass
            
    total_collected = 0
    total_checked = 0
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    # Loop year by year, backwards
    for year in range(current_year, year_start - 1, -1):
        # Start the counter with whatever is already in the database for this year!
        year_collected = existing_per_year.get(year, 0)
        
        print(f"\n{'='*50}")
        print(f"=== Searching Year: {year} (Target: {max_per_year}) ===")
        print(f"=== Already in database for {year}: {year_collected} ===")
        print(f"{'='*50}")
        
        end_month = current_month if year == current_year else 12
        
        # Loop months backward
        for month in range(end_month, 0, -1):
            if year_collected >= max_per_year:
                print(f"Reached {max_per_year} papers for {year}. Skipping remaining months.")
                break
                
            start_date = datetime(year, month, 1, 0, 0)
            _, last_day = calendar.monthrange(year, month)
            end_date = datetime(year, month, last_day, 23, 59)
            
            # Format for arXiv API: YYYYMMDDHHMM
            start_str = start_date.strftime("%Y%m%d%H%M")
            end_str = end_date.strftime("%Y%m%d%H%M")
            
            query = f"{cat_query} AND submittedDate:[{start_str} TO {end_str}]"
            print(f"\nSearching: {start_date.strftime('%B %Y')}...")
            
            search = arxiv.Search(
                query=query,
                max_results=10000, 
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending
            )
            
            month_checked = 0
            month_collected = 0
            
            try:
                for paper in client.results(search):
                    # Stop processing if we hit our yearly limit
                    if year_collected >= max_per_year:
                        break
                        
                    month_checked += 1
                    total_checked += 1
                    
                    # Skip if we already have it
                    if store.has_paper(paper.get_short_id()):
                        continue
                        
                    if is_valid_paper(paper, config):
                        store.add_paper(paper)
                        month_collected += 1
                        year_collected += 1
                        total_collected += 1
                        print(f"[{year_collected}/{max_per_year} in {year}] Found: {paper.title}")
                        
                        # Save periodically
                        if total_collected % 50 == 0:
                            store.save()
                            
                print(f"  -> Checked {month_checked}, found {month_collected} valid papers.")
            except Exception as e:
                print(f"  -> Error fetching {start_date.strftime('%B %Y')}: {e}")
                
            store.save()
            
    store.save()
    print(f"\nDone! Checked {total_checked} papers across all years.")
    print(f"Collected {total_collected} new valid papers.")
    print(f"Total papers in database: {len(store.records)}")

if __name__ == "__main__":
    collect_papers()
