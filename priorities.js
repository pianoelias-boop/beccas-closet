// Her priorities, in order. The owner changes these by asking Claude; see MAKE-YOUR-OWN.md for the fields.
// Everything after "window.CLOSET_PRIORITIES =" must stay strict JSON.
// match: categories (any of), occasions (any of), colors (any of), words (regex that must match), all (list of
// regexes that must all match), not (regex that must not match), pin (ids always included), drop (ids never
// included). Text searched: name, fabric, description, details, colour and category detail. prefer (regex):
// matching pieces sort first while the priority is open.
window.CLOSET_PRIORITIES = [
 {
  "key": "dance-skirt",
  "label": "A skirt for dancing",
  "note": "Something that swings and breathes. Linen is a good start, not a must.",
  "match": {"categories": ["Skirts"], "occasions": ["dance"]},
  "prefer": "linen"
 },
 {
  "key": "dance-jumpsuit",
  "label": "A jumpsuit for dancing",
  "note": "Room to move and a fabric that breathes.",
  "match": {"categories": ["Jumpsuits & Rompers"], "occasions": ["dance"]}
 },
 {
  "key": "cord-pants",
  "label": "Corduroy pants",
  "note": "Corduroy trousers in any colour.",
  "match": {"categories": ["Pants", "Jeans"], "words": "\\bcord\\b|\\bcords\\b|corduroy"}
 },
 {
  "key": "black-jeans",
  "label": "Black jeans that go over bandages",
  "note": "Roomy through the leg with a narrower hem: a barrel that isn't too wide, or a relaxed or wide taper. No wide-leg openings.",
  "match": {"categories": ["Jeans", "Pants"], "colors": ["Black"],
            "all": ["denim|\\bjeans?\\b", "barrel|taper|relaxed|balloon|carrot|curved|boyfriend|loose"],
            "not": "wide[- ]leg|flare|boot ?cut|skinny|palazzo|cord"}
 }
];
