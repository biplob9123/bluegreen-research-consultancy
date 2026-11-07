# BlueGreen Research and Consultancy: website source

Website of BlueGreen Research and Consultancy (Gazipur, Bangladesh), published at https://www.bgrcbd.com in English and Bangla.

| Folder or file | What it holds |
| --- | --- |
| `content/` | Every text of the site, English (`en:`) and Bangla (`bn:`) side by side, one file per page. `_shared.txt` is the menu and footer, `_site.txt` is phone, email, links and web address. |
| `templates/` | Page layouts in HTML, with `{{keys}}` where texts go and `<!-- ===== Section: ... ===== -->` labels. Shared parts start with `_`, pictures are in `_svg/`. |
| `static/` | Style sheet, script, logo and images, copied as they are. |
| `build_site.py` | Joins templates and content into `_site/` (English pages plus the `bn/` Bangla pages, sitemap and robots file). Python standard library only. |
| `.github/workflows/deploy.yml` | Runs the build and publishes `_site/` on GitHub Pages after every commit. Pages source must be set to "GitHub Actions". |

To edit text: change the lines after `en:` or `bn:` in the right file under `content/` and commit. The site rebuilds in a minute or two.
Step-by-step guide in Bangla: `HOW-TO-EDIT.txt`.

Build locally: `python3 build_site.py`, then open `_site/index.html`.
