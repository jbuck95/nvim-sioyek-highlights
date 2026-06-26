#!/usr/bin/env python3
import sys
import subprocess
import sqlite3
import time
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
        result = None

    if not result:
        # Fallback: Kein Highlight in der DB – direkt in Sioyek suchen
        # Versuche PDF-Pfad aus local.db zu finden
        try:
            conn = sqlite3.connect(local_db)
            rows = conn.execute(
                "SELECT path FROM document_hash ORDER BY last_opened DESC LIMIT 5"
            ).fetchall()
            conn.close()
        except sqlite3.Error:
            rows = []

        if rows:
            for row in rows:
                pdf_path = row[0]
                if Path(pdf_path).exists():
                    _sioyek_search(pdf_path, search_text)
                    return True

        print(f"Text '{search_text}' nicht gefunden und kein PDF bekannt.")
        return False

    doc_hash, begin_y = result

    conn_local = sqlite3.connect(local_db)
    path_res = conn_local.execute(
        "SELECT path FROM document_hash WHERE hash=?", (doc_hash,)
    ).fetchone()
    conn_local.close()

    if not path_res:
        return False
    pdf_path = path_res[0]

    # begin_y in page-relative Koordinaten umrechnen
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
        subprocess.Popen(
            ["sioyek", pdf_path, "--page", str(page_number + 1), "--yloc", str(in_page_y)]
        )
    else:
        subprocess.Popen(["sioyek", pdf_path])

    return True


def _sioyek_search(pdf_path, search_text):
    subprocess.Popen(["sioyek", str(pdf_path)])
    time.sleep(0.35)
    # Anführungszeichen = exakte Phrase in Sioyek
    phrase = f'"{search_text}"'
    subprocess.run(
        ["sioyek", "--execute-command", "search", "--execute-command-data", phrase]
    )
    subprocess.Popen(["sioyek", "--execute-command", "next_item"])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)
    search = " ".join(sys.argv[1:])
    # PDF-Pfad als erstes Argument, wenn durch || getrennt (von Analyse-Dateien)
    if "||" in search:
        parts = search.split("||", 1)
        pdf_path = parts[0].strip()
        search_text = parts[1].strip()
        _sioyek_search(pdf_path, search_text)
    else:
        find_and_jump(search)
