import os
import re
import time
from decimal import Decimal, InvalidOperation
from urllib.parse import urljoin, urlsplit

import requests
from bs4 import BeautifulSoup

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from core.models import Product

BOOKS_BASE = "https://books.toscrape.com/catalogue/"
DUMMYJSON_URL = "https://dummyjson.com/products?limit=0"
HEADERS = {"User-Agent": "Mozilla/5.0 (studentski-projekt-scraper)"}

# Scrapani podaci nemaju polja interests/occasion, pa kategoriju preslikavamo
# u prikladne vrijednosti. To je most prema AI logici (core/ai_logic.py).
# --- knjige (books.toscrape.com) ---
CATEGORY_MAP = {
    "Travel":           {"interests": "putovanja, avantura, istrazivanje", "occasion": "rodendan, godisnjica"},
    "Mystery":          {"interests": "napetost, misterija, citanje",      "occasion": "rodendan, Bozic"},
    "Romance":          {"interests": "ljubav, romantika, citanje",        "occasion": "Valentinovo, godisnjica"},
    "Science Fiction":  {"interests": "tehnologija, sci-fi, masta",        "occasion": "rodendan, diplomiranje"},
    "Music":            {"interests": "glazba, umjetnost, opustanje",      "occasion": "rodendan, Bozic"},
    "Sports and Games": {"interests": "sport, fitness, zabava",            "occasion": "rodendan"},
    "Business":         {"interests": "posao, edukacija, razvoj",          "occasion": "promocija, diplomiranje"},
    "Food and Drink":   {"interests": "kuhanje, gastronomija, uzivanje",   "occasion": "majcin dan, useljenje"},
    "Art":              {"interests": "umjetnost, kreativnost, dizajn",    "occasion": "rodendan, godisnjica"},
    "Poetry":           {"interests": "poezija, romantika, citanje",       "occasion": "Valentinovo"},
}
DEFAULT_ENRICH = {"interests": "citanje, knjige, edukacija", "occasion": "rodendan, Bozic"}

# --- dummyjson.com (slug kategorije -> interests/occasion) ---
DUMMY_MAP = {
    "mobile-accessories": {"interests": "tehnologija, gadgeti",       "occasion": "rodendan, Bozic"},
    "smartphones":        {"interests": "tehnologija, posao",         "occasion": "diplomiranje, rodendan"},
    "tablets":            {"interests": "tehnologija, posao",         "occasion": "diplomiranje, rodendan"},
    "laptops":            {"interests": "tehnologija, posao",         "occasion": "diplomiranje, rodendan"},
    "beauty":             {"interests": "ljepota, njega",             "occasion": "Valentinovo, majcin dan"},
    "skin-care":          {"interests": "ljepota, njega",             "occasion": "Valentinovo, majcin dan"},
    "fragrances":         {"interests": "ljepota, njega",             "occasion": "Valentinovo, majcin dan"},
    "womens-jewellery":   {"interests": "moda, elegancija",           "occasion": "godisnjica, Valentinovo"},
    "womens-bags":        {"interests": "moda, elegancija",           "occasion": "godisnjica, Valentinovo"},
    "womens-dresses":     {"interests": "moda, stil",                 "occasion": "rodendan, godisnjica"},
    "tops":               {"interests": "moda, stil",                 "occasion": "rodendan, godisnjica"},
    "womens-shoes":       {"interests": "moda, stil",                 "occasion": "rodendan, godisnjica"},
    "mens-shirts":        {"interests": "moda, stil",                 "occasion": "rodendan, godisnjica"},
    "mens-shoes":         {"interests": "moda, stil",                 "occasion": "rodendan, godisnjica"},
    "mens-watches":       {"interests": "moda, stil",                 "occasion": "rodendan, godisnjica"},
    "womens-watches":     {"interests": "moda, stil",                 "occasion": "rodendan, godisnjica"},
    "sunglasses":         {"interests": "moda, stil",                 "occasion": "rodendan, godisnjica"},
    "sports-accessories": {"interests": "sport, fitness",             "occasion": "rodendan"},
    "kitchen-accessories":{"interests": "dom, kuhanje",               "occasion": "useljenje, majcin dan"},
    "home-decoration":    {"interests": "dom, kuhanje",               "occasion": "useljenje, majcin dan"},
    "furniture":          {"interests": "dom, kuhanje",               "occasion": "useljenje, majcin dan"},
    "groceries":          {"interests": "dom, kuhanje",               "occasion": "useljenje, majcin dan"},
    "motorcycle":         {"interests": "auto, hobi",                 "occasion": "rodendan"},
    "vehicle":            {"interests": "auto, hobi",                 "occasion": "rodendan"},
}


