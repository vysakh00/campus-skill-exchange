from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404, redirect, render
from .forms import RegisterForm, ProfileForm, UserSkillForm, RequestForm, SessionForm, ReviewForm
from .models import Skill, UserSkill, ExchangeRequest, Session, Review, Notification

def home(request):
    featured = UserSkill.objects.filter(skill_type="Offering").select_related("user", "skill", "user__profile")[:6]
    return render(request, "exchange/home.html", {"featured": featured, "skills_count": Skill.objects.count(), "students_count": User.objects.count()})

def register(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save(); login(request, user)
        messages.success(request, "Welcome! Complete your profile and add a skill.")
        return redirect("dashboard")
    return render(request, "exchange/form_page.html", {"form": form, "title": "Join the exchange"})

@login_required
def dashboard(request):
    user = request.user
    sessions = Session.objects.filter(Q(request__sender=user) | Q(request__receiver=user), status="Scheduled").select_related("request__skill")
    return render(request, "exchange/dashboard.html", {"offers": user.skills.filter(skill_type="Offering").select_related("skill"), "learning": user.skills.filter(skill_type="Learning").select_related("skill"), "incoming": user.received_requests.select_related("sender", "skill")[:5], "sent": user.sent_requests.select_related("receiver", "skill")[:5], "sessions": sessions, "completed": ExchangeRequest.objects.filter(Q(sender=user) | Q(receiver=user), status="Completed").distinct().count(), "unread": user.notifications.filter(read_status=False).count()})

def marketplace(request):
    skills = UserSkill.objects.filter(skill_type="Offering").select_related("skill", "user", "user__profile")
    if request.user.is_authenticated: skills = skills.exclude(user=request.user)
    q = request.GET.get("q", "").strip(); category = request.GET.get("category", "")
    if q: skills = skills.filter(Q(skill__name__icontains=q) | Q(user__first_name__icontains=q) | Q(user__last_name__icontains=q))
    if category: skills = skills.filter(skill__category=category)
    return render(request, "exchange/marketplace.html", {"skills": skills, "categories": Skill.Category.choices, "q": q, "category": category})

@login_required
def add_skill(request):
    form = UserSkillForm(request.POST or None)
    if form.is_valid():
        name = form.cleaned_data["skill_name"].strip()
        skill, _ = Skill.objects.get_or_create(name__iexact=name, defaults={"name": name, "category": request.POST.get("category", "Other")})
        item = form.save(commit=False); item.skill = skill; item.user = request.user
        item.save(); messages.success(request, "Your skill has been added."); return redirect("profile")
    return render(request, "exchange/form_page.html", {"form": form, "title": "Add a skill", "show_category": True})

@login_required
def profile(request):
    form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user.profile, initial={"first_name": request.user.first_name, "last_name": request.user.last_name, "email": request.user.email})
    if form.is_valid():
        request.user.first_name = form.cleaned_data["first_name"]; request.user.last_name = form.cleaned_data["last_name"]; request.user.email = form.cleaned_data["email"]; request.user.save(); form.save()
        messages.success(request, "Profile updated."); return redirect("profile")
    return render(request, "exchange/profile.html", {"profile_user": request.user, "form": form, "skills": request.user.skills.select_related("skill")})

def student_profile(request, user_id):
    person = get_object_or_404(User.objects.select_related("profile"), pk=user_id)
    return render(request, "exchange/student_profile.html", {"profile_user": person, "skills": person.skills.select_related("skill")})

