"""Print source catalog buckets without scraping anything."""

from open_reason.sources.catalog import partition_sources

buckets = partition_sources()
for name, rows in buckets.items():
    print(name, len(rows), [row["id"] for row in rows[:8]])
