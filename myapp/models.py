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
    # applicants = models.ManyToManyField(Applicant, blank=True, related_name="applied_jobs") commented bcuz of applicaiton model introduced

    def __str__(self):
        return self.title
    
class Message(models.Model):
    sender_applicant = models.ForeignKey(
        "Applicant",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="sent_messages"
    )
    sender_recruiter = models.ForeignKey(
        "Recruiter",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="sent_messages"
    )
    receiver_applicant = models.ForeignKey(
        "Applicant",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="received_messages"
    )
    receiver_recruiter = models.ForeignKey(
        "Recruiter",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="received_messages"
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.content[:30]}..."
    
class Application(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("reviewed", "Reviewed"),
        ("interviewed", "Interviewed"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    ]

    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('applicant', 'job')

    def __str__(self):
        return f"{self.applicant.full_name} - {self.job.title} ({self.status})"
