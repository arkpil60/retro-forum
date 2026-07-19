# Retro Forum 2006 (MVP Release 1.0)

A nostalgic web forum and bulletin board designed to recreate the authentic visual aesthetic and atmosphere of the internet's golden era (mid-2006). The project is built on top of a modern, fault-tolerant backend infrastructure while preserving canonical HTML table layouts and raw SQL performance.

## 🏛️ Architecture & Tech Stack

*   **Operating System:** Linux Debian 13 (Deployed directly on bare-metal hardware).
*   **Backend Platform:** Python 3.13 + Flask 3.1 microframework.
*   **Database Engine:** PostgreSQL 17 (Raw SQL execution via `psycopg2` connection pooling, completely ORM-free).
*   **Frontend:** Pure HTML tables (phpBB3-inspired retro styling) + Jinja2 templating + Vanilla JavaScript.
*   **OS Security:** Custom SSH configuration (Port 2222), UFW Firewall (TCP-only egress traffic restricted), and Fail2ban automated log monitoring.
*   **Networking & DDoS Protection:** Locally-managed Cloudflare Tunnel forced to use the HTTP/2 over TCP protocol to bypass UDP-traffic throttling imposed by ISPs.

## 🚀 Key Features (Release 1.0)

1.  **Retro Timeshift Engine:** The PostgreSQL database stores the exact real-world server timestamps, while the Jinja2 frontend dynamically subtracts exactly 20 years, plunging users back into July 2006.
2.  **Live Asian-Style YMD Clock:** The forum footer features live ticking seconds formatted as `YYYY.MM.DD HH:MM:SS`, updating via client-side JavaScript without page reloads.
3.  **Secure Authentication:** User passwords are transformed into irreversible cryptographic hashes using the `scrypt` algorithm. Fully integrated session management keeps users logged in.
4.  **Dynamic Statistics Grid:** Real-time generation of global forum metrics (total users, topics, and posts counters) combined with a "Who is Online" block tracking active users from the last 5 minutes.
5.  **Core Forum Mechanics:** Board layout featuring Categories and Topics managed via atomic SQL transactions (`commit`/`rollback`), with a Quick Reply form embedded below the post list.
6.  **Admin Maintenance Switch:** Built-in `MAINTENANCE_MODE` toggle within the configuration. When activated, Flask locks all endpoints and serves a custom 503 service unavailable screen.

## 🔧 System Administration (Service Management)

The application is fully demonized and runs continuously in the background under `systemd` control.

*   **Check Web Server Status:** `sudo systemctl status forum.service`
*   **Check Internet Tunnel Status:** `sudo systemctl status cloudflared`
*   **Monitor Real-time Request Logs:** `sudo journalctl -u forum.service -n 20 -f`

---
*Launched into active production in July 2026 (2006). Core infrastructure engineer and administrator: arkpil60.*
