import argparse
import json
import os
import sys
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "contacts.json")


def load_contacts():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_contacts(contacts):
    with open(DATA_FILE, "w") as f:
        json.dump(contacts, f, indent=2)


def next_id(contacts):
    return max((c["id"] for c in contacts), default=0) + 1


def cmd_add(args):
    contacts = load_contacts()
    contact = {
        "id": next_id(contacts),
        "name": args.name,
        "phone": args.phone,
        "email": args.email,
        "created_at": datetime.now().isoformat(),
    }
    contacts.append(contact)
    save_contacts(contacts)
    print(f"Contact added (id={contact['id']})")


def cmd_list(args):
    contacts = load_contacts()
    if not contacts:
        print("No contacts found.")
        return

    sort_key = args.sort or "name"
    reverse = args.reverse
    contacts = sorted(contacts, key=lambda c: c.get(sort_key, ""), reverse=reverse)

    for c in contacts:
        print(f"{c['id']:>4}  {c['name']:<20}  {c['phone']:<15}  {c['email']:<30}")


def cmd_find(args):
    contacts = load_contacts()
    query = args.query.lower()
    results = [
        c
        for c in contacts
        if query in c["name"].lower()
        or query in c.get("phone", "").lower()
        or query in c.get("email", "").lower()
    ]
    if not results:
        print("No matching contacts.")
        return
    for c in results:
        print(f"{c['id']:>4}  {c['name']:<20}  {c['phone']:<15}  {c['email']:<30}")


def cmd_remove(args):
    contacts = load_contacts()
    before = len(contacts)
    contacts = [c for c in contacts if c["id"] != args.id]
    if len(contacts) == before:
        print(f"No contact with id={args.id}")
        return
    save_contacts(contacts)
    print(f"Contact id={args.id} removed.")


def cmd_update(args):
    contacts = load_contacts()
    for c in contacts:
        if c["id"] == args.id:
            if args.name is not None:
                c["name"] = args.name
            if args.phone is not None:
                c["phone"] = args.phone
            if args.email is not None:
                c["email"] = args.email
            save_contacts(contacts)
            print(f"Contact id={args.id} updated.")
            return
    print(f"No contact with id={args.id}")


def main():
    parser = argparse.ArgumentParser(
        prog="contact-manager", description="A simple command-line contact manager"
    )
    sub = parser.add_subparsers(title="commands", dest="command", required=True)

    p_add = sub.add_parser("add", help="Add a new contact")
    p_add.add_argument("name", help="Contact name")
    p_add.add_argument("--phone", default="", help="Phone number")
    p_add.add_argument("--email", default="", help="Email address")
    p_add.set_defaults(func=cmd_add)

    p_list = sub.add_parser("list", help="List all contacts")
    p_list.add_argument(
        "--sort",
        choices=["id", "name", "phone", "email"],
        default="name",
        help="Sort field (default: name)",
    )
    p_list.add_argument("--reverse", action="store_true", help="Reverse sort order")
    p_list.set_defaults(func=cmd_list)

    p_find = sub.add_parser("find", help="Search contacts")
    p_find.add_argument("query", help="Search query")
    p_find.set_defaults(func=cmd_find)

    p_remove = sub.add_parser("remove", help="Remove a contact by ID")
    p_remove.add_argument("id", type=int, help="Contact ID")
    p_remove.set_defaults(func=cmd_remove)

    p_update = sub.add_parser("update", help="Update a contact")
    p_update.add_argument("id", type=int, help="Contact ID")
    p_update.add_argument("--name", help="New name")
    p_update.add_argument("--phone", help="New phone")
    p_update.add_argument("--email", help="New email")
    p_update.set_defaults(func=cmd_update)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
