from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from .models import ShippingAddress


class ShippingForm(forms.ModelForm):
    shipping_first_name = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
        required=True
    )
    shipping_last_name = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
        required=True
    )
    shipping_email = forms.EmailField(  # ← EmailField statt CharField
        label="",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
        required=True
    )
    shipping_address1 = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address1'}),
        required=True
    )
    shipping_address2 = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address2'}),
        required=False
    )
    shipping_city = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
        required=True
    )
    shipping_state = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'}),
        required=False
    )
    shipping_zipcode = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Zipcode'}),
        required=False
    )
    shipping_country = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}),
        required=True
    )

    # Optionale Passwort-Felder für Kontoerstellung nach Checkout
    account_password1 = forms.CharField(
        label="",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Create password (optional)'}),
        required=False
    )
    account_password2 = forms.CharField(
        label="",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Repeat password'}),
        required=False
    )

    class Meta:
        model = ShippingAddress
        fields = [
            'shipping_first_name', 'shipping_last_name', 'shipping_email',
            'shipping_address1', 'shipping_address2', 'shipping_city',
            'shipping_state', 'shipping_zipcode', 'shipping_country'
        ]
        # Passwort-Felder sind keine Model-Felder und gehören nicht in Meta.fields.

    # Optional fields return None instead of empty string
    def clean_shipping_address2(self):
        return self.cleaned_data.get('shipping_address2') or None

    def clean_shipping_state(self):
        return self.cleaned_data.get('shipping_state') or None

    def clean_shipping_zipcode(self):
        return self.cleaned_data.get('shipping_zipcode') or None

    def clean(self):
        """
        Wenn eins der Passwort-Felder ausgefüllt ist:
        - Müssen beide übereinstimmen
        - Läuft über Django's Passwort-Validatoren
        """
        cleaned = super().clean()
        p1 = cleaned.get('account_password1') or ''
        p2 = cleaned.get('account_password2') or ''

        if p1 or p2:
            if p1 != p2:
                self.add_error('account_password2', "Passwords don't match.")
            else:
                try:
                    # nutzt settings.AUTH_PASSWORD_VALIDATORS
                    validate_password(p1)
                except ValidationError as e:
                    self.add_error('account_password1', e)

        return cleaned


class PaymentForm(forms.Form):
    card_name = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name On Card'}), required=True)
    card_number = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Card Number'}), required=True)
    card_exp_date = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Expiration Date'}), required=True)
    card_cvv_number = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CVV Code'}), required=True)
    card_address1 = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Billing Address 1'}), required=True)
    card_address2 = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Billing Address 2'}), required=False)
    card_city = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Billing City'}), required=True)
    card_state = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Billing State'}), required=True)
    card_zipcode = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Billing Zipcode'}), required=True)
    card_country = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Billing Country'}), required=True)
