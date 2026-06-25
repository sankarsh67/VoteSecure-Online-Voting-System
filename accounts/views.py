"""
Accounts Views
Includes: MFA login with role toggle, OTP verify, voter self-registration,
profile page, password change, CSV upload.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib import messages
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.conf import settings
import csv, io

from .models import User, VoterProfile, OTPRecord, AuditLog
from .forms import LoginForm, OTPForm


class LoginView(View):
    template_name = 'accounts/login.html'

    @method_decorator(csrf_protect)
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard:home')
        return render(request, self.template_name, {'form': LoginForm()})

    @method_decorator(csrf_protect)
    def post(self, request):
        form = LoginForm(data=request.POST)
        login_role = request.POST.get('login_role', 'voter')

        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)

            if user and user.is_active:
                if login_role == 'admin' and not user.is_admin:
                    messages.error(request, 'This account does not have admin access.')
                    return render(request, self.template_name, {'form': form})
                if login_role == 'voter' and not user.is_voter:
                    messages.error(request, 'Please use Admin Login for admin accounts.')
                    return render(request, self.template_name, {'form': form})

                otp = OTPRecord.generate(user, purpose='login')
                self._send_otp_email(user, otp.otp_code)
                request.session['pre_auth_user_id'] = user.id
                AuditLog.log('otp_sent', request, user, 'Login OTP sent')
                messages.info(request, f'OTP sent to {user.email}. Valid for {settings.OTP_EXPIRY_MINUTES} minutes.')
                return redirect('accounts:verify_otp')
            else:
                AuditLog.log('login_failed', request, description=f'Failed login for {form.cleaned_data.get("email")}')
                messages.error(request, 'Invalid email or password.')

        return render(request, self.template_name, {'form': form})

    def _send_otp_email(self, user, code):
        try:
            send_mail(
                subject='VoteSecure — Your Login OTP',
                message=f'Dear {user.full_name},\n\nYour OTP is: {code}\n\nValid for {settings.OTP_EXPIRY_MINUTES} minutes.\n\nDo not share this with anyone.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception:
            print(f"[DEV] OTP for {user.email}: {code}")


class OTPVerificationView(View):
    template_name = 'accounts/otp_verify.html'

    def get(self, request):
        if 'pre_auth_user_id' not in request.session:
            return redirect('accounts:login')
        return render(request, self.template_name, {'form': OTPForm()})

    @method_decorator(csrf_protect)
    def post(self, request):
        user_id = request.session.get('pre_auth_user_id')
        if not user_id:
            return redirect('accounts:login')

        form = OTPForm(data=request.POST)
        if form.is_valid():
            entered_otp = form.cleaned_data['otp_code']
            try:
                user = User.objects.get(id=user_id)
                otp = OTPRecord.objects.filter(user=user, purpose='login', is_used=False).latest('created_at')

                if otp.is_valid() and otp.otp_code == entered_otp:
                    otp.is_used = True
                    otp.save()
                    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
                    user.last_login_ip = ip
                    user.save(update_fields=['last_login_ip'])
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    del request.session['pre_auth_user_id']
                    AuditLog.log('login', request, user, 'Successful MFA login')
                    messages.success(request, f'Welcome, {user.first_name}!')
                    return redirect('dashboard:home')
                else:
                    messages.error(request, 'Invalid or expired OTP.')
                    AuditLog.log('login_failed', request, user, 'Invalid OTP')
            except (User.DoesNotExist, OTPRecord.DoesNotExist):
                messages.error(request, 'OTP verification failed.')

        return render(request, self.template_name, {'form': form})


class LogoutView(LoginRequiredMixin, View):
    def post(self, request):
        AuditLog.log('logout', request, request.user)
        logout(request)
        messages.info(request, 'You have been securely logged out.')
        return redirect('accounts:login')


class VoterRegisterView(View):
    """Self-registration for new voters."""
    template_name = 'accounts/register_voter.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard:home')
        return render(request, self.template_name)

    @method_decorator(csrf_protect)
    def post(self, request):
        data = request.POST
        errors = []

        email = data.get('email', '').strip().lower()
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        voter_id = data.get('voter_id', '').strip()
        phone = data.get('phone', '').strip()
        constituency = data.get('constituency', '').strip()
        password1 = data.get('password1', '')
        password2 = data.get('password2', '')

        if not all([email, first_name, last_name, voter_id, password1]):
            errors.append('All required fields must be filled.')
        if password1 != password2:
            errors.append('Passwords do not match.')
        if len(password1) < 8:
            errors.append('Password must be at least 8 characters.')
        if User.objects.filter(email=email).exists():
            errors.append('An account with this email already exists.')
        if VoterProfile.objects.filter(voter_id=voter_id).exists():
            errors.append('This Voter ID is already registered.')

        if errors:
            return render(request, self.template_name, {'errors': errors})

        user = User.objects.create_user(
            email=email, password=password1, first_name=first_name,
            last_name=last_name, role='voter',
        )
        VoterProfile.objects.create(
            user=user, voter_id=voter_id, phone=phone, constituency=constituency,
        )
        AuditLog.log('admin_action', request, description=f'New voter self-registered: {email}')
        messages.success(request, 'Registration successful! Please login.')
        return redirect('accounts:login')


class ProfileView(LoginRequiredMixin, View):
    template_name = 'accounts/profile.html'

    def get(self, request):
        from votes.models import Vote
        votes = Vote.objects.filter(voter=request.user).select_related('election').order_by('-cast_at')
        return render(request, self.template_name, {'votes': votes})


class ChangePasswordView(LoginRequiredMixin, View):
    @method_decorator(csrf_protect)
    def post(self, request):
        current = request.POST.get('current_password', '')
        new1 = request.POST.get('new_password1', '')
        new2 = request.POST.get('new_password2', '')

        if not request.user.check_password(current):
            messages.error(request, 'Current password is incorrect.')
        elif new1 != new2:
            messages.error(request, 'New passwords do not match.')
        elif len(new1) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
        else:
            request.user.set_password(new1)
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Password changed successfully!')

        return redirect('accounts:profile')


class VoterCSVUploadView(LoginRequiredMixin, View):
    template_name = 'accounts/voter_upload.html'

    def get(self, request):
        if not request.user.is_admin:
            return redirect('dashboard:home')
        return render(request, self.template_name)

    def post(self, request):
        if not request.user.is_admin:
            return redirect('dashboard:home')

        csv_file = request.FILES.get('csv_file')
        if not csv_file or not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a valid CSV file.')
            return render(request, self.template_name)

        created, errors = 0, []
        decoded = csv_file.read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(decoded))

        for i, row in enumerate(reader, start=2):
            try:
                email = row['email'].strip().lower()
                if User.objects.filter(email=email).exists():
                    errors.append(f"Row {i}: {email} already exists")
                    continue
                user = User.objects.create_user(
                    email=email, password=User.objects.make_random_password(12),
                    first_name=row.get('first_name', '').strip(),
                    last_name=row.get('last_name', '').strip(), role='voter',
                )
                VoterProfile.objects.create(
                    user=user, voter_id=row.get('voter_id', '').strip(),
                    phone=row.get('phone', '').strip(),
                    constituency=row.get('constituency', '').strip(),
                )
                created += 1
            except Exception as e:
                errors.append(f"Row {i}: {str(e)}")

        AuditLog.log('voter_uploaded', request, request.user, f'{created} voters imported')
        messages.success(request, f'{created} voters registered successfully.')
        if errors:
            messages.warning(request, f'{len(errors)} errors: {"; ".join(errors[:5])}')
        return redirect('dashboard:home')
