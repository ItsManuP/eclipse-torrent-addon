import httpx
from typing import List, Dict, Any

async def search_torrents(query: str) -> List[Dict[str, Any]]:
    try:
        url = f"https://apibay.org/q.php?q={query}&cat=100"
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(url)
            data = r.json()
        results = []
        for item in data:
            if not item.get("name"):
                continue
            info_hash = item["info_hash"]
            magnet = f"magnet:?xt=urn:btih:{info_hash}&dn={item['name']}"
            results.append({
                "name": item["name"],
                "magnet": magnet,
                "seeders": int(item.get("seeders", 0)),
                "leechers": int(item.get("leechers", 0)),
                "size": item.get("size", "0"),
                "info_hash": info_hash
            })
        results.sort(key=lambda x: x["seeders"], reverse=True)
        return results
    except Exception as e:
        print(f"Errore apibay: {e}")
        return []
