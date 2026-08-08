import json
import traceback
from pathlib import Path
import fitz  # PyMuPDF
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PDF_DIR = DATA_DIR / "pdfs"
MD_DIR = DATA_DIR / "markdown"
IMG_DIR = DATA_DIR / "extracted_images"
JSON_DIR = DATA_DIR / "structured_json"
FAILED_LOG = DATA_DIR / "failed_stage3.txt"

IMG_DIR.mkdir(parents=True, exist_ok=True)
JSON_DIR.mkdir(parents=True, exist_ok=True)

def stage_b_visual_isolation(pdf_path: Path):
    print(f"\n--- [Stage 3] Visual Isolation for {pdf_path.name} ---")
    paper_id = pdf_path.stem
    paper_img_dir = IMG_DIR / paper_id
    paper_img_dir.mkdir(parents=True, exist_ok=True)
    
    doc = fitz.open(pdf_path)
    visual_metadata = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        dict_data = page.get_text("dict")
        blocks = dict_data.get("blocks", [])
        
        image_blocks = [b for b in blocks if b["type"] == 1]
        text_blocks = [b for b in blocks if b["type"] == 0]
        
        for i, img_b in enumerate(image_blocks):
            img_bbox = img_b["bbox"]
            width = img_bbox[2] - img_bbox[0]
            height = img_bbox[3] - img_bbox[1]
            if width < 50 or height < 50:
                continue
                
            mat = fitz.Matrix(4.0, 4.0)
            pix = page.get_pixmap(clip=img_bbox, matrix=mat)
            
            img_path = paper_img_dir / f"page_{page_num+1}_img_{i+1}.webp"
            
            try:
                if pix.n - pix.alpha < 4:
                    fmt = "RGB" if pix.alpha == 0 else "RGBA"
                    img = Image.frombytes(fmt, [pix.w, pix.h], pix.samples)
                    img.save(img_path, format="WEBP", quality=85)
                else:
                    img_path_png = img_path.with_suffix(".png")
                    pix.save(str(img_path_png))
                    img_path = img_path_png
            except Exception as e:
                print(f"Failed to save image {i+1} on page {page_num+1}: {e}")
                continue
                
            img_y1 = img_bbox[3]
            caption = ""
            closest_dist = float('inf')
            
            for tb in text_blocks:
                tb_y0 = tb["bbox"][1]
                if tb_y0 >= img_y1 and (tb_y0 - img_y1) < 60:
                    dist = tb_y0 - img_y1
                    if dist < closest_dist:
                        closest_dist = dist
                        lines = [span["text"] for l in tb["lines"] for span in l.get("spans", [])]
                        caption = " ".join(lines)
            
            visual_metadata.append({
                "figure_id": f"FIGURE_{page_num+1}_{i+1}",
                "type": "figure",
                "local_path": str(img_path.resolve()).replace("\\", "/"),
                "caption": caption.strip(),
                "page": page_num + 1,
                "bbox": img_bbox
            })
            
    doc.close()
    print(f"Extracted {len(visual_metadata)} visual assets.")
    return visual_metadata

def stage_c_compile_json(paper_id: str, visual_metadata: list):
    md_file = MD_DIR / paper_id / f"{paper_id}.md"
    markdown_content = ""
    if md_file.exists():
        with open(md_file, "r", encoding="utf-8") as f:
            markdown_content = f.read()
    else:
        print(f"Warning: Markdown file {md_file} not found.")
        
    for vis in visual_metadata:
        caption_snippet = vis["caption"][:40]
        if caption_snippet and caption_snippet in markdown_content:
            placeholder = f"\n\n[{vis['figure_id']}_INSERT_HERE: {vis['local_path']}]\n\n"
            markdown_content = markdown_content.replace(caption_snippet, placeholder + caption_snippet, 1)

    master_json = {
        "metadata": {
            "paper_id": paper_id,
            "title": f"Document {paper_id}",
        },
        "visual_metadata": visual_metadata,
        "full_text": markdown_content
    }
    
    json_path = JSON_DIR / f"{paper_id}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(master_json, f, indent=2, ensure_ascii=False)
        
    print(f"JSON compiled and saved to {json_path}")
    return json_path

def main(max_records=None):
    pdfs = list(PDF_DIR.glob("*.pdf"))
    print(f"Found {len(pdfs)} downloaded PDFs ready for Visual Extraction.")
    
    extracted_count = 0
    for pdf_path in pdfs:
        if max_records is not None and extracted_count >= max_records:
            print(f"Reached batch extraction limit of {max_records} files.")
            break
            
        paper_id = pdf_path.stem
        json_path = JSON_DIR / f"{paper_id}.json"
        
        if json_path.exists():
            try:
                pdf_path.unlink()
            except Exception:
                pass
            continue
            
        md_file = MD_DIR / paper_id / f"{paper_id}.md"
        if not md_file.exists():
            continue
            
        try:
            visual_metadata = stage_b_visual_isolation(pdf_path)
            stage_c_compile_json(paper_id, visual_metadata)
            pdf_path.unlink()
            extracted_count += 1
            print(f"Successfully processed and cleaned up {pdf_path.name}")
        except Exception as e:
            error_msg = f"Failed to process {pdf_path.name}: {e}"
            print(f"ERROR: {error_msg}")
            traceback.print_exc()
            with open(FAILED_LOG, "a", encoding="utf-8") as f:
                f.write(error_msg + "\n")
                
    print(f"\nPhase 3 (Visuals & Compile) Complete! Processed {extracted_count} PDFs.")

if __name__ == "__main__":
    main()
