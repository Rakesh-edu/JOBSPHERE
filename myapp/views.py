from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.db import models
from .models import Applicant, Recruiter, Job, Message, Application
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.http import require_http_methods
from django.db import IntegrityError


# Optional: Custom decorators to cleanly manage session checks
from functools import wraps

def applicant_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('applicant_id'):
            messages.error(request, "You must be logged in as an applicant.")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

def recruiter_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('recruiter_id'):
            messages.error(request, "You must be logged in as a recruiter.")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def base(request):
    jobs = Job.objects.order_by('-posted_at')[:6]
    return render(request, 'myapp/base.html', {'jobs': jobs})


def register(request):
    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        email = request.POST.get('email')

        if user_type == 'applicant':
            if Applicant.objects.filter(email=email).exists():
                messages.error(request, "User with this email already exists.")
                return redirect('register')

            full_name = request.POST.get('full_name')
            phone = request.POST.get('phone')
            password = request.POST.get('password')
            resume = request.FILES.get('resume')
            skills = request.POST.get('skills')
            desired_job = request.POST.get('desired_job')
            location = request.POST.get('location')

            applicant = Applicant.objects.create(
                full_name=full_name,
                email=email,
                phone=phone,
                password=password,
                resume=resume,
                skills=skills,
                desired_job=desired_job,
                location=location
            )
            request.session['applicant_id'] = applicant.id
            messages.success(request, "Hello User, You are successfully registered!")
            return redirect('home')

        elif user_type == 'recruiter':
            if Recruiter.objects.filter(email=email).exists():
                messages.error(request, "User with this email already exists.")
                return redirect('register')

            full_name = request.POST.get('full_name')
            phone = request.POST.get('phone')
            password = request.POST.get('password')
            company_name = request.POST.get('company_name')
            company_website = request.POST.get('company_website')
            company_address = request.POST.get('company_address')

            recruiter = Recruiter.objects.create(
                full_name=full_name,
                email=email,
                phone=phone,
                password=password,
                company_name=company_name,
                company_website=company_website,
                company_address=company_address
            )
            request.session['recruiter_id'] = recruiter.id
            messages.success(request, "Hello recruiter, You are successfully registered!")
            return redirect('rhome')

    return render(request, 'myapp/register.html')


def login(request):
    return render(request, 'myapp/login.html')


def profile(request):
    applicant_id = request.session.get('applicant_id')
    if applicant_id:
        applicant = Applicant.objects.get(id=applicant_id)
        return render(request, 'myapp/profile.html', {'applicant': applicant})
    else:
        messages.error(request, "You are not logged in.")
        return redirect('register')


@recruiter_login_required
def rdashboard(request):
    recruiter = Recruiter.objects.get(id=request.session['recruiter_id'])
    jobs_posted = Job.objects.filter(recruiter=recruiter)
    total_jobs = jobs_posted.count()

    # Count distinct applicants who applied to the recruiter's jobs
    total_applicants = Application.objects.filter(
        job__in=jobs_posted
    ).values('applicant').distinct().count()

    return render(request, 'myapp/rdashboard.html', {
        'recruiter': recruiter,
        'total_jobs': total_jobs,
        'total_applicants': total_applicants,
        'jobs_posted': jobs_posted,
    })



def jobs(request):
    all_jobs = Job.objects.select_related("recruiter").order_by('-posted_at')

    # Get filter values
    role = request.GET.get("role")
    date_filter = request.GET.get("date_filter")

    # Filter by job role/title
    if role:
        all_jobs = all_jobs.filter(title__icontains=role)

    # Filter by posted date
    if date_filter:
        now = timezone.now()
        if date_filter == "today":
            all_jobs = all_jobs.filter(posted_at__date=now.date())
        elif date_filter == "yesterday":
            all_jobs = all_jobs.filter(posted_at__date=(now - timedelta(days=1)).date())
        elif date_filter == "last_week":
            all_jobs = all_jobs.filter(posted_at__gte=now - timedelta(days=7))
        elif date_filter == "last_month":
            all_jobs = all_jobs.filter(posted_at__gte=now - timedelta(days=30))

    return render(request, "myapp/jobs.html", {
        "jobs": all_jobs,
    })

def logout_view(request):
    request.session.flush()
    messages.success(request, "You have been logged out.")
    return redirect("login")


def company(request):
    return render(request, 'myapp/company.html')


@applicant_login_required
def udashboard(request):
    applicant = get_object_or_404(Applicant, id=request.session['applicant_id'])
    applications = Application.objects.filter(applicant=applicant).select_related('job')
    return render(request, 'myapp/udashboard.html', {
        'applicant': applicant,
        'applications': applications
    })



@recruiter_login_required
def rhome(request):
    return render(request, 'myapp/rhome.html')


