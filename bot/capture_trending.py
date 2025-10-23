import os, datetime, pytz
from pathlib import Path
from playwright.sync_api import sync_playwright

TREND_URLS = ["https://x.com/explore", "https://x.com/explore/tabs/news"]

def capture_trending(storage_state_path, out_dir, timezone="America/New_York"):
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now(pytz.timezone(timezone)).astimezone(pytz.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    file_ts = ts.replace(":","").replace("-","").replace("T","_").replace("Z","Z")
    out_png = os.path.join(out_dir, f"trending_{file_ts}.png")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context(storage_state=storage_state_path,
                                      viewport={"width": 1200, "height": 2200},
                                      device_scale_factor=2)
        page = context.new_page()
        clip = None
        for url in TREND_URLS:
            page.goto(url, wait_until="networkidle")
            try:
                page.get_by_role("tab", name="Trending", exact=False).click(timeout=3000)
                page.wait_for_load_state("networkidle", timeout=3000)
            except Exception:
                pass
            try:
                header = page.get_by_text("Today's News", exact=False).first
                box = header.bounding_box()
                if box:
                    y = max(int(box["y"] - 60), 0)
                    clip = {"x": 0, "y": y, "width": 1200, "height": 1400}
                    break
            except Exception:
                pass
        if clip:
            page.screenshot(path=out_png, clip=clip)
        else:
            page.screenshot(path=out_png, full_page=False)
        context.close(); browser.close()
    return out_png, ts
