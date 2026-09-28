from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from exchange.models import Skill, UserSkill

class Command(BaseCommand):
    help = "Create a handful of sample students and skills for local previews."
    def handle(self, *args, **options):
        data = [("Aarav", "aarav", "Guitar", "Music", "Advanced"), ("Maya", "maya", "Figma", "Design", "Intermediate"), ("Ishaan", "ishaan", "Python", "Programming", "Advanced"), ("Anika", "anika", "Spanish", "Languages", "Intermediate"), ("Kabir", "kabir", "Calculus", "Academics", "Advanced")]
        for first, username, skill_name, category, level in data:
            user, created = User.objects.get_or_create(username=username, defaults={"first_name": first, "email": f"{username}@campus.edu"})
            if created: user.set_password("campus-demo"); user.save()
            skill, _ = Skill.objects.get_or_create(name=skill_name, defaults={"category": category})
            UserSkill.objects.get_or_create(user=user, skill=skill, skill_type="Offering", defaults={"level": level})
        self.stdout.write(self.style.SUCCESS("Demo students added. Their password is campus-demo."))
