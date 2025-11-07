# core/views.py
import json
import re
from datetime import timedelta

from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.html import strip_tags
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from .models import (
    StudentProfile, OTPCode,
    Course, Topic, Lesson, Enrollment, LessonProgress,
    QuizQuestion, QuizChoice, QuizAttempt, AttemptAnswer,
    AssistantThread, AssistantMessage,
    StudyPlan, StudyTask,
    Exam, Subject, SubjectWeightage, Resource
)
from .utils import create_otp_for_user, update_last_login


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def ok(data=None, status=200):
    return JsonResponse({"ok": True, "data": data or {}}, status=status)


def fail(message, status=400):
    return JsonResponse({"ok": False, "error": message}, status=status)


def json_payload(request):
    try:
        return json.loads(request.body.decode("utf-8") or "{}")
    except Exception:
        return {}


# ---------------------------------------------------------------------
# Page view
# ---------------------------------------------------------------------
@ensure_csrf_cookie
def index(request):
    """Serve SPA and set a CSRF cookie."""
    return render(request, "index.html")


# ---------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------
@require_POST
def api_signup(request):
    p = json_payload(request)
    name = (p.get("student_name") or "").strip()
    email = (p.get("email") or "").strip().lower()
    phone = (p.get("phone") or "").strip()
    password = p.get("password") or ""
    student_type = (p.get("student_type") or "").strip()

    if not all([name, email, phone, password, student_type]):
        return fail("All fields are required.")

    if User.objects.filter(username=email).exists():
        return fail("Email already registered.", status=409)

    first_name = name.split(" ")[0]
    last_name = " ".join(name.split(" ")[1:])

    user = User.objects.create_user(
        username=email,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
    )
    profile = StudentProfile.objects.create(
        user=user, phone=phone, student_type=student_type
    )

    login(request, user)
    profile.last_login_at = timezone.now()
    profile.save()

    return ok(
        {
            "student_name": name,
            "email": email,
            "phone": phone,
            "student_type": student_type,
            "created_at": profile.created_at.isoformat(),
            "last_login": profile.last_login_at.isoformat(),
        }
    )


@require_POST
def api_login(request):
    """
    JSON login:
      { "email": "...", "password": "..." }
    or
      { "username": "...", "password": "..." }
    Accepts either email or username in the same field.
    """
    p = json_payload(request)
    username = (p.get("username") or p.get("email") or "").strip()
    password = p.get("password") or ""

    if not username or not password:
        return fail("username/email and password are required")

    user = authenticate(request, username=username, password=password)
    if not user:
        # Try email lookup then authenticate with stored username
        U = get_user_model()
        try:
            u = U.objects.get(email__iexact=username)
            user = authenticate(request, username=u.username, password=password)
        except U.DoesNotExist:
            user = None

    if not user:
        return fail("Invalid credentials", 401)

    login(request, user)
    update_last_login(user)
    pfp = user.profile  # assuming OneToOne related_name='profile'
    return ok(
        {
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone": pfp.phone,
            "student_type": pfp.student_type,
            "created_at": pfp.created_at.isoformat(),
            "last_login": (pfp.last_login_at.isoformat() if pfp.last_login_at else None),
        }
    )


@require_POST
def api_logout(request):
    logout(request)
    return ok()


@require_GET
def api_me(request):
    if not request.user.is_authenticated:
        return fail("Not logged in.", status=401)

    u = request.user
    p = u.profile
    display_name = (f"{u.first_name} {u.last_name}".strip() or u.username.split("@")[0])
    return ok(
        {
            "student_name": display_name,
            "email": u.email,
            "phone": p.phone,
            "student_type": p.student_type,
            "created_at": p.created_at.isoformat(),
            "last_login": (p.last_login_at.isoformat() if p.last_login_at else None),
        }
    )


