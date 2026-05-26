# api/search.py
import os
from fastapi import FastAPI, HTTPException
import httpx

app = FastAPI()

async def search_apibay(query: str):
    url = f"https://apibay.org/q.php?q={query}&cat=100"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url, headers=headers)
        if resp.status_code != 200:
            raise Exception(f"apibay error {resp.status_code}")
        data = resp.json()
    results = []
    for item in data:
        if not item.get("name"):
            continue
        results.append({
            "name": item["name"],
            "magnet": f"magnet:?xt=urn:btih:{item['info_hash']}&dn={item['name']}",
            "seeders": int(item.get("seeders", 0))
        })
    results.sort(key=lambda x: x["seeders"], reverse=True)
    return results

@app.get("/search")
async def search_endpoint(q: str):
    if not q:
        raise HTTPException(400, "Missing q parameter")
    try:
        torrents = await search_apibay(q)
        if not torrents:
            raise HTTPException(404, "No torrents found")
        best = torrents[0]
        return {
            "title": best["name"],
            "magnet": best["magnet"],
            "seeders": best["seeders"]
        }
    except Exception as e:
        raise HTTPException(500, f"Search error: {str(e)}")

@app.get("/")
async def root():
    return {"status": "ok"}
