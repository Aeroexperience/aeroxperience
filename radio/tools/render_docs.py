"""Turn the SVGs in ../docs into PNG pictures and a printable PDF (needs Playwright + Chrome)."""
import asyncio
import os
import re
from playwright.async_api import async_playwright

here = os.path.dirname(os.path.abspath(__file__))
docs = os.path.join(here, "..", "docs")


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        pg = await b.new_page(device_scale_factor=2)
        for name in ("label_sheet", "panel_preview", "wiring"):
            svg = os.path.join(docs, name + ".svg")
            if not os.path.exists(svg):
                continue
            src = open(svg).read()
            m = re.search(r'width="([\d.]+)(mm)?" height="([\d.]+)(mm)?"', src)
            w, h = float(m.group(1)), float(m.group(3))
            if m.group(2):
                w, h = w * 96 / 25.4, h * 96 / 25.4
            await pg.set_viewport_size({"width": int(w) + 1, "height": int(h) + 1})
            await pg.goto("file://" + os.path.abspath(svg))
            await pg.screenshot(path=os.path.join(docs, name + ".png"))
            if name == "label_sheet":
                await pg.pdf(path=os.path.join(docs, name + ".pdf"), width=m.group(1) + "mm", height=m.group(3) + "mm",
                             print_background=True, margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
            print("rendered", name)
        await b.close()

asyncio.run(main())
