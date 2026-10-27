from django.core.management.base import BaseCommand
from django.utils import timezone
from api.models import MarketCenter, CardamomPrice
from decimal import Decimal


class Command(BaseCommand):
    help = 'Seeds realistic cardamom market centers and spot prices in Nepal'

    def handle(self, *args, **options):
        self.stdout.write("Seeding Nepali cardamom market data...")

        # 1. Market Centers
        centers_data = [
            {'name': 'Birtamod', 'district': 'Jhapa', 'location_notes': 'Primary Eastern Nepal Trading Hub'},
            {'name': 'Taplejung', 'district': 'Taplejung', 'location_notes': 'High Altitude Premium Production'},
            {'name': 'Ilam', 'district': 'Ilam', 'location_notes': 'Fikkal Commercial Mandi'},
            {'name': 'Panchthar', 'district': 'Panchthar', 'location_notes': 'Phidim Collection Hub'},
            {'name': 'Sankhuwasabha', 'district': 'Sankhuwasabha', 'location_notes': 'Khandbari Organic Belt'},
            {'name': 'Dhankuta', 'district': 'Dhankuta', 'location_notes': 'Hilly Agro-Market Center'},
        ]

        created_centers = {}
        for c in centers_data:
            center, created = MarketCenter.objects.get_or_create(
                name=c['name'],
                defaults={'district': c['district'], 'location_notes': c['location_notes']}
            )
            created_centers[c['name']] = center
            status_text = "Created" if created else "Exists"
            self.stdout.write(f"  [{status_text}] Market Center: {center.name}")

        # 2. Cardamom Prices (NPR rates)
        # Note: 1 'man' in Nepali agricultural trade is exactly 40 kilograms.
        today = timezone.now().date()
        prices_data = [
            {
                'market': 'Birtamod',
                'variety': 'Jhirse',
                'price_per_kg': Decimal('1065.00'),
                'price_per_man': Decimal('42600.00'),
                'trend': 'up',
                'change_percentage': '+2.5%'
            },
            {
                'market': 'Taplejung',
                'variety': 'Ramsai',
                'price_per_kg': Decimal('1045.00'),
                'price_per_man': Decimal('41800.00'),
                'trend': 'stable',
                'change_percentage': '0.0%'
            },
            {
                'market': 'Ilam',
                'variety': 'Jhirse',
                'price_per_kg': Decimal('1055.00'),
                'price_per_man': Decimal('42200.00'),
                'trend': 'down',
                'change_percentage': '-1.2%'
            },
            {
                'market': 'Panchthar',
                'variety': 'Golshai',
                'price_per_kg': Decimal('1030.00'),
                'price_per_man': Decimal('41200.00'),
                'trend': 'up',
                'change_percentage': '+1.8%'
            },
            {
                'market': 'Sankhuwasabha',
                'variety': 'Ramsai',
                'price_per_kg': Decimal('1040.00'),
                'price_per_man': Decimal('41600.00'),
                'trend': 'stable',
                'change_percentage': '+0.5%'
            },
            {
                'market': 'Dhankuta',
                'variety': 'Jhirse',
                'price_per_kg': Decimal('1035.00'),
                'price_per_man': Decimal('41400.00'),
                'trend': 'down',
                'change_percentage': '-0.8%'
            },
        ]

        # Clear existing prices for today to allow re-seeding cleanly
        CardamomPrice.objects.filter(recorded_date=today).delete()

        for p in prices_data:
            center = created_centers[p['market']]
            CardamomPrice.objects.create(
                market=center,
                variety=p['variety'],
                price_per_kg=p['price_per_kg'],
                price_per_man=p['price_per_man'],
                trend=p['trend'],
                change_percentage=p['change_percentage'],
                recorded_date=today
            )
            self.stdout.write(f"  [Seeded] {p['market']} - {p['variety']}: NPR {p['price_per_kg']}/kg")

        self.stdout.write(self.style.SUCCESS("Successfully seeded KrishiMitra database with realistic Nepali market data!"))
