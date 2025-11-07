import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import ensure_csrf_cookie

from .models import StudentProfile, OTPCode
from .utils import create_otp_for_user, update_last_login


# ------------------------------
# Page view
# ------------------------------
@ensure_csrf_cookie
def index(request):
    """
    Serves the main SPA (templates/index.html) and sets a CSRF cookie.
    """
    return render(request, 'index.html')


# ------------------------------
# Helpers (response format)
# ------------------------------
def ok(data=None, status=200):
    return JsonResponse({'ok': True, 'data': data or {}}, status=status)


def fail(message, status=400):
    return JsonResponse({'ok': False, 'error': message}, status=status)


def json_payload(request):
    try:
        return json.loads(request.body.decode('utf-8'))
    except Exception:
        return {}


# ------------------------------
# Auth: Sign up
# ------------------------------
@require_POST
def api_signup(request):
    payload = json_payload(request)
    name = (payload.get('student_name') or '').strip()
    email = (payload.get('email') or '').strip().lower()
    phone = (payload.get('phone') or '').strip()
    password = payload.get('password') or ''
    student_type = (payload.get('student_type') or '').strip()

    if not all([name, email, phone, password, student_type]):
        return fail('All fields are required.')

    if User.objects.filter(username=email).exists():
        return fail('Email already registered.', status=409)

    first_name = name.split(' ')[0]
    last_name = ' '.join(name.split(' ')[1:])

    user = User.objects.create_user(
        username=email,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name
    )
    profile = StudentProfile.objects.create(
        user=user,
        phone=phone,
        student_type=student_type
    )

    login(request, user)
    profile.last_login_at = timezone.now()
    profile.save()

    return ok({
        'student_name': name,
        'email': email,
        'phone': phone,
        'student_type': student_type,
        'created_at': profile.created_at.isoformat(),
        'last_login': profile.last_login_at.isoformat(),
    })


# ------------------------------
# Auth: Login
# ------------------------------
@require_POST
def api_login(request):
    payload = json_payload(request)
    email = (payload.get('email') or '').strip().lower()
    password = payload.get('password') or ''

    user = authenticate(request, username=email, password=password)
    if user is None:
        return fail('Invalid email or password.', status=401)

    login(request, user)
    # update last login on our StudentProfile
    update_last_login(user)

    p = user.profile
    return ok({
        'student_name': (f"{user.first_name} {user.last_name}".strip() or user.username.split('@')[0]),
        'email': user.email,
        'phone': p.phone,
        'student_type': p.student_type,
        'created_at': p.created_at.isoformat(),
        'last_login': (p.last_login_at.isoformat() if p.last_login_at else None),
    })


# ------------------------------
# Auth: Logout
# ------------------------------
@require_POST
def api_logout(request):
    logout(request)
    return ok()


# ------------------------------
# Me: current user
# ------------------------------
@require_GET
def api_me(request):
    if not request.user.is_authenticated:
        return fail('Not logged in.', status=401)

    user = request.user
    p = user.profile
    return ok({
        'student_name': (f"{user.first_name} {user.last_name}".strip() or user.username.split('@')[0]),
        'email': user.email,
        'phone': p.phone,
        'student_type': p.student_type,
        'created_at': p.created_at.isoformat(),
        'last_login': (p.last_login_at.isoformat() if p.last_login_at else None),
    })


# ------------------------------
# Forgot password: start (send OTP)
# ------------------------------
@require_POST
def api_forgot_password(request):
    payload = json_payload(request)
    email = (payload.get('email') or '').strip().lower()

    try:
        user = User.objects.get(username=email)
    except User.DoesNotExist:
        return fail('Email not found.', status=404)

    # Create and (in dev) "send" OTP; we return it for demo so UI can auto-fill.
    otp = create_otp_for_user(user)

    phone = user.profile.phone
    masked = '*' * max(len(phone) - 4, 0) + phone[-4:]

    return ok({
        'otp_demo': otp,         # for local/dev demo auto-fill
        'phone_masked': masked,  # show masked phone in UI
    })


# ------------------------------
# Forgot password: verify OTP (check only)
# ------------------------------
@require_POST
def api_verify_otp(request):
    """
    Verifies that an un-used OTP exists for this user.
    Does NOT consume the OTP; consumption happens on reset.
    """
    payload = json_payload(request)
    email = (payload.get('email') or '').strip().lower()
    code = (payload.get('code') or '').strip()

    try:
        user = User.objects.get(username=email)
    except User.DoesNotExist:
        return fail('Invalid user.', status=404)

    otp_obj = OTPCode.objects.filter(user=user, code=code, is_used=False).order_by('-created_at').first()
    if not otp_obj:
        return fail('Invalid OTP.', status=400)

    return ok()  # valid


