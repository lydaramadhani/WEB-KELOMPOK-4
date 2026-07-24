import os
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, default='')
    is_organizer = models.BooleanField(default=False)
    organization_name = models.CharField(max_length=100, blank=True, default='')

    def __str__(self):
        return f"{self.user.username} - {'Organizer' if self.is_organizer else 'Peserta'}"


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    icon = models.CharField(max_length=50, default='fa-calendar-alt')
    description = models.TextField(blank=True, default='')

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Event(models.Model):
    STATUS_CHOICES = (
        ('UPCOMING', 'Upcoming'),
        ('ONGOING', 'Sedang Berlangsung'),
        ('FINISHED', 'Selesai'),
        ('CANCELLED', 'Dibatalkan'),
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='events')
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_events')
    description = models.TextField()
    venue = models.CharField(max_length=200)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    ticket_price = models.DecimalField(max_digits=12, decimal_places=0)
    total_quota = models.IntegerField()
    quota_sold = models.IntegerField(default=0)
    poster = models.ImageField(upload_to='posters/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='UPCOMING')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Event.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def remaining_quota(self):
        return max(0, self.total_quota - self.quota_sold)

    @property
    def is_sold_out(self):
        return self.remaining_quota <= 0

    def __str__(self):
        return self.title


class Order(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ('BANK_TRANSFER', 'Transfer Bank (BCA / BNI / BRI)'),
        ('EWALLET', 'E-Wallet (GoPay / OVO / Dana)'),
        ('QRIS', 'QRIS Instant'),
    )

    PAYMENT_STATUS_CHOICES = (
        ('PENDING', 'Menunggu Verifikasi'),
        ('PAID', 'Lunas / Disetujui'),
        ('REJECTED', 'Ditolak'),
        ('CANCELLED', 'Dibatalkan'),
    )

    order_code = models.CharField(max_length=30, unique=True)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='orders')
    quantity = models.IntegerField(default=1)
    total_amount = models.DecimalField(max_digits=12, decimal_places=0)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, default='QRIS')
    payment_proof = models.ImageField(upload_to='payment_proofs/', blank=True, null=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    payment_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order_code} - {self.buyer.username} ({self.event.title})"


class Ticket(models.Model):
    ticket_code = models.CharField(max_length=30, unique=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='tickets')
    attendee_name = models.CharField(max_length=150)
    attendee_email = models.EmailField()
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    is_checked_in = models.BooleanField(default=False)
    checked_in_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['ticket_code']

    def __str__(self):
        return f"{self.ticket_code} - {self.attendee_name}"
