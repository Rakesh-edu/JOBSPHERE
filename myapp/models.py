from django.db import models

class Applicant(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=20)
    phone = models.CharField(max_length=20)
    password = models.CharField(max_length=128)
    resume = models.FileField(upload_to='resumes/')
    skills = models.TextField(help_text="Comma-separated skills")
    desired_job = models.CharField(max_length=100)
    location = models.CharField(max_length=100)

    def __str__(self):
        return self.full_name


class Recruiter(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=20)
    phone = models.CharField(max_length=20)
    password = models.CharField(max_length=128)
    company_name = models.CharField(max_length=100)
    company_website = models.URLField()
    company_address = models.TextField()

    def __str__(self):
        return f"{self.full_name} ({self.company_name})"

class Job(models.Model):
    recruiter = models.ForeignKey(Recruiter, on_delete=models.CASCADE, related_name="jobs")
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=100)
    job_type = models.CharField(max_length=50)
    salary_range = models.CharField(max_length=50)
    posted_at = models.DateTimeField(auto_now_add=True)
    applicants = models.ManyToManyField(Applicant, blank=True, related_name="applied_jobs")

    def __str__(self):
        return self.title