# ------------------------------
# Forgot password: reset (consume OTP)
# ------------------------------
@require_POST
def api_reset_password(request):
    payload = json_payload(request)
    email = (payload.get('email') or '').strip().lower()
    code = (payload.get('code') or '').strip()
    new_password = payload.get('new_password') or ''

    if len(new_password) < 6:
        return fail('Password must be at least 6 characters.')

    try:
        user = User.objects.get(username=email)
    except User.DoesNotExist:
        return fail('Invalid user.', status=404)

    otp_obj = OTPCode.objects.filter(user=user, code=code, is_used=False).order_by('-created_at').first()
    if not otp_obj:
        return fail('Invalid OTP.', status=400)

    # Set new password and consume OTP
    user.set_password(new_password)
    user.save()
    otp_obj.is_used = True
    otp_obj.save()

    return ok({'message': 'Password updated'})
from django.views.decorators.http import require_http_methods
from django.db.models import Count
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Course, Topic, Lesson, Enrollment, LessonProgress

# ---------- Learning: list courses ----------
@require_GET
def api_courses(request):
    qs = Course.objects.annotate(
        topics_count=Count('topics'),
        lessons_count=Count('topics__lessons')
    ).order_by('title')

    courses = [{
        'id': c.id,
        'title': c.title,
        'description': c.description,
        'topics_count': c.topics_count,
        'lessons_count': c.lessons_count,
    } for c in qs]
    return ok({'courses': courses})


# ---------- Learning: list topics in a course ----------
@require_GET
def api_topics(request):
    course_id = request.GET.get('course_id')
    try:
        course = Course.objects.get(id=course_id)
    except (Course.DoesNotExist, ValueError, TypeError):
        return fail('Invalid course_id', 400)

    topics = [{
        'id': t.id,
        'title': t.title,
        'summary': t.summary,
        'lessons_count': t.lessons.count()
    } for t in course.topics.all()]
    return ok({'course': {'id': course.id, 'title': course.title}, 'topics': topics})


# ---------- Learning: list lessons in a topic ----------
@require_GET
def api_lessons(request):
    topic_id = request.GET.get('topic_id')
    try:
        topic = Topic.objects.get(id=topic_id)
    except (Topic.DoesNotExist, ValueError, TypeError):
        return fail('Invalid topic_id', 400)

    user = request.user if request.user.is_authenticated else None
    done = set()
    if user:
        done = set(LessonProgress.objects.filter(user=user, completed=True, lesson__topic=topic)
                   .values_list('lesson_id', flat=True))

    lessons = [{
        'id': l.id,
        'title': l.title,
        'content': l.content,
        'order': l.order,
        'completed': (l.id in done)
    } for l in topic.lessons.all().order_by('order')]
    return ok({'topic': {'id': topic.id, 'title': topic.title}, 'lessons': lessons})


# ---------- Learning: mark lesson complete ----------
@require_POST
def api_mark_lesson(request):
    if not request.user.is_authenticated:
        return fail('Login required', 401)

    payload = json_payload(request)
    lesson_id = payload.get('lesson_id')
    try:
        lesson = Lesson.objects.get(id=lesson_id)
    except (Lesson.DoesNotExist, ValueError, TypeError):
        return fail('Invalid lesson_id', 400)

    lp, _ = LessonProgress.objects.get_or_create(user=request.user, lesson=lesson)
    lp.completed = True
    lp.completed_at = timezone.now()
    lp.save()

    # auto-enroll into course if not already
    Enrollment.objects.get_or_create(user=request.user, course=lesson.topic.course)

    return ok({'lesson_id': lesson.id, 'completed': True})


# ---------- Learning: my progress summary ----------
@require_GET
def api_my_progress(request):
    if not request.user.is_authenticated:
        return fail('Login required', 401)

    enrolls = Enrollment.objects.filter(user=request.user).select_related('course')
    result = []
    for e in enrolls:
        total = Lesson.objects.filter(topic__course=e.course).count()
        done = LessonProgress.objects.filter(user=request.user, lesson__topic__course=e.course, completed=True).count()
        pct = (done / total * 100) if total else 0
        result.append({
            'course_id': e.course.id,
            'course_title': e.course.title,
            'lessons_done': done,
            'lessons_total': total,
            'percent': round(pct, 1)
        })
    return ok({'progress': result})


