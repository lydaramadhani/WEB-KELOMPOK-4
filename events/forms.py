from django import forms
from django.contrib.auth.models import User
from .models import Event, Category, Order, UserProfile


class RegisterForm(forms.ModelForm):
    full_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Nama Lengkap'
    }))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control', 'placeholder': 'Email'
    }))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Nomor Telepon / WhatsApp'
    }))
    is_organizer = forms.BooleanField(required=False, label="Daftar sebagai Event Organizer (EO)", widget=forms.CheckboxInput(attrs={
        'class': 'form-check-input'
    }))
    organization_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Nama Organisasi / Komunitas (opsional)'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Kata Sandi'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Konfirmasi Kata Sandi'
    }))

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Konfirmasi password tidak cocok.")
        return cleaned_data


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'category', 'description', 'venue', 'start_date', 'end_date', 'ticket_price', 'total_quota', 'status', 'poster']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Judul Event'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Deskripsi rinci mengenai event...'}),
            'venue': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Lokasi / Nama Tempat (Venue)'}),
            'start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'ticket_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Harga tiket per lembar (Rp)'}),
            'total_quota': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Total kuota tiket'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'poster': forms.FileInput(attrs={'class': 'form-control'}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'icon', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama Kategori'}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'FontAwesome Icon class (e.g. fa-music)'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Deskripsi singkat'}),
        }


class CheckoutForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, initial=1, widget=forms.NumberInput(attrs={
        'class': 'form-control text-center fw-bold', 'id': 'id_quantity'
    }))
    payment_method = forms.ChoiceField(choices=Order.PAYMENT_METHOD_CHOICES, widget=forms.RadioSelect(attrs={
        'class': 'form-check-input'
    }))
    attendee_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Nama Lengkap Pemegang Tiket'
    }))
    attendee_email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control', 'placeholder': 'Email Pengiriman E-Ticket'
    }))


class PaymentProofForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['payment_proof', 'notes']
        widgets = {
            'payment_proof': forms.FileInput(attrs={'class': 'form-control', 'required': True}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Catatan transfer / Nama pengirim rekening...'}),
        }


class TicketValidationForm(forms.Form):
    ticket_code = forms.CharField(max_length=50, widget=forms.TextInput(attrs={
        'class': 'form-control form-control-lg text-uppercase font-monospace',
        'placeholder': 'Masukkan Kode Tiket (misal: TKT-20260724-XXXX)',
        'autofocus': True
    }))
