from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Avg

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    department = models.CharField(max_length=100, blank=True)
    year = models.PositiveSmallIntegerField(default=1)
    bio = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to="profiles/", blank=True)
    availability = models.CharField(max_length=120, default="Flexible")

    @property
    def average_rating(self):
        value = self.user.reviews_received.aggregate(avg=Avg("rating"))["avg"]
        return round(value, 1) if value else None

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}'s profile"

class Skill(models.Model):
    class Category(models.TextChoices):
        PROGRAMMING = "Programming", "Programming"
        DESIGN = "Design", "Design"
        MUSIC = "Music", "Music"
        LANGUAGES = "Languages", "Languages"
        SPORTS = "Sports", "Sports"
        ACADEMICS = "Academics", "Academics"
        OTHER = "Other", "Other"
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.OTHER)

    def __str__(self): return self.name

class UserSkill(models.Model):
    class Type(models.TextChoices):
        OFFERING = "Offering", "Offering"
        LEARNING = "Learning", "Learning"
    class Level(models.TextChoices):
        BEGINNER = "Beginner", "Beginner"
        INTERMEDIATE = "Intermediate", "Intermediate"
        ADVANCED = "Advanced", "Advanced"
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="skills")
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="memberships")
    skill_type = models.CharField(max_length=10, choices=Type.choices)
    level = models.CharField(max_length=15, choices=Level.choices, default=Level.BEGINNER)
    class Meta: unique_together = ("user", "skill", "skill_type")
    def __str__(self): return f"{self.user}: {self.skill} ({self.skill_type})"

class ExchangeRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "Pending", "Pending"
        ACCEPTED = "Accepted", "Accepted"
        REJECTED = "Rejected", "Rejected"
        COMPLETED = "Completed", "Completed"
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_requests")
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_requests")
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="exchange_requests")
    message = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.sender} → {self.receiver}: {self.skill}"

class Session(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "Scheduled", "Scheduled"
        COMPLETED = "Completed", "Completed"
        CANCELLED = "Cancelled", "Cancelled"
    request = models.ForeignKey(ExchangeRequest, on_delete=models.CASCADE, related_name="sessions")
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.SCHEDULED)
    notes = models.CharField(max_length=240, blank=True)
    class Meta: ordering = ["date", "time"]
    def __str__(self): return f"{self.request.skill} · {self.date}"

class Review(models.Model):
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews_written")
    reviewed_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews_received")
    exchange = models.ForeignKey(ExchangeRequest, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: unique_together = ("reviewer", "exchange")
    def __str__(self): return f"{self.rating}/5 for {self.reviewed_user}"

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    message = models.CharField(max_length=240)
    read_status = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ["-timestamp"]
    def __str__(self): return self.message
