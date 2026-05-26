import os
import cloudscraper
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException

app = FastAPI()

def search_1337x(query: str):
    """
    Cerca un torrent su 1337x e restituisce le informazioni del primo risultato valido.
    """
    print(f"[LOG] Avvio ricerca per: {query}")
    
    # 1. Prepara la richiesta
    search_url = f"https://1337x.to/search/{query}/1/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    scraper = cloudscraper.create_scraper()
    
    # 2. Esegue la richiesta
    try:
        response = scraper.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"[ERROR] Richiesta fallita: {e}")
        return None

    # 3. Analizza l'HTML della pagina dei risultati
    soup = BeautifulSoup(response.text, 'html.parser')
    # Cerca la prima riga della tabella dei risultati (escludendo l'header)
    first_row = soup.select('tbody tr')
    if not first_row:
        print("[WARN] Nessun risultato trovato.")
        return None

    # Estrae il link alla pagina del torrent
    torrent_link_tag = first_row[0].select_one('td.name a[href*="/torrent/"]')
    if not torrent_link_tag:
        return None
    torrent_page_url = "https://1337x.to" + torrent_link_tag.get('href')
    
    # 4. Visita la pagina del torrent per ottenere il magnet link
    torrent_page_response = scraper.get(torrent_page_url, headers=headers, timeout=10)
    torrent_page_soup = BeautifulSoup(torrent_page_response.text, 'html.parser')
    magnet_link_tag = torrent_page_soup.select_one('a[href*="magnet:?xt=urn:btih:"]')
    
    if not magnet_link_tag:
        print("[WARN] Magnet link non trovato.")
        return None
        
    magnet_link = magnet_link_tag.get('href')
    print(f"[LOG] 🔗 Magnet link trovato: {magnet_link[:50]}...")
    return magnet_link

@app.get("/search")
async def search_endpoint(q: str):
    """
    Endpoint principale per la ricerca.
    """
    if not q:
        raise HTTPException(status_code=400, detail="Parametro 'q' mancante")
    
    magnet_link = search_1337x(q)
    if not magnet_link:
        raise HTTPException(status_code=404, detail="Nessun torrent trovato")
    
    return {"magnet": magnet_link}

@app.get("/")
async def root():
    return {"status": "ok", "message": "API di ricerca torrent per Eclipse Music"}
