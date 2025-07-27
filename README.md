
# Adobe PDF Title & Heading Extractor

This project extracts the **title** and **section headings** (H1, H2, H3) from PDF documents and generates structured JSON output. It's especially useful for organizing large, unstructured PDF documents by identifying their semantic structure.

---

##  Approach

The core logic of this tool focuses on **visual and textual heuristics**:

1. **Text Extraction & Font Analysis**
   - The PDF is parsed using `PyMuPDF` to extract text blocks, font sizes, and font families.
   - A frequency map of font-size and font-family pairs is built to identify the most commonly used font for titles and headings.

2. **Title Identification**
   - The largest font text on the **first page** is assumed to be the document title.
   - Top 1–3 lines with the largest font size are extracted as potential titles.

3. **Heading Detection**
   - Headings are inferred based on:
     - Font size hierarchy (larger font = higher heading level)
     - Numbering patterns (e.g. `1.`, `1.1.`, etc.)
     - Length and punctuation heuristics (e.g., excludes lines ending in colons or too short)
     - **Date exclusion logic** to prevent misclassification of dates as headings

4. **Output**
   - The result is a structured JSON with:
     - `title`: Inferred title of the document
     - `outline`: A list of headings with `level`, `text`, and `page` number

---

##  Models & Libraries Used

- **[PyMuPDF (`fitz`)](https://pypi.org/project/PyMuPDF/)** – PDF parsing and text layout extraction
- **`re`** – Regular expressions for heading and date pattern detection
- **`json`** – For structured output serialization
- **`os` & `logging`** – File and execution management

>  No machine learning models are used. The solution is rule-based and deterministic for simplicity, interpretability, and performance.

---

## How to Build and Run the Solution

### 1. Clone the Repository

```bash
git clone https://github.com/AnujRawat1/Adobe-Pdf-Title-Extractor.git
cd Adobe-Pdf-Title-Extractor
```

### 2. Set Up the Environment

#### Using pip:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Using Docker Build Commands
```
docker build --platform linux/amd64 -t pdfoutliner:v1 "PWD"
docker run --rm -v "PWD\input:/app/input" -v "PWD\output:/app/output" --network none pdfoutliner:v1

```

3. Prepare Your Files
   
Place your .pdf files in the input/ folder.

4. Run the Script

```
python process_pdfs.py
```

5. Check the Output
The output/ folder will contain one .json file per PDF processed, e.g.:

```

{
  "title": "Annual Report 2024",
  "outline": [
    {
      "level": "H1",
      "text": "1. Introduction",
      "page": 1
    },
    {
      "level": "H2",
      "text": "1.1 Background",
      "page": 2
    }
  ]
}
```




