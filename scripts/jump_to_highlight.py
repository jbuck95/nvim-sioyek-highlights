#!/usr/bin/env python3
import sys
import subprocess
import sqlite3
import time
from pathlib import Path

def find_and_jump(search_text):
    local_db = Path.home() / ".local/share/sioyek/local.db"
    shared_db = Path.home() / ".local/share/sioyek/shared.db"
    
    # Fuzzy-Pattern erstellen: "Of course we" -> "%Of%course%we%"
    words = search_text.split()
    fuzzy_query = "%" + "%".join(words) + "%"

    try:
        conn = sqlite3.connect(shared_db)
        cursor = conn.cursor()
        query = "SELECT document_path FROM highlights WHERE desc LIKE ? LIMIT 1"
        result = cursor.execute(query, (fuzzy_query,)).fetchone()
        conn.close()
    except sqlite3.Error:
        return False
    
    if not result:
        return False
    
    doc_hash = result[0]
    
    conn_local = sqlite3.connect(local_db)
    path_res = conn_local.execute("SELECT path FROM document_hash WHERE hash=?", (doc_hash,)).fetchone()
    conn_local.close()
    
    if not path_res: return False
    pdf_path = path_res[0]

    try:
        # Sioyek starten/fokussieren
        subprocess.Popen(["sioyek", pdf_path])
        time.sleep(0.35) # Latenz für Wayland/Hyprland
        
        # 1. Suche ausführen
        # 2. Zum Treffer springen (next_item)
        # 3. An Seitenbreite anpassen (fit_to_page_width)
        subprocess.run([
            "sioyek", 
            "--execute-command", "search", 
            "--execute-command-data", search_text,
            "--execute-command", "next_item",
            "--execute-command", "fit_to_page_width"
        ])
        
        return True
    except Exception:
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        find_and_jump(" ".join(sys.argv[1:]))
