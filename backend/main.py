from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# List of bots with their official User-Agents
BOTS = {
    "Normal User": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Googlebot": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Bingbot": "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
    "YandexBot": "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)",
    "DuckDuckBot": "DuckDuckBot/1.0; (+http://duckduckgo.com/duckduckbot.html)",
    "BaiduSpider": "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)",
    "FacebookCrawler": "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)",
    "WhatsAppBot": "WhatsApp/2.19.81 A",
    "AhrefsBot": "Mozilla/5.0 (compatible; AhrefsBot/7.0; +http://ahrefs.com/robot/)",
    "SemrushBot": "Mozilla/5.0 (compatible; SemrushBot/7~bl; +http://www.semrush.com/bot.html)",
    "AppleBot": "Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Safari/600.1.4 (Applebot/0.1)"
}


async def fetch_with_bot(url: str, user_agent: str):
    """
    Fetch URL with tracking redirect chain.
    """

    redirect_chain = []

    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(url, headers={"User-Agent": user_agent})

        # Build redirect chain
        history = response.history

        for h in history:
            redirect_chain.append({"status": h.status_code, "url": str(h.url)})

        # Append final URL
        redirect_chain.append({"status": response.status_code, "url": str(response.url)})

        return {
            "final_url": str(response.url),
            "status": response.status_code,
            "redirects": redirect_chain
        }


@app.get("/check")
async def check_redirect(url: str):
    results = {}

    # Fetch for every bot
    for bot, ua in BOTS.items():
        results[bot] = await fetch_with_bot(url, ua)

    normal_url = results["Normal User"]["final_url"]

    # Detect cloaking
    cloaking_flag = False

    for bot, data in results.items():
        if bot != "Normal User" and data["final_url"] != normal_url:
            cloaking_flag = True

    status = "FAIL" if cloaking_flag else "PASS"

    return {
        "cloaking_status": status,
        "results": results
    }
  