# ---------- Learning: seed demo content ----------
@require_http_methods(['POST'])
def api_seed_demo(request):
    """Creates demo Course/Topic/Lesson if not present."""
    if Course.objects.exists():
        return ok({'message': 'Demo content already present'})

    # Course
    c = Course.objects.create(
        title='Data Structures (Beginner)',
        description='Start with arrays, stacks, queues and complexity basics.'
    )
    # Topics
    t1 = Topic.objects.create(course=c, title='Arrays', summary='Basics, indexing, operations')
    t2 = Topic.objects.create(course=c, title='Stacks & Queues', summary='LIFO/FIFO with examples')

    # Lessons
    Lesson.objects.create(topic=t1, order=1, title='What is an Array?',
                          content='<p>Array is a contiguous block of memory...</p>')
    Lesson.objects.create(topic=t1, order=2, title='Array Operations',
                          content='<ul><li>Insert</li><li>Delete</li><li>Traverse</li></ul>')
    Lesson.objects.create(topic=t2, order=1, title='Stacks',
                          content='<p>Stack supports push/pop/peek. Use cases...</p>')
    Lesson.objects.create(topic=t2, order=2, title='Queues',
                          content='<p>Queue supports enqueue/dequeue. Use cases...</p>')

    return ok({'message': 'Demo course created'})
from datetime import timedelta
from django.db.models import Count
from django.db.models.functions import TruncDate

@require_GET
def api_progress_weekly(request):
    """
    Returns last 7 days (including today) of lesson completions for the logged-in user.
    Response:
      {
        "days": [{"date":"2025-11-07","label":"Fri","count":2}, ... 7 items ...],
        "total_week": 7,
        "max_day": {"date":"2025-11-06","label":"Thu","count":3}
      }
    """
    if not request.user.is_authenticated:
        return fail('Login required', 401)

    user = request.user
    today = timezone.localdate()
    start = today - timedelta(days=6)

    # Get counts grouped by day within range
    raw = (LessonProgress.objects
           .filter(user=user, completed=True,
                   completed_at__date__gte=start,
                   completed_at__date__lte=today)
           .annotate(day=TruncDate('completed_at'))
           .values('day')
           .annotate(count=Count('id')))

    # Map results to dict for quick lookup
    day_counts = {row['day']: row['count'] for row in raw}

    # Build 7-day sequence
    labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    days = []
    for i in range(7):
        d = start + timedelta(days=i)
        cnt = int(day_counts.get(d, 0))
        days.append({
            'date': d.isoformat(),
            'label': labels[d.weekday()],
            'count': cnt
        })

    total_week = sum(item['count'] for item in days)
    max_item = max(days, key=lambda x: x['count']) if days else {'date': None, 'label': None, 'count': 0}

    return ok({
        'days': days,
        'total_week': total_week,
        'max_day': max_item
    })
from django.db.models import Count
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .models import QuizQuestion, QuizChoice, QuizAttempt, AttemptAnswer

def pick_weak_topics_for_user(user, limit_topics=2):
    """
    Infer weak areas:
    - Topics with lowest completion % in enrolled courses
    - If no enrollment, fallback to topics with most lessons overall
    """
    enrolls = Enrollment.objects.filter(user=user).select_related('course')
    if not enrolls.exists():
        # fallback: top topics by lesson count
        return list(Topic.objects.annotate(n=Count('lessons')).order_by('-n')[:limit_topics])

    topic_stats = []
    for e in enrolls:
        for t in e.course.topics.all():
            total = t.lessons.count()
            if total == 0:
                continue
            done = LessonProgress.objects.filter(user=user, lesson__topic=t, completed=True).count()
            pct = done / total
            topic_stats.append((t, pct))
    topic_stats.sort(key=lambda x: x[1])  # lowest first
    topics = [t for (t, _) in topic_stats[:limit_topics]]
    if not topics:
        topics = list(Topic.objects.annotate(n=Count('lessons')).order_by('-n')[:limit_topics])
    return topics

