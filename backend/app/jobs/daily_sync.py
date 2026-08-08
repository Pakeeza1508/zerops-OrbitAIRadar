from __future__ import annotations

import asyncio
import json
import sys

from app.db import close_client, ensure_indexes, ping_db
from app.services.scrapper.pipeline import run_ingestion
from app.services.sources import seed_default_sources


async def main() -> int:
    if not await ping_db():
        print(json.dumps({"status": "failed", "error": "MongoDB is unavailable"}))
        return 1
    await ensure_indexes()
    await seed_default_sources()
    result = await run_ingestion(trigger="cron")
    print(json.dumps(result, default=str))
    return 0 if result.get("status") in {"success", "partial"} else 1


if __name__ == "__main__":
    try:
        code = asyncio.run(main())
    finally:
        try:
            asyncio.run(close_client())
        except Exception:
            pass
    sys.exit(code)
