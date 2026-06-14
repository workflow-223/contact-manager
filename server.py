import json
import os
import re
import webbrowser
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from mimetypes import guess_type
from pathlib import Path
from urllib.parse import unquote_plus

DATA_FILE = Path(__file__).parent / "contacts.json"
PORT = 8080


def load_contacts():
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_contacts(contacts):
    with open(DATA_FILE, "w") as f:
        json.dump(contacts, f, indent=2)


def next_id(contacts):
    return max((c["id"] for c in contacts), default=0) + 1


PHONE_RE = re.compile(r"^\+?\d+$")


def validate_phone(raw):
    value = raw.strip()
    if not value:
        return value, None
    if not PHONE_RE.match(value):
        return None, "Phone can only contain digits and an optional + at the start"
    digits = value.lstrip("+")
    if len(digits) < 7 or len(digits) > 15:
        return None, "Phone must have between 7 and 15 digits"
    return value, None


def validate_email(raw):
    value = raw.strip()
    if not value:
        return value, None
    if " " in value:
        return None, "Email cannot contain spaces"
    if value.count("@") != 1:
        return None, "Email must contain exactly one @"
    local, domain = value.split("@")
    if not local:
        return None, "Email must have text before @"
    if not domain or "." not in domain:
        return None, "Email must have a valid domain after @"
    if domain.startswith(".") or domain.endswith("."):
        return None, "Email domain cannot start or end with a dot"
    return value, None


class Handler(SimpleHTTPRequestHandler):
    def _send_json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length))

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _serve_file(self, path):
        filepath = os.path.join(os.getcwd(), path.lstrip("/"))
        if not os.path.exists(filepath) or not os.path.isfile(filepath):
            self.send_error(404)
            return
        mime, _ = guess_type(filepath)
        with open(filepath, "rb") as f:
            body = f.read()
        self.send_response(200)
        self.send_header("Content-Type", mime or "application/octet-stream")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/":
            return self._serve_file("/index.html")

        if self.path.startswith("/api/contacts"):
            contacts = load_contacts()
            q = self._get_query_param("q")
            if q:
                q = q.lower()
                contacts = [
                    c for c in contacts
                    if q in c["name"].lower()
                    or q in c.get("phone", "").lower()
                    or q in c.get("email", "").lower()
                ]
            return self._send_json(contacts)

        self._serve_file(self.path)

    def do_POST(self):
        if self.path == "/api/contacts":
            data = self._read_body()
            name = data.get("name", "").strip()
            if not name:
                return self._send_json({"error": "Name is required"}, 400)
            phone, err = validate_phone(data.get("phone", ""))
            if err:
                return self._send_json({"error": err}, 400)
            email, err = validate_email(data.get("email", ""))
            if err:
                return self._send_json({"error": err}, 400)
            contacts = load_contacts()
            contact = {
                "id": next_id(contacts),
                "name": name,
                "phone": phone,
                "email": email,
                "created_at": datetime.now().isoformat(),
            }
            contacts.append(contact)
            save_contacts(contacts)
            return self._send_json(contact, 201)

        return self._send_json({"error": "Not found"}, 404)

    def do_PATCH(self):
        m = re.match(r"^/api/contacts/(\d+)$", self.path)
        if not m:
            return self._send_json({"error": "Not found"}, 404)
        cid = int(m.group(1))
        data = self._read_body()
        contacts = load_contacts()
        for c in contacts:
            if c["id"] == cid:
                if "name" in data and data["name"].strip():
                    c["name"] = data["name"].strip()
                if "phone" in data:
                    phone, err = validate_phone(data["phone"])
                    if err:
                        return self._send_json({"error": err}, 400)
                    c["phone"] = phone
                if "email" in data:
                    email, err = validate_email(data["email"])
                    if err:
                        return self._send_json({"error": err}, 400)
                    c["email"] = email
                save_contacts(contacts)
                return self._send_json(c)
        return self._send_json({"error": "Not found"}, 404)

    def do_DELETE(self):
        m = re.match(r"^/api/contacts/(\d+)$", self.path)
        if m:
            cid = int(m.group(1))
            contacts = load_contacts()
            before = len(contacts)
            contacts = [c for c in contacts if c["id"] != cid]
            if len(contacts) == before:
                return self._send_json({"error": "Not found"}, 404)
            save_contacts(contacts)
            return self._send_json({"deleted": cid})
        return self._send_json({"error": "Not found"}, 404)

    def _get_query_param(self, name):
        if "?" not in self.path:
            return None
        qs = self.path.split("?", 1)[1]
        for part in qs.split("&"):
            if "=" in part:
                k, v = part.split("=", 1)
                if k == name:
                    return unquote_plus(v)
        return None


def main():
    static_dir = Path(__file__).parent / "static"
    static_dir.mkdir(exist_ok=True)

    os.chdir(static_dir)

    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"  Server running at http://localhost:{PORT}")
    webbrowser.open(f"http://localhost:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")


if __name__ == "__main__":
    main()
