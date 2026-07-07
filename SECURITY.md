# Security Policy

## Supported Versions

MusicMind for Plex is under active development. Only the latest
version on the `main` branch is supported with security fixes.

| Version | Supported |
| ------- | --------- |
| Latest (main) | ✅ |
| Older releases | ❌ |

## Reporting a Vulnerability

If you discover a security vulnerability, **please do not open a
public GitHub Issue.** Instead, email
**info@verbenaprojects.com** with details.

Please include:
- A description of the vulnerability and its potential impact
- Steps to reproduce it
- Any relevant logs, screenshots, or code

You should expect an initial response within a few days. This is a
self-hosted, open-source project maintained outside of full-time
work, so response times may vary — but every report will be read and
taken seriously.

## Scope

MusicMind for Plex is a self-hosted application. You run it on your
own hardware, with your own credentials (Plex token, OpenAI key,
Last.fm key), and it stores data in a local SQLite database. There is
no MusicMind-operated server, account system, or shared infrastructure
— your installation's security is your installation's own.

That said, real vulnerability classes worth reporting include:
- Anything that could expose another user's data on a shared/multi-
  user install
- SQL injection or command injection in any of the web routes or
  scripts
- Anything that could execute arbitrary code via a crafted audio
  file, filename, or Plex library entry
- Credential handling issues (e.g. secrets logged in plaintext where
  they shouldn't be)

## Known Security-Relevant Notes

- `config.py` contains real credentials (Plex token, OpenAI key,
  Last.fm key). It is gitignored by default — never commit it.
- The app has no authentication of its own. It's designed to run on
  a trusted local network. If you expose it to the internet (e.g. via
  a reverse proxy or tunnel), put your own authentication in front of
  it.
- The DB Console (`/db`) allows arbitrary SELECT queries against your
  local database. It does not allow INSERT/UPDATE/DELETE, but treat
  it as sensitive if you ever expose the app beyond your own network.

## Non-Security Bugs

For regular bugs and feature requests, please use
[GitHub Issues](https://github.com/earthmonkey419/musicmindforplex/issues)
instead of email — see the [Guide](https://musicmind.vp-fun.com/guide#support)
for details.
