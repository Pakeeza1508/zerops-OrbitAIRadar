"""MongoDB SRV DNS selection for Windows local development.

Some Windows routers resolve SRV records but time out on MongoDB Atlas TXT
records. dnspython may continue selecting the router even after Windows Wi-Fi
DNS settings change. Use known-working public resolvers for MongoDB+SRV on
Windows only; keep platform defaults on hosting/Linux.

Override via MONGO_DNS_SERVERS=9.9.9.9,1.1.1.1 or disable with
MONGO_DNS_SERVERS=system. This does not change MongoDB credentials or schema.
"""
from __future__ import annotations

import logging
import os
import platform

import dns.resolver

logger = logging.getLogger("orbit.db")

_configured = False


def configure_mongo_dns(mongo_url: str) -> None:
    global _configured
    if _configured or not mongo_url.startswith("mongodb+srv://"):
        return

    raw = os.getenv("MONGO_DNS_SERVERS", "").strip()
    if raw.lower() == "system":
        logger.info("stage=mongo.dns mode=system")
        return
    if not raw and platform.system() != "Windows":
        logger.info("stage=mongo.dns mode=system")
        return

    nameservers = [item.strip() for item in (raw or "1.1.1.1,1.0.0.1").split(",") if item.strip()]
    resolver = dns.resolver.Resolver(configure=False)
    try:
        resolver.nameservers = nameservers  # dnspython validates address format.
    except ValueError as exc:
        raise ValueError("Invalid MONGO_DNS_SERVERS configuration") from exc
    resolver.timeout = 3
    resolver.lifetime = 10
    dns.resolver.default_resolver = resolver
    _configured = True
    logger.info("stage=mongo.dns mode=explicit resolver_count=%d", len(nameservers))
