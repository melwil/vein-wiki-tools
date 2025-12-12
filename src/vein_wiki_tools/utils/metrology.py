def imperial_to_metric(
    pounds: float | None = None,
    feet: float | None = None,
    inches: float | None = None,
) -> float | None:
    if pounds is not None:
        kilograms = pounds * 0.45359237
        return kilograms
    if inches is not None:
        meters = inches * 0.0254
        return meters
    if feet is not None:
        meters = feet * 0.3048
        return meters

    return None
