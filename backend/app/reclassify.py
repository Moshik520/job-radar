"""Recompute derived fields of every stored job: its category (from the title) and UTC dates.

Run after changing the rules in classify.py, or after upgrading old data.
Run from the backend folder:  python -m app.reclassify
"""

import asyncio
import collections
from datetime import UTC, datetime

from pymongo import UpdateOne

from app.classify import classify_category
from app.dates import to_utc_iso
from app.db import details_collection, ensure_indexes, jobs_collection


async def main() -> None:
    await ensure_indexes()
    now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    updates = []
    counts = collections.Counter()
    async for job in jobs_collection.find({}, {"title": 1, "published_at": 1, "updated_at": 1}):
        category = classify_category(job.get("title", ""))
        counts[category] += 1
        updated_at = to_utc_iso(job.get("updated_at"))
        published_at = to_utc_iso(job.get("published_at")) or updated_at or now
        updates.append(UpdateOne(
            {"_id": job["_id"]},
            {"$set": {"category": category, "published_at": published_at, "updated_at": updated_at}},
        ))
    if updates:
        await jobs_collection.bulk_write(updates)

    # Cached details remember the job's updated_at; keep them matching the normalized value.
    detail_updates = [
        UpdateOne({"_id": doc["_id"]}, {"$set": {"job_updated_at": to_utc_iso(doc.get("job_updated_at"))}})
        async for doc in details_collection.find({}, {"job_updated_at": 1})
    ]
    if detail_updates:
        await details_collection.bulk_write(detail_updates)

    print(f"Updated {len(updates)} jobs and {len(detail_updates)} cached details")
    for category, count in counts.most_common():
        print(f"{count:6}  {category}")


if __name__ == "__main__":
    asyncio.run(main())