# ---------------------------------------------------------------------
# Forgot password (OTP)
# ---------------------------------------------------------------------
@require_POST
def api_forgot_password(request):
    p = json_payload(request)
    email = (p.get("email") or "").strip().lower()

    try:
        user = User.objects.get(username=email)
    except User.DoesNotExist:
        return fail("Email not found.", status=404)

    otp = create_otp_for_user(user)

    phone = user.profile.phone or ""
    masked = "*" * max(len(phone) - 4, 0) + phone[-4:]

    # Return otp_demo only in dev/demo environments in your utils if needed
    return ok({"otp_demo": otp, "phone_masked": masked})


@require_POST
def api_verify_otp(request):
    """Check OTP exists and is unused. Does not consume the OTP."""
    p = json_payload(request)
    email = (p.get("email") or "").strip().lower()
    code = (p.get("code") or "").strip()

    try:
        user = User.objects.get(username=email)
    except User.DoesNotExist:
        return fail("Invalid user.", status=404)

    otp_obj = (
        OTPCode.objects.filter(user=user, code=code, is_used=False)
        .order_by("-created_at")
        .first()
    )
    if not otp_obj:
        return fail("Invalid OTP.", status=400)

    return ok()  # valid


@require_POST
def api_reset_password(request):
    p = json_payload(request)
    email = (p.get("email") or "").strip().lower()
    code = (p.get("code") or "").strip()
    new_password = p.get("new_password") or ""

    if len(new_password) < 6:
        return fail("Password must be at least 6 characters.")

    try:
        user = User.objects.get(username=email)
    except User.DoesNotExist:
        return fail("Invalid user.", status=404)

    otp_obj = (
        OTPCode.objects.filter(user=user, code=code, is_used=False)
        .order_by("-created_at")
        .first()
    )
    if not otp_obj:
        return fail("Invalid OTP.", status=400)

    user.set_password(new_password)
    user.save()
    otp_obj.is_used = True
    otp_obj.save()

    return ok({"message": "Password updated"})


# ---------------------------------------------------------------------
# Learning: Courses / Topics / Lessons / Progress
# ---------------------------------------------------------------------
@require_GET
def api_courses(request):
    qs = Course.objects.annotate(
        topics_count=Count("topics"), lessons_count=Count("topics__lessons")
    ).order_by("title")

    courses = [
        {
            "id": c.id,
            "title": c.title,
            "description": c.description,
            "topics_count": c.topics_count,
            "lessons_count": c.lessons_count,
        }
        for c in qs
    ]
    return ok({"courses": courses})


@require_GET
def api_topics(request):
    course_id = request.GET.get("course_id")
    try:
        course = Course.objects.get(id=course_id)
    except (Course.DoesNotExist, ValueError, TypeError):
        return fail("Invalid course_id", 400)

    topics = [
        {
            "id": t.id,
            "title": t.title,
            "summary": t.summary,
            "lessons_count": t.lessons.count(),
        }
        for t in course.topics.all()
    ]
    return ok({"course": {"id": course.id, "title": course.title}, "topics": topics})


@require_GET
def api_lessons(request):
    topic_id = request.GET.get("topic_id")
    try:
        topic = Topic.objects.get(id=topic_id)
    except (Topic.DoesNotExist, ValueError, TypeError):
        return fail("Invalid topic_id", 400)

    user = request.user if request.user.is_authenticated else None
    done = set()
    if user:
        done = set(
            LessonProgress.objects.filter(
                user=user, completed=True, lesson__topic=topic
            ).values_list("lesson_id", flat=True)
        )

    lessons = [
        {
            "id": l.id,
            "title": l.title,
            "content": l.content,
            "order": l.order,
            "completed": (l.id in done),
        }
        for l in topic.lessons.all().order_by("order")
    ]
    return ok({"topic": {"id": topic.id, "title": topic.title}, "lessons": lessons})


