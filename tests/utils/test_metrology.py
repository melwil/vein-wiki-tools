import pytest

from vein_wiki_tools.utils.metrology import imperial_to_metric, metric_to_imperial

#
# imperial to metric
#


async def test_pounds_to_kilograms():
    pounds = 150.0
    expected_kg = 68.0  # 150 lbs is approximately 68.0 kg
    result_kg = imperial_to_metric(pounds=pounds)
    assert round(result_kg, 1) == expected_kg


async def test_feet_to_meters():
    feet = 6.0
    expected_meters = 1.83  # 6 feet is approximately 1.83 meters
    result_meters = imperial_to_metric(feet=feet)
    assert round(result_meters, 2) == expected_meters


async def test_inches_to_meters():
    inches = 72.0
    expected_meters = 1.83  # 72 inches is approximately 1.83 meters
    result_meters = imperial_to_metric(inches=inches)
    assert round(result_meters, 2) == expected_meters


async def test_fluid_ounces_to_litres():
    fl_oz = 100
    expected_litres = 2.84
    result_litres = imperial_to_metric(fluid_ounces=fl_oz)
    assert round(result_litres, 2) == expected_litres


async def test_fluid_ounces_to_litres_1L():
    fl_oz = 35.19508
    expected_litres = 1
    result_litres = imperial_to_metric(fluid_ounces=fl_oz)
    assert round(result_litres, 2) == expected_litres


@pytest.mark.parametrize(
    ["f", "expected_c"],
    [
        [32, 0],
        [98.6, 37],
        [-40, -40],
    ],
)
async def test_fahrenheit_to_celcius(f: float, expected_c: float):
    c = imperial_to_metric(fahrenheit=f)
    assert c == expected_c


#
# metric to imperial
#


async def test_ml_to_fluid_ounce():
    ml = 100
    expected_fl_oz = 3.520
    result_fl_oz = metric_to_imperial(ml=ml)
    assert round(result_fl_oz, 3) == expected_fl_oz
