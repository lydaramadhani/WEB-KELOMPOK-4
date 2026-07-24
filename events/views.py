# Modul checkout tiket dan proses transaksi pengguna
# Proses transaksi dan metode pembayaran tiket pengguna
import datetime
from django.shortcuts import render, redirect, get_object_or_404
# Pengelolaan proses pembayaran digital dan transaksi tiket pengguna
# Pengelolaan alur booking tiket hingga penerbitan e-ticket
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth.models import User

from .models import Event, Category, Order, Ticket, UserProfile
from .forms import (
    RegisterForm, EventForm, CategoryForm, CheckoutForm,
    PaymentProofForm, TicketValidationForm
)
from .utils import generate_order_code, generate_ticket_code, generate_qr_code_image


# ==========================================
# AUTHENTICATION & PROFILE VIEWS
# ==========================================

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.first_name = form.cleaned_data['full_name']
            user.email = form.cleaned_data['email']
            user.save()

            UserProfile.objects.create(
                user=user,
                phone=form.cleaned_data.get('phone', ''),
                is_organizer=form.cleaned_data.get('is_organizer', False),
                organization_name=form.cleaned_data.get('organization_name', '')
            )

            messages.success(request, f"Akun {user.username} berhasil dibuat! Silakan masuk.")
            return redirect('login')
        else:
            messages.error(request, "Terjadi kesalahan pada formulir pendaftaran. Silakan periksa kembali data Anda.")
    else:
        form = RegisterForm()

    return render(request, 'auth/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Selamat datang kembali, {user.first_name or user.username}!")
                
                # Check profile redirect
                if hasattr(user, 'profile') and user.profile.is_organizer or user.is_staff:
                    return redirect('organizer_dashboard')
                return redirect('home')
            else:
                messages.error(request, "Username atau password tidak valid.")
        else:
            messages.error(request, "Username atau password salah.")
    else:
        form = AuthenticationForm()

    return render(request, 'auth/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "Anda telah berhasil keluar.")
    return redirect('home')


@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        organization_name = request.POST.get('organization_name')

        request.user.first_name = full_name
        request.user.email = email
        request.user.save()

        profile.phone = phone
        profile.organization_name = organization_name
        profile.save()

        messages.success(request, "Profil Anda telah diperbarui.")
        return redirect('profile')

    return render(request, 'auth/profile.html', {'profile': profile})


# ==========================================
# PUBLIC EVENT & PESERTA VIEWS
# ==========================================

def home_view(request):
    query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '').strip()
    status_filter = request.GET.get('status', '').strip()
    sort_by = request.GET.get('sort', '-start_date')

    events = Event.objects.all()

    if query:
        events = events.filter(
            Q(title__icontains=query) |
            Q(venue__icontains=query) |
            Q(description__icontains=query)
        )

    if category_slug:
        events = events.filter(category__slug=category_slug)

    if status_filter:
        events = events.filter(status=status_filter)

    events = events.order_by(sort_by)

    paginator = Paginator(events, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    featured_events = Event.objects.filter(status='UPCOMING')[:3]

    context = {
        'events': page_obj,
        'page_obj': page_obj,
        'featured_events': featured_events,
        'selected_category': category_slug,
        'selected_status': status_filter,
        'query': query,
        'sort_by': sort_by,
    }
    return render(request, 'events/event_list.html', context)


def event_detail_view(request, slug):
    event = get_object_or_404(Event, slug=slug)
    related_events = Event.objects.filter(category=event.category).exclude(id=event.id)[:3]

    is_eo_or_admin = False
    if request.user.is_authenticated:
        if request.user.is_staff or (hasattr(request.user, 'profile') and request.user.profile.is_organizer):
            is_eo_or_admin = True

    context = {
        'event': event,
        'related_events': related_events,
        'is_eo_or_admin': is_eo_or_admin,
    }
    return render(request, 'events/event_detail.html', context)


@login_required
def checkout_view(request, slug):
    # Restrict Organizers & Admin from buying tickets
    if request.user.is_staff or (hasattr(request.user, 'profile') and request.user.profile.is_organizer):
        messages.warning(request, "Akun Event Organizer / Admin tidak dapat membeli tiket. Silakan gunakan akun Peserta untuk memesan tiket.")
        return redirect('event_detail', slug=slug)

    event = get_object_or_404(Event, slug=slug)

    if event.is_sold_out:
        messages.error(request, "Maaf, tiket untuk event ini telah habis (Sold Out).")
        return redirect('event_detail', slug=event.slug)

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            payment_method = form.cleaned_data['payment_method']
            attendee_name = form.cleaned_data['attendee_name']
            attendee_email = form.cleaned_data['attendee_email']

            if quantity > event.remaining_quota:
                messages.error(request, f"Jumlah pesanan melebihi sisa tiket yang tersedia ({event.remaining_quota} tiket tersisa).")
                return redirect('checkout', slug=event.slug)

            total_amount = event.ticket_price * quantity
            order_code = generate_order_code()

            # Strictly PENDING until Organizer verifies payment proof
            order = Order.objects.create(
                order_code=order_code,
                buyer=request.user,
                event=event,
                quantity=quantity,
                total_amount=total_amount,
                payment_method=payment_method,
                payment_status='PENDING',
                notes=f"Pemegang Tiket: {attendee_name} ({attendee_email})"
            )

            messages.success(request, f"Pesanan {order_code} berhasil dibuat. Silakan unggah bukti pembayaran untuk diverifikasi oleh Organizer.")
            return redirect('order_confirmation', order_code=order.order_code)
    else:
        initial_data = {
            'quantity': 1,
            'attendee_name': request.user.get_full_name() or request.user.username,
            'attendee_email': request.user.email
        }
        form = CheckoutForm(initial=initial_data)

    context = {
        'event': event,
        'form': form
    }
    return render(request, 'events/checkout.html', context)


@login_required
def order_confirmation_view(request, order_code):
    order = get_object_or_404(Order, order_code=order_code, buyer=request.user)

    if request.method == 'POST':
        form = PaymentProofForm(request.POST, request.FILES, instance=order)
        if form.is_valid():
            order_obj = form.save(commit=False)
            order_obj.payment_status = 'PENDING'  # Always PENDING for Organizer review
            order_obj.save()
            
            messages.success(request, "Bukti pembayaran berhasil diunggah! Data Anda langsung masuk ke Organizer untuk diverifikasi.")
            return redirect('my_tickets')
    else:
        form = PaymentProofForm(instance=order)

    context = {
        'order': order,
        'form': form
    }
    return render(request, 'events/order_confirmation.html', context)


@login_required
def my_tickets_view(request):
    orders = Order.objects.filter(buyer=request.user).order_by('-created_at')
    tickets = Ticket.objects.filter(order__buyer=request.user).order_by('-created_at')

    context = {
        'orders': orders,
        'tickets': tickets
    }
    return render(request, 'events/my_tickets.html', context)


@login_required
def ticket_detail_view(request, ticket_code):
    ticket = get_object_or_404(Ticket, ticket_code=ticket_code)

    # Allow buyer, organizer of event, or staff to view ticket
    if ticket.order.buyer != request.user and ticket.order.event.organizer != request.user and not request.user.is_staff:
        messages.error(request, "Anda tidak memiliki akses untuk melihat tiket ini.")
        return redirect('my_tickets')

    context = {
        'ticket': ticket
    }
    return render(request, 'events/ticket_detail.html', context)


# ==========================================
# ORGANIZER & ADMIN VIEWS (DIFFERENTIATED)
# ==========================================

def organizer_required(view_func):
    """Decorator ensuring user is logged in and is an organizer or staff."""
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        is_org = hasattr(request.user, 'profile') and request.user.profile.is_organizer
        if not (is_org or request.user.is_staff):
            messages.error(request, "Akses khusus Event Organizer. Silakan hubungi admin atau daftar sebagai EO.")
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


@organizer_required
def organizer_dashboard_view(request):
    is_master_admin = request.user.is_staff or request.user.is_superuser

    # Differentiate scope: Master Admin sees all events/data system-wide; Regular EO sees only their events
    if is_master_admin:
        user_events = Event.objects.all()
        related_orders = Order.objects.all()
        user_count = User.objects.count()
        organizer_count = UserProfile.objects.filter(is_organizer=True).count()
    else:
        user_events = Event.objects.filter(organizer=request.user)
        related_orders = Order.objects.filter(event__in=user_events)
        user_count = None
        organizer_count = None

    total_events = user_events.count()
    active_events = user_events.filter(status__in=['UPCOMING', 'ONGOING']).count()

    paid_orders = related_orders.filter(payment_status='PAID')
    pending_orders = related_orders.filter(payment_status='PENDING')

    # Live Real-time Active Analytics calculations
    total_tickets_sold = paid_orders.aggregate(Sum('quantity'))['quantity__sum'] or 0
    total_revenue = paid_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    tickets_created = Ticket.objects.filter(order__in=paid_orders)
    total_tickets_created = tickets_created.count()
    total_checked_in = tickets_created.filter(is_checked_in=True).count()
    attendance_rate = round((total_checked_in / total_tickets_created * 100), 1) if total_tickets_created > 0 else 0

    recent_orders = related_orders.select_related('event', 'buyer')[:6]
    recent_events = user_events[:6]

    # Category revenue breakdown for chart/analytics display
    category_analytics = Category.objects.annotate(
        event_count=Count('events'),
        revenue=Sum('events__orders__total_amount', filter=Q(events__orders__payment_status='PAID'))
    ).values('name', 'event_count', 'revenue')

    context = {
        'is_master_admin': is_master_admin,
        'total_events': total_events,
        'active_events': active_events,
        'total_tickets_sold': total_tickets_sold,
        'total_revenue': total_revenue,
        'pending_orders_count': pending_orders.count(),
        'total_checked_in': total_checked_in,
        'attendance_rate': attendance_rate,
        'user_count': user_count,
        'organizer_count': organizer_count,
        'recent_orders': recent_orders,
        'recent_events': recent_events,
        'category_analytics': category_analytics,
    }
    return render(request, 'organizer/dashboard.html', context)


@organizer_required
def organizer_event_list_view(request):
    is_master_admin = request.user.is_staff or request.user.is_superuser
    events = Event.objects.all() if is_master_admin else Event.objects.filter(organizer=request.user)
    return render(request, 'organizer/event_list_manage.html', {'events': events, 'is_master_admin': is_master_admin})


@organizer_required
def organizer_event_create_view(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            messages.success(request, f"Event '{event.title}' berhasil dibuat!")
            return redirect('organizer_event_list')
    else:
        form = EventForm()

    return render(request, 'organizer/event_form.html', {'form': form, 'title': 'Tambah Event Baru'})


@organizer_required
def organizer_event_edit_view(request, pk):
    is_master_admin = request.user.is_staff or request.user.is_superuser
    event = get_object_or_404(Event, pk=pk)
    
    if not is_master_admin and event.organizer != request.user:
        messages.error(request, "Anda tidak memiliki hak untuk mengedit event milik EO lain.")
        return redirect('organizer_event_list')

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, f"Event '{event.title}' berhasil diperbarui!")
            return redirect('organizer_event_list')
    else:
        form = EventForm(instance=event)

    return render(request, 'organizer/event_form.html', {'form': form, 'title': f'Edit Event: {event.title}', 'event': event})


@organizer_required
def organizer_event_delete_view(request, pk):
    is_master_admin = request.user.is_staff or request.user.is_superuser
    event = get_object_or_404(Event, pk=pk)
    
    if not is_master_admin and event.organizer != request.user:
        messages.error(request, "Anda tidak memiliki hak untuk menghapus event ini.")
        return redirect('organizer_event_list')

    if request.method == 'POST':
        title = event.title
        event.delete()
        messages.success(request, f"Event '{title}' telah dihapus.")
        return redirect('organizer_event_list')

    return render(request, 'organizer/event_confirm_delete.html', {'event': event})


@organizer_required
def organizer_category_list_view(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            cat = form.save()
            messages.success(request, f"Kategori '{cat.name}' berhasil ditambahkan!")
            return redirect('organizer_category_list')
    else:
        form = CategoryForm()

    return render(request, 'organizer/category_list.html', {'categories': categories, 'form': form})


@organizer_required
def organizer_order_list_view(request):
    is_master_admin = request.user.is_staff or request.user.is_superuser
    
    if is_master_admin:
        orders = Order.objects.all().select_related('event', 'buyer')
    else:
        user_events = Event.objects.filter(organizer=request.user)
        orders = Order.objects.filter(event__in=user_events).select_related('event', 'buyer')

    status_filter = request.GET.get('status', '').strip()
    search_query = request.GET.get('q', '').strip()

    if status_filter:
        orders = orders.filter(payment_status=status_filter)

    if search_query:
        orders = orders.filter(
            Q(order_code__icontains=search_query) |
            Q(buyer__username__icontains=search_query) |
            Q(buyer__first_name__icontains=search_query) |
            Q(notes__icontains=search_query)
        )

    context = {
        'orders': orders,
        'selected_status': status_filter,
        'search_query': search_query,
        'is_master_admin': is_master_admin,
    }
    return render(request, 'organizer/order_list.html', context)


@organizer_required
def organizer_order_detail_view(request, pk):
    is_master_admin = request.user.is_staff or request.user.is_superuser
    
    if is_master_admin:
        order = get_object_or_404(Order, pk=pk)
    else:
        user_events = Event.objects.filter(organizer=request.user)
        order = get_object_or_404(Order, pk=pk, event__in=user_events)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            if order.payment_status != 'PAID':
                order.payment_status = 'PAID'
                order.payment_date = timezone.now()
                order.save()

                # Update event quota sold
                event = order.event
                event.quota_sold += order.quantity
                event.save()

                # Auto generate tickets upon organizer approval
                if not order.tickets.exists():
                    attendee_name = order.buyer.get_full_name() or order.buyer.username
                    attendee_email = order.buyer.email
                    for _ in range(order.quantity):
                        t_code = generate_ticket_code()
                        qr_file = generate_qr_code_image(t_code)
                        Ticket.objects.create(
                            ticket_code=t_code,
                            order=order,
                            attendee_name=attendee_name,
                            attendee_email=attendee_email,
                            qr_code=qr_file
                        )

                messages.success(request, f"Pesanan {order.order_code} disetujui & E-Ticket QR Code telah diterbitkan untuk pembeli.")
        elif action == 'reject':
            order.payment_status = 'REJECTED'
            order.save()
            messages.warning(request, f"Pesanan {order.order_code} telah ditolak.")

        return redirect('organizer_order_detail', pk=order.pk)

    return render(request, 'organizer/order_detail.html', {'order': order, 'is_master_admin': is_master_admin})


@organizer_required
def organizer_ticket_validation_view(request):
    is_master_admin = request.user.is_staff or request.user.is_superuser
    validation_result = None
    scanned_ticket = None

    if request.method == 'POST':
        form = TicketValidationForm(request.POST)
        if form.is_valid():
            t_code = form.cleaned_data['ticket_code'].strip().upper()
            try:
                scanned_ticket = Ticket.objects.select_related('order__event').get(ticket_code=t_code)
                
                # Verify organizer ownership if not master admin
                if not is_master_admin and scanned_ticket.order.event.organizer != request.user:
                    validation_result = {
                        'success': False,
                        'message': 'Tiket ini milik event EO lain. Anda tidak memiliki akses untuk check-in.'
                    }
                elif scanned_ticket.is_checked_in:
                    validation_result = {
                        'success': False,
                        'already_checked_in': True,
                        'message': f'PERINGATAN: Tiket sudah digunakan check-in pada {scanned_ticket.checked_in_at.strftime("%d %b %Y %H:%M")}.'
                    }
                elif scanned_ticket.order.payment_status != 'PAID':
                    validation_result = {
                        'success': False,
                        'message': 'TIKET TIDAK VALID: Pembayaran pesanan belum disetujui oleh Organizer.'
                    }
                else:
                    # Check in ticket
                    scanned_ticket.is_checked_in = True
                    scanned_ticket.checked_in_at = timezone.now()
                    scanned_ticket.save()

                    validation_result = {
                        'success': True,
                        'message': f'BERHASIL CHECK-IN! Selamat datang {scanned_ticket.attendee_name}.'
                    }
            except Ticket.DoesNotExist:
                validation_result = {
                    'success': False,
                    'message': f'Tiket dengan kode "{t_code}" tidak ditemukan dalam sistem.'
                }
    else:
        form = TicketValidationForm()

    context = {
        'form': form,
        'scanned_ticket': scanned_ticket,
        'result': validation_result,
        'is_master_admin': is_master_admin
    }
    return render(request, 'organizer/ticket_validation.html', context)


@organizer_required
def organizer_reports_view(request):
    is_master_admin = request.user.is_staff or request.user.is_superuser
    user_events = Event.objects.all() if is_master_admin else Event.objects.filter(organizer=request.user)

    selected_event_id = request.GET.get('event_id', '').strip()
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()

    filtered_events = user_events
    if selected_event_id:
        filtered_events = filtered_events.filter(id=selected_event_id)

    orders = Order.objects.filter(event__in=filtered_events, payment_status='PAID').select_related('event', 'buyer')

    if date_from:
        orders = orders.filter(created_at__date__gte=date_from)
    if date_to:
        orders = orders.filter(created_at__date__lte=date_to)

    total_sales_count = orders.aggregate(Sum('quantity'))['quantity__sum'] or 0
    total_income = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    tickets = Ticket.objects.filter(order__in=orders)
    total_tickets_created = tickets.count()
    total_checked_in = tickets.filter(is_checked_in=True).count()

    context = {
        'is_master_admin': is_master_admin,
        'events': user_events,
        'orders': orders,
        'selected_event_id': selected_event_id,
        'date_from': date_from,
        'date_to': date_to,
        'total_sales_count': total_sales_count,
        'total_income': total_income,
        'total_tickets_created': total_tickets_created,
        'total_checked_in': total_checked_in,
        'attendance_percentage': round((total_checked_in / total_tickets_created * 100), 1) if total_tickets_created > 0 else 0,
    }
    return render(request, 'organizer/reports.html', context)
