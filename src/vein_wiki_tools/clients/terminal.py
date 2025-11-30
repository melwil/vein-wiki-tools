async def create_page(name: str, text: str, summary: str):
    print(f"Creating page: {name}")
    print(f"With text: {text}")
    print(f"And summary: {summary}")


async def edit_page(name: str, text: str, summary: str):
    await create_page(name, text, summary)
