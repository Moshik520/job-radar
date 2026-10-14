"""Load the list of companies (and their ATS board tokens) into MongoDB.

Run from the backend folder:  python -m app.seed_companies
"""

import asyncio
import csv
from pathlib import Path

from app.db import db

COMPANIES_CSV = Path(__file__).resolve().parent.parent / "data" / "companies.csv"
companies_collection = db["companies"]


async def main():
    count = 0
    with open(COMPANIES_CSV, encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["ats"] != "greenhouse":
                continue
            await companies_collection.update_one(
                {"_id": f"greenhouse:{row['board']}"},
                {"$set": {"ats": row["ats"], "board": row["board"]}},
                upsert=True,
            )
            count += 1

    print(f"Loaded {count} Greenhouse companies")


if __name__ == "__main__":
    asyncio.run(main())
