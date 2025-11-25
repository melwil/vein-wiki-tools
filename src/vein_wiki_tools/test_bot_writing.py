"""
This script tests writing to a Vein Wiki page using the VeinBot account.

First use the login command, then run this script to update the test page.

https://vein.wiki.gg/wiki/User:VeinBot/TestPage
"""

import asyncio
import datetime

import pywikibot

test_text = f"""
This is a test page created by VeinBot.<br><br>

VeinBot is a bot account used to automatically update pages on the Vein Wiki.<br><br>

Test write successful @ {datetime.datetime.now().isoformat()}
"""


async def main():
    site = pywikibot.Site("en", "vein")
    user = site.user()
    print(f"Logged in as: {user}")
    page = pywikibot.Page(site, "User:VeinBot/TestPage")
    page.text = test_text
    page.save(summary="Test script - ignore me", bot=True)


if __name__ == "__main__":
    asyncio.run(main())
