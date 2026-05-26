import cloudscraper
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional

# --- Costanti e Configurazione ---
BASE_URL = "https://www.1377x.to"  # Dominio principale di 1337x, aggiornabile se necessario
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Inizializza lo scraper una volta all'avvio del modulo
scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True,
    }
)

def search_torrents(query: str, category: str = "music", page: int = 1) -> List[Dict[str, Any]]:
    """
    Cerca torrent su 1337x (www.1377x.to).

    Args:
        query (str): Termine di ricerca.
        category (str): Categoria per filtrare i risultati. Di default usa 'music'.
        page (int): Numero di pagina dei risultati.

    Returns:
        List[Dict[str, Any]]: Lista di dizionari, ciascuno contenente le info di un torrent.
    """
    try:
        # 1. Costruzione dell'URL di ricerca
        # Esempio: https://www.1377x.to/search/music/query/1/
        search_url = f"{BASE_URL}/search/{category}/{query}/{page}/"
        headers = {"User-Agent": USER_AGENT}
        print(f"[LOG] 🔍 Invio richiesta a 1337x: {search_url}")

        # 2. Esecuzione della richiesta HTTP
        response = scraper.get(search_url, headers=headers, timeout=20)
        response.raise_for_status()
        print(f"[LOG] ✅ Richiesta completata (status: {response.status_code})")

        # 3. Parsing della pagina HTML con BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")
        # Selettori CSS basati sulla struttura della tabella dei risultati di 1337x
        torrent_rows = soup.select("table.table-list tbody tr")

        torrents = []
        for row in torrent_rows:
            # Estrae il link alla pagina del torrent e il nome
            link_tag = row.select_one("td.coll-1 a[href*='/torrent/']")
            if not link_tag:
                continue
            torrent_url = BASE_URL + link_tag.get("href")
            title = link_tag.get_text(strip=True)

            # Estrae altri dettagli
            seeders_tag = row.select_one("td.coll-2")
            leechers_tag = row.select_one("td.coll-3")
            size_tag = row.select_one("td.coll-4")
            time_tag = row.select_one("td.coll-date")
            uploader_tag = row.select_one("td.coll-5")

            seeders = int(seeders_tag.get_text(strip=True)) if seeders_tag and seeders_tag.get_text(strip=True).isdigit() else 0
            leechers = int(leechers_tag.get_text(strip=True)) if leechers_tag and leechers_tag.get_text(strip=True).isdigit() else 0
            size = size_tag.get_text(strip=True) if size_tag else "N/A"
            time = time_tag.get_text(strip=True) if time_tag else "N/A"
            uploader = uploader_tag.get_text(strip=True) if uploader_tag else "N/A"

            # Ottieni il magnet link dalla pagina dei dettagli del torrent
            magnet_link = _get_magnet_link(torrent_url)

            torrents.append({
                'name': title,
                'magnet': magnet_link,
                'seeders': seeders,
                'leechers': leechers,
                'size': size,
                'time': time,
                'uploader': uploader,
                'info_hash': _extract_info_hash(magnet_link) if magnet_link else None
            })

        print(f"[LOG] ➡️ Trovati {len(torrents)} torrent su 1337x per la query '{query}'")
        # Ordina per seeders (dai più alti ai più bassi)
        torrents.sort(key=lambda x: x['seeders'], reverse=True)
        return torrents

    except Exception as e:
        print(f"[ERROR] ❌ Errore nella ricerca su 1337x: {e}")
        return []

def _get_magnet_link(torrent_url: str) -> Optional[str]:
    """
    Visita la pagina dei dettagli di un torrent per estrarre il link magnet.
    """
    try:
        headers = {"User-Agent": USER_AGENT}
        response = scraper.get(torrent_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        # Cerca il primo link che inizia con 'magnet:'
        magnet_link_tag = soup.select_one('a[href^="magnet:?xt=urn:btih:"]')
        if magnet_link_tag:
            return magnet_link_tag.get("href")
        else:
            print(f"[WARN] ⚠️ Link magnet non trovato per {torrent_url}")
            return None
    except Exception as e:
        print(f"[ERROR] ❌ Errore nel recupero del magnet link da {torrent_url}: {e}")
        return None

def _extract_info_hash(magnet_link: str) -> Optional[str]:
    """Estrae l'info hash (BTIH) da un link magnet."""
    import re
    match = re.search(r'btih:([a-fA-F0-9]{40})', magnet_link)
    return match.group(1) if match else None