@require_http_methods(['POST'])
def api_quiz_seed(request):
    """
    Create a few sample questions if none exist.
    Requires Course/Topic/Lesson from earlier seeding.
    """
    if QuizQuestion.objects.exists():
        return ok({'message': 'Quiz items already present'})

    # Find some topics to attach to
    topics = Topic.objects.all()[:2]
    if topics.count() == 0:
        return fail('Create topics first (use /api/seed-demo).', 400)

    # Simple seed: 4 questions per available topic
    for t in topics:
        q1 = QuizQuestion.objects.create(topic=t, difficulty='easy',
             text=f"In {t.title}, what is the typical time to access an element by index?",
             explanation="Index access in arrays is O(1) on average.")
        QuizChoice.objects.bulk_create([
            QuizChoice(question=q1, text='O(1)', is_correct=True),
            QuizChoice(question=q1, text='O(n)'),
            QuizChoice(question=q1, text='O(log n)'),
            QuizChoice(question=q1, text='O(n log n)'),
        ])

        q2 = QuizQuestion.objects.create(topic=t, difficulty='med',
             text=f"Which operation is NOT typical for {t.title.lower()}?",
             explanation="Trick depends on topic; the incorrect choice identifies the odd one.")
        QuizChoice.objects.bulk_create([
            QuizChoice(question=q2, text='Traversal'),
            QuizChoice(question=q2, text='Insertion'),
            QuizChoice(question=q2, text='Compilation', is_correct=True),
            QuizChoice(question=q2, text='Deletion'),
        ])

        q3 = QuizQuestion.objects.create(topic=t, difficulty='med',
             text=f"{t.title}: Which is true about space usage?",
             explanation="Generic conceptual explanation.")
        QuizChoice.objects.bulk_create([
            QuizChoice(question=q3, text='Depends on implementation', is_correct=True),
            QuizChoice(question=q3, text='Always O(1) space'),
            QuizChoice(question=q3, text='Always O(n^2) space'),
            QuizChoice(question=q3, text='Space is irrelevant'),
        ])

        q4 = QuizQuestion.objects.create(topic=t, difficulty='hard',
             text=f"Select the best use-case for {t.title.lower()}.",
             explanation="Patterns differ by DS; correct choice names a realistic use-case.")
        QuizChoice.objects.bulk_create([
            QuizChoice(question=q4, text='Scheduling / order maintenance', is_correct=True),
            QuizChoice(question=q4, text='Washing machine cycle'),
            QuizChoice(question=q4, text='Color calibration'),
            QuizChoice(question=q4, text='DNS root hints'),
        ])

    return ok({'message': 'Quiz seed created'})

@login_required
@require_http_methods(['GET'])
def api_quiz_history(request):
    attempts = (QuizAttempt.objects
                .filter(user=request.user)
                .order_by('-created_at')[:10])
    data = []
    for a in attempts:
        data.append({
            'id': a.id,
            'score': a.score,
            'total': a.total,
            'created_at': a.created_at.isoformat(),
            'source': a.source
        })
    return ok({'attempts': data})

@login_required
@require_http_methods(['GET'])
def api_quiz_generate(request):
    """
    Generate an adaptive quiz based on weak topics + weekly need.
    Params (optional): ?count=5
    """
    try:
        count = int(request.GET.get('count', 6))
    except ValueError:
        count = 6

    topics = pick_weak_topics_for_user(request.user, limit_topics=2)
    qs = QuizQuestion.objects.filter(topic__in=topics)

    # Diversify by difficulty: 2 easy, 2 med, 2 hard (as available)
    def take(d, n):
        return list(qs.filter(difficulty=d).order_by('?')[:n])

    chosen = take('easy', 2) + take('med', 2) + take('hard', 2)
    if len(chosen) < count:
        remaining = count - len(chosen)
        more = list(qs.exclude(id__in=[q.id for q in chosen]).order_by('?')[:remaining])
        chosen += more

    payload = []
    for q in chosen[:count]:
        choices = q.choices.all().order_by('?')
        payload.append({
            'id': q.id,
            'text': q.text,
            'topic': q.topic.title,
            'difficulty': q.difficulty,
            'choices': [{'id': c.id, 'text': c.text} for c in choices]
        })
    return ok({'questions': payload})

@login_required
@require_http_methods(['POST'])
def api_quiz_submit(request):
    """
    Body: {
      answers: [{question_id, choice_id}, ...],
      source: 'weekly'
    }
    """
    payload = json_payload(request)
    answers = payload.get('answers') or []
    source = (payload.get('source') or 'weekly')[:32]

    attempt = QuizAttempt.objects.create(user=request.user, source=source)

    # score
    score = 0
    total = 0

    for item in answers:
        qid = item.get('question_id')
        cid = item.get('choice_id')
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

    # Return per-question feedback
    feedback = []
    for a in attempt.answers.select_related('question', 'chosen_choice'):
        correct_choice = a.question.choices.filter(is_correct=True).first()
        feedback.append({
            'question': a.question.text,
            'your_answer': a.chosen_choice.text if a.chosen_choice else None,
            'correct_answer': correct_choice.text if correct_choice else None,
            'correct': a.correct,
            'explanation': a.question.explanation
        })

    return ok({
        'attempt_id': attempt.id,
        'score': score,
        'total': total,
        'feedback': feedback
    })