@require_POST
def api_mark_lesson(request):
    if not request.user.is_authenticated:
        return fail("Login required", 401)

    p = json_payload(request)
    lesson_id = p.get("lesson_id")
    try:
        lesson = Lesson.objects.get(id=lesson_id)
    except (Lesson.DoesNotExist, ValueError, TypeError):
        return fail("Invalid lesson_id", 400)

    lp, _ = LessonProgress.objects.get_or_create(user=request.user, lesson=lesson)
    lp.completed = True
    lp.completed_at = timezone.now()
    lp.save()

    Enrollment.objects.get_or_create(user=request.user, course=lesson.topic.course)
    return ok({"lesson_id": lesson.id, "completed": True})


@require_GET
def api_my_progress(request):
    if not request.user.is_authenticated:
        return fail("Login required", 401)

    enrolls = Enrollment.objects.filter(user=request.user).select_related("course")
    result = []
    for e in enrolls:
        total = Lesson.objects.filter(topic__course=e.course).count()
        done = LessonProgress.objects.filter(
            user=request.user, lesson__topic__course=e.course, completed=True
        ).count()
        pct = (done / total * 100) if total else 0
        result.append(
            {
                "course_id": e.course.id,
                "course_title": e.course.title,
                "lessons_done": done,
                "lessons_total": total,
                "percent": round(pct, 1),
            }
        )
    return ok({"progress": result})


@require_http_methods(["POST"])
def api_seed_demo(request):
    """Create demo Course/Topic/Lesson if not present."""
    if Course.objects.exists():
        return ok({"message": "Demo content already present"})

    c = Course.objects.create(
        title="Data Structures (Beginner)",
        description="Start with arrays, stacks, queues and complexity basics.",
    )
    t1 = Topic.objects.create(course=c, title="Arrays", summary="Basics, indexing, operations")
    t2 = Topic.objects.create(
        course=c, title="Stacks & Queues", summary="LIFO/FIFO with examples"
    )

    Lesson.objects.create(
        topic=t1,
        order=1,
        title="What is an Array?",
        content="<p>Array is a contiguous block of memory...</p>",
    )
    Lesson.objects.create(
        topic=t1,
        order=2,
        title="Array Operations",
        content="<ul><li>Insert</li><li>Delete</li><li>Traverse</li></ul>",
    )
    Lesson.objects.create(
        topic=t2, order=1, title="Stacks", content="<p>Stack supports push/pop/peek. Use cases...</p>"
    )
    Lesson.objects.create(
        topic=t2, order=2, title="Queues", content="<p>Queue supports enqueue/dequeue. Use cases...</p>"
    )

    return ok({"message": "Demo course created"})


# ---------------------------------------------------------------------
# Weekly progress chart
# ---------------------------------------------------------------------
@require_GET
def api_progress_weekly(request):
    """
    Returns the last 7 days (including today) of lesson completions for the logged-in user.
    """
    if not request.user.is_authenticated:
        return fail("Login required", 401)

    user = request.user
    today = timezone.localdate()
    start = today - timedelta(days=6)

    raw = (
        LessonProgress.objects.filter(
            user=user,
            completed=True,
            completed_at__date__gte=start,
            completed_at__date__lte=today,
        )
        .annotate(day=TruncDate("completed_at"))
        .values("day")
        .annotate(count=Count("id"))
    )

    day_counts = {row["day"]: row["count"] for row in raw}

    labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    days = []
    for i in range(7):
        d = start + timedelta(days=i)
        cnt = int(day_counts.get(d, 0))
        days.append({"date": d.isoformat(), "label": labels[d.weekday()], "count": cnt})

    total_week = sum(item["count"] for item in days)
    max_item = max(days, key=lambda x: x["count"]) if days else {"date": None, "label": None, "count": 0}

    return ok({"days": days, "total_week": total_week, "max_day": max_item})


