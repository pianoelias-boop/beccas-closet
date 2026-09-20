// The one file to personalise. Names, the recipient's email, every sentence written for her, the photos,
// the occasion tags and the notebook settings all live here; colours and fonts live in theme.css.
// Everything after "window.CLOSET_CONFIG =" must stay strict JSON (double quotes, no trailing commas,
// no comments, nothing after the closing "};") because the build scripts read this file too.
// Field guide: MAKE-YOUR-OWN.md. In text fields, {n} becomes the number of pieces and {date} the date
// the return terms were last checked; a little HTML such as <em> or <br> is fine.
window.CLOSET_CONFIG = {
 "slug": "beccas-closet",
 "notebookKey": "becca",
 "syncUrl": "https://script.google.com/macros/s/AKfycbxEsWyI6ilfr3OP7OYeyXp8X_wBOXPJW2xAlZ_0CVdcmDZy8ZFZ14u5FtMmDP7SXR4/exec",
 "siteTitle": "Becca's Closet",
 "description": "A closet curated for Becca.",
 "icon": "🎀",
 "text": {
  "eyebrow": "Welcome to",
  "wordmark": "Becca’s <em>Closet</em>",
  "tagline": "{n} curated pieces for Rebecca Pruente",
  "heroNote": "Tap a heart to tuck something away. Your saved list lives right here in this browser, and you can email it to yourself whenever you like.",
  "aboutLink": "About this closet",
  "aboutTitle": "How this closet came to be",
  "personLink": "About Becca",
  "personTitle": "About Becca",
  "personText": "Becca is a clothes-wearing, French-teaching, baking Lindy Hopper who loves her friends and her community. She lives in Portland, Maine, with her sloth, Slothie.",
  "storesTitle": "Where the closet shops",
  "storesIntro": "Thirty stores have pieces in the closet today; the other ten were browsed and came up empty. Return terms are as each store states them for US orders, checked on {date}. The policy link is the source of truth.",
  "footer": "Every piece here was picked with you in mind.<br>Happy birthday, Becca."
 },
 "about": {
  "considered": "10,000+",
  "storefronts": 40,
  "paragraphs": [
   "Everything here was sifted from more than ten thousand pieces across forty storefronts. The brands made the cut for one of two reasons: they make genuinely great clothes, or they make good clothes at a good price. Then each piece was chosen with you in mind.",
   "You'll notice that many of these items come in more colors than shown! You can click straight to the brand's website (or click to search for it on eBay/Poshmark). Also, most of these brands have big sales that make things 50% off."
  ],
  "fine": [
   "Wondering about returns? Tap the storefront count above for every store’s return terms.",
   "Hearts and “not for me” marks are kept in a little notebook so your list follows you between your phone and laptop, and so the closet can be tidied up over time."
  ]
 },
 "person": {
  "photos": [
   {"src": "images/becca/06.jpg", "alt": "Becca holding a bowl of pasta she made"},
   {"src": "images/becca/01.jpg", "alt": "Becca in a garden in a long patterned dress"},
   {"src": "images/becca/03.jpg", "alt": "Becca with Slothie"},
   {"src": "images/becca/02.jpg", "alt": "Becca with friends outdoors"},
   {"src": "images/becca/04.jpg", "alt": "Becca outside with a bottle of wine"},
   {"src": "images/becca/05.jpg", "alt": "Becca in a cabin bunk with Slothie"}
  ]
 },
 "email": {
  "to": "beccapruente@gmail.com",
  "bcc": "",
  "subject": "My picks from Becca’s Closet",
  "intro": "My saved pieces from Becca's Closet:"
 },
 "occasions": [
  {"key": "teaching", "label": "For teaching",
   "auto": {"categories": ["Dresses", "Skirts", "Pants", "Shirts & Blouses", "Sweaters & Knitwear", "Jumpsuits & Rompers", "Jackets & Coats"], "not": "\\bmini\\b|crop|sheer|strapless|bodycon|bralette"}},
  {"key": "dance", "label": "For dancing",
   "auto": {"all": ["cotton|linen|merino|tencel|lyocell|viscose|rayon|jersey|modal|cupro|silk", "jersey|knit|wrap|a-line|a line|tiered|wide[- ]leg|elastic|stretch|swing|circle|relaxed|linen|culotte"], "not": "jacket|coat|blazer|rigid|structured|strapless|sheer"}},
  {"key": "friend", "label": "With friends",
   "auto": {"role": "otherwise"}},
  {"key": "hang", "label": "Hanging out",
   "auto": {"role": "default", "categories": ["Jeans", "Tops & Tees", "Pants", "Sweaters & Knitwear"]}},
  {"key": "dressy", "label": "Dressy",
   "auto": {"any": "silk|satin|velvet|chiffon|occasion|evening|party|wedding"}},
  {"key": "outdoors", "label": "Outdoors",
   "auto": {"any": "jacket|coat|cargo|utility|hike|trail|wool|fleece|canvas|waxed"}}
 ],
 "resale": {"ebayCategory": "15724", "poshmarkDepartment": "Women"}
};