import re
from django.utils.html import strip_tags
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import (
    AssistantThread, AssistantMessage,
    Course, Topic, Lesson, Enrollment, LessonProgress
)

def _shorten(text, limit=400):
    t = strip_tags(text or "")
    return t if len(t) <= limit else t[:limit].rsplit(' ', 1)[0] + "…"

def _next_incomplete_lesson(user):
    """Find the next not-completed lesson from enrolled courses."""
    enrolls = Enrollment.objects.filter(user=user).select_related('course')
    for e in enrolls:
        lessons = Lesson.objects.filter(topic__course=e.course).order_by('topic__id', 'order')
        for l in lessons:
            done = LessonProgress.objects.filter(user=user, lesson=l, completed=True).exists()
            if not done:
                return l
    # If no enrollments or all done, offer first lesson available
    l = Lesson.objects.order_by('topic__course__title', 'topic__title', 'order').first()
    return l

def _search_lesson_snippets(term):
    """Find lessons by term in title/content; return list of (title, snippet)."""
    term = term.strip()
    if not term:
        return []
    qs = Lesson.objects.filter(
        Q(title__icontains=term) | Q(content__icontains=term)
    ).select_related('topic', 'topic__course')[:5]
    results = []
    for l in qs:
        snippet = _shorten(l.content, 500)
        results.append({
            'lesson_id': l.id,
            'title': f"{l.topic.course.title} → {l.topic.title} → {l.title}",
            'snippet': snippet
        })
    return results

def _make_reply(user, message):
    """Very small intent engine."""
    msg = (message or "").strip().lower()

    # Greetings / help
    if re.search(r'\b(hi|hello|hey)\b', msg):
        return ("Hey! I can recommend the next lesson, explain a topic, "
                "and generate a quick quiz. Try:\n"
                "- next lesson\n- explain arrays\n- weekly quiz\n- my progress")

    # Next lesson / recommendation
    if 'next' in msg or 'recommend' in msg or 'continue' in msg:
        l = _next_incomplete_lesson(user)
        if not l:
            return "I couldn’t find any lessons yet. Seed demo content or enroll in a course first."
        return (f"You can continue with **{l.topic.course.title} → {l.topic.title} → {l.title}**.\n\n"
                f"Summary:\n{_shorten(l.content, 300)}\n\n"
                "Ready? Open Learn → choose this topic, or say **quiz** to practice it.")

    # Explain {something}
    m = re.search(r'(explain|what is|define)\s+(.+)', msg)
    if m:
        term = m.group(2)
        hits = _search_lesson_snippets(term)
        if not hits:
            return f"I couldn’t find “{term}” in your lessons. Try another term or open Learn."
        parts = []
        for h in hits:
            parts.append(f"• **{h['title']}**\n{h['snippet']}")
        return "Here’s what I found:\n\n" + "\n\n".join(parts)

    # Quiz
    if 'quiz' in msg:
        return ("Great idea. Click **Interactive Quizzes → Take Weekly Quiz** to start. "
                "I’ll pick questions from topics where you need practice.")

    # Progress
    if 'progress' in msg or 'weekly' in msg or 'streak' in msg:
        return ("Open **Track Progress → Weekly** to see your 7-day chart, totals, and achievements. "
                "Want a recommendation? Say **next lesson**.")

    # Default
    return ("I can help with: **next lesson**, **explain {topic}**, **quiz**, **progress**.\n"
            "What would you like to do?")
    if 'plan' in msg or 'study plan' in msg:
        return ("I can build a study plan from your exam date or days left and your topics.\n"
                "Click **Plan with AI** or tell me your exam date and topics like:\n"
                "`plan: exam 2025-11-28, topics = arrays; stacks; queues, daily = 180`")    

@login_required
@require_POST
def api_ai_start(request):
    thread = AssistantThread.objects.create(user=request.user)
    AssistantMessage.objects.create(thread=thread, role='system',
                                    content="Assistant thread created.")
    return ok({'thread_id': thread.id})

@login_required
@require_POST
def api_ai_message(request):
    payload = json_payload(request)
    thread_id = payload.get('thread_id')
    text = (payload.get('message') or '').strip()
    if not text:
        return fail('Empty message')

    try:
        thread = AssistantThread.objects.get(id=thread_id, user=request.user, is_active=True)
    except AssistantThread.DoesNotExist:
        return fail('Invalid thread', 404)

    AssistantMessage.objects.create(thread=thread, role='user', content=text)
    reply = _make_reply(request.user, text)
    AssistantMessage.objects.create(thread=thread, role='assistant', content=reply)

    return ok({'reply': reply})
