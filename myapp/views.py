from django.shortcuts import render, redirect,get_object_or_404
from .models import Applicant,Recruiter,Job
from django.contrib import messages
from django.core.mail import send_mail
from .models import Message
from django.db import models


def base(request):
    jobs = Job.objects.order_by('-posted_at')[:6]
    return render(request,'myapp/base.html',{'jobs':jobs})

def register(request):
    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        if user_type == 'applicant':
            full_name = request.POST.get('full_name')
            email = request.POST.get('email')
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
            messages.success(request,"Hello User,You are successfully registered!")
            return redirect('home')
        elif user_type == 'recruiter':
            full_name = request.POST.get('full_name')
            email = request.POST.get('email')
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
            messages.success(request,"Hello recruiter,You are successfully registered!")
            return redirect('rhome')
    return render(request,'myapp/register.html')

def login(request):
    return render(request,'myapp/login.html')

def profile(request):
    applicant_id = request.session.get('applicant_id')
    if applicant_id:
        applicant = Applicant.objects.get(id=applicant_id)
        return render(request, 'myapp/profile.html', {'applicant': applicant})
    else:
        messages.error(request, "You are not logged in.")
        return redirect('register')


def rdashboard(request):
    recruiter_id = request.session.get('recruiter_id')
    if not recruiter_id:
        messages.error(request, "You are not logged in as a recruiter.")
        return redirect('login')

    recruiter = Recruiter.objects.get(id=recruiter_id)
    jobs_posted = Job.objects.filter(recruiter=recruiter)
    total_jobs = jobs_posted.count()

    total_applicants = Applicant.objects.filter(applied_jobs__in=jobs_posted).distinct().count()

    return render(request, 'myapp/rdashboard.html', {
        'recruiter': recruiter,
        'total_jobs': total_jobs,
        'total_applicants': total_applicants,
        'jobs_posted': jobs_posted,
    })

def jobs(request):
    all_jobs = Job.objects.select_related("recruiter").order_by('-posted_at')
    return render(request, 'myapp/jobs.html', {
        'jobs': all_jobs
    })


def company(request):
    return render(request,'myapp/company.html')

def udashboard(request):
    applicant_id = request.session.get('applicant_id')
    if not applicant_id:
        messages.error(request, "You are not logged in as an applicant.")
        return redirect('register')

    applicant = Applicant.objects.get(id=applicant_id)
    applied_jobs = applicant.applied_jobs.all()

    return render(request, 'myapp/udashboard.html', {
        'applicant': applicant,
        'applied_jobs': applied_jobs
    })


def rhome(request):
    return render(request,'myapp/rhome.html')

def postjob(request):
    if request.method == 'POST':
        recruiter_id = request.session.get('recruiter_id')
        if not recruiter_id:
            messages.error(request, "You must be logged in as a recruiter to post a job.")
            return redirect('login')
        recruiter = Recruiter.objects.get(id=recruiter_id)

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
            message=f"Dear {recruiter.full_name},\n\nYour job '{job_title}' has been successfully posted on the platform.\n\nThank you!",
            from_email="rakeshbanavath5@gmail.com",
            recipient_list=[recruiter.email],
            fail_silently=True,
        )
        messages.success(request, "Job posted successfully!")
        return redirect('postjob')

    return render(request, 'myapp/postjob.html')


def applicants(request):
    recruiter_id = request.session.get("recruiter_id")
    if not recruiter_id:
        messages.error(request, "You must be logged in as a recruiter.")
        return redirect("login")

    recruiter = Recruiter.objects.get(id=recruiter_id)

    # Get all jobs posted by this recruiter
    jobs = Job.objects.filter(recruiter=recruiter)

    # Get all applicants who applied to any of these jobs
    applicants = Applicant.objects.filter(applied_jobs__in=jobs).distinct()

    return render(request, "myapp/applicants.html", {
        "applicants": applicants
    })

def rprofile(request):
    recruiter_id = request.session.get('recruiter_id')
    if recruiter_id:
        recruiter = Recruiter.objects.get(id=recruiter_id)
        return render(request, 'myapp/rprofile.html', {'recruiter': recruiter})
    else:
        messages.error(request, "You are not logged in.")
        return redirect('register')


def apply_to_job(request, job_id):
    applicant_id = request.session.get('applicant_id')
    if not applicant_id:
        messages.error(request, "Please log in as an applicant to apply for jobs.")
        return redirect('login')

    applicant = get_object_or_404(Applicant, id=applicant_id)
    job = get_object_or_404(Job, id=job_id)

    job.applicants.add(applicant)

    messages.success(request, f"You have successfully applied to '{job.title}'!")
    # Email to applicant
    send_mail(
        subject="Application Submitted Successfully",
        message=(
            f"Dear {applicant.full_name},\n\n"
            f"Your application for '{job.title}' has been submitted successfully.\n\n"
            "Thank you for applying!"
        ),
        from_email="rakeshbanavath5@gmail.com",
        recipient_list=[applicant.email],
        fail_silently=False,
    )

    # Email to recruiter
    send_mail(
        subject="New Application Received",
        message=(
            f"Dear {job.recruiter.full_name},\n\n"
            f"{applicant.full_name} has applied for '{job.title}'.\n\n"
            "Please review their application in your dashboard."
        ),
        from_email="rakeshbanavath5@gmail.com",
        recipient_list=[job.recruiter.email],
        fail_silently=False,
    )
    return redirect('udashboard')

def job_details(request, job_id):
    recruiter_id = request.session.get("recruiter_id")
    if not recruiter_id:
        messages.error(request, "You must be logged in as a recruiter.")
        return redirect("login")
    recruiter = get_object_or_404(Recruiter, id=recruiter_id)
    job = get_object_or_404(Job, id=job_id, recruiter_id=recruiter_id)
    applicants = job.applicants.all()

    return render(request, "myapp/job_details.html", {
        "job": job,
        "applicants": applicants,
        "recruiter": recruiter,
    })

def applicant_chat(request, recruiter_id):
    applicant_id = request.session.get('applicant_id')
    if not applicant_id:
        messages.error(request, "You must be logged in as an applicant.")
        return redirect('login')

    applicant = get_object_or_404(Applicant, id=applicant_id)
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


def recruiter_chat(request, applicant_id):
    recruiter_id = request.session.get('recruiter_id')
    if not recruiter_id:
        messages.error(request, "You must be logged in as a recruiter.")
        return redirect('login')

    recruiter = get_object_or_404(Recruiter, id=recruiter_id)
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