@recruiter_login_required
def postjob(request):
    if request.method == 'POST':
        recruiter = Recruiter.objects.get(id=request.session['recruiter_id'])

        job_title = request.POST.get('job_title')
        job_description = request.POST.get('job_description')
        job_location = request.POST.get('job_location')
        job_type = request.POST.get('job_type')
        salary = request.POST.get('salary')

        Job.objects.create(
            recruiter=recruiter,
            title=job_title,
            description=job_description,
            location=job_location,
            job_type=job_type,
            salary_range=salary
        )
        send_mail(
            subject="Your job has been posted",
            message=f"Dear {recruiter.full_name},\n\nYour job '{job_title}' has been successfully posted.\n\nThanks!",
            from_email="rakeshbanavath5@gmail.com",
            recipient_list=[recruiter.email],
            fail_silently=True,
        )
        messages.success(request, "Job posted successfully!")
        return redirect('postjob')

    return render(request, 'myapp/postjob.html')


@recruiter_login_required
def applicants(request):
    recruiter = Recruiter.objects.get(id=request.session['recruiter_id'])
    jobs = Job.objects.filter(recruiter=recruiter)

    applicants = Applicant.objects.filter(
        application__job__in=jobs
    ).prefetch_related(
        models.Prefetch(
            'application_set',
            queryset=Application.objects.select_related('job')
        )
    ).distinct()

    return render(request, "myapp/applicants.html", {
        "applicants": applicants
    })




@recruiter_login_required
def rprofile(request):
    recruiter = Recruiter.objects.get(id=request.session['recruiter_id'])
    return render(request, 'myapp/rprofile.html', {'recruiter': recruiter})


@applicant_login_required
def apply_to_job(request, job_id):
    applicant = get_object_or_404(Applicant, id=request.session['applicant_id'])
    job = get_object_or_404(Job, id=job_id)

    # Try to create an Application record
    try:
        Application.objects.create(
            applicant=applicant,
            job=job,
            status="pending"
        )
        messages.success(request, f"You have successfully applied to '{job.title}'!")

        # Email to applicant
        send_mail(
            subject="Application Submitted",
            message=f"Dear {applicant.full_name},\n\nYou applied for '{job.title}' successfully.",
            from_email="rakeshbanavath5@gmail.com",
            recipient_list=[applicant.email],
            fail_silently=False,
        )
        # Email to recruiter
        send_mail(
            subject="New Application Received",
            message=f"{applicant.full_name} applied for '{job.title}'.",
            from_email="rakeshbanavath5@gmail.com",
            recipient_list=[job.recruiter.email],
            fail_silently=False,
        )
    except IntegrityError:
        messages.warning(request, "You have already applied to this job.")

    return redirect('udashboard')

@recruiter_login_required
def job_details(request, job_id):
    recruiter = get_object_or_404(Recruiter, id=request.session['recruiter_id'])
    job = get_object_or_404(Job, id=job_id, recruiter_id=recruiter.id)

    # get all applications for this job
    applications = Application.objects.filter(job=job).select_related('applicant')

    return render(request, "myapp/job_details.html", {
        "job": job,
        "applications": applications,
        "recruiter": recruiter,
    })


@applicant_login_required
def applicant_chat(request, recruiter_id):
    applicant = get_object_or_404(Applicant, id=request.session['applicant_id'])
    recruiter = get_object_or_404(Recruiter, id=recruiter_id)

    chat_messages = Message.objects.filter(
        models.Q(sender_applicant=applicant, receiver_recruiter=recruiter) |
        models.Q(sender_recruiter=recruiter, receiver_applicant=applicant)
    ).order_by('timestamp')

    if request.method == 'POST':
        content = request.POST.get('content')
        Message.objects.create(
            sender_applicant=applicant,
            receiver_recruiter=recruiter,
            content=content
        )
        return redirect('applicant_chat', recruiter_id=recruiter.id)

    return render(request, 'myapp/applicant_chat.html', {
        'chat_messages': chat_messages,
        'applicant': applicant,
        'recruiter': recruiter,
    })


@recruiter_login_required
def recruiter_chat(request, applicant_id):
    recruiter = get_object_or_404(Recruiter, id=request.session['recruiter_id'])
    applicant = get_object_or_404(Applicant, id=applicant_id)

    chat_messages = Message.objects.filter(
        models.Q(sender_applicant=applicant, receiver_recruiter=recruiter) |
        models.Q(sender_recruiter=recruiter, receiver_applicant=applicant)
    ).order_by('timestamp')

    if request.method == 'POST':
        content = request.POST.get('content')
        Message.objects.create(
            sender_recruiter=recruiter,
            receiver_applicant=applicant,
            content=content
        )
        return redirect('recruiter_chat', applicant_id=applicant.id)

    return render(request, 'myapp/recruiter_chat.html', {
        'chat_messages': chat_messages,
        'applicant': applicant,
        'recruiter': recruiter,
    })