# ---------------------------------------------------------------------
# Quizzes (seed, generate, submit, history)
# ---------------------------------------------------------------------
def pick_weak_topics_for_user(user, limit_topics=2):
    """
    Infer weak areas:
    - Topics with lowest completion % in enrolled courses
    - If no enrollment or empty, fallback to topics with most lessons
    """
    enrolls = Enrollment.objects.filter(user=user).select_related("course")
    if not enrolls.exists():
        return list(Topic.objects.annotate(n=Count("lessons")).order_by("-n")[:limit_topics])

    stats = []
    for e in enrolls:
        for t in e.course.topics.all():
            total = t.lessons.count()
            if total == 0:
                continue
            done = LessonProgress.objects.filter(user=user, lesson__topic=t, completed=True).count()
            pct = done / total
            stats.append((t, pct))
    stats.sort(key=lambda x: x[1])
    topics = [t for (t, _) in stats[:limit_topics]]
    if not topics:
        topics = list(Topic.objects.annotate(n=Count("lessons")).order_by("-n")[:limit_topics])
    return topics


@require_http_methods(["POST"])
def api_quiz_seed(request):
    """Create a few sample questions if none exist."""
    if QuizQuestion.objects.exists():
        return ok({"message": "Quiz items already present"})

    topics = Topic.objects.all()[:2]
    if topics.count() == 0:
        return fail("Create topics first (use /api/seed-demo).", 400)

    for t in topics:
        q1 = QuizQuestion.objects.create(
            topic=t,
            difficulty="easy",
            text=f"In {t.title}, what is the typical time to access an element by index?",
            explanation="Index access in arrays is O(1) on average.",
        )
        QuizChoice.objects.bulk_create(
            [
                QuizChoice(question=q1, text="O(1)", is_correct=True),
                QuizChoice(question=q1, text="O(n)"),
                QuizChoice(question=q1, text="O(log n)"),
                QuizChoice(question=q1, text="O(n log n)"),
            ]
        )

        q2 = QuizQuestion.objects.create(
            topic=t,
            difficulty="med",
            text=f"Which operation is NOT typical for {t.title.lower()}?",
            explanation="Trick depends on topic; the incorrect choice identifies the odd one.",
        )
        QuizChoice.objects.bulk_create(
            [
                QuizChoice(question=q2, text="Traversal"),
                QuizChoice(question=q2, text="Insertion"),
                QuizChoice(question=q2, text="Compilation", is_correct=True),
                QuizChoice(question=q2, text="Deletion"),
            ]
        )

        q3 = QuizQuestion.objects.create(
            topic=t,
            difficulty="med",
            text=f"{t.title}: Which is true about space usage?",
            explanation="Generic conceptual explanation.",
        )
        QuizChoice.objects.bulk_create(
            [
                QuizChoice(question=q3, text="Depends on implementation", is_correct=True),
                QuizChoice(question=q3, text="Always O(1) space"),
                QuizChoice(question=q3, text="Always O(n^2) space"),
                QuizChoice(question=q3, text="Space is irrelevant"),
            ]
        )

        q4 = QuizQuestion.objects.create(
            topic=t,
            difficulty="hard",
            text=f"Select the best use-case for {t.title.lower()}.",
            explanation="Patterns differ by DS; correct choice names a realistic use-case.",
        )
        QuizChoice.objects.bulk_create(
            [
                QuizChoice(question=q4, text="Scheduling / order maintenance", is_correct=True),
                QuizChoice(question=q4, text="Washing machine cycle"),
                QuizChoice(question=q4, text="Color calibration"),
                QuizChoice(question=q4, text="DNS root hints"),
            ]
        )

    return ok({"message": "Quiz seed created"})


@login_required
@require_GET
def api_quiz_history(request):
    attempts = QuizAttempt.objects.filter(user=request.user).order_by("-created_at")[:10]
    data = [
        {
            "id": a.id,
            "score": a.score,
            "total": a.total,
            "created_at": a.created_at.isoformat(),
            "source": a.source,
        }
        for a in attempts
    ]
    return ok({"attempts": data})


