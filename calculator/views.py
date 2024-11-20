
from .serializers import UserProfileSerializer, PregnancyCheckupSerializer, CheckupVisitSerializer
from .models import UserProfile, PregnancyCheckup, CheckupVisit
from rest_framework import viewsets
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile
from django.contrib.auth import logout
from datetime import datetime
from django.utils.timezone import make_aware
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from datetime import timedelta
from django.utils import timezone
from datetime import datetime
from .models import PregnancyCheckup, CheckupVisit
from .forms import *
from .models import *
from datetime import datetime, timedelta
import nepali_datetime
from django.shortcuts import render, redirect
from .forms import UserProfileForm
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile


from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile
from django.contrib.auth import update_session_auth_hash
from django.views.decorators.csrf import csrf_protect


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            return redirect('login')
    else:
        form = UserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Redirect to home page after successful login
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def user_logout(request):
    logout(request)
    return redirect('login')


@login_required
def profile(request, user_id=None):
    if user_id:
        user = get_object_or_404(User, id=user_id)
    else:
        if request.user.is_authenticated:
            user = request.user
        else:
            return render(request, 'accounts/error.html', {'message': 'User not found'})

    # Use get_or_create to ensure a UserProfile exists
    user_profile, created = UserProfile.objects.get_or_create(user=user)

    return render(request, 'accounts/view_profile.html', {'profile': user_profile})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES,
                               instance=request.user.userprofile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user.userprofile)
    return render(request, 'accounts/edit_profile.html', {'form': form})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Keep the user logged in after password change
            update_session_auth_hash(request, user)
            messages.success(
                request, 'Your password was successfully updated!')
            return redirect('profile')  # Redirect to profile or any other page
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'accounts/change_password.html', {'form': form})


@login_required
def base(request):
    return render(request, 'base.html')


@login_required
def home(request):
    return render(request, 'calculator/home.html')


@login_required
def english_date(request):
    result = None
    today = datetime.today().date()  # Current date

    if request.method == 'POST':
        form = PregnancyCalculatorForm(request.POST)
        if form.is_valid():
            last_period_date = form.cleaned_data['last_period_date']

            # Calculate days since the last period
            days_since_lmp = (today - last_period_date).days

            # Calculate current weeks of pregnancy (approx)
            pregnancy_weeks = days_since_lmp // 7

            # Calculate EDD (Estimated Due Date) by adding 280 days (standard 40 weeks)
            edd = last_period_date + timedelta(days=280)

            # Current gestational age or POG (Pregnancy of Gestation) in weeks
            current_pog = pregnancy_weeks

            result = {
                'edd': edd,
                'current_pog': current_pog,
                'pregnancy_weeks': pregnancy_weeks
            }
    else:
        form = PregnancyCalculatorForm()

    return render(request, 'calculator/english_date.html', {'form': form, 'result': result, 'today': today})


@login_required
def nepali_date(request):
    gestational_age_weeks = None
    gestational_age_days = None
    due_date_ad = None
    lmp_ad = None
    lmp_bs = None
    due_date_bs = None
    visit_date_bs = None
    visit_date_ad = None
    today_weekday = None
    lmp_weekday = None

    if request.method == 'POST':
        form = GestationalAgeForm(request.POST)

        if form.is_valid():
            # Get the LMP and Visit dates from the form
            lmp_nepali_str = form.cleaned_data.get('lmp_date')
            visit_date_nepali_str = form.cleaned_data.get('visit_date')

            try:
                # Convert the LMP date from BS to AD
                lmp_nepali = nepali_datetime.date(
                    *map(int, lmp_nepali_str.split('-')))
                lmp_ad = lmp_nepali.to_datetime_date()
                lmp_bs = lmp_nepali.strftime('%Y-%m-%d')

                # Calculate the Due Date (280 days from LMP)
                due_date_ad = lmp_ad + timedelta(days=280)
                due_date_bs = nepali_datetime.date.from_datetime_date(
                    due_date_ad).strftime('%Y-%m-%d')

                # Convert the manually entered visit date from BS to AD
                visit_date_nepali = nepali_datetime.date(
                    *map(int, visit_date_nepali_str.split('-')))
                visit_date_ad = visit_date_nepali.to_datetime_date()
                visit_date_bs = visit_date_nepali.strftime('%Y-%m-%d')

                # Calculate gestational age based on visit date and LMP
                total_gestational_age_days = (visit_date_ad - lmp_ad).days
                gestational_age_weeks = total_gestational_age_days // 7
                gestational_age_days = total_gestational_age_days % 7

                # Get weekday names
                nepali_weekdays = ['आइतबार', 'सोमबार', 'मङ्गलबार',
                                   'बुधबार', 'बिहीबार', 'शुक्रबार', 'शनिबार']
                today_weekday = nepali_weekdays[visit_date_nepali.weekday()]
                lmp_weekday = nepali_weekdays[lmp_nepali.weekday()]

            except ValueError:
                form.add_error(
                    'lmp_date', 'Invalid date format for LMP. Use the format: 2081-05-19')
                form.add_error(
                    'visit_date', 'Invalid date format for Visit Date. Use the format: 2081-06-15')
    else:
        form = GestationalAgeForm()

    return render(request, 'calculator/nepali_date.html', {
        'form': form,
        'gestational_age': f"{gestational_age_weeks} weeks, {gestational_age_days} days" if gestational_age_weeks is not None else None,
        'due_date': due_date_ad,
        'due_date_bs': due_date_bs,
        'lmp_ad': lmp_ad,
        'lmp_bs': lmp_bs,
        'visit_date_bs': visit_date_bs,
        'today_weekday': today_weekday,
        'lmp_weekday': lmp_weekday,
    })


@login_required
def add_pregnancy_checkup(request):
    if request.method == 'POST':
        form = PregnancyCheckupForm(request.POST)
        if form.is_valid():
            # Get the form data without saving it to the database yet
            checkup = form.save(commit=False)

            # Assign the current logged-in user to the checkup record
            checkup.user = request.user

            # If the arrival_date is not provided, use today's date in Nepali (BS)
            if not checkup.arrival_date:
                # This assumes you're using a custom date conversion
                nepali_date = datetime.now().date()
                checkup.arrival_date = str(nepali_date)

            # Convert Nepali date to AD date (if applicable)
            try:
                nepali_date_bs = datetime.strptime(
                    checkup.arrival_date, "%Y-%m-%d")
                # Assuming you have a function to convert BS to AD
                ad_date = nepali_date_bs.to_datetime_date()  # Convert to AD date if needed
                checkup.ad_arrival_date = ad_date.strftime("%Y-%m-%d")
            except Exception as e:
                print("Error in converting Nepali date to AD:", e)

            # Save the checkup with the user assigned
            checkup.save()
            return redirect('checkup_list')
    else:
        form = PregnancyCheckupForm()

    return render(request, 'calculator/add_pregnancy_checkup.html', {'form': form})


@login_required
def checkup_list(request):
    # Retrieve all checkups
    checkups = PregnancyCheckup.objects.all().order_by('-id')

    return render(request, 'calculator/checkup_list.html', {'checkups': checkups})


@login_required
def delete_checkup(request, checkup_id):
    checkup = get_object_or_404(PregnancyCheckup, id=checkup_id)
    checkup.delete()
    return redirect('checkup_list')


