from fastapi import FastAPI, HTTPException, Header
from typing import Optional
from utils.torrent_scraper import search_torrents
from utils.realdebrid import get_streamable_link

app = FastAPI()

@app.get("/search")

@app.get("/")
async def root():
    return {"message": "Eclipse Torrent Addon is running. Use /search?q=..."}


async def search_torrents_endpoint(q: str, authorization: Optional[str] = Header(None)):
    """
    Endpoint per cercare torrent e ottenere un link di streaming.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Real-Debrid API token")
    api_token = authorization.replace("Bearer ", "")

    # 1. Cerca il torrent su 1337x
    torrents = search_torrents(q)
    if not torrents:
        raise HTTPException(status_code=404, detail="No torrents found")
    # Prendi il primo risultato (il più seeded)
    best_match = torrents[0]
    magnet_link = best_match.get("magnet")
    if not magnet_link:
        raise HTTPException(status_code=500, detail="Magnet link not available")
    # 2. Ottieni il link di streaming da Real-Debrid
    stream_url = await get_streamable_link(magnet_link, api_token)
    if not stream_url:
        raise HTTPException(status_code=500, detail="Failed to generate stream URL")
    # 3. Restituisci il risultato
    return {
        "title": best_match["name"],
        "artist": "Unknown Artist", # Da estrarre se possibile
        "stream_url": stream_url,
        "format": "audio/mpeg",
        "quality": "320kbps"
    }
