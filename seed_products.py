import os
import django

# Postavljanje Django okruženja
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'giftai_backend.settings')
django.setup()

from core.models import Product

def seed_data():
    products = [
        {
            "name": "Pametni sat GT4",
            "description": "Prati korake, spavanje i obavijesti. Vodootporan.",
            "price": 199.99,
            "category": "Elektronika",
            "interests": "tehnologija, fitness, gadgeti",
            "occasion": "rođendan, Božić"
        },
        {
            "name": "Set za njegu lica (Organic)",
            "description": "Prirodna ulja i kreme za dubinsku hidrataciju.",
            "price": 45.00,
            "category": "Njega",
            "interests": "ljepota, kozmetika, opuštanje",
            "occasion": "Valentinovo, majčin dan"
        },
        {
            "name": "Kožni novčanik",
            "description": "Ručno izrađen od prave talijanske kože.",
            "price": 35.50,
            "category": "Moda",
            "interests": "stil, elegancija, praktičnost",
            "occasion": "godišnjica, promocija"
        },
        {
            "name": "Bežične slušalice Noise-Cancelling",
            "description": "Vrhunski zvuk bez vanjske buke.",
            "price": 120.00,
            "category": "Elektronika",
            "interests": "glazba, tehnologija, putovanja",
            "occasion": "rođendan, diplomiranje"
        }
    ]

    for p in products:
        Product.objects.get_or_create(
            name=p['name'],
            defaults=p
        )
    print("Baza uspješno popunjena proizvodima!")

if __name__ == '__main__':
    seed_data()