@login_required
def checkup_detail(request, patient_id):
    # Fetch the PregnancyCheckup object based on the patient_id
    checkup = get_object_or_404(PregnancyCheckup, pk=patient_id)

    # Initialize variables for the Nepali date calculation
    gestational_age_weeks = None
    gestational_age_days = None
    due_date_ad = None
    lmp_ad = None
    lmp_bs = None
    due_date_bs = None
    today_nepali = None
    today_weekday = None
    lmp_weekday = None

    if request.method == 'POST':
        form = GestationalAgeForm(request.POST)

        if form.is_valid():
            # Get the Nepali LMP date from the form
            lmp_nepali_str = form.cleaned_data['lmp_date']

            try:
                # Parse the Nepali date (e.g., '2081-05-19')
                lmp_nepali = nepali_datetime.date(
                    *map(int, lmp_nepali_str.split('-')))

                # Convert Nepali date to AD (Gregorian date)
                lmp_ad = lmp_nepali.to_datetime_date()

                # Convert LMP back to BS (Bikram Sambat)
                lmp_bs = lmp_nepali.strftime('%Y-%m-%d')

                # Calculate the Due Date (280 days from LMP)
                due_date_ad = lmp_ad + timedelta(days=280)

                # Convert the Due Date to BS
                due_date_bs = nepali_datetime.date.from_datetime_date(
                    due_date_ad).strftime('%Y-%m-%d')

                # Get today's date in Nepali Date
                today_nepali = nepali_datetime.date.today()

                # Calculate gestational age in days and convert it to weeks and days
                today_ad = today_nepali.to_datetime_date()
                total_gestational_age_days = (today_ad - lmp_ad).days
                gestational_age_weeks = total_gestational_age_days // 7
                gestational_age_days = total_gestational_age_days % 7

                # Get weekday names for LMP and today's date
                nepali_weekdays = ['आइतबार', 'सोमबार', 'मङ्गलबार',
                                   'बुधबार', 'बिहीबार', 'शुक्रबार', 'शनिबार']

                # Weekday for today's Nepali date
                today_weekday = nepali_weekdays[today_nepali.weekday()]

                # Weekday for the LMP date
                lmp_weekday = nepali_weekdays[lmp_nepali.weekday()]

            except ValueError:
                form.add_error(
                    'lmp_date', 'Invalid date format. Please use the correct Nepali date format (e.g., 2081-05-19).')

    else:
        form = GestationalAgeForm()

    # Now include the checkup details and Nepali date calculations in the context
    context = {
        'checkup': checkup,
        'form': form,
        'gestational_age': f"{gestational_age_weeks} weeks, {gestational_age_days} days" if gestational_age_weeks is not None else None,
        'due_date': due_date_ad,
        'due_date_bs': due_date_bs,
        'lmp_ad': lmp_ad,
        'lmp_bs': lmp_bs,
        'today_nepali': today_nepali,
        'today_weekday': today_weekday,
        'lmp_weekday': lmp_weekday,
    }

    return render(request, 'calculator/checkup_detail.html', context)


@login_required
def edit_visit(request, visit_id):
    # Fetch the visit object
    visit = get_object_or_404(CheckupVisit, id=visit_id)

    if request.method == 'POST':
        # Update the visit fields with new values
        visit.visit_week = request.POST.get('visit_week')
        visit.visit_date_bs = request.POST.get('visit_date_bs')
        visit.iron_intake = request.POST.get('iron_intake')
        visit.calcium_intake = request.POST.get('calcium_intake')
        visit.dt_injection = request.POST.get('dt_injection') == 'yes'
        visit.intestinal_parasites_medicine = request.POST.get(
            'intestinal_parasites_medicine') == 'yes'
        visit.folic_acid = request.POST.get('folic_acid') == 'yes'

        # Save the updated visit record
        visit.save()

        # Redirect to the checkup detail page (or any other page)
        return redirect('checkup_detail', patient_id=visit.patient.id)

    return render(request, 'calculator/edit_visit.html', {'visit': visit})


