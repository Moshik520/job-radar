"""Recompute the category of every stored job from its title. Run after changing the rules in classify.py.

Run from the backend folder:  python -m app.reclassify
"""

import asyncio
import collections

from pymongo import UpdateOne

from app.classify import classify_category
from app.db import ensure_indexes, jobs_collection


async def main() -> None:
    await ensure_indexes()
    updates = []
    counts = collections.Counter()
    async for job in jobs_collection.find({}, {"title": 1}):
        category = classify_category(job.get("title", ""))
        counts[category] += 1
        updates.append(UpdateOne({"_id": job["_id"]}, {"$set": {"category": category}}))
    if updates:
        await jobs_collection.bulk_write(updates)
    print(f"Classified {len(updates)} jobs")
    for category, count in counts.most_common():
        print(f"{count:6}  {category}")


if __name__ == "__main__":
    asyncio.run(main())
