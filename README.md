# Academic profile site — Dr. Himanshu Verma

A single self-contained page. No build step, no framework, no dependencies except
the Google Fonts stylesheet. Everything — CSS, JavaScript, and the portrait photo —
is embedded in `index.html`.

```
index.html            the whole site
assets/portrait.jpg   a copy of the photo, used only for link previews
.nojekyll             tells GitHub Pages to serve the files as-is
README.md             this file
```

---

## 1. Create the repository on GitHub

The repository name decides the URL.

| Repository name | Site URL |
|---|---|
| `DrHimanshuV16.github.io` (username`.github.io`) | `https://drhimanshuv16.github.io/` |
| anything else, e.g. `profile` | `https://drhimanshuv16.github.io/profile/` |

The first gives the cleaner address and is the usual choice for a personal academic
page. The repository must be **public** for GitHub Pages on a free account.

Go to [github.com/new](https://github.com/new) → **Repository name:** `DrHimanshuV16.github.io`
→ **Public** → leave *Add a README*, *.gitignore* and *license* all **unticked**, so the
repository starts empty → **Create repository**.

> Starting empty matters: an auto-created README would conflict with the first push.

## 2. Push the files

The local repository is already committed and already has `origin` pointing at
`https://github.com/DrHimanshuV16/DrHimanshuV16.github.io.git`. From this folder:

```bash
git push -u origin main
```

The first push opens a browser window to sign in to GitHub. If it instead asks for a
password in the terminal, use a [personal access token](https://github.com/settings/tokens)
rather than the account password — GitHub stopped accepting passwords over HTTPS in 2021.

## 3. Turn on GitHub Pages

Repository → **Settings** → **Pages** → under *Build and deployment*, set
**Source: Deploy from a branch**, **Branch: main**, **Folder: / (root)** → **Save**.

The first build takes one to two minutes. The URL appears at the top of that same
Settings → Pages screen.

## 4. Link-preview URLs

Already done. The `canonical`, `og:url` and `og:image` tags near the top of `index.html`
point at `https://drhimanshuv16.github.io/`. They only affect how the page looks when
shared on LinkedIn, WhatsApp or X — the site works either way. If the site ever moves to
another domain, update those three tags to match.

## 5. Optional: your own domain

Buy a domain, add a file named `CNAME` at the repository root containing only the
domain (for example `himanshuverma.in`), then point the domain's DNS at GitHub:
four `A` records for the apex domain — `185.199.108.153`, `185.199.109.153`,
`185.199.110.153`, `185.199.111.153` — or a `CNAME` record for `www` pointing at
`DrHimanshuV16.github.io`. Then set the domain under Settings → Pages and tick
**Enforce HTTPS** once the certificate is issued.

---

## Keeping the page current

**Adding a publication.** Near the bottom of `index.html`, find the block commented
`PUBLICATION DATA`. Add one object to the `PUBS` array — nothing else needs to change;
the filter counts and the list update themselves.

```js
{ type:'journal', year:2026,
  title:'Title of the paper, sentence case, no trailing period',
  au:'*H. Verma*, N. Chauhan',              // your own name goes in *asterisks*
  ve:'<em>Journal Name</em>, Publisher, vol. 12, pp. 1–14',
  tags:['SCI','Q1','IF 4.4'],               // a tag containing "Q1" gets the accent colour
  doi:'https://doi.org/10.xxxx/yyyyy' },    // omit the field if there is no DOI
```

`type` is one of `journal`, `chapter`, `conference` or `review`. Items marked
`review` always sort to the bottom of the list and carry an amber "under review" chip;
move one to its real type and year when it is accepted.

**Updating the metrics.** The six figures (h-index, citations, cumulative impact
factor, and so on) are plain numbers in the `<div class="metrics">` block — search for
`class="metrics"`. Worth refreshing from Google Scholar once or twice a year.

**Changing the photo.** Encode a new image as a data URI and replace the long
`src="data:image/jpeg;base64,..."` string on the `<img>` inside `<figure class="portrait">`.
Or, simpler: drop the new file into `assets/`, replace that whole `src` value with
`assets/portrait.jpg`, and update `assets/portrait.jpg` in the repository. A 4:5
portrait crop, about 680 × 850 pixels, matches the current frame.

**Anything else** — new patents, awards, service entries — is ordinary HTML in the
relevant section, written the same way as the entries already there.

## Notes

- The page reads in both light and dark mode; it follows the visitor's system setting.
- The network diagram in the hero is drawn on a `<canvas>` and pauses for visitors who
  have "reduce motion" enabled.
- Google Fonts is the one external request. If your institution's network blocks it,
  the page still renders in its fallback stack (Georgia and a system sans-serif).