@login_required
def send_request(request, skill_id):
    offered = get_object_or_404(UserSkill.objects.select_related("skill", "user"), pk=skill_id, skill_type="Offering")
    if offered.user == request.user: messages.error(request, "You cannot request your own skill."); return redirect("marketplace")
    form = RequestForm(request.POST or None)
    if form.is_valid():
        exchange = form.save(commit=False); exchange.sender = request.user; exchange.receiver = offered.user; exchange.skill = offered.skill; exchange.save()
        Notification.objects.create(user=offered.user, message=f"{request.user.get_full_name() or request.user.username} wants to learn {offered.skill}.")
        messages.success(request, "Request sent!"); return redirect("dashboard")
    return render(request, "exchange/form_page.html", {"form": form, "title": f"Learn {offered.skill}", "subtitle": f"Ask {offered.user.get_full_name() or offered.user.username} to exchange skills."})

@login_required
def requests_page(request):
    return render(request, "exchange/requests.html", {"incoming": request.user.received_requests.select_related("sender", "skill"), "sent": request.user.sent_requests.select_related("receiver", "skill")})

@login_required
def request_action(request, request_id, action):
    obj = get_object_or_404(ExchangeRequest, pk=request_id)
    if obj.receiver != request.user or action not in ("accept", "reject") or obj.status != "Pending": messages.error(request, "This action is unavailable."); return redirect("requests")
    obj.status = "Accepted" if action == "accept" else "Rejected"; obj.save()
    Notification.objects.create(user=obj.sender, message=f"Your request to learn {obj.skill} was {obj.status.lower()}.")
    return redirect("requests")

@login_required
def schedule_session(request, request_id):
    obj = get_object_or_404(ExchangeRequest, pk=request_id, status="Accepted")
    if request.user not in (obj.sender, obj.receiver): return redirect("requests")
    form = SessionForm(request.POST or None)
    if form.is_valid():
        session = form.save(commit=False); session.request = obj; session.save()
        other = obj.sender if request.user == obj.receiver else obj.receiver
        Notification.objects.create(user=other, message=f"A session for {obj.skill} is scheduled on {session.date}.")
        return redirect("sessions")
    return render(request, "exchange/form_page.html", {"form": form, "title": "Schedule a session"})

@login_required
def sessions_page(request):
    sessions = Session.objects.filter(Q(request__sender=request.user) | Q(request__receiver=request.user)).select_related("request__sender", "request__receiver", "request__skill").distinct()
    return render(request, "exchange/sessions.html", {"sessions": sessions})

@login_required
def complete_session(request, session_id):
    session = get_object_or_404(Session, pk=session_id)
    if request.user not in (session.request.sender, session.request.receiver): return redirect("sessions")
    session.status = "Completed"; session.save(); session.request.status = "Completed"; session.request.save()
    return redirect("review_exchange", request_id=session.request_id)

@login_required
def review_exchange(request, request_id):
    exchange = get_object_or_404(ExchangeRequest, pk=request_id, status="Completed")
    if request.user not in (exchange.sender, exchange.receiver): return redirect("dashboard")
    reviewed = exchange.receiver if request.user == exchange.sender else exchange.sender
    form = ReviewForm(request.POST or None)
    if form.is_valid():
        review = form.save(commit=False); review.reviewer = request.user; review.reviewed_user = reviewed; review.exchange = exchange; review.save()
        messages.success(request, "Thanks for sharing your feedback."); return redirect("student_profile", user_id=reviewed.id)
    return render(request, "exchange/form_page.html", {"form": form, "title": f"Review {reviewed.get_full_name() or reviewed.username}", "subtitle": f"Share how your {exchange.skill} exchange went."})

@login_required
def notifications(request):
    request.user.notifications.filter(read_status=False).update(read_status=True)
    return render(request, "exchange/notifications.html", {"notifications": request.user.notifications.all()})

@user_passes_test(lambda user: user.is_staff)
def admin_dashboard(request):
    return render(request, "exchange/admin_dashboard.html", {"user_count": User.objects.count(), "skill_count": Skill.objects.count(), "exchange_count": ExchangeRequest.objects.count(), "completed_count": ExchangeRequest.objects.filter(status="Completed").count(), "popular": Skill.objects.annotate(exchange_count=Count("exchange_requests")).order_by("-exchange_count")[:8]})
