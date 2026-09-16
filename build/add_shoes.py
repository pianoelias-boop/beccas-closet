"""Add the first Shoes shelf (owner-curated 2026-09-16) to build/extras.json as ids 422-432.

Everything here opens to the toe (zipper around the toe, straps that peel the vamp back,
or a soft moccasin) and stops below the calf, so it fits over Becca's bandages.
"""
import json, ssl, urllib.request, re, html, io
from PIL import Image
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
H = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1', 'Accept': 'application/json,image/*,*/*'}
def get(u): return urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=40, context=ctx).read()
def shopify_side(url):
    d = json.loads(get(url.split('?')[0] + '.js'))
    src = d['images'][0]; return ('https:' + src) if src.startswith('//') else src

BILLY_SINGLE = 'Single shoes in any size per foot: email info@billyfootwear.com, then order with their single-shoe code'
NORDSTROM = 'Nordstrom sells a split pair (two different sizes) for the price of one when the sizes differ by 1.5 or more: call 1-888-282-6060 or ask in store'
COSY_SHIP = 'Ships from the UK: about $20, free over $150; 90-day returns'
BANDAGE = 'Bandage days: left foot in her usual size, right foot one to two sizes up.'

T = [
 dict(id=422, brand='BILLY Footwear', name='Goat Classic High, 6E', price=150, color='Black', colorDetail='Black/White',
      url='https://billyfootwear.com/products/womens-black-white-billy-goat-classic-high', img=('shopify', 'https://billyfootwear.com/products/womens-black-white-billy-goat-classic-high'),
      categoryDetail='Zip-open high-top', occasions=['teaching', 'hang', 'friend'],
      desc='Designed with certified orthotists for braces, orthotics and prosthetics. The Full Wrap zipper runs down the side and around the toe, so the whole upper folds open, then zips shut without squeezing anything. Canvas high-top with a padded collar and a custom last that adds width and volume in the toe box.',
      details=['Choose width 6E (Extra-Extra-Wide), the widest BILLY makes; women’s 6 to 16', 'If her size is missing in 6E here, the men’s listing is the same shoe in B to 6E from a men’s 4 (men’s size = women’s minus 1.5)', BILLY_SINGLE, 'Also at Nordstrom in men’s sizing, wide and extra wide. ' + NORDSTROM, 'Canvas upper, triple-layer knit lining, removable insole'],
      fabric='Canvas upper, rubber sole', why='zips shut over anything and stays on without lacing; a plain black high-top for trousers or a skirt',
      note=BANDAGE + ' The zipper closes with no pressure, so it holds like a boot without being one.'),
 dict(id=423, brand='BILLY Footwear', name='Comfort Chukka, men’s 3E', price=135, color='Beige/Tan', colorDetail='Sand suede',
      url='https://billyfootwear.com/products/mens-sand-suede-billy-comfort-chukkas', img=('shopify', 'https://billyfootwear.com/products/mens-sand-suede-billy-comfort-chukkas'),
      categoryDetail='Zip-open chukka', occasions=['teaching', 'hang', 'friend'],
      desc='A real suede desert boot with BILLY’s Full Wrap zipper: the entire top lifts away to the toe (their product page shows it open), so the foot drops in unobstructed and the zipper does the closing. Multilayer, multi-density insole that aligns and cushions.',
      details=['Men’s sizing 7 to 14; choose 3E (Wide). A men’s 7 is about a women’s 8.5', 'Full Wrap zipper plus decorative adjustable laces', 'Suede upper, low chukka collar', BILLY_SINGLE],
      fabric='Suede leather upper', why='the dressiest full-open shoe BILLY makes; reads as an ordinary chukka',
      note=BANDAGE + ' Low collar, so the zipper alone holds it on, which it does.'),
 dict(id=424, brand='BILLY Footwear', name='CS High, 3E', price=90, color='Purple', colorDetail='Purple/Gold (White and Wine listed, purple in stock)',
      url='https://billyfootwear.com/products/womens-purple-gold-billy-cs-high', img=('shopify', 'https://billyfootwear.com/products/womens-purple-gold-billy-cs-high'),
      categoryDetail='Zip-open canvas high-top', occasions=['hang', 'friend'],
      desc='A skate-style canvas high-top with the same Full Wrap zipper as the Goat: down the side, around the toe, whole upper folds open. Padded ribbed collar that supports the ankle without restricting it.',
      details=['Choose 3E (Extra-Wide), the widest this style comes in; women’s 6 to 16', 'Full Wrap zipper with adjustable laces', 'Softer sole than the Goat; a cheaper way to test the fold-open idea', BILLY_SINGLE],
      fabric='Canvas upper', why='cheapest full-open high-top, for testing the idea before buying two Goats',
      note=BANDAGE),
 dict(id=425, brand='Cosyfeet', name='Patty', price=175, color='Black', colorDetail='Black',
      url='https://www.cosyfeet.com/usa/patty', img=('url', 'https://www.cosyfeet.com/media/catalog/product/c/o/core-024_vy31-patty-black_bandaged_in-progress.jpg'),
      categoryDetail='Strap boot for bandaged feet', occasions=['teaching', 'hang'],
      desc='A lightweight, extra roomy boot in soft, stretchy elastane, made to fit very swollen feet and ankles as well as bandaged feet and legs. Two touch-fastening straps; it opens right out so it is easy to get on and off, then closes as loosely as she likes.',
      details=['6E extra-extra-roomy fitting; sizes 5 to 11', 'Opens right out: both straps release the whole vamp', 'Strap extensions for extremely swollen feet: Patty Strap Extensions, $9, at cosyfeet.com/usa/patty-strap-extensions', 'Stretch elastane upper, short shaft that stops below the calf', COSY_SHIP],
      fabric='Elastane upper', why='the boot Cosyfeet designed for bandage days; short shaft, straps set as loose as the Arizonas',
      note=BANDAGE + ' Cosyfeet does not split sizes on boots, so it is two pairs.'),
 dict(id=426, brand='Cosyfeet', name='Ali', price=149, color='Blue', colorDetail='Blue Leopard (also Denim Metallica, Black Croc, Black Cheetah, Leopard Shimmer, Stone Cheetah)',
      url='https://www.cosyfeet.com/usa/ali', img=('url', 'https://www.cosyfeet.com/media/catalog/product/a/l/ali201_hero.jpg'),
      categoryDetail='Strap shoe, opens right out', occasions=['teaching', 'hang'],
      desc='Made on Cosyfeet’s deepest last with a generous fit across the toe and instep. Two touch-fastening straps run right down to the toe and the shoe opens right out, so it goes on over a bandage and closes loosely, the way her Arizonas do.',
      details=['6E fitting; sizes 6 to 11', 'Two straps right down to the toe; opens right out', 'Strap extensions: Ali Strap Extensions, $9, at cosyfeet.com/usa/ali-strap-extensions', 'Leather upper, cushioned sole', COSY_SHIP],
      fabric='Leather upper', why='an everyday shoe that opens flat; the straps hold it on without a shaft',
      note=BANDAGE),
 dict(id=427, brand='Cosyfeet', name='Alison', price=159, color='Red', colorDetail='Claret (also Black, Taupe)',
      url='https://www.cosyfeet.com/usa/alison', img=('url', 'https://www.cosyfeet.com/media/catalog/product/a/w/aw19_ud57_1_1.jpg'),
      categoryDetail='Three-strap leather shoe', occasions=['teaching', 'hang'],
      desc='A seam-free leather shoe with three touch-fastening straps that opens right out, so it goes on even when the foot is bandaged or very swollen. Cushioned underfoot with nothing inside to rub.',
      details=['6E fitting; sizes 5 to 12', 'Three leather straps; opens almost down to the toe', 'Strap extensions: Alison Strap Extensions, $9, at cosyfeet.com/usa/alison-strap-extensions', 'Seam-free lining', COSY_SHIP],
      fabric='Leather upper', why='the most conventional-looking of the strap shoes; teaching days',
      note=BANDAGE),
 dict(id=428, brand='Cosyfeet', name='Luna', price=165, color='Red', colorDetail='Claret (also Black Leopard)',
      url='https://www.cosyfeet.com/usa/luna', img=('url', 'https://www.cosyfeet.com/media/catalog/product/a/w/aw25-345_luna_claret.jpg'),
      categoryDetail='Strap ankle boot', occasions=['teaching', 'hang'],
      desc='Crafted from hand-polished leathers, this ankle boot opens right out to get on a swollen foot. One wide touch-fastening strap, a warm lining and a deep, seam-free toe area for sensitive toes.',
      details=['6E fitting; sizes 6 to 11', 'One wide strap; opens right out', 'Strap extensions: Luna Strap Extensions, $9, at cosyfeet.com/usa/luna-strap-extensions', 'Polished leather, warm lining, short shaft', COSY_SHIP],
      fabric='Leather upper', why='a warmer, dressier sibling of the Patty for cold teaching days',
      note=BANDAGE + ' Single strap, so check the vamp lifts as far as the Patty’s.'),
 dict(id=429, brand='Cosyfeet', name='Emma house shoe', price=85, color='Blue', colorDetail='Navy',
      url='https://www.cosyfeet.com/usa/emma', img=('url', 'https://www.cosyfeet.com/media/catalog/product/a/w/aw19_e1002_1_1.jpg'),
      categoryDetail='Wrap-around house shoe', occasions=['hang'],
      desc='Designed to fit the most difficult or swollen feet. The wrap-around style opens out completely flat, then rolls up around the foot and fastens with two touch-fastening straps, one over the foot and one at the heel, so it stays on however loosely it is closed.',
      details=['6E extra-extra-roomy fitting; sizes 5 to 11', 'Opens out completely flat; heel strap holds it on', 'Cosyfeet’s own pick for heavily bandaged feet', 'Rubber sole for indoors and out', 'Strap extensions: Emma Strap Extensions, $9, at cosyfeet.com/usa/emma-strap-extensions', COSY_SHIP],
      fabric='Soft textile upper, rubber sole', why='for the house, the studio and quick errands on bandage days',
      note=BANDAGE),
 dict(id=430, brand='Cosyfeet', name='Rowan Suede', price=129, color='Black', colorDetail='Black (also Burgundy, Navy; leather version $139)',
      url='https://www.cosyfeet.com/usa/rowan', img=('url', 'https://www.cosyfeet.com/media/catalog/product/x/w/xw21_01v2_9.jpg'),
      categoryDetail='Slipper-shoe, opens down the front', occasions=['hang'],
      desc='Designed for swelling or heavy bandaging, Rowan is for when nothing else fits. Supple as a slipper but supportive as a shoe, with one long touch-fastening strap and a front that opens right down to the toe. Surprisingly neat on the foot.',
      details=['Extra roomy unisex fitting; sizes 6 to 14', 'One long strap; the front opens right down', 'Suede upper, EVA sole', COSY_SHIP],
      fabric='Suede upper, EVA sole', why='between a slipper and a shoe; goes outside',
      note=BANDAGE),
 dict(id=431, brand='Converse', name='Chuck 70 High, Wide', price=95, color='Black', colorDetail='Black',
      url='https://www.converse.com/shop/p/chuck-70-canvas-unisex-high-top-shoe/162050C.html', img=('file', 'build/shoes/chuck70_black.jpg'),
      categoryDetail='Canvas high-top', occasions=['hang', 'friend', 'teaching'],
      desc='The Chuck geometry is the point: eight eyelets start just behind the rubber toe cap, so unlaced the canvas throat opens flat to the toe, and the high collar holds the shoe on. The 70 has a thicker sole and cushioned insole than the classic Chuck.',
      details=['Choose the Wide width on converse.com (Standard/Wide selector); unisex sizing, runs long, so size down half', 'Eyelets from the toe cap; wear it unlaced or loosely laced', NORDSTROM + '. Nordstrom stocks the standard-width Chuck 70 High at $95 (nordstrom.com/s/converse-chuck-70-high-top-sneaker-men/9064356)', 'Add a firm insole; the sole flexes'],
      fabric='Canvas upper, rubber sole', why='the everyday high-top that goes with a skirt and opens to the toe',
      note=BANDAGE + ' Two pairs, or one split pair through Nordstrom in the standard width.'),
 dict(id=432, brand='Steger Mukluks', name='Arctic, Double Wide', price=249.95, color='Beige/Tan', colorDetail='Natural canvas, maple leather',
      url='https://mukluks.com/products/arctic-ladies', img=('shopify', 'https://mukluks.com/products/arctic-ladies'),
      categoryDetail='Mukluk', occasions=['hang', 'outdoors'],
      desc='Steger’s expedition mukluk: a soft moosehide moccasin foot with nothing crossing the instep, and a weather-treated canvas shaft that cinches with straps around the leg. Full-grain leather, 9 mm wool felt liner, 9 mm wool felt insole, and their aggressively treaded sole. Rated for colder than minus 40, with larger and wider sizes rated colder still.',
      details=['Ladies sizes 5 to 11 in Regular, Wide and Double Wide; choose Double Wide, and Steger says to buy wider for a high instep', 'Nothing crosses the foot: the moccasin drapes over a bandage', '16-inch shaft of soft cloth, so it does not fight a calf wrap', 'The felt liner lifts out (spare liners $33.95)', 'Soft sole and not waterproof: slush is the enemy', 'Made in Ely, Minnesota'],
      fabric='Moosehide, full-grain leather, treated canvas, wool felt', why='the gentlest thing to put over a bandage and the warmest thing for a Maine winter',
      note=BANDAGE + ' Full sizes only.'),
]

