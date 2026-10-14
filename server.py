#!/usr/bin/env python3
"""
LexDigit UCA — Plateforme Simple & Officielle
Licence d'Excellence : Droit Privé et Transformation Digitale (2026-2027)
FSJP El Kelaâ des Sraghna — Université Cadi Ayyad
"""

import json
import mimetypes
import os
import re
import socket
import sqlite3
import subprocess
import threading
import time
import urllib.parse
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "lexdigit_simple.db"
UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

PORT = int(os.environ.get("PORT", "8090"))
PUBLIC_URL = ""

# ──────────────────────────────────────────────────────────────────────
#  Codes Secrets des Professeurs (Espace Professeur Verrouillé)
# ──────────────────────────────────────────────────────────────────────
PROF_CODES = {
    "SALAH2026": {
        "prof_name": "Délégué de Promotion",
        "default_module": "s5-m1",
        "is_admin": True,
        "is_coord": True,
    },
    "COORD2026": {
        "prof_name": "Délégué de Promotion",
        "default_module": "s5-m1",
        "is_admin": True,
        "is_coord": True,
    },
    "DELEGUE2026": {
        "prof_name": "Délégué de Promotion",
        "default_module": "s5-m1",
        "is_admin": True,
        "is_coord": True,
    },
    "FSJP2026": {
        "prof_name": "Pr. LHAROUAL MOHAMED (Coordonnateur)",
        "default_module": "s5-m1",
        "is_admin": True,
    },
    "LHAROUAL2026": {
        "prof_name": "Pr. LHAROUAL MOHAMED",
        "default_module": "s5-m1",
        "is_admin": True,
    },
    "ASSEMAHLI2026": {
        "prof_name": "Pr. ASSEMAHLI SOUKAINA",
        "default_module": "s5-m2",
        "is_admin": False,
    },
    "BEYYOUDH2026": {
        "prof_name": "Pr. BEYYOUDH MED SAMI",
        "default_module": "s5-m3",
        "is_admin": False,
    },
    "BOUSSETTA2026": {
        "prof_name": "Pr. BOUSSETTA FATIM EZZAHRA",
        "default_module": "s5-m4",
        "is_admin": False,
    },
    "RAHMOUNE2026": {
        "prof_name": "Pr. RAHMOUNE NOUHA",
        "default_module": "s5-m5",
        "is_admin": False,
    },
    "CHAKIR2026": {
        "prof_name": "Pr. CHAKIR MOHAMED",
        "default_module": "s5-m6",
        "is_admin": False,
    },
}

