import fitz  # PyMuPDF
import os
import json
import re
import logging

def is_heading_pattern(text):
    return bool(re.match(r"^\d+(\.\d+)*\.?\s+.+", text.strip()))


def is_date_text(text):
    text = text.lower()
    if "date" in text or "dated" in text:
        return True
    date_patterns = [
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",        # 01/01/2024 or 1-1-2023
        r"\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b",          # 2024-01-01
        r"\b\d{1,2}\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{2,4}\b",  # 1 Jan 2024
        r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2},?\s+\d{2,4}\b",  # Jan 1, 2024
    ]
    return any(re.search(pat, text) for pat in date_patterns)


def is_meaningful_heading(text):
    text = text.strip()
    words = text.split()
    return (
        not is_date_text(text) and (
            is_heading_pattern(text)
            or (len(words) >= 3 and len(text) >= 20 and not text.endswith(":"))
        )
    )


def extract_headings_from_pdf(filepath):
    doc = fitz.open(filepath)
    headings = []
    title_lines = []

    font_stats = {}

    # Pass 1: collect font stats
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"].strip()
                    if not text or len(text) > 200:
                        continue
                    font_size = round(span["size"])
                    font = span["font"]
                    font_key = (font_size, font)
                    font_stats[font_key] = font_stats.get(font_key, 0) + 1

    # Determine title and heading fonts
    sorted_fonts = sorted(font_stats.items(), key=lambda x: (-x[0][0], -x[1]))
    likely_title_font = sorted_fonts[0][0] if sorted_fonts else (12, "Times")
    h1_font = sorted_fonts[1][0] if len(sorted_fonts) > 1 else likely_title_font
    h2_font = sorted_fonts[2][0] if len(sorted_fonts) > 2 else h1_font
    h3_font = sorted_fonts[3][0] if len(sorted_fonts) > 3 else h2_font

    # Pass 2: extract headings
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                spans = line["spans"]
                full_line_text = " ".join(span["text"].strip() for span in spans if span["text"].strip())
                if not full_line_text or len(full_line_text) > 200:
                    continue

                span = spans[0]
                f_key = (round(span["size"]), span["font"])

                # Title (first page, largest font)
                if f_key == likely_title_font and len(title_lines) < 3 and page_num == 0:
                    title_lines.append(full_line_text)
                    continue

                # Heading detection logic
                level = None
                if f_key == h1_font:
                    level = "H1"
                elif f_key == h2_font:
                    level = "H2"
                elif f_key == h3_font:
                    level = "H3"
                elif is_heading_pattern(full_line_text):
                    level = "H2" if "." in full_line_text.split()[0] else "H1"

                if level and is_meaningful_heading(full_line_text):
                    headings.append({
                        "level": level,
                        "text": full_line_text.strip(),
                        "page": page_num + 1
                    })

    title = " ".join(title_lines).strip() or "Untitled Document"

    return {
        "title": title,
        "outline": headings
    }

def main():
    input_dir = "input"
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    pdf_files = [f for f in os.listdir(input_dir) if f.endswith(".pdf")]

    if not pdf_files:
        logging.info("No PDF files found in input directory.")
        return

    for filename in pdf_files:
        pdf_path = os.path.join(input_dir, filename)
        logging.info(f"Start processing: {filename}")

        try:
            result = extract_headings_from_pdf(pdf_path)
            json_filename = os.path.splitext(filename)[0] + ".json"
            output_path = os.path.join(output_dir, json_filename)

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Error processing {filename}: {e}")

    logging.info("✅ All PDFs Processed.")

if __name__ == "__main__":
    main()