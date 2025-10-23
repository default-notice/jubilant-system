from PIL import Image
import pytesseract, re

def extract_headlines(image_path):
    txt = pytesseract.image_to_string(Image.open(image_path), config="--psm 6")
    lines = [re.sub(r"\s+", " ", ln).strip() for ln in txt.splitlines()]
    cleaned = []
    for ln in lines:
        if len(ln) < 18: 
            continue
        if re.search(r"\b(minutes?|hours?|days?) ago\b", ln, re.I):
            continue
        if re.match(r"^\W+$", ln):
            continue
        ln = re.sub(r"^[•·\-–—\*]+\s*", "", ln)
        if sum(c.isdigit() for c in ln) > 6:
            continue
        cleaned.append(ln)
    seen, out = set(), []
    for ln in cleaned:
        if ln not in seen:
            seen.add(ln); out.append(ln)
    return out[:2]