def aboutus(request):
    return render(request, 'myapp/aboutus.html')


def helpcenter(request):
    return render(request, 'myapp/helpcenter.html')

def contactus(request):
    return render(request,'myapp/contactus.html')

def privacy_policy(request):
    return render(request, 'myapp/privacy.html')

def terms_of_service(request):
    return render(request, 'myapp/terms.html')

def careers(request):
    return render(request, 'myapp/careers.html')

def login(request):
    if request.method == 'POST':
        user_type = request.POST.get('user_type')  # 'applicant' or 'recruiter'
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if user_type == 'applicant':
            try:
                applicant = Applicant.objects.get(email=email, full_name=username)
                if applicant.password == password:
                    request.session['applicant_id'] = applicant.id
                    messages.success(request, f"Welcome back {applicant.full_name}!")
                    return redirect('home')
                else:
                    messages.error(request, "Incorrect password.")
            except Applicant.DoesNotExist:
                messages.error(request, "Applicant with these credentials does not exist.")

        elif user_type == 'recruiter':
            try:
                recruiter = Recruiter.objects.get(email=email, full_name=username)
                if recruiter.password == password:
                    request.session['recruiter_id'] = recruiter.id
                    messages.success(request, f"Welcome back {recruiter.full_name}!")
                    return redirect('rhome')
                else:
                    messages.error(request, "Incorrect password.")
            except Recruiter.DoesNotExist:
                messages.error(request, "Recruiter with these credentials does not exist.")

        else:
            messages.error(request, "Invalid user type selected.")

    return render(request, 'myapp/login.html')

def jobsearch(request):
    query = request.GET.get("q")

    if not query or not query.strip():
        return redirect("jobs")  # this assumes you have `jobs` URL named as 'jobs'

    all_jobs = Job.objects.select_related("recruiter").order_by("-posted_at")
    all_jobs = all_jobs.filter(title__icontains=query)

    return render(request, "myapp/jobsearch.html", {
        "jobs": all_jobs,
        "query": query.strip(),
    })

def recruiter_about(request):
    return render(request,'myapp/recruiter_about.html')

def recruiter_carrers(request):
    return render(request,'myapp/recruiter_carrers.html')

def recruiter_contact(request):
    return render(request,'myapp/recruiter_contact.html')

def recruiter_privacy(request):
    return render(request,'myapp/recruiter_privacy.html')

def recruiter_terms(request):
    return render(request,'myapp/recruiter_terms.html')

def recruiter_FAQ(request):
    return render(request,'myapp/recruiter_FAQ.html')

def recruiter_helpcenter(request):
    return render(request,'myapp/recruiter_helpcenter.html')

def applicant_FAQ(request):
    return render(request,'myapp/applicant_FAQ.html')

@applicant_login_required
@require_http_methods(["GET", "POST"])
def edit_profile(request):
    applicant = get_object_or_404(Applicant, id=request.session['applicant_id'])

    if request.method == 'POST':
        applicant.full_name = request.POST.get('full_name')
        applicant.email = request.POST.get('email')
        applicant.phone = request.POST.get('phone')
        applicant.location = request.POST.get('location')
        applicant.desired_job = request.POST.get('desired_job')
        applicant.skills = request.POST.get('skills')

        # Update resume only if a new file is uploaded
        if 'resume' in request.FILES:
            applicant.resume = request.FILES['resume']

        applicant.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('profile')

    return render(request, 'myapp/edit_profile.html', {'applicant': applicant})

@recruiter_login_required
@require_http_methods(["GET", "POST"])
def rprofile_edit(request):
    recruiter = get_object_or_404(Recruiter, id=request.session['recruiter_id'])

    if request.method == 'POST':
        recruiter.full_name = request.POST.get('full_name')
        recruiter.email = request.POST.get('email')
        recruiter.phone = request.POST.get('phone')
        recruiter.company_name = request.POST.get('company_name')
        recruiter.company_website = request.POST.get('company_website')
        recruiter.company_address = request.POST.get('company_address')

        recruiter.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('rprofile')

    return render(request, 'myapp/rprofile_edit.html', {'recruiter': recruiter})

@recruiter_login_required
def update_application_status(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    if request.method == "POST":
        new_status = request.POST.get("status")
        application.status = new_status
        application.save()
        messages.success(request, "Application status updated.")
    return redirect('job_details', job_id=application.job.id)

def getting_started(request):
    return render(request,'myapp/getting_started.html')

def account_management(request):
    return render(request,'myapp/account_management.html')

def job_applications(request):
    return render(request, "myapp/job_applications.html")

def technical_issues(request):
    return render(request, "myapp/technical_issues.html")