@login_required
def record_visit(request, checkup_id):
    checkup = get_object_or_404(PregnancyCheckup, id=checkup_id)
    previous_visits = CheckupVisit.objects.filter(
        patient=checkup).order_by('-visit_week')
    last_visit = previous_visits.first()
    next_visit_week = 20

    # Define checkup intervals
    checkup_intervals = [
        (12, 12), (16, 16),
        (20, 24),  # Single checkup between weeks 20-24
        (28, 28), (32, 32), (34, 34), (36, 36),
        (38, 40)   # Frequent checkups between weeks 38-40
    ]

    # # Calculate next visit week based on the last visit
    # if last_visit:
    #     next_visit_week = last_visit.visit_week + 4
    #     if next_visit_week == 24:
    #         next_visit_week += 4  # Skip week 24
    #     elif next_visit_week == 32:
    #         next_visit_week = 34  # Next visit after 32 weeks should be 34 weeks
    #     elif next_visit_week > 32:
    #         next_visit_week += 2  # Add 2 weeks after week 32
    # else:
    #     next_visit_week = "First"

    visit_weeks = []
    for start_week, end_week in checkup_intervals:
        if start_week == 'First':  # Handle first-time visit
            visit_weeks.append('First')
        else:
            for week in range(start_week, end_week + 1):
                visit_weeks.append(week)

    if request.method == 'POST':
        visit_week = request.POST.get('visit_week')

        # Check if a visit already exists for the same visit_week and patient
        if visit_week == "First":
            visit_week = 0
        existing_visit = CheckupVisit.objects.filter(
            patient=checkup, visit_week=visit_week).first()
        if existing_visit:
            # If the visit already exists, display an error message
            messages.error(request, f"A visit for week {
                           visit_week} already exists.")
            return redirect('record_visit', checkup_id=checkup.id)

        # Handle form data
        iron_intake = int(request.POST.get('iron_intake', 0))
        calcium_intake = int(request.POST.get('calcium_intake', 0))
        dt_injection = request.POST.get('dt_injection', 'no') == 'yes'
        intestinal_parasites_medicine = request.POST.get(
            'intestinal_parasites_medicine', 'no') == 'yes'
        folic_acid = request.POST.get('folic_acid', 'no') == 'yes'
        visit_date_bs = request.POST.get('visit_date_bs', None)

        # Only validate the visit_date_bs if the form is being submitted
        if not visit_date_bs:
            messages.error(request, "Visit Date (BS) is required.")
            return redirect('record_visit', checkup_id=checkup.id)

        # Create the visit record if the form is valid
        new_visit = CheckupVisit.objects.create(
            patient=checkup,
            visit_week=visit_week,
            visit_date_bs=visit_date_bs,
            iron_intake=iron_intake,
            calcium_intake=calcium_intake,
            dt_injection=dt_injection,
            intestinal_parasites_medicine=intestinal_parasites_medicine,
            folic_acid=folic_acid,
        )

        # Update the checkup totals (you should implement the update_totals method if needed)
        checkup.update_totals()

        messages.success(request, f"Visit for week {
                         visit_week} has been successfully recorded.")
        return redirect('checkup_detail', patient_id=checkup.pk)

    return render(request, 'calculator/record_visit.html', {
        'checkup': checkup,
        'previous_visits': previous_visits,
        'next_visit_week': next_visit_week,
        'visit_weeks': visit_weeks,
        'next_visit_week': next_visit_week,
        'weeks': range(1, 41)
    })

# def record_visit(request, checkup_id):
#     checkup = get_object_or_404(PregnancyCheckup, id=checkup_id)
#     previous_visits = CheckupVisit.objects.filter(
#         patient=checkup).order_by('-visit_week')
#     last_visit = previous_visits.first()
#     next_visit_week = 20

#     # Define checkup intervals
#     checkup_intervals = [
#         ('First', 'First'),  # First-time visit before 12 weeks
#         (12, 12), (16, 16), (20, 24),
#         (28, 28), (32, 32), (34, 34), (36, 36),
#         (38, 40)
#     ]

#     # Determine next visit week
#     if last_visit:
#         next_visit_week = last_visit.visit_week + 4
#         if next_visit_week == 24:
#             next_visit_week += 4  # Skip week 24
#         elif next_visit_week == 32:
#             next_visit_week = 34
#         elif next_visit_week > 32:
#             next_visit_week += 2
#     else:
#         next_visit_week = "First"

#     visit_weeks = ['First'] + [week for start, end in checkup_intervals if isinstance(
#         start, int) for week in range(start, end + 1)]

#     # Handle form submission
#     if request.method == 'POST':
#         form = GestationalAgeForm(request.POST)

