import re
from typing import List, Dict, Any, Optional
from scrapers.x1337 import Scraper1337, Params1337, Category1337, Order1337

# Inizializza lo scraper di 1337x
scraper_1337 = Scraper1337()

def search_torrents(query: str) -> List[Dict[str, Any]]:
    """
    Cerca torrent su 1337x per una data query.
    Restituisce una lista di dizionari, ciascuno contenente le info di un torrent.
    """
    try:
        print(f"[LOG] 🔍 Ricerca su 1337x per: '{query}'")
        # Configura i parametri di ricerca: nome, categoria Musical, ordine per seeders
        params = Params1337(
            name=query,
            category=Category1337.MUSIC,
            order_column=Order1337.SEEDERS,
            order_ascending=False
        )
        # Esegue la ricerca
        results = scraper_1337.find_torrents(params, (1,)) # limitato alla prima pagina
        print(f"[LOG] ➡️ Trovati {len(results)} risultati su 1337x.")
        # Pulisce e restituisce i risultati
        torrents_list = []
        for torrent in results:
            # Pulisce il nome del torrent: rimuove estensioni video comuni
            name_clean = re.sub(r'\.(mkv|mp4|avi|webm|mov|flv|wmv)$', '', torrent.name, flags=re.IGNORECASE)
            torrents_list.append({
                'name': name_clean,
                'magnet': torrent.magnet,
                'seeders': torrent.seeders,
                'leechers': torrent.leechers,
                'size': torrent.size,
                'info_hash': extract_info_hash(torrent.magnet) if torrent.magnet else None
            })
        return torrents_list
    except Exception as e:
        print(f"[ERROR] ❌ Errore durante la ricerca su 1337x: {e}")
        return []

def extract_info_hash(magnet_link: str) -> Optional[str]:
    """Estrae l'info hash da un link magnet."""
    match = re.search(r'btih:([a-fA-F0-9]{40})', magnet_link)
    return match.group(1) if match else None