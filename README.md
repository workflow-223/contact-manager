# Contact Manager

Full-stack contact management app with a CLI tool, Tkinter GUI, and REST API HTTP server for managing contacts with phone/email validation.

## Interfaces

- **CLI**: `python contact_manager.py` - Command-line contact management
- **GUI**: `python gui.py` - Tkinter-based graphical interface
- **Web Server**: `python server.py` - REST API server on port 8080

## Deployment

The web UI is deployed to GitHub Pages at:
`https://workflow-223.github.io/contact-manager/`

**Setup:** In repo Settings → Pages → Source: **Deploy from a branch**, branch: `main`, folder: `/docs`.

Note: The web UI is a static frontend. For full functionality (CLI, GUI, REST API), run locally with Python 3.

## Local Setup

```bash
python server.py
# Then visit http://localhost:8080
```