@login_required
@require_GET
def api_quiz_generate(request):
    """Generate an adaptive quiz based on weak topics. Param: ?count=6"""
    try:
        count = int(request.GET.get("count", 6))
    except ValueError:
        count = 6

    topics = pick_weak_topics_for_user(request.user, limit_topics=2)
    qs = QuizQuestion.objects.filter(topic__in=topics)

    def take(d, n):
        return list(qs.filter(difficulty=d).order_by("?")[:n])

    chosen = take("easy", 2) + take("med", 2) + take("hard", 2)
    if len(chosen) < count:
        remaining = count - len(chosen)
        more = list(qs.exclude(id__in=[q.id for q in chosen]).order_by("?")[:remaining])
        chosen += more

    payload = []
    for q in chosen[:count]:
        choices = q.choices.all().order_by("?")
        payload.append(
            {
                "id": q.id,
                "text": q.text,
                "topic": q.topic.title,
                "difficulty": q.difficulty,
                "choices": [{"id": c.id, "text": c.text} for c in choices],
            }
        )
    return ok({"questions": payload})


@login_required
@require_http_methods(["POST"])
def api_quiz_submit(request):
    """
    Body:
    {
      "answers": [{ "question_id": int, "choice_id": int }, ...],
      "source": "weekly"
    }
    """
    p = json_payload(request)
    answers = p.get("answers") or []
    source = (p.get("source") or "weekly")[:32]

    attempt = QuizAttempt.objects.create(user=request.user, source=source)

    score = 0
    total = 0

    for item in answers:
        qid = item.get("question_id")
        cid = item.get("choice_id")
        try:
            q = QuizQuestion.objects.get(id=qid)
        except QuizQuestion.DoesNotExist:
            continue
        chosen = QuizChoice.objects.filter(id=cid, question=q).first()
        correct = bool(chosen and chosen.is_correct)
        AttemptAnswer.objects.create(
            attempt=attempt, question=q, chosen_choice=chosen, correct=correct
        )
        total += 1
        if correct:
            score += 1

    attempt.score = score
    attempt.total = total
    attempt.save()

    feedback = []
    for a in attempt.answers.select_related("question", "chosen_choice"):
        correct_choice = a.question.choices.filter(is_correct=True).first()
        feedback.append(
            {
                "question": a.question.text,
                "your_answer": a.chosen_choice.text if a.chosen_choice else None,
                "correct_answer": correct_choice.text if correct_choice else None,
                "correct": a.correct,
                "explanation": a.question.explanation,
            }
        )

    return ok({"attempt_id": attempt.id, "score": score, "total": total, "feedback": feedback})


# ---------------------------------------------------------------------
# In-app Assistant (very light intent engine)
# ---------------------------------------------------------------------
def _shorten(text, limit=400):
    t = strip_tags(text or "")
    return t if len(t) <= limit else t[:limit].rsplit(" ", 1)[0] + "…"


def _next_incomplete_lesson(user):
    enrolls = Enrollment.objects.filter(user=user).select_related("course")
    for e in enrolls:
        lessons = Lesson.objects.filter(topic__course=e.course).order_by("topic__id", "order")
        for l in lessons:
            done = LessonProgress.objects.filter(user=user, lesson=l, completed=True).exists()
            if not done:
                return l
    return Lesson.objects.order_by("topic__course__title", "topic__title", "order").first()


def _search_lesson_snippets(term):
    term = (term or "").strip()
    if not term:
        return []
    qs = (
        Lesson.objects.filter(Q(title__icontains=term) | Q(content__icontains=term))
        .select_related("topic", "topic__course")[:5]
    )
    results = []
    for l in qs:
        snippet = _shorten(l.content, 500)
        results.append(
            {
                "lesson_id": l.id,
                "title": f"{l.topic.course.title} → {l.topic.title} → {l.title}",
                "snippet": snippet,
            }
        )
    return results


