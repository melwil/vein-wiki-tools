from pywikibot import family


class Family(family.Family):
    name = "vein"
    langs = {
        "en": "vein.wiki.gg",
    }

    def version(self, code):
        """
        Return the version of the MediaWiki software.

        Updating the version
        Go to https://vein.wiki.gg/wiki/Special:Version
        Installed software -> MediaWiki version goes below
        """
        return "1.43.5"

    def scriptpath(self, code):
        """
        Return the Entry point for script path.

        Go to https://vein.wiki.gg/wiki/Special:Version
        Entry point URLs -> Script path goes below
        """
        return ""

    def protocol(self, code):
        return "https"
