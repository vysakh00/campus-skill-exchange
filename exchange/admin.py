from django.contrib import admin
from .models import UserProfile, Skill, UserSkill, ExchangeRequest, Session, Review, Notification
admin.site.register([UserProfile, Skill, UserSkill, ExchangeRequest, Session, Review, Notification])
