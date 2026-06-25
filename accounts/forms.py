"""Accounts Forms"""

from django import forms


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control', 'placeholder': 'your@email.com', 'autocomplete': 'email',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 'placeholder': '••••••••', 'autocomplete': 'current-password',
        })
    )


class OTPForm(forms.Form):
    otp_code = forms.CharField(
        max_length=6, min_length=6, label='Enter 6-Digit OTP',
        widget=forms.TextInput(attrs={
            'class': 'form-control otp-input', 'placeholder': '000000',
            'inputmode': 'numeric', 'autocomplete': 'one-time-code', 'maxlength': '6',
        })
    )

    def clean_otp_code(self):
        code = self.cleaned_data['otp_code']
        if not code.isdigit():
            raise forms.ValidationError('OTP must contain only digits.')
        return code
