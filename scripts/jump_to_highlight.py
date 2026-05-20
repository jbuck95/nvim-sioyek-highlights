#!/usr/bin/env python3
import sys
import subprocess
import sqlite3
from pathlib import Path

def find_and_jump(search_text):
    local_db = Path.home() / ".local/share/sioyek/local.db"
    shared_db = Path.home() / ".local/share/sioyek/shared.db"

    words = search_text.split()
    fuzzy_query = "%" + "%".join(words) + "%"

    try:
        conn = sqlite3.connect(shared_db)
        cursor = conn.cursor()
        query = "SELECT document_path, begin_y FROM highlights WHERE desc LIKE ? LIMIT 1"
        result = cursor.execute(query, (fuzzy_query,)).fetchone()
        conn.close()
    except sqlite3.Error:
        return False

    if not result:
        return False

    doc_hash, begin_y = result

    conn_local = sqlite3.connect(local_db)
    path_res = conn_local.execute("SELECT path FROM document_hash WHERE hash=?", (doc_hash,)).fetchone()
    conn_local.close()

    if not path_res:
        return False
    pdf_path = path_res[0]

    # begin_y in page-relative koordinaten umrechnen
    page_number = None
    in_page_y = None
    try:
        import fitz
        doc = fitz.open(pdf_path)
        remaining = begin_y
        for i in range(doc.page_count):
            height = doc[i].rect.height
            if remaining < height:
                page_number = i
                in_page_y = remaining
                break
            remaining -= height
        doc.close()
    except Exception:
        pass

    if page_number is not None:
        subprocess.Popen([
            "sioyek", pdf_path,
            "--page", str(page_number + 1),
            "--yloc", str(in_page_y)
        ])
    else:
        subprocess.Popen(["sioyek", pdf_path])

    return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        find_and_jump(" ".join(sys.argv[1:]))
