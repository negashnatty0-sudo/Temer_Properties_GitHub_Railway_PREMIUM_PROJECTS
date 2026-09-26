# Live Admin Setup

In Railway -> Variables add:
- ADMIN_PASSWORD = your private admin password
- SESSION_SECRET = a long random secret

Then open `/admin` on your Railway domain.

The admin can edit contact details and messages and upload hero images/videos.

For permanent uploaded media across redeploys, attach a Railway volume or use object storage.
