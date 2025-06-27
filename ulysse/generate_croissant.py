import pandas as pd
import json
import sys
from pathlib import Path
from datetime import datetime
import hashlib
import urllib.parse

def calculate_sha256(file_path: Path) -> str:
    """Calculate SHA256 hash of a file."""
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def sanitize_id(text: str) -> str:
    """Sanitize strings to be valid @ids."""
    return urllib.parse.quote(text.replace(" ", "_").replace("/", "_"))

def infer_data_type(series: pd.Series) -> str:
    """Determine the appropriate data type for a pandas series."""
    if series.empty:
        return "Text"
    
    series = series.dropna()
    
    try:
        pd.to_numeric(series)
        if series.astype(str).str.isdigit().all():
            return "Integer"
        return "Float"
    except:
        pass
    
    if set(series.astype(str).str.lower().unique()) <= {"true", "false", "0", "1"}:
        return "Boolean"
    
    date_formats = ['%Y%m%d', '%d/%m/%Y', '%Y-%m-%d']
    for fmt in date_formats:
        try:
            pd.to_datetime(series, format=fmt, errors='raise')
            return "Date"
        except:
            continue
    
    return "Text"

def generate_croissant_metadata(csv_path: Path) -> dict:
    """Generate Croissant metadata for a single CSV file."""
    df = pd.read_csv(csv_path, sep=';', engine='python')
    
    # Generate file object
    file_object = {
        "@type": "FileObject",
        "name": sanitize_id(csv_path.stem),
        "description": f"CSV file: {csv_path.name}",
        "encodingFormat": "text/csv",
        "contentUrl": f"file://{csv_path.absolute().as_posix()}",
        "sha256": calculate_sha256(csv_path),
        "@id": f"file/{sanitize_id(csv_path.stem)}"
    }
    
    # Generate fields
    fields = []
    for col in df.columns:
        sanitized_col = sanitize_id(col)
        fields.append({
            "@type": "Field",
            "name": sanitized_col,
            "dataType": infer_data_type(df[col]),
            "source": {
                "fileObject": {"@id": f"file/{sanitize_id(csv_path.stem)}"},
                "extract": {"column": col}
            },
            "@id": f"field/{sanitize_id(csv_path.stem)}/{sanitized_col}"
        })
    
    # Complete metadata
    metadata = {
        "@context": "https://mlcommons.org/croissant/1.0/context.json",
        "@type": "Dataset",
        "name": f"Dataset_{sanitize_id(csv_path.stem)}",
        "description": f"Dataset generated from {csv_path.name}",
        "license": "https://creativecommons.org/licenses/by/4.0/",
        "datePublished": datetime.now().date().isoformat(),
        "version": "1.0",
        "citation": "Generated from CSV data",
        "distribution": [file_object],
        "recordSet": [{
            "@type": "RecordSet",
            "name": sanitize_id(csv_path.stem),
            "description": f"Data from {csv_path.name}",
            "fields": fields,
            "@id": f"recordset/{sanitize_id(csv_path.stem)}"
        }]
    }
    
    return metadata

def main():
    if len(sys.argv) != 2:
        print("Usage: python generate_croissant.py input.csv")
        sys.exit(1)
    
    input_csv = Path(sys.argv[1])
    output_json = Path(f"{input_csv.stem}_croissant.jsonld")
    
    try:
        # Generate metadata
        metadata = generate_croissant_metadata(input_csv)
        
        # Save to file
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Successfully generated: {output_json}")
        print("Note: The validation step has been removed to avoid version conflicts.")
        print("You can validate the file separately using mlcroissant if needed.")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()