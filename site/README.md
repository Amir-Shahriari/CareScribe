# CareScribe site

Landing page for CareScribe. Single-page React + Vite + Tailwind v4, static, no backend.

Deployed to GitHub Pages at `https://amir-shahriari.github.io/CareScribe/` by
`.github/workflows/deploy.yml` on every push to `main` that touches `site/`.

## Local

```bash
npm install
npm run dev        # http://localhost:5173/CareScribe/
npm run build      # -> dist/
npm run preview    # serve the build
```

## Notes

- `vite.config.ts` sets `base: '/CareScribe/'` to match the Pages project path.
- The hero "Original / De-identified" panel is an illustrative typographic
  diagram (`RedactionVisual` in `src/App.tsx`), not a product screenshot. Swap
  in a real screenshot there if you want one.
- Light theme only, matching the CareScribe app.