def _make_reply(user, message):
    msg = (message or "").strip().lower()

    # Greetings / help
    if re.search(r"\b(hi|hello|hey)\b", msg):
        return (
            "Hey! I can recommend the next lesson, explain a topic, and generate a quick quiz. Try:\n"
            "- next lesson\n- explain arrays\n- weekly quiz\n- my progress\n"
            "- plan: exam 2025-11-28, topics = arrays; stacks; queues, daily = 180"
        )

    # Next lesson / recommendation
    if any(k in msg for k in ["next", "recommend", "continue"]):
        l = _next_incomplete_lesson(user)
        if not l:
            return "I couldn't find any lessons yet. Seed demo content or enroll in a course first."
        return (
            f"You can continue with **{l.topic.course.title} → {l.topic.title} → {l.title}**.\n\n"
            f"Summary:\n{_shorten(l.content, 300)}\n\n"
            "Ready? Open Learn → choose this topic, or say **quiz** to practice it."
        )

    # Explain {something}
    m = re.search(r"(?:explain|what is|define)\s+(.+)", msg)
    if m:
        term = m.group(1).strip()
        hits = _search_lesson_snippets(term)
        if not hits:
            return f'I couldn\'t find "{term}" in your lessons. Try another term or open Learn.'
        # Return a short list of matching lesson snippets
        lines = ["Here are a few places that cover that:"]
        for h in hits:
            lines.append(f'- **{h["title"]}**\n  {h["snippet"]}')
        lines.append("\nSay **open <lesson_id>** in the Learn section, or **quiz** to practice.")
        return "\n".join(lines)

    # Quick quiz
    if "weekly quiz" in msg or "quiz" in msg:
        return (
            "Opening a quick adaptive quiz. Use the Quiz tab or call `/api/quiz_generate?count=6`.\n"
            "When you're done, submit answers to `/api/quiz_submit` to get feedback."
        )

    # Progress
    if "my progress" in msg or "progress" in msg:
        return (
            "Check your dashboard for progress, or call `/api/my-progress`.\n"
            "If you want a 7-day chart, call `/api/progress-weekly`."
        )

    # Simple study plan parser (non-persisting hint)
    if msg.startswith("plan:"):
        # This is a light acknowledgement to confirm parsing intent.
        return (
            "Got it — I'll set up a study plan outline based on your message. "
            "For now, open the Plan page to review and save it."
        )

    # Default fallback
    return (
        "I can help with:\n"
        "- next lesson\n- explain <topic>\n- weekly quiz\n- my progress\n"
        "Try one of those, or ask about a topic directly."
    )


# ---------------------------------------------------------------------
# Assistant API endpoints
# ---------------------------------------------------------------------
@login_required
@require_POST
def api_ai_start(request):
    """
    Starts a new assistant chat thread for the logged-in user.
    """
    thread = AssistantThread.objects.create(user=request.user, title="New Assistant Session")
    return ok({"thread_id": thread.id, "message": "New AI session started."})


@login_required
@require_POST
def api_ai_message(request):
    """
    Handles incoming user messages to the AI assistant and returns a reply.
    Expected JSON:
    {
        "thread_id": int,
        "message": "string"
    }
    """
    p = json_payload(request)
    thread_id = p.get("thread_id")
    message = (p.get("message") or "").strip()

    if not message:
        return fail("Message required.")

    try:
        thread = AssistantThread.objects.get(id=thread_id, user=request.user)
    except AssistantThread.DoesNotExist:
        return fail("Invalid thread ID.", 404)

    # Save user message
    user_msg = AssistantMessage.objects.create(thread=thread, role="user", content=message)

    # Generate assistant reply using the helper
    reply_text = _make_reply(request.user, message)

    # Save assistant message
    AssistantMessage.objects.create(thread=thread, role="assistant", content=reply_text)

    return ok({"reply": reply_text, "thread_id": thread.id, "message_id": user_msg.id})
