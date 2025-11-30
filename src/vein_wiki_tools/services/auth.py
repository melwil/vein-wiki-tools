import logging

import pywikibot

logger = logging.getLogger(__name__)


async def login() -> pywikibot._BaseSite:
    site = pywikibot.Site("en", "vein")
    await site.login()
    logger.debug(f"Logged in as: {site.user()}")
    return site
