def imperial_to_metric(
    pounds: float | None = None,
    feet: float | None = None,
    inches: float | None = None,
) -> float:
    if pounds is not None:
        kilograms = round(pounds * 0.45359237, 1)
        return kilograms
    if inches is not None:
        meters = round(inches * 0.0254, 2)
        return meters
    if feet is not None:
        meters = round(feet * 0.3048, 2)
        return meters

    return 0.0
