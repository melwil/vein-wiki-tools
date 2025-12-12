from vein_wiki_tools.services.template import trim_bad_newlines


async def test_trim_bad_newlines():
    input_text = "\n\nThis is a test.\n\n\n\nThis is only a test.\n\n\n"
    expected_output = "This is a test.\n\nThis is only a test."
    result = trim_bad_newlines(input_text)
    assert result == expected_output


async def test_trim_bad_newlines2():
    input_text = r"""
{{Infobox Item
|title=9mm Round
|image=BP_Ammo_9mm.png
|description=A box of 9mm rounds.
|weight=0.02 lbs / 0.01 kg
|used-as=
|stackable=None
|renewable=None
|itemID=BP_Ammo_9mm
}}
"""
    expected_output = """{{Infobox Item
|title=9mm Round
|image=BP_Ammo_9mm.png
|description=A box of 9mm rounds.
|weight=0.02 lbs / 0.01 kg
|used-as=
|stackable=None
|renewable=None
|itemID=BP_Ammo_9mm
}}"""
    result = trim_bad_newlines(input_text)
    assert result == expected_output