from datetime import timedelta, date
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.views.decorators.http import require_http_methods
from .models import StudyPlan, StudyTask, Topic, Lesson, LessonProgress, Enrollment

def _match_topics_by_name(topic_names):
    """Try to map user-entered names to Topic objects; fallback as plain strings."""
    mappings = []
    for raw in topic_names:
        name = (raw or '').strip()
        if not name:
            continue
        qs = Topic.objects.filter(title__icontains=name)[:1]
        if qs:
            t = qs[0]
            lessons_count = t.lessons.count() or 1
            mappings.append({'label': t.title, 'topic_obj': t, 'weight': lessons_count})
        else:
            mappings.append({'label': name, 'topic_obj': None, 'weight': 1})
    return mappings

def _boost_weak_topics(user, mapped):
    """Multiply weight for weak topics (low completion)."""
    boosted = []
    for item in mapped:
        w = item['weight']
        t = item['topic_obj']
        if t:
            total = t.lessons.count()
            done = LessonProgress.objects.filter(user=user, lesson__topic=t, completed=True).count()
            pct = (done / total) if total else 0
            if pct < 0.5:
                w = max(1, int(round(w * 1.5)))
        boosted.append({**item, 'weight': w})
    return boosted

def _days_between(today, exam_date, days):
    if exam_date:
        delta = (exam_date - today).days + 1  # include today
        return max(1, delta)
    return max(1, days)