extras = json.load(open('build/extras.json'))
extras = [e for e in extras if e['id'] < 422]
for t in T:
    kind, src = t.pop('img')
    if kind == 'shopify': src = shopify_side(src)
    im = Image.open(src) if kind == 'file' else Image.open(io.BytesIO(get(src))); im.load()
    if im.mode in ('RGBA', 'LA', 'P'):
        bg = Image.new('RGB', im.size, (255, 255, 255)); bg.paste(im.convert('RGBA'), mask=im.convert('RGBA').split()[-1]); im = bg
    else: im = im.convert('RGB')
    im.thumbnail((900, 900)); path = f"images/full/{t['id']}.jpg"; im.save(path, 'JPEG', quality=84, optimize=True)
    details = [t['note']] + t['details']   # the modal shows details, not note; lead with the sizing line
    extras.append(dict(id=t['id'], brand=t['brand'], retailer=t['brand'], name=t['name'], category='Shoes', color=t['color'], occasions=t['occasions'], why=t['why'], price=t['price'],
                       colorDetail=t['colorDetail'], categoryDetail=t['categoryDetail'], url=t['url'], img=path, hi=True, desc=t['desc'], details=details, fabric=t['fabric'], note=t['note']))
    print(t['id'], t['brand'], t['name'], '| photo', im.size, '<-', src[:70])
json.dump(extras, open('build/extras.json', 'w'), indent=1, ensure_ascii=False)
print(len(extras), 'extras written')