#         if form.is_valid():
#             # Get the LMP and Visit dates from the form
#             lmp_nepali_str = form.cleaned_data.get('lmp_date')
#             visit_date_nepali_str = form.cleaned_data.get('visit_date')

#             try:
#                 # Convert LMP date (BS) to AD
#                 lmp_nepali = nepali_datetime.date(
#                     *map(int, lmp_nepali_str.split('-')))
#                 lmp_ad = lmp_nepali.to_datetime_date()
#                 checkup.lmp_date_bs = lmp_nepali_str
#                 checkup.lmp_date_ad = lmp_ad

#                 # Calculate the Due Date (280 days from LMP)
#                 due_date_ad = lmp_ad + timedelta(days=280)
#                 due_date_bs = nepali_datetime.date.from_datetime_date(
#                     due_date_ad).strftime('%Y-%m-%d')

#                 # Convert the Visit date (BS) to AD
#                 visit_date_nepali = nepali_datetime.date(
#                     *map(int, visit_date_nepali_str.split('-')))
#                 visit_date_ad = visit_date_nepali.to_datetime_date()
#                 visit_date_bs = visit_date_nepali.strftime('%Y-%m-%d')

#                 # Calculate gestational age
#                 total_gestational_age_days = (visit_date_ad - lmp_ad).days
#                 gestational_age_weeks = total_gestational_age_days // 7
#                 gestational_age_days = total_gestational_age_days % 7

#                 # Save the new visit record
#                 visit_week = request.POST.get('visit_week')
#                 if visit_week == "First":
#                     visit_week = 0

#                 # Check for duplicate visits
#                 existing_visit = CheckupVisit.objects.filter(
#                     patient=checkup, visit_week=visit_week).first()
#                 if existing_visit:
#                     messages.error(request, f"A visit for week {
#                                    visit_week} already exists.")
#                     return redirect('record_visit', checkup_id=checkup.id)

#                 iron_intake = int(request.POST.get('iron_intake', 0))
#                 calcium_intake = int(request.POST.get('calcium_intake', 0))
#                 dt_injection = request.POST.get('dt_injection', 'no') == 'yes'
#                 intestinal_parasites_medicine = request.POST.get(
#                     'intestinal_parasites_medicine', 'no') == 'yes'
#                 folic_acid = request.POST.get('folic_acid', 'no') == 'yes'

#                 new_visit = CheckupVisit.objects.create(
#                     patient=checkup,
#                     visit_week=visit_week,
#                     visit_date_bs=visit_date_bs,
#                     iron_intake=iron_intake,
#                     calcium_intake=calcium_intake,
#                     dt_injection=dt_injection,
#                     intestinal_parasites_medicine=intestinal_parasites_medicine,
#                     folic_acid=folic_acid
#                 )

#                 checkup.update_totals()  # If you have this method to update totals
#                 checkup.save()

#                 messages.success(request, f"Visit for week {
#                                  visit_week} recorded successfully.")
#                 return redirect('checkup_detail', patient_id=checkup.pk)

#             except ValueError:
#                 messages.error(
#                     request, "Invalid date format. Use the format: 2081-05-19")

#     else:
#         form = GestationalAgeForm()

#     return render(request, 'calculator/record_visit.html', {
#         'checkup': checkup,
#         'previous_visits': previous_visits,
#         'next_visit_week': next_visit_week,
#         'visit_weeks': visit_weeks,
#         'form': form,
#         'next_visit_week': next_visit_week,
#         'weeks': range(1, 41)
#     })


# Viewset for UserProfile

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

# Viewset for PregnancyCheckup


class PregnancyCheckupViewSet(viewsets.ModelViewSet):
    queryset = PregnancyCheckup.objects.all()
    serializer_class = PregnancyCheckupSerializer

# Viewset for CheckupVisit


class CheckupVisitViewSet(viewsets.ModelViewSet):
    queryset = CheckupVisit.objects.all()
    serializer_class = CheckupVisitSerializer
