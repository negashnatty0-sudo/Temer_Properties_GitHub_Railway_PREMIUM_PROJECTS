# Temer Properties — GitHub + Railway Ready

This is a clean, dependency-light Temer Properties starter.

## Run locally

### Option 1 — Python
```bash
python3 -m http.server 8000 --bind 0.0.0.0
```
Open http://localhost:8000

### Option 2 — Node
```bash
npm start
```

## Deploy to GitHub
Upload the whole folder/repository, including:

- `index.html`
- `styles.css`
- `app.js`
- `assets/hero-background.jpg`
- `assets/mahlet-ademe.jpg`
- `assets/design-reference.png`
- `package.json`
- `README.md`

Do NOT move the assets outside the repository. The site uses relative paths such as `assets/mahlet-ademe.jpg`, so GitHub and Railway can serve them correctly.

## Deploy to Railway
Connect the GitHub repository. Railway can run the included start command:
```bash
python3 -m http.server $PORT --bind 0.0.0.0
```

## Important
The `mahlet-ademe.jpg` and `hero-background.jpg` included here are crops made from the Temer Properties design reference available in this conversation. Replace them with the original high-resolution assets later **using the exact same filenames**. No code changes are required.

## Next production steps
- Connect a real property database
- Connect contact/WhatsApp forms
- Add real property photos
- Add authentication/customer dashboard
- Add admin property management
- Connect domain

## Included image assets

The repository now contains the visual assets inside `assets/`, including:
- hero background
- Mahlet Ademe portrait
- multiple property images
- project images
- original design reference

All website image references are relative paths, so they remain available after GitHub/Railway deployment.


## Featured development
The site includes the Megenagna Chaka (መገናኛ ጫካ) project image and the supplied Amharic pricing, unit sizes, payment plan and discount options in `assets/megenagna-chaka-project.jpg` and the featured-project section.
