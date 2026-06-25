import os
import django
import sys

# Postavljanje putanja (giftai_backend i core)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'giftai_backend.settings')
django.setup()

from core.models import Product

def seed_perfumes():
    # Lista 30 stvarnih parfema (100ml) s "perfume" u interests
    perfume_data = [
        # MUŠKI PARFEMI
        {"name": "Dior Sauvage Eau de Parfum 100ml", "price": 130.00, "cat": "Cosmetics", "int": "perfume", "occ": "Birthday Gift"},
        {"name": "Bleu de Chanel Eau de Parfum 100ml", "price": 145.00, "cat": "Cosmetics", "int": "perfume", "occ": "Business"},
        {"name": "Creed Aventus Eau de Parfum 100ml", "price": 320.00, "cat": "Cosmetics", "int": "perfume", "occ": "Luxury Gift"},
        {"name": "Giorgio Armani Acqua Di Gio Profondo 100ml", "price": 110.00, "cat": "Cosmetics", "int": "perfume", "occ": "Summer Style"},
        {"name": "Versace Eros Eau de Parfum 100ml", "price": 95.00, "cat": "Cosmetics", "int": "perfume", "occ": "Night Out"},
        {"name": "Yves Saint Laurent Y Eau de Parfum 100ml", "price": 120.00, "cat": "Cosmetics", "int": "perfume", "occ": "Daily Wear"},
        {"name": "Tom Ford Noir Extreme Eau de Parfum 100ml", "price": 165.00, "cat": "Cosmetics", "int": "perfume", "occ": "Anniversary"},
        {"name": "Hermes Terre d'Hermes Eau de Toilette 100ml", "price": 115.00, "cat": "Cosmetics", "int": "perfume", "occ": "Father's Day"},
        {"name": "Prada Luna Rossa Ocean Eau de Parfum 100ml", "price": 110.00, "cat": "Cosmetics", "int": "perfume", "occ": "Casual Wear"},
        {"name": "Paco Rabanne 1 Million Elixir 100ml", "price": 105.00, "cat": "Cosmetics", "int": "perfume", "occ": "Celebration"},
        {"name": "Jean Paul Gaultier Le Male Le Parfum 100ml", "price": 110.00, "cat": "Cosmetics", "int": "perfume", "occ": "Night Out"},
        {"name": "Valentino Uomo Born In Roma EDP 100ml", "price": 115.00, "cat": "Cosmetics", "int": "perfume", "occ": "Birthday Gift"},

        # ŽENSKI PARFEMI
        {"name": "Chanel Coco Mademoiselle Eau de Parfum 100ml", "price": 150.00, "cat": "Cosmetics", "int": "perfume", "occ": "Anniversary"},
        {"name": "Dior J'adore Eau de Parfum 100ml", "price": 140.00, "cat": "Cosmetics", "int": "perfume", "occ": "Mother's Day"},
        {"name": "Yves Saint Laurent Libre Eau de Parfum 100ml", "price": 135.00, "cat": "Cosmetics", "int": "perfume", "occ": "Luxury Gift"},
        {"name": "Lancome La Vie Est Belle Eau de Parfum 100ml", "price": 125.00, "cat": "Cosmetics", "int": "perfume", "occ": "Birthday Gift"},
        {"name": "Carolina Herrera Good Girl EDP 100ml", "price": 130.00, "cat": "Cosmetics", "int": "perfume", "occ": "Night Out"},
        {"name": "Armani Si Passione Eau de Parfum 100ml", "price": 130.00, "cat": "Cosmetics", "int": "perfume", "occ": "Valentine's Day"},
        {"name": "Tom Ford Black Orchid Eau de Parfum 100ml", "price": 175.00, "cat": "Cosmetics", "int": "perfume", "occ": "Special Occasion"},
        {"name": "Marc Jacobs Daisy Eau de Toilette 100ml", "price": 98.00, "cat": "Cosmetics", "int": "perfume", "occ": "Graduation"},
        {"name": "Gucci Bloom Eau de Parfum 100ml", "price": 135.00, "cat": "Cosmetics", "int": "perfume", "occ": "Daily Wear"},
        {"name": "Prada Paradoxe Eau de Parfum 100ml", "price": 145.00, "cat": "Cosmetics", "int": "perfume", "occ": "Luxury Gift"},
        {"name": "Dolce & Gabbana Light Blue EDT 100ml", "price": 95.00, "cat": "Cosmetics", "int": "perfume", "occ": "Summer Style"},
        {"name": "Versace Bright Crystal Absolu EDP 100ml", "price": 100.00, "cat": "Cosmetics", "int": "perfume", "occ": "Birthday Gift"},

        # UNISEX / NICHE PARFEMI
        {"name": "Maison Francis Kurkdjian Baccarat Rouge 540 100ml", "price": 340.00, "cat": "Cosmetics", "int": "perfume", "occ": "Luxury Gift"},
        {"name": "Tom Ford Lost Cherry Eau de Parfum 100ml", "price": 390.00, "cat": "Cosmetics", "int": "perfume", "occ": "Anniversary"},
        {"name": "Byredo Gypsy Water Eau de Parfum 100ml", "price": 220.00, "cat": "Cosmetics", "int": "perfume", "occ": "Unique Gift"},
        {"name": "Le Labo Santal 33 Eau de Parfum 100ml", "price": 290.00, "cat": "Cosmetics", "int": "perfume", "occ": "Premium Tech Style"},
        {"name": "Jo Malone Wood Sage & Sea Salt Cologne 100ml", "price": 140.00, "cat": "Cosmetics", "int": "perfume", "occ": "Daily Wear"},
        {"name": "Diptyque Philosykos Eau de Parfum 100ml", "price": 165.00, "cat": "Cosmetics", "int": "perfume", "occ": "Special Gift"}
    ]

    print(f"Ubacujem {len(perfume_data)} stvarnih parfema u bazu...")
    
    count = 0
    for p in perfume_data:
        obj, created = Product.objects.get_or_create(
            name=p['name'],
            defaults={
                'description': f"Istaknite svoj stil i eleganciju uz miris {p['name']}. Ovaj ekskluzivni proizvod iz kategorije {p['cat'].lower()} savršen je odabir za ljubitelje kategorije {p['int'].lower()}. Idealan poklon za prigode poput {p['occ'].lower()}.",
                'price': p['price'],
                'category': p['cat'],
                'interests': p['int'],
                'occasion': p['occ']
            }
        )
        if created:
            count += 1

    print(f"Uspješno dodano {count} novih parfema!")

if __name__ == "__main__":
    seed_perfumes()