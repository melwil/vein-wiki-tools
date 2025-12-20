def imperial_to_metric(
    *,
    pounds: float | None = None,
    feet: float | None = None,
    inches: float | None = None,
    fluid_ounces: float | None = None,
    fahrenheit: float | None = None,
) -> float:
    if pounds is not None:
        return pounds * 0.45359237
    if inches is not None:
        return inches * 0.0254
    if feet is not None:
        return feet * 0.3048
    if fluid_ounces is not None:
        return fluid_ounces * 0.02841306
    if fahrenheit is not None:
        return round((fahrenheit - 32) / (9 / 5), 0)

    raise ValueError("Unknown conversion")


def metric_to_imperial(
    *,
    ml: float | None = None,
) -> float:
    if ml is not None:
        return ml / 28.41306

    raise ValueError("Unknown conversion")
