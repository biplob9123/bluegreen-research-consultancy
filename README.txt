BLUEGREEN WEBSITE - KIVABE CHALABEN
====================================

1) Computer-e dekhben kivabe
   index.html file-e double-click korun. Browser-e site khulbe. (Internet thakle font ar map thik moto dekhabe.)

2) Free-te online korben kivabe (hosting)
   Eta static website: shudhu HTML, CSS, JS file. Kono server, database ba programming lage na.
   Ei folder-er shob file upload korle hosting company seta internet-e dekhay.

   Option A (shohoj): Cloudflare Pages - free, free HTTPS, pore nijer domain jora jay.
     - cloudflare.com-e free account kholen
     - Workers & Pages -> Create -> Pages -> "Upload assets" (Direct Upload)
     - Project name din, ei folder-er shob file (ba zip) drag kore din, Deploy
     - Apni ekta link pabe (jemon bluegreen.pages.dev)
   Option B (aro shohoj): Netlify Drop - app.netlify.com/drop-e ei folder drag-drop korun.
   Option C: GitHub Pages (GitHub account lagbe).
   (Hosting site-er menu kokhono kokhono bodlay; kothao atke gele amake bolben.)

3) Contact form
   Web3Forms key boshano ache. Form submit korle message apnar Web3Forms email-e jabe.

4) Domain keno-r por
   - Domain kinle amake bolben. Ami sitemap, canonical link ar social share image set kore dibo.

5) Chobi bodlano
   images folder-er chobi gulo placeholder (illustration). Nijer chobi diye bodlate chaile
   same nam-e (photo-river.jpg, photo-industry.jpg) rekhe replace korun, ba amake chobi din.
   training-civil-duet.jpg apnar asol group photo.

6) Trade Licence: shudhu number ar issuer-er nam site-e ache. License-er chobi site-e nei.

7) Kon bodlale kon file replace korben (GitHub-e shudhu bodlano file upload korlei hobe)
   Home page lekha/chobi ........ index.html
   Services ..................... services.html
   Team (nam, pod, link, chobi) .. team.html  (+ chobi images/team/ folder-e)
   Contact page ................. contact.html
   Rong, button, font, animation . style.css
   Menu, popup, form, animation .. script.js
   Phone, email, social link, menu, footer bodlale: shob .html file replace korte hobe.

8) Team member-er chobi bodlate: images/team/ folder-e same nam-e (400x400 jpg) rakhun.

9) Saf URL (.html chhara)
   Online-e ঠিকানা hobe bgrcbd.com/about, /services, /team ... (GitHub Pages nijei .html chhara kholay).
   Nijer computer-e double-click kore khulle bhetorer link kaj korbe na. Shudhu GitHub-e (online) dekhben.

UPGRADE v3: Replace ALL files and folders (index/services/training/team/contact etc., style.css, script.js, images/art/, images/team/). Keep your CNAME file.

UPGRADE v4: business email (info@, projects@, training@bgrcbd.com), 8 illustrated client cards,
Projects and Insights as popup windows, Humayra's Google Scholar link, Mamun designation.
NOTE: the contact form still delivers to the Gmail address registered with Web3Forms until you create a new
key for info@bgrcbd.com at web3forms.com and paste it into build.py (web3forms_key) or send it to Claude.

UPGRADE v5: fixed mobile menu (Services no longer stuck open, closed menu no longer blocks taps/scroll),
mid-width dropdown, lighter animations on phones, bigger tap areas, Mamun's photo and details, 4-up team row.

UPGRADE v6: Bangla version of every page in the new "bn" folder (bgrcbd.com/bn/...), EN | বাং switch in the
header, Services menu grouped into 3 columns (Industrial compliance / Environmental engineering and data /
Training and academia), sitemap lists both languages. Upload the whole folder INCLUDING the new "bn" folder.
