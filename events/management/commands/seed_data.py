import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from events.models import Category, Event, Order, Ticket, UserProfile
from events.utils import generate_order_code, generate_ticket_code, generate_qr_code_image


class Command(BaseCommand):
    help = 'Populates 3 sample events for Summer Pop Festival 2026 (Kelompok 4)'

    def handle(self, *args, **options):
        self.stdout.write("Mereset data dan mengisi 3 event utama Summer Pop Festival...")

        # Clear old events to ensure exactly 3 events
        Ticket.objects.all().delete()
        Order.objects.all().delete()
        Event.objects.all().delete()

        # 1. Create Superuser / Admin
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@summerpopfest.com',
                'first_name': 'Panitia Summer Pop',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            UserProfile.objects.get_or_create(user=admin_user, defaults={'phone': '081234567890', 'is_organizer': True, 'organization_name': 'Summer Pop Official'})
            self.stdout.write("-> User Superuser/Admin: admin / admin123")
        else:
            admin_user.set_password('admin123')
            admin_user.save()

        # 2. Create Event Organizer User
        org_user, created = User.objects.get_or_create(
            username='organizer',
            defaults={
                'email': 'eo@summerpopfest.com',
                'first_name': 'Kelompok 4 Organizer'
            }
        )
        if created:
            org_user.set_password('organizer123')
            org_user.save()
            UserProfile.objects.get_or_create(user=org_user, defaults={'phone': '081987654321', 'is_organizer': True, 'organization_name': 'Kelompok 4 Music Tour'})
            self.stdout.write("-> User Organizer: organizer / organizer123")
        else:
            org_user.set_password('organizer123')
            org_user.save()

        # 3. Create Regular Customer User
        peserta_user, created = User.objects.get_or_create(
            username='peserta1',
            defaults={
                'email': 'peserta1@gmail.com',
                'first_name': 'Nabila Fajrin'
            }
        )
        if created:
            peserta_user.set_password('peserta123')
            peserta_user.save()
            UserProfile.objects.get_or_create(user=peserta_user, defaults={'phone': '085712345678', 'is_organizer': False})
            self.stdout.write("-> User Peserta: peserta1 / peserta123")
        else:
            peserta_user.set_password('peserta123')
            peserta_user.save()

        # 4. Create Categories
        categories_data = [
            {'name': 'Main Stage (Pop & Live)', 'slug': 'main-stage', 'icon': 'fa-music', 'description': 'Konser musik live panggung utama.'},
            {'name': 'Beach & Sunset Vibe', 'slug': 'beach-stage', 'icon': 'fa-sun', 'description': 'Panggung santai pantai dengan sunset acoustic.'},
            {'name': 'Mountain Camping Zone', 'slug': 'camping-chill', 'icon': 'fa-campground', 'description': 'Festival camp di area pegunungan sejuk.'},
        ]

        category_objs = {}
        for cat in categories_data:
            c_obj, _ = Category.objects.get_or_create(
                slug=cat['slug'],
                defaults={
                    'name': cat['name'],
                    'icon': cat['icon'],
                    'description': cat['description']
                }
            )
            category_objs[cat['slug']] = c_obj

        # 5. Create EXACTLY 3 EVENTS
        now = timezone.now()
        events_data = [
            {
                'title': 'Summer Pop Festival 2026 - Jakarta Edition',
                'slug': 'summer-pop-festival-jakarta-2026',
                'category': category_objs['main-stage'],
                'organizer': admin_user,
                'description': '🌈 Festival Musik Musim Panas Terbesar di Jakarta! Menampilkan 15+ Guest Star Papan Atas, Giant Stage, Food Trucks, Photo Spot Aesthetic, & Fireworks Show 🎆.\n\nLineup: Hivi!, Maliq & D\'Essentials, Juicy Luicy, Nadin Amizah, & Special Guest Star!',
                'venue': 'Ancol Beach Park, Jakarta',
                'start_date': now + timedelta(days=15),
                'end_date': now + timedelta(days=17),
                'ticket_price': 250000,
                'total_quota': 1000,
                'quota_sold': 350,
                'status': 'UPCOMING'
            },
            {
                'title': 'Summer Pop Festival 2026 - Bali Sunset Vibes',
                'slug': 'summer-pop-festival-bali-2026',
                'category': category_objs['beach-stage'],
                'organizer': org_user,
                'description': '🌴 Pesta Musik Pantai Sunset Terbaik di Bali! Rasakan alunan musik akustik & DJ sunset party tepat di tepi pantai tropis yang memukau 🌊✨.',
                'venue': 'GWK Cultural Park, Bali',
                'start_date': now + timedelta(days=25),
                'end_date': now + timedelta(days=27),
                'ticket_price': 300000,
                'total_quota': 800,
                'quota_sold': 210,
                'status': 'UPCOMING'
            },
            {
                'title': 'Summer Pop Festival 2026 - Bandung Mountain Breeze',
                'slug': 'summer-pop-festival-bandung-2026',
                'category': category_objs['camping-chill'],
                'organizer': admin_user,
                'description': '🏕️ Konser Musik Hawa Sejuk Pegunungan Bandung! Dilengkapi area Glamping Festival, Stand Up Comedy Stage, dan Culinary Market 🍓.',
                'venue': 'Lembang Festival Park, Bandung',
                'start_date': now + timedelta(days=35),
                'end_date': now + timedelta(days=37),
                'ticket_price': 180000,
                'total_quota': 600,
                'quota_sold': 140,
                'status': 'UPCOMING'
            }
        ]

        for edata in events_data:
            Event.objects.create(**edata)

        self.stdout.write("-> Tepat 3 Event Summer Pop Festival berhasil dibuat.")

        # 6. Create Sample Order & Tickets
        sample_event = Event.objects.get(slug='summer-pop-festival-jakarta-2026')

        order_code = generate_order_code()
        order = Order.objects.create(
            order_code=order_code,
            buyer=peserta_user,
            event=sample_event,
            quantity=2,
            total_amount=sample_event.ticket_price * 2,
            payment_method='QRIS',
            payment_status='PAID',
            payment_date=timezone.now(),
            notes='Pemegang Tiket: Nabila & Sifriah'
        )

        for i in range(2):
            t_code = generate_ticket_code()
            qr_img = generate_qr_code_image(t_code)
            Ticket.objects.create(
                ticket_code=t_code,
                order=order,
                attendee_name=f"Peserta Demo {i+1} (Nabila/Sifriah)",
                attendee_email="peserta1@gmail.com",
                qr_code=qr_img,
                is_checked_in=(i == 0),
                checked_in_at=timezone.now() if i == 0 else None
            )

        self.stdout.write(self.style.SUCCESS("BERHASIL! 3 Event utama telah disiapkan."))