class Command(BaseCommand):
    help = "Uvozi proizvode (knjige + dummyjson) s pravim slikama koje odgovaraju proizvodu."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit", type=int, default=1000,
            help="Maksimalno proizvoda po izvoru (default 1000).",
        )
        parser.add_argument(
            "--source", choices=["books", "dummyjson", "all"], default="all",
            help="Izvor: books | dummyjson | all (default all = books + dummyjson).",
        )
        parser.add_argument(
            "--flush", action="store_true",
            help="Obrisi sve postojece proizvode prije uvoza (cisti start).",
        )

    # ---------- pomocne ----------
    def _say(self, msg, style=None):
        """Ispis otporan na Windows cp1252 konzolu (zamijeni neprikazive znakove)."""
        try:
            self.stdout.write(style(msg) if style else msg)
        except UnicodeEncodeError:
            safe = msg.encode("ascii", "replace").decode("ascii")
            self.stdout.write(style(safe) if style else safe)

    def _parse_price(self, raw):
        """Cisti '£51.77' / '$295.99' u Decimal."""
        if raw is None:
            return Decimal("0.00")
        cleaned = re.sub(r"[^\d.]", "", str(raw))
        try:
            return Decimal(cleaned) if cleaned else Decimal("0.00")
        except InvalidOperation:
            return Decimal("0.00")

    def _has_image(self, product):
        return bool(product.image and product.image.name)

    def _ensure_image(self, product, image_url=None):
        """Skine i spremi PRAVU sliku proizvoda. Bez slike -> ostavi prazno (nikad random)."""
        if self._has_image(product):
            return False
        if not image_url:
            return False
        try:
            resp = requests.get(image_url, headers=HEADERS, timeout=20)
            if resp.status_code != 200 or not resp.content:
                return False
            ext = os.path.splitext(urlsplit(image_url).path)[1].lower()
            if ext not in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
                ext = ".jpg"
            fname = f"{slugify(product.name)[:60] or 'proizvod'}{ext}"
            product.image.save(fname, ContentFile(resp.content), save=True)
            return True
        except requests.RequestException:
            return False

    def _upsert(self, name, defaults):
        return Product.objects.get_or_create(name=name, defaults=defaults)

    # ---------- izvori ----------
    def scrape_books(self, limit):
        self._say(self.style.NOTICE("== Knjige (books.toscrape.com) =="))
        processed = created = images = 0

        for page in range(1, 51):  # 50 stranica x 20 = max 1000
            if processed >= limit:
                break
            url = f"{BOOKS_BASE}page-{page}.html"
            try:
                resp = requests.get(url, headers=HEADERS, timeout=15)
            except requests.RequestException as exc:
                self.stderr.write(f"Greska pri dohvatu {url}: {exc}")
                break
            if resp.status_code != 200:
                break

            pods = BeautifulSoup(resp.text, "html.parser").select("article.product_pod")
            if not pods:
                break

            for pod in pods:
                if processed >= limit:
                    break
                processed += 1

                link = pod.select_one("h3 a")
                title = link.get("title", "").strip()
                price_el = pod.select_one(".price_color")
                price = self._parse_price(price_el.get_text(strip=True) if price_el else "")
                detail_url = urljoin(BOOKS_BASE, link.get("href", ""))

                category, description, image_url = self._fetch_book_detail(detail_url, title)
                enrich = CATEGORY_MAP.get(category, DEFAULT_ENRICH)

                product, was_created = self._upsert(
                    title,
                    defaults={
                        "description": description,
                        "price": price,
                        "category": category or "Knjige",
                        "interests": enrich["interests"],
                        "occasion": enrich["occasion"],
                    },
                )
                created += int(was_created)
                if self._ensure_image(product, image_url):
                    images += 1

                self._say(f"[knjige {processed}] {title} ({category or 'Knjige'}) - {price}")
                time.sleep(0.1)

        self._say(f"-> knjige: obradeno {processed}, novih {created}, slika dodano {images}")
        return processed, created, images

    def _fetch_book_detail(self, url, title):
        """Vraca (kategorija, opis, url_korica) s detaljne stranice knjige."""
        try:
            soup = BeautifulSoup(requests.get(url, headers=HEADERS, timeout=15).text, "html.parser")

            crumbs = soup.select("ul.breadcrumb li a")
            category = crumbs[2].get_text(strip=True) if len(crumbs) >= 3 else ""

            desc_el = soup.select_one("#product_description ~ p")
            description = desc_el.get_text(strip=True) if desc_el else f"Knjiga: {title}"

            img_el = soup.select_one("#product_gallery img")
            image_url = urljoin(url, img_el.get("src")) if img_el and img_el.get("src") else None

            return category, description, image_url
        except requests.RequestException:
            return "", f"Knjiga: {title}", None

    def scrape_dummyjson(self, limit):
        self._say(self.style.NOTICE("== Proizvodi (dummyjson.com) =="))
        processed = created = images = 0

        try:
            data = requests.get(DUMMYJSON_URL, headers=HEADERS, timeout=30).json().get("products", [])
        except (requests.RequestException, ValueError) as exc:
            self.stderr.write(f"Greska pri dohvatu dummyjson: {exc}")
            return 0, 0, 0

        for item in data:
            if processed >= limit:
                break
            title = (item.get("title") or "").strip()
            if not title:
                continue
            processed += 1

            slug = item.get("category", "")
            enrich = DUMMY_MAP.get(slug, DEFAULT_ENRICH)
            category = slug.replace("-", " ").title() if slug else "Razno"
            price = self._parse_price(item.get("price"))
            description = (item.get("description") or title).strip()
            image_url = item.get("thumbnail")

            product, was_created = self._upsert(
                title,
                defaults={
                    "description": description,
                    "price": price,
                    "category": category,
                    "interests": enrich["interests"],
                    "occasion": enrich["occasion"],
                },
            )
            created += int(was_created)
            if self._ensure_image(product, image_url):
                images += 1

            self._say(f"[dummyjson {processed}] {title} ({category}) - {price}")
            time.sleep(0.05)

        self._say(f"-> dummyjson: obradeno {processed}, novih {created}, slika dodano {images}")
        return processed, created, images

    # ---------- glavni tok ----------
    def handle(self, *args, **opts):
        limit = opts["limit"]
        source = opts["source"]

        if opts["flush"]:
            n = Product.objects.count()
            Product.objects.all().delete()
            self._say(self.style.WARNING(f"FLUSH: obrisano {n} postojecih proizvoda."))

        before = Product.objects.count()
        self._say(f"Proizvoda u bazi PRIJE: {before}")

        if source in ("books", "all"):
            self.scrape_books(limit)
        if source in ("dummyjson", "all"):
            self.scrape_dummyjson(limit)

        after = Product.objects.count()
        with_image = sum(1 for p in Product.objects.all() if self._has_image(p))
        without_image = after - with_image

        self._say("")
        self._say(self.style.SUCCESS("===== IZVJESTAJ ====="))
        self._say(f"Proizvoda PRIJE: {before} | POSLIJE: {after} (novih: {after - before})")
        self._say(f"Sa slikom: {with_image} | bez slike: {without_image}")

        self._say("Kategorije (proizvoda po kategoriji):")
        counts = {}
        for cat in Product.objects.values_list("category", flat=True):
            counts[cat] = counts.get(cat, 0) + 1
        for cat, n in sorted(counts.items(), key=lambda x: -x[1]):
            self._say(f"  - {cat}: {n}")

        empty = Product.objects.filter(interests="").count() + Product.objects.filter(occasion="").count()
        if empty == 0:
            self._say(self.style.SUCCESS("Svi proizvodi imaju popunjeno interests i occasion."))
        else:
            self._say(self.style.ERROR(f"PAZNJA: {empty} proizvoda ima prazno interests/occasion!"))