# ──────────────────────────────────────────────────────────────────────
#  Modules Officiels S5 (avec Emploi du Temps 2026-2027) & S6
# ──────────────────────────────────────────────────────────────────────
MODULES = [
    # SEMESTRE 5 (Données exactes de l'affiche officielle FSJP El Kelaâ)
    {
        "id": "s5-m1",
        "semester": "S5",
        "title": "Droit des affaires",
        "prof": "Pr. LHAROUAL MOHAMED",
        "salle": "Salle 8",
        "jour": "LUNDI",
        "horaire": "13h00 - 14h30",
        "icon": "fa-briefcase",
    },
    {
        "id": "s5-m5",
        "semester": "S5",
        "title": "Droit du travail numérique",
        "prof": "Pr. RAHMOUNE NOUHA",
        "salle": "Salle 10",
        "jour": "LUNDI",
        "horaire": "11h30 - 13h00",
        "icon": "fa-laptop-file",
    },
    {
        "id": "s5-m6",
        "semester": "S5",
        "title": "Gouvernance et éthique du numérique",
        "prof": "Pr. CHAKIR MOHAMED",
        "salle": "Salle 5",
        "jour": "MERCREDI",
        "horaire": "13h00 - 14h30",
        "icon": "fa-shield-halved",
    },
    {
        "id": "s5-m4",
        "semester": "S5",
        "title": "Droit du commerce électronique",
        "prof": "Pr. BOUSSETTA FATIM EZZAHRA",
        "salle": "Salle 5",
        "jour": "MERCREDI",
        "horaire": "11h30 - 13h00",
        "icon": "fa-cart-shopping",
    },
    {
        "id": "s5-m2",
        "semester": "S5",
        "title": "Droit processuel",
        "prof": "Pr. ASSEMAHLI SOUKAINA",
        "salle": "Salle 2BIS",
        "jour": "JEUDI",
        "horaire": "16h00 - 17h30",
        "icon": "fa-scale-balanced",
    },
    {
        "id": "s5-m3",
        "semester": "S5",
        "title": "Droit des contrats numériques",
        "prof": "Pr. BEYYOUDH MED SAMI",
        "salle": "Salle 2BIS",
        "jour": "JEUDI",
        "horaire": "17h30 - 19h00",
        "icon": "fa-file-signature",
    },
    {
        "id": "s5-m7",
        "semester": "S5",
        "title": "Langues étrangères (Anglais)",
        "prof": "À programmer",
        "salle": "—",
        "jour": "À définir",
        "horaire": "—",
        "icon": "fa-language",
    },
    # SEMESTRE 6
    {
        "id": "s6-m1",
        "semester": "S6",
        "title": "Culture entrepreneuriale",
        "prof": "Équipe Pédagogique FSJP",
        "salle": "S6",
        "jour": "Semestre 6",
        "horaire": "—",
        "icon": "fa-rocket",
    },
    {
        "id": "s6-m2",
        "semester": "S6",
        "title": "Éthique et droit de l’intelligence artificielle",
        "prof": "Équipe Pédagogique FSJP",
        "salle": "S6",
        "jour": "Semestre 6",
        "horaire": "—",
        "icon": "fa-brain",
    },
    {
        "id": "s6-m3",
        "semester": "S6",
        "title": "Droit pénal des affaires",
        "prof": "Équipe Pédagogique FSJP",
        "salle": "S6",
        "jour": "Semestre 6",
        "horaire": "—",
        "icon": "fa-gavel",
    },
    {
        "id": "s6-m4",
        "semester": "S6",
        "title": "Droit de la consommation numérique",
        "prof": "Équipe Pédagogique FSJP",
        "salle": "S6",
        "jour": "Semestre 6",
        "horaire": "—",
        "icon": "fa-user-check",
    },
    {
        "id": "s6-m5",
        "semester": "S6",
        "title": "Droit bancaire et transaction monétaire",
        "prof": "Équipe Pédagogique FSJP",
        "salle": "S6",
        "jour": "Semestre 6",
        "horaire": "—",
        "icon": "fa-building-columns",
    },
    {
        "id": "s6-m6",
        "semester": "S6",
        "title": "Langues étrangères (Anglais)",
        "prof": "Équipe Pédagogique FSJP",
        "salle": "S6",
        "jour": "Semestre 6",
        "horaire": "—",
        "icon": "fa-language",
    },
    {
        "id": "s6-m7",
        "semester": "S6",
        "title": "Modes alternatifs de règlement de différends (MARD)",
        "prof": "Équipe Pédagogique FSJP",
        "salle": "S6",
        "jour": "Semestre 6",
        "horaire": "—",
        "icon": "fa-handshake",
    },
]

for _idx, _m in enumerate(MODULES, 1):
    _m.setdefault("code", _m["id"].upper())
    _m.setdefault("room", _m.get("salle", "—"))
    _m.setdefault("professor", _m.get("prof", "—"))
    _j = _m.get("jour", "")
    _h = _m.get("horaire", "")
    _m.setdefault("schedule", f"{_j} · {_h}" if _h and _h != "—" else _j)
    _clean_title = re.sub(r"[^A-Za-z0-9]+", "_", _m["title"]).strip("_")
    _m["folder_name"] = f"{_m['id'].upper()}_{_clean_title}"

PDF_DROP_DIR = BASE_DIR / "PDF_DES_PROFS"
PDF_DROP_DIR.mkdir(parents=True, exist_ok=True)
for _m in MODULES:
    (PDF_DROP_DIR / _m["folder_name"]).mkdir(parents=True, exist_ok=True)


