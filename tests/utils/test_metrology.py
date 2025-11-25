from vein_wiki_tools.utils.metrology import imperial_to_metric


async def test_pounds_to_kilograms():
    pounds = 150.0
    expected_kg = 68.0  # 150 lbs is approximately 68.0 kg
    result_kg = imperial_to_metric(pounds=pounds)
    assert result_kg == expected_kg


async def test_feet_to_meters():
    feet = 6.0
    expected_meters = 1.83  # 6 feet is approximately 1.83 meters
    result_meters = imperial_to_metric(feet=feet)
    assert result_meters == expected_meters


async def test_inches_to_meters():
    inches = 72.0
    expected_meters = 1.83  # 72 inches is approximately 1.83 meters
    result_meters = imperial_to_metric(inches=inches)
    assert result_meters == expected_meters
