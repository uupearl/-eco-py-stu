



"""Build a firm-year digital transformation index from annual reports."""

from pathlib import Path
import csv
import math
import re


DATA_DIR = Path(
    '/Users/ww/Desktop/pre/txt'
)
OUTPUT_FILE = DATA_DIR.parent / "digital_transformation_panel.csv"
FIRM_ID = "Microsoft"


# Specific terms are used to reduce false positives from generic words
# such as "data", "software", "system", and "technology".
DIGITAL_DICTIONARY = {
    "artificial_intelligence": [
        "artificial intelligence",
        "machine learning",
        "deep learning",
        "neural network",
        "neural networks",
        "natural language processing",
        "computer vision",
        "generative ai",
        "large language model",
        "large language models",
        "cognitive computing",
        "ai",
    ],
    "big_data_analytics": [
        "big data",
        "data analytics",
        "advanced analytics",
        "predictive analytics",
        "real time analytics",
        "data mining",
        "data driven",
        "data platform",
        "data lake",
        "data warehouse",
        "business intelligence",
    ],
    "cloud_computing": [
        "cloud computing",
        "cloud platform",
        "cloud service",
        "cloud services",
        "cloud infrastructure",
        "public cloud",
        "private cloud",
        "hybrid cloud",
        "multi cloud",
        "software as a service",
        "platform as a service",
        "infrastructure as a service",
        "saas",
        "paas",
        "iaas",
    ],
    "automation_robotics": [
        "intelligent automation",
        "robotic process automation",
        "process automation",
        "business process automation",
        "industrial automation",
        "automation",
        "automated",
        "robotics",
        "robot",
        "rpa",
    ],
    "iot_connectivity": [
        "internet of things",
        "industrial internet",
        "connected device",
        "connected devices",
        "smart device",
        "smart devices",
        "edge computing",
        "5g network",
        "5g networks",
        "iot",
    ],
    "blockchain": [
        "distributed ledger",
        "smart contract",
        "smart contracts",
        "blockchain",
        "cryptocurrency",
        "digital currency",
    ],
    "digital_business": [
        "digital transformation",
        "digital technology",
        "digital technologies",
        "digital platform",
        "digital platforms",
        "digital economy",
        "digital capability",
        "digital capabilities",
        "digital solution",
        "digital solutions",
        "digital service",
        "digital services",
        "digital ecosystem",
        "digital ecosystems",
        "digital business",
        "digital experience",
        "digital workplace",
        "digitalization",
        "digitization",
        "e commerce",
        "electronic commerce",
        "online platform",
        "online platforms",
        "mobile application",
        "mobile applications",
        "mobile app",
        "mobile apps",
    ],
    "cybersecurity": [
        "cybersecurity",
        "cyber security",
        "information security",
        "data security",
        "network security",
        "cloud security",
        "zero trust",
        "identity management",
        "access management",
        "encryption",
    ],
    "digital_infrastructure": [
        "application programming interface",
        "application programming interfaces",
        "api",
        "apis",
        "microservice",
        "microservices",
        "devops",
        "virtual reality",
        "augmented reality",
        "mixed reality",
        "digital twin",
        "digital twins",
        "quantum computing",
        "3d printing",
        "additive manufacturing",
    ],
}


def normalize_text(text):
    """Convert punctuation and line breaks to spaces."""
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def count_category(text, phrases):
    """Count complete phrases, matching longer phrases first."""
    patterns = []
    for phrase in sorted(phrases, key=len, reverse=True):
        normalized_phrase = normalize_text(phrase)
        patterns.append(r"\b" + r"\s+".join(normalized_phrase.split()) + r"\b")

    combined_pattern = "(?:" + "|".join(patterns) + ")"
    return len(re.findall(combined_pattern, text))


def build_panel():
    report_files = sorted(DATA_DIR.glob("*_Annual_Report.txt"))
    if not report_files:
        raise FileNotFoundError(f"No annual reports found in: {DATA_DIR}")

    rows = []

    for file_path in report_files:
        year_match = re.search(r"(?:19|20)\d{2}", file_path.stem)
        if not year_match:
            continue

        raw_text = file_path.read_text(encoding="utf-8", errors="ignore")
        text = normalize_text(raw_text)
        word_count = len(text.split())

        if word_count == 0:
            print(f"Skipped empty report: {file_path.name}")
            continue

        row = {
            "firm_id": FIRM_ID,
            "year": int(year_match.group()),
            "word_count": word_count,
        }

        category_columns = []
        for category, phrases in DIGITAL_DICTIONARY.items():
            column = f"{category}_count"
            row[column] = count_category(text, phrases)
            category_columns.append(column)

        total_count = sum(row[column] for column in category_columns)
        intensity = total_count / word_count * 10_000

        row["digital_keyword_count"] = total_count
        row["digital_keywords_per_10k_words"] = intensity

        # Final Digital Transformation Index:
        # ln(1 + digital keyword occurrences per 10,000 words)
        row["digital_transformation_index"] = math.log1p(intensity)

        rows.append(row)

    return sorted(rows, key=lambda row: (row["firm_id"], row["year"]))


def save_panel(rows):
    if not rows:
        raise ValueError("No valid firm-year observations were created.")

    with OUTPUT_FILE.open("w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    panel = build_panel()
    save_panel(panel)

    print(f"{'Year':<6} {'Words':>10} {'Keywords':>10} {'DT Index':>12}")
    for row in panel:
        print(
            f"{row['year']:<6} "
            f"{row['word_count']:>10} "
            f"{row['digital_keyword_count']:>10} "
            f"{row['digital_transformation_index']:>12.4f}"
        )

    print(f"\nProcessed {len(panel)} annual reports.")
    print(f"Output saved to: {OUTPUT_FILE}")
