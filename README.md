# Cloud Notes App

A modern, fast, responsive notes application built with FastAPI, SQLite, Tailwind CSS, and Alpine.js. Designed to be hosted easily behind your Cloudflare Tunnel at port `9110`.

## Features
- ✨ **Clean, Modern UI**: Built with Tailwind CSS and support for Dark / Light mode.
- 📝 **Markdown Support**: Write notes in markdown with instant live preview.
- 🏷️ **Categories & Tags**: Organize notes cleanly with custom categories and tag clouds.
- 📌 **Pinning**: Pin important notes to the top of your dashboard.
- 🔍 **Instant Search**: Real-time filtering across titles and contents.
- 🚀 **Fast & Lightweight**: Powered by FastAPI and SQLite (`notes.db`).

---

## Getting Started

1. **Activate virtual environment**:
   ```bash
   source venv/bin/activate
   ```

2. **Run the application**:
   ```bash
   python run.py
   ```
   The server will start on `http://localhost:9110`.

---

## Hosting via Cloudflare Tunnel (`notes.<mydomain>`)

Since your cloudflared tunnel is configured to listen to `localhost:9110`, simply run the app on port `9110` (as configured in `run.py`), and your tunnel will automatically route traffic from `https://notes.<mydomain>` to this app!