def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            module_id TEXT NOT NULL,
            prof_name TEXT NOT NULL,
            status_type TEXT NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            module_id TEXT NOT NULL,
            title TEXT NOT NULL,
            prof_name TEXT NOT NULL,
            filename TEXT NOT NULL,
            original_name TEXT NOT NULL,
            file_size_kb REAL DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            module_id TEXT NOT NULL,
            author_name TEXT NOT NULL,
            author_role TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def parse_multipart(headers, body: bytes):
    ctype = headers.get("Content-Type", "")
    m = re.search(r"boundary=([^;]+)", ctype)
    if not m:
        return {}, {}
    boundary = m.group(1).strip().strip('"').encode("utf-8")
    parts = body.split(b"--" + boundary)
    fields = {}
    files = {}
    for part in parts[1:]:
        if part.startswith(b"--") or not part.strip():
            continue
        if b"\r\n\r\n" not in part:
            continue
        head_raw, content = part.split(b"\r\n\r\n", 1)
        if content.endswith(b"\r\n"):
            content = content[:-2]
        head_str = head_raw.decode("utf-8", errors="replace")
        name_m = re.search(r'name="([^"]+)"', head_str)
        if not name_m:
            continue
        field_name = name_m.group(1)
        fn_m = re.search(r'filename="([^"]*)"', head_str)
        if fn_m and fn_m.group(1):
            files[field_name] = {
                "filename": Path(fn_m.group(1)).name,
                "content": content,
            }
        else:
            fields[field_name] = content.decode("utf-8", errors="replace").strip()
    return fields, files


def verify_code(code: str):
    c = (code or "").strip().upper()
    return PROF_CODES.get(c)


class SimpleLexHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def _send_json(self, data, status=200):
        raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def do_HEAD(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        if path in ("/", "/index.html"):
            raw = (BASE_DIR / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            return
        if path == "/api/state":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            return
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path in ("/", "/index.html"):
            raw = (BASE_DIR / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
            return

        if path == "/robots.txt":
            rf = BASE_DIR / "robots.txt"
            raw = rf.read_bytes() if rf.exists() else b"User-agent: *\nAllow: /\n"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
            return

        if path == "/sitemap.xml":
            sf = BASE_DIR / "sitemap.xml"
            raw = sf.read_bytes() if sf.exists() else b""
            self.send_response(200)
            self.send_header("Content-Type", "application/xml; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
            return

        # Favicons and static branding assets
        clean_name = path.lstrip("/")
        if clean_name in (
            "favicon.ico", "favicon-32x32.png", "favicon-48x48.png",
            "favicon-192x192.png", "apple-touch-icon.png", "logo_filiere_droit_digital.jpg"
        ):
            sf = BASE_DIR / clean_name
            if sf.exists():
                ext = sf.suffix.lower()
                mime = "image/x-icon" if ext == ".ico" else ("image/png" if ext == ".png" else "image/jpeg")
                raw = sf.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", mime)
                self.send_header("Content-Length", str(len(raw)))
                self.send_header("Cache-Control", "public, max-age=86400")
                self.end_headers()
                self.wfile.write(raw)
                return

        if path == "/api/state":
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT * FROM announcements ORDER BY id DESC")
            announcements = []
            for r in cur.fetchall():
                d = dict(r)
                d.setdefault("date_label", d.get("title", ""))
                announcements.append(d)
            cur.execute("SELECT * FROM documents ORDER BY id DESC")
            documents = []
            for r in cur.fetchall():
                d = dict(r)
                d.setdefault("size_kb", d.get("file_size_kb", 0))
                d.setdefault("url", f"/uploads/{d.get('filename', '')}")
                documents.append(d)
            cur.execute("SELECT * FROM comments ORDER BY id ASC")
            comments = []
            for r in cur.fetchall():
                d = dict(r)
                d.setdefault("author", d.get("author_name", "Étudiant"))
                d.setdefault("role", d.get("author_role", "student"))
                comments.append(d)
            conn.close()
            self._send_json({
                "modules": MODULES,
                "announcements": announcements,
                "documents": documents,
                "comments": comments,
                "public_url": PUBLIC_URL,
            })
            return

        if path.startswith("/uploads/"):
            rel_name = urllib.parse.unquote(path[len("/uploads/"):])
            safe_name = Path(rel_name).name
            fpath = UPLOADS_DIR / safe_name
            if not fpath.exists() or not fpath.is_file():
                self.send_error(404, "File not found")
                return
            mime, _ = mimetypes.guess_type(str(fpath))
            mime = mime or "application/octet-stream"
            raw = fpath.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(len(raw)))
            self.send_header("Content-Disposition", f'inline; filename="{safe_name}"')
            self.end_headers()
            self.wfile.write(raw)
            return

        self.send_error(404, "Not Found")

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        length = int(self.headers.get("Content-Length", "0") or "0")
        body = self.rfile.read(length) if length > 0 else b""
        now_str = datetime.now().strftime("%d/%m/%Y à %H:%M")

        # 1. Verify Professor Access Code
        if path == "/api/prof/login":
            payload = json.loads(body.decode("utf-8"))
            info = verify_code(payload.get("code") or payload.get("access_code") or "")
            if not info:
                self._send_json({"ok": False, "error": "Code d'accès Professeur incorrect."}, status=403)
                return
            self._send_json({
                "ok": True,
                "prof_name": info["prof_name"],
                "default_module": info["default_module"],
                "module_id": info["default_module"],
            })
            return

        # 2. Post Professor Announcement (Requires Valid Prof Code)
        if path == "/api/announcements":
            payload = json.loads(body.decode("utf-8"))
            info = verify_code(payload.get("code") or payload.get("access_code") or "")
            if not info:
                self._send_json({"ok": False, "error": "Accès réservé aux professeurs."}, status=403)
                return
            conn = get_db()
            cur = conn.cursor()
            cur.execute(
                """INSERT INTO announcements (module_id, prof_name, status_type, title, message, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    payload.get("module_id", "s5-m1"),
                    payload.get("prof_name") or info["prof_name"],
                    payload.get("status_type", "present"),
                    (payload.get("title") or payload.get("date_label") or "").strip(),
                    payload.get("message", "").strip(),
                    now_str,
                ),
            )
            new_id = cur.lastrowid
            conn.commit()
            conn.close()
            self._send_json({"ok": True, "id": new_id})
            return

        # 3. Delete Announcement (Requires Valid Prof Code)
        if path == "/api/announcements/delete":
            payload = json.loads(body.decode("utf-8"))
            if not verify_code(payload.get("code") or payload.get("access_code") or ""):
                self._send_json({"ok": False, "error": "Accès refusé."}, status=403)
                return
            conn = get_db()
            if payload.get("purge_all"):
                conn.execute("DELETE FROM announcements")
            else:
                raw_id = str(payload.get("id", "")).strip()
                msg_text = str(payload.get("message", "")).strip()
                if raw_id.isdigit():
                    conn.execute("DELETE FROM announcements WHERE id = ?", (int(raw_id),))
                if msg_text:
                    conn.execute("DELETE FROM announcements WHERE message = ?", (msg_text,))
            conn.commit()
            conn.close()
            self._send_json({"ok": True})
            return

        # 4. Upload PDF by Professor (Requires Valid Prof Code)
        if path == "/api/upload":
            fields, files = parse_multipart(self.headers, body)
            info = verify_code(fields.get("code") or fields.get("access_code") or "")
            if not info:
                self._send_json({"ok": False, "error": "Code Professeur invalide."}, status=403)
                return
            file_item = files.get("file")
            if not file_item or not file_item["content"]:
                self._send_json({"ok": False, "error": "Aucun fichier sélectionné."}, status=400)
                return

            orig_name = file_item["filename"]
            clean_name = re.sub(r"[^A-Za-z0-9._-]", "_", orig_name)
            unique_name = f"{int(time.time())}_{clean_name}"
            dest = UPLOADS_DIR / unique_name
            dest.write_bytes(file_item["content"])
            size_kb = round(len(file_item["content"]) / 1024, 1)
            prof_name = fields.get("prof_name") or info["prof_name"]
            mod_id = fields.get("module_id", info["default_module"])
            doc_title = fields.get("title") or orig_name

            conn = get_db()
            cur = conn.cursor()
            cur.execute(
                """INSERT INTO documents (module_id, title, prof_name, filename, original_name, file_size_kb, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (mod_id, doc_title, prof_name, unique_name, orig_name, size_kb, now_str),
            )
            new_doc_id = cur.lastrowid
            conn.commit()
            conn.close()
            self._send_json({
                "ok": True,
                "document": {
                    "id": new_doc_id,
                    "filename": unique_name,
                    "title": doc_title,
                    "prof_name": prof_name,
                    "module_id": mod_id,
                    "file_size": f"{size_kb} Ko",
                    "uploaded_at": now_str
                }
            })
            return

        # 5. Delete PDF (Requires Valid Prof Code)
        if path == "/api/documents/delete":
            payload = json.loads(body.decode("utf-8"))
            if not verify_code(payload.get("code") or payload.get("access_code") or ""):
                self._send_json({"ok": False, "error": "Accès refusé."}, status=403)
                return
            conn = get_db()
            cur = conn.cursor()
            files_to_remove = set()
            if payload.get("purge_all"):
                cur.execute("SELECT filename, original_name FROM documents")
                for r in cur.fetchall():
                    if r["filename"]:
                        files_to_remove.add(r["filename"])
                    if r["original_name"]:
                        files_to_remove.add(r["original_name"])
                conn.execute("DELETE FROM documents")
            else:
                raw_id = str(payload.get("id", "")).strip()
                filename = str(payload.get("filename", "")).strip()
                title = str(payload.get("title", "")).strip()
                if filename:
                    files_to_remove.add(filename)
                if raw_id.isdigit():
                    cur.execute("SELECT filename, original_name FROM documents WHERE id = ?", (int(raw_id),))
                    for r in cur.fetchall():
                        if r["filename"]:
                            files_to_remove.add(r["filename"])
                        if r["original_name"]:
                            files_to_remove.add(r["original_name"])
                    conn.execute("DELETE FROM documents WHERE id = ?", (int(raw_id),))
                if filename:
                    cur.execute("SELECT filename, original_name FROM documents WHERE filename = ? OR original_name = ?", (filename, filename))
                    for r in cur.fetchall():
                        if r["filename"]:
                            files_to_remove.add(r["filename"])
                        if r["original_name"]:
                            files_to_remove.add(r["original_name"])
                    conn.execute("DELETE FROM documents WHERE filename = ? OR original_name = ?", (filename, filename))
                if title:
                    cur.execute("SELECT filename, original_name FROM documents WHERE title = ?", (title,))
                    for r in cur.fetchall():
                        if r["filename"]:
                            files_to_remove.add(r["filename"])
                        if r["original_name"]:
                            files_to_remove.add(r["original_name"])
                    conn.execute("DELETE FROM documents WHERE title = ?", (title,))
            conn.commit()
            conn.close()

            for fname in files_to_remove:
                try:
                    up_file = UPLOADS_DIR / Path(fname).name
                    if up_file.exists() and up_file.is_file():
                        up_file.unlink()
                except Exception:
                    pass
                try:
                    for mod_dir in PDF_DROP_DIR.iterdir():
                        if mod_dir.is_dir():
                            drop_file = mod_dir / Path(fname).name
                            if drop_file.exists() and drop_file.is_file():
                                drop_file.unlink()
                except Exception:
                    pass

            self._send_json({"ok": True})
            return

        # 6. Post Comment / Question inside a Module (Students & Verified Profs)
        if path == "/api/comments":
            payload = json.loads(body.decode("utf-8"))
            role = "student"
            author = (payload.get("author_name") or payload.get("author") or "Étudiant").strip()
            prof_info = verify_code(payload.get("code") or payload.get("access_code") or "")
            if prof_info and (payload.get("as_prof") or payload.get("role") == "prof"):
                role = "prof"
                author = prof_info["prof_name"]
            conn = get_db()
            conn.execute(
                """INSERT INTO comments (module_id, author_name, author_role, message, created_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    payload.get("module_id", "s5-m1"),
                    author,
                    role,
                    payload.get("message", "").strip(),
                    now_str,
                ),
            )
            conn.commit()
            conn.close()
            self._send_json({"ok": True})
            return

        self.send_error(404, "Not Found")


def _get_lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def sync_prof_pdf_folders():
    """Watch PDF_DES_PROFS/<Module>/ folders and auto-import any dropped PDF/DOCX/PPTX into the site."""
    allowed_exts = {".pdf", ".doc", ".docx", ".ppt", ".pptx"}
    while True:
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT original_name, module_id FROM documents")
            existing = {(r["original_name"], r["module_id"]) for r in cur.fetchall()}
            now_str = datetime.now().strftime("%d/%m/%Y à %H:%M")

            for m in MODULES:
                mod_dir = PDF_DROP_DIR / m["folder_name"]
                if not mod_dir.exists():
                    mod_dir.mkdir(parents=True, exist_ok=True)
                for fpath in mod_dir.iterdir():
                    if not fpath.is_file() or fpath.suffix.lower() not in allowed_exts:
                        continue
                    orig_name = fpath.name
                    if (orig_name, m["id"]) in existing:
                        continue
                    raw = fpath.read_bytes()
                    if not raw:
                        continue
                    clean_name = re.sub(r"[^A-Za-z0-9._-]", "_", orig_name)
                    unique_name = f"{int(time.time())}_{clean_name}"
                    dest = UPLOADS_DIR / unique_name
                    dest.write_bytes(raw)
                    size_kb = round(len(raw) / 1024, 1)
                    doc_title = fpath.stem.replace("_", " ")
                    prof_name = m.get("prof", "Professeur")

                    cur.execute(
                        """INSERT INTO documents (module_id, title, prof_name, filename, original_name, file_size_kb, created_at)
                           VALUES (?, ?, ?, ?, ?, ?, ?)""",
                        (m["id"], doc_title, prof_name, unique_name, orig_name, size_kb, now_str),
                    )
                    conn.commit()
                    existing.add((orig_name, m["id"]))
                    print(f"[AUTO-PDF] Ajout automatique de '{orig_name}' dans {m['title']}", flush=True)
            conn.close()
        except Exception as e:
            print(f"[WARN] Auto-PDF sync: {e}", flush=True)
        time.sleep(5)


def start_cloudflare_tunnel():
    """Launch free Cloudflare HTTPS tunnel (https://*.trycloudflare.com) with 24/7 auto-reconnect."""
    global PUBLIC_URL
    cf_bin = BASE_DIR / "cloudflared.exe"
    if not cf_bin.exists():
        return
    url_re = re.compile(r"(https://[a-zA-Z0-9-]+\.trycloudflare\.com)")
    while True:
        proc = None
        try:
            proc = subprocess.Popen(
                [str(cf_bin), "tunnel", "--url", f"http://127.0.0.1:{PORT}", "--no-autoupdate"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="ignore",
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
            for line in proc.stdout:
                m = url_re.search(line)
                if m and not m.group(1).startswith("https://api."):
                    PUBLIC_URL = m.group(1)
                    try:
                        (BASE_DIR / "LIEN_PUBLIC.txt").write_text(PUBLIC_URL + "\n", encoding="utf-8")
                        desktop_dir = Path.home() / "Desktop"
                        if desktop_dir.exists():
                            (desktop_dir / "LIEN_SITE_LEXDIGIT.txt").write_text(
                                f"====================================================================\n"
                                f"  LEXDIGIT UCA — FSJP EL KELAÂ DES SRAGHNA (2026-2027)\n"
                                f"  Plateforme Licence Droit Privé et Transformation Digitale\n"
                                f"====================================================================\n\n"
                                f"🌐 LIEN PUBLIC MONDIAL (Accessible partout : 4G / 5G / Téléphone / WiFi) :\n"
                                f"{PUBLIC_URL}\n\n"
                                f"💻 LIEN LOCAL (Sur ce PC uniquement) :\n"
                                f"http://127.0.0.1:{PORT}\n\n"
                                f"ℹ️ Ce fichier et le raccourci sur votre bureau se mettent à jour automatiquement !\n",
                                encoding="utf-8",
                            )
                            (desktop_dir / "LexDigit_Site_Fac.url").write_text(
                                f"[InternetShortcut]\nURL={PUBLIC_URL}\nIconIndex=0\n",
                                encoding="utf-8",
                            )
                    except Exception as err:
                        print(f"[WARN] Desktop shortcut update: {err}", flush=True)
                    print("\n" + "=" * 68, flush=True)
                    print("[PUBLIC HTTPS] LIEN PUBLIC MONDIAL (4G / 5G / WiFi - 100% GRATUIT) :", flush=True)
                    print(f"-> {PUBLIC_URL}", flush=True)
                    print("=" * 68 + "\n", flush=True)
            proc.wait()
        except Exception as e:
            if proc:
                try:
                    proc.terminate()
                except Exception:
                    pass
            print(f"[WARN] Tunnel Cloudflare reconnexion dans 5s: {e}", flush=True)
        time.sleep(5)


def main():
    init_db()
    threading.Thread(target=sync_prof_pdf_folders, daemon=True).start()
    server = ThreadingHTTPServer(("0.0.0.0", PORT), SimpleLexHandler)
    url = f"http://127.0.0.1:{PORT}"
    lan_url = f"http://{_get_lan_ip()}:{PORT}"
    print(f"Serveur LexDigit UCA demarre sur :", flush=True)
    print(f"  - PC Local : {url}", flush=True)
    print(f"  - WiFi LAN : {lan_url}", flush=True)
    print(f"  - Dossier Auto-PDF Profs : {PDF_DROP_DIR}", flush=True)
    if os.environ.get("NO_TUNNEL") != "1":
        threading.Thread(target=start_cloudflare_tunnel, daemon=True).start()
    if os.environ.get("NO_BROWSER") != "1":
        try:
            webbrowser.open(url)
        except Exception:
            pass
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
