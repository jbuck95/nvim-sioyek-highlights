#!/usr/bin/env python3
import re
import sys
import subprocess
import sqlite3
import time
import uuid
from pathlib import Path


def get_doc_hash(pdf_path):
    local_db = Path.home() / ".local/share/sioyek/local.db"
    try:
        conn = sqlite3.connect(str(local_db))
        row = conn.execute(
            "SELECT hash FROM document_hash WHERE path = ?", (str(pdf_path),)
        ).fetchone()
        conn.close()
        return row[0] if row else None
    except sqlite3.Error:
        return None


def get_pdf_path(doc_hash):
    local_db = Path.home() / ".local/share/sioyek/local.db"
    try:
        conn = sqlite3.connect(str(local_db))
        row = conn.execute(
            "SELECT path FROM document_hash WHERE hash = ?", (doc_hash,)
        ).fetchone()
        conn.close()
        return row[0] if row else None
    except sqlite3.Error:
        return None


def search_highlights(search_text, doc_hash=None):
    shared_db = Path.home() / ".local/share/sioyek/shared.db"
    # remove punctuation but keep hyphens (e.g. "BCI-driven")
    words = [re.sub(r'[^\w-]', '', w) for w in search_text.split() if re.sub(r'[^\w-]', '', w)]
    fuzzy = "%" + "%".join(words) + "%"

    try:
        conn = sqlite3.connect(str(shared_db))
        if doc_hash:
            row = conn.execute(
                "SELECT document_path, begin_y FROM highlights "
                "WHERE desc LIKE ? AND document_path = ? LIMIT 1",
                (fuzzy, doc_hash),
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT document_path, begin_y FROM highlights "
                "WHERE desc LIKE ? LIMIT 1",
                (fuzzy,),
            ).fetchone()
        conn.close()
        return row
    except sqlite3.Error:
        return None


def open_at_position(pdf_path, begin_y):
    try:
        import fitz
        doc = fitz.open(pdf_path)
        remaining = begin_y
        for i in range(doc.page_count):
            h = doc[i].rect.height
            if remaining < h:
                page, y = i, remaining
                doc.close()
                subprocess.Popen(
                    ["sioyek", pdf_path, "--page", str(page + 1), "--yloc", str(y)]
                )
                return
            remaining -= h
        doc.close()
    except Exception:
        pass
    subprocess.Popen(["sioyek", pdf_path])


def find_text_position(pdf_path, search_text):
    try:
        import fitz
        doc = fitz.open(pdf_path)
        # Erste 5 Wörter als Suchsignatur (passt auf eine Zeile, unique genug)
        sig_words = search_text.split()[:5]
        if not sig_words:
            doc.close()
            return None
        sig = ' '.join(sig_words)
        offset = 0.0
        for page_num in range(doc.page_count):
            page = doc[page_num]
            rects = page.search_for(sig)
            if rects:
                r = rects[0]
                begin_y = offset + r.y0
                end_y = offset + r.y1
                doc.close()
                return page_num, begin_y, end_y
            offset += page.rect.height
        doc.close()
    except Exception:
        pass
    return None


def create_highlight(doc_hash, search_text, begin_y, end_y):
    shared_db = Path.home() / ".local/share/sioyek/shared.db"
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    uid = str(uuid.uuid4())
    try:
        conn = sqlite3.connect(str(shared_db))
        conn.execute(
            """INSERT INTO highlights
               (document_path, desc, type, begin_x, begin_y, end_x, end_y,
                text_annot, creation_time, modification_time, uuid)
               VALUES (?, ?, 'h', 0, ?, 0, ?, '', ?, ?, ?)""",
            (doc_hash, search_text, begin_y, end_y, now, now, uid),
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error:
        return False


def reverse_highlight_and_jump(pdf_path, search_text):
    pos = find_text_position(pdf_path, search_text)
    if pos is None:
        return False

    page_num, begin_y, end_y = pos
    doc_hash = get_doc_hash(pdf_path)
    if doc_hash and search_text:
        create_highlight(doc_hash, search_text, begin_y, end_y)

    subprocess.Popen(
        ["sioyek", pdf_path, "--page", str(page_num + 1), "--yloc", str(begin_y)]
    )
    return True


def _sioyek_search(pdf_path, search_text):
    sig = ' '.join(search_text.split()[:8])
    subprocess.Popen(["sioyek", str(pdf_path)])
    time.sleep(0.5)
    subprocess.run([
        "sioyek", "--execute-command", "search",
        "--execute-command-data", f'"{sig}"'
    ])
    subprocess.Popen(["sioyek", "--execute-command", "next_item"])


def find_and_jump(search_text, pdf_path=None):
    if pdf_path:
        doc_hash = get_doc_hash(pdf_path)
        result = search_highlights(search_text, doc_hash) if doc_hash else None
        if result:
            open_at_position(pdf_path, result[1])
            return True
        if reverse_highlight_and_jump(pdf_path, search_text):
            return True
        _sioyek_search(pdf_path, search_text)
        return True

    result = search_highlights(search_text)
    if result:
        doc_hash, begin_y = result
        resolved = get_pdf_path(doc_hash)
        if resolved and Path(resolved).exists():
            open_at_position(resolved, begin_y)
            return True

    local_db = Path.home() / ".local/share/sioyek/local.db"
    try:
        conn = sqlite3.connect(str(local_db))
        rows = conn.execute(
            "SELECT path FROM document_hash ORDER BY id DESC LIMIT 5"
        ).fetchall()
        conn.close()
    except sqlite3.Error:
        rows = []

    for row in rows:
        p = row[0]
        if Path(p).exists():
            _sioyek_search(p, search_text)
            return True

    return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)
    query = " ".join(sys.argv[1:])
    if "||" in query:
        parts = query.split("||", 1)
        pdf_path = parts[0].strip()
        search_text = parts[1].strip()
        find_and_jump(search_text, pdf_path)
    else:
        find_and_jump(query)