def _distribute_sessions(mapped, total_minutes):
    """
    Returns a list of session topics sized to total_minutes.
    Each session is 45m, followed by 15m break (except the last).
    """
    session_len = 45
    break_len = 15
    sessions = max(1, total_minutes // session_len)  # count of study blocks
    # Build a weighted pool
    pool = []
    for m in mapped:
        pool += [m['label']] * max(1, m['weight'])
    if not pool:
        pool = ['General Review']

    plan_topics = []
    idx = 0
    for s in range(sessions):
        topic = pool[idx % len(pool)]
        plan_topics.append({'topic': topic, 'minutes': session_len, 'break_after': (s != sessions - 1), 'break_minutes': break_len})
        idx += 1
    return plan_topics

@login_required
@require_http_methods(['POST'])
def api_plan_create(request):
    """
    Body:
    {
      "exam_date": "2025-11-20" OR "days_left": 10,
      "daily_minutes": 180,          # optional (default 180)
      "topics": ["Arrays", "Stacks", "Queues"]  # required (strings)
    }
    """
    p = json_payload(request)
    topics_in = p.get('topics') or []
    if not topics_in:
        return fail('Please provide topics list.')

    daily_minutes = int(p.get('daily_minutes') or 180)
    days_left = p.get('days_left')
    exam_date_str = p.get('exam_date')
    exam_dt = None
    if exam_date_str:
        try:
            y, m, d = [int(x) for x in exam_date_str.split('-')]
            exam_dt = date(y, m, d)
        except Exception:
            return fail('Invalid exam_date (YYYY-MM-DD).')

    today = timezone.localdate()
    total_days = _days_between(today, exam_dt, int(days_left or 0))

    # Close any existing active plan
    StudyPlan.objects.filter(user=request.user, is_active=True).update(is_active=False)

    plan = StudyPlan.objects.create(
        user=request.user,
        title='Exam Study Plan',
        exam_date=exam_dt,
        days=total_days,
        daily_minutes=daily_minutes,
        is_active=True,
    )

    # Map topics and boost weak ones
    mapped = _match_topics_by_name(topics_in)
    mapped = _boost_weak_topics(request.user, mapped)

    # Build daily tasks
    for i in range(total_days):
        day = today + timedelta(days=i)
        # Every 4th day: light buffer/review day at 60% load
        day_minutes = int(round(daily_minutes * (0.6 if (i + 1) % 4 == 0 else 1.0)))
        sessions = _distribute_sessions(mapped, day_minutes)

        # Insert a short "weekly-style review" block every 3rd session
        counter = 0
        for s in sessions:
            StudyTask.objects.create(plan=plan, date=day, topic=s['topic'], minutes=s['minutes'], is_break=False)
            counter += 1
            if s['break_after']:
                StudyTask.objects.create(plan=plan, date=day, topic='Break', minutes=s['break_minutes'], is_break=True)
            if counter % 3 == 0:
                StudyTask.objects.create(plan=plan, date=day, topic='Review & practice (weak areas)', minutes=20, is_break=False)

        # Add final 10m buffer recap on heavy days
        if day_minutes >= daily_minutes:
            StudyTask.objects.create(plan=plan, date=day, topic='Quick recap / flashcards', minutes=10, is_break=False)

    return ok({'plan_id': plan.id})

@login_required
@require_http_methods(['GET'])
def api_plan_current(request):
    plan = StudyPlan.objects.filter(user=request.user, is_active=True).order_by('-created_at').first()
    if not plan:
        return ok({'plan': None})
    tasks = [{
        'id': t.id,
        'date': t.date.isoformat(),
        'topic': t.topic,
        'minutes': t.minutes,
        'is_break': t.is_break,
        'done': t.done,
    } for t in plan.tasks.all()]
    return ok({
        'plan': {
            'id': plan.id,
            'title': plan.title,
            'exam_date': plan.exam_date.isoformat() if plan.exam_date else None,
            'days': plan.days,
            'daily_minutes': plan.daily_minutes,
            'created_at': plan.created_at.isoformat(),
        },
        'tasks': tasks
    })

@login_required
@require_http_methods(['POST'])
def api_plan_toggle(request):
    p = json_payload(request)
    task_id = p.get('task_id')
    try:
        task = StudyTask.objects.get(id=task_id, plan__user=request.user, plan__is_active=True)
    except StudyTask.DoesNotExist:
        return fail('Invalid task', 404)
    task.done = not task.done
    task.save()
    return ok({'task_id': task.id, 'done': task.done})

@login_required
@require_http_methods(['POST'])
def api_plan_clear(request):
    StudyPlan.objects.filter(user=request.user, is_active=True).update(is_active=False)
    return ok({'message': 'Active plan cleared'})
# inside _make_reply(...)from django.views.decorators.http import require_GET, require_http_methods
from django.db.models import Max
from .models import Exam, Subject, SubjectWeightage, Resource

@require_GET
def api_exams(request):
    exams = Exam.objects.all().order_by('name')
    data = [{'id': e.id, 'name': e.name, 'grade': e.grade, 'slug': e.slug} for e in exams]
    return ok({'exams': data})

@require_GET
def api_subjects_by_exam(request):
    slug = request.GET.get('exam_slug')
    try:
        exam = Exam.objects.get(slug=slug)
    except Exam.DoesNotExist:
        return fail('Invalid exam_slug', 400)
    subs = exam.subjects.all()
    data = [{'id': s.id, 'name': s.name} for s in subs]
    return ok({'exam': {'id': exam.id, 'name': exam.name, 'slug': exam.slug}, 'subjects': data})

@require_GET
def api_resources_by_subject(request):
    try:
        subject_id = int(request.GET.get('subject_id'))
    except (TypeError, ValueError):
        return fail('subject_id is required', 400)

    kinds = request.GET.get('kinds', 'youtube,notes,paper').split(',')
    kinds = [k.strip() for k in kinds if k.strip()]

    rs = Resource.objects.filter(subject_id=subject_id, kind__in=kinds)
    items = []
    for r in rs:
        items.append({
            'id': r.id,
            'kind': r.kind,
            'title': r.title,
            'url': r.url,
            'source': r.source,
            'year': r.year,
            'solution_url': r.solution_url,
        })
    return ok({'resources': items})

@require_GET
def api_weightages_by_exam(request):
    slug = request.GET.get('exam_slug')
    year = request.GET.get('year')
    try:
        exam = Exam.objects.get(slug=slug)
    except Exam.DoesNotExist:
        return fail('Invalid exam_slug', 400)

    qs = SubjectWeightage.objects.filter(subject__exam=exam)
    if year:
        try:
            year = int(year)
            qs = qs.filter(year=year)
        except ValueError:
            return fail('Invalid year', 400)
    else:
        latest = qs.aggregate(m=Max('year'))['m']
        if latest:
            qs = qs.filter(year=latest)

    data = [{
        'subject_id': w.subject_id,
        'subject': w.subject.name,
        'weight_percent': w.weight_percent,
        'year': w.year
    } for w in qs]
    return ok({'exam': {'id': exam.id, 'name': exam.name, 'slug': exam.slug}, 'weights': data})

@require_http_methods(['POST'])
def api_studyhub_seed(request):
    """One-click demo data to see UI working."""
    if Exam.objects.exists():
        return ok({'message': 'Study Hub demo already present'})

    # Example: CBSE Class 12
    cbse = Exam.objects.create(name='CBSE', grade='Class 12', slug='cbse-12', description='CBSE Class 12 Board')
    phy = Subject.objects.create(exam=cbse, name='Physics')
    chem = Subject.objects.create(exam=cbse, name='Chemistry')
    math = Subject.objects.create(exam=cbse, name='Mathematics')

    SubjectWeightage.objects.bulk_create([
        SubjectWeightage(subject=phy, weight_percent=30, year=2025),
        SubjectWeightage(subject=chem, weight_percent=30, year=2025),
        SubjectWeightage(subject=math, weight_percent=40, year=2025),
    ])

    Resource.objects.bulk_create([
        # Physics
        Resource(subject=phy, kind='youtube', title='Ray Optics Crash Course', url='https://www.youtube.com/watch?v=xxxxx', source='XYZ Channel'),
        Resource(subject=phy, kind='notes', title='Electrostatics Handwritten Notes (PDF)', url='https://example.com/notes/electrostatics.pdf', source='Example Notes'),
        Resource(subject=phy, kind='paper', title='Physics Board Paper 2024', url='https://example.com/papers/phy-2024.pdf', solution_url='https://example.com/papers/phy-2024-sol.pdf', year=2024),

        # Chemistry
        Resource(subject=chem, kind='youtube', title='Organic Chemistry in 2 Hours', url='https://www.youtube.com/watch?v=yyyyy', source='ABC Channel'),
        Resource(subject=chem, kind='notes', title='Inorganic One-shot Notes', url='https://example.com/notes/inorganic.pdf', source='Notes Hub'),
        Resource(subject=chem, kind='paper', title='Chemistry Board Paper 2024', url='https://example.com/papers/chem-2024.pdf', solution_url='https://example.com/papers/chem-2024-sol.pdf', year=2024),

        # Math
        Resource(subject=math, kind='youtube', title='Calculus Essentials', url='https://www.youtube.com/watch?v=zzzzz', source='Math Pro'),
        Resource(subject=math, kind='notes', title='Vectors & 3D Geometry Notes', url='https://example.com/notes/vectors.pdf', source='NoteStack'),
        Resource(subject=math, kind='paper', title='Math Board Paper 2024', url='https://example.com/papers/math-2024.pdf', solution_url='https://example.com/papers/math-2024-sol.pdf', year=2024),
    ])

    # Example 2: JEE Main
    jee = Exam.objects.create(name='JEE Main', grade='UG', slug='jee-main', description='JEE Main Entrance')
    p = Subject.objects.create(exam=jee, name='Physics')
    c = Subject.objects.create(exam=jee, name='Chemistry')
    m = Subject.objects.create(exam=jee, name='Mathematics')

    SubjectWeightage.objects.bulk_create([
        SubjectWeightage(subject=p, weight_percent=33, year=2025),
        SubjectWeightage(subject=c, weight_percent=33, year=2025),
        SubjectWeightage(subject=m, weight_percent=34, year=2025),
    ])

    Resource.objects.bulk_create([
        Resource(subject=p, kind='youtube', title='Kinematics Marathon', url='https://www.youtube.com/watch?v=aaaaa', source='Top Channel'),
        Resource(subject=c, kind='notes', title='Physical Chemistry Formula Sheet', url='https://example.com/notes/phychem.pdf', source='ChemNotes'),
        Resource(subject=m, kind='paper', title='JEE Main Jan 2024 Shift 1', url='https://example.com/jee/jan24s1.pdf', solution_url='https://example.com/jee/jan24s1-sol.pdf', year=2024),
    ])

    return ok({'message': 'Seeded Study Hub demo data'})

import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login

def _json(request):
    try:
        return json.loads(request.body.decode() or "{}")
    except Exception:
        return {}

def ok(data): return JsonResponse({"ok": True, "data": data})
def fail(msg, code=400): return JsonResponse({"ok": False, "message": msg}, status=code)

@require_POST
def api_login(request):
    """JSON login: { "email": "...", "password": "..." } or { "username": "...", "password": "..." }"""
    payload = _json(request)
    username = payload.get("username") or payload.get("email")
    password = payload.get("password") or ""

    if not username or not password:
        return fail("username/email and password are required")

    # Try by username, then by email->username
    user = authenticate(request, username=username, password=password)
    if not user:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            u = User.objects.get(email__iexact=username)
            user = authenticate(request, username=u.username, password=password)
        except User.DoesNotExist:
            user = None

    if not user:
        return fail("Invalid credentials", 401)

    login(request, user)
    return ok({
        "username": user.username,
        "email": getattr(user, "email", ""),
        "first_name": user.first_name,
        "last_name": user.last_name,
    })

