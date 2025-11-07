// --------------------------------------------------------
// Adhyeta Frontend Logic (Connected to Django Backend)
// --------------------------------------------------------

console.log("Adhyeta frontend initialized ✅");

const API = {
    signup: '/api/signup',
    login: '/api/login',
    logout: '/api/logout',
    me: '/api/me',
    forgotPassword: '/api/forgot-password',
    verifyOtp: '/api/verify-otp',
    resetPassword: '/api/reset-password'
};

// -------------------------------
// Utility Functions
// -------------------------------
function showToast(message, type = "success") {
    const div = document.createElement("div");
    div.className = `fixed top-4 right-4 px-6 py-3 rounded-lg text-white shadow-lg z-50 transition-transform duration-300 ${
        type === "error" ? "bg-red-600" : "bg-green-600"
    }`;
    div.textContent = message;
    document.body.appendChild(div);
    setTimeout(() => (div.style.transform = "translateX(0)"), 50);
    setTimeout(() => {
        div.style.transform = "translateX(200%)";
        setTimeout(() => div.remove(), 300);
    }, 3000);
}

// ---- CSRF helpers (Django) ----
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
}

async function fetchJSON(url, method = "GET", body) {
  const opts = {
    method,
    headers: { "Content-Type": "application/json" },
    credentials: "same-origin", // send cookies (incl. csrftoken)
  };
  if (body !== undefined) {
    opts.body = JSON.stringify(body);
    // add CSRF for unsafe methods (POST/PUT/PATCH/DELETE)
    const csrf = getCookie("csrftoken");
    if (csrf) opts.headers["X-CSRFToken"] = csrf;
  }
  const resp = await fetch(url, opts);
  const data = await resp.json().catch(() => ({}));
  return resp.ok ? { ok: true, data } : { ok: false, error: data?.message || resp.statusText };
}


// -------------------------------
// Modal Helper
// -------------------------------
function createModal(title, content) {
    const modal = document.createElement("div");
    modal.className = "fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4";
    modal.innerHTML = `
        <div class="bg-white rounded-3xl p-8 max-w-md w-full relative cool-shadow animate-fadeIn">
            <h2 class="text-2xl font-bold text-center bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-4">${title}</h2>
            ${content}
            <button id="closeModal" class="absolute top-4 right-4 text-gray-400 hover:text-gray-600 text-2xl">&times;</button>
        </div>
    `;
    document.body.appendChild(modal);
    document.getElementById("closeModal").addEventListener("click", () => modal.remove());
    modal.addEventListener("click", (e) => e.target === modal && modal.remove());
    return modal;
}

// -------------------------------
// Sign Up
// -------------------------------
document.querySelectorAll('a[href="#signup"]').forEach(link => {
    link.addEventListener("click", (e) => {
        e.preventDefault();
        const content = `
            <form id="signupForm" class="space-y-4">
                <input id="student_name" placeholder="Full Name" class="w-full border rounded-xl p-3" required>
                <input id="email" type="email" placeholder="Email Address" class="w-full border rounded-xl p-3" required>
                <input id="phone" placeholder="Phone Number" class="w-full border rounded-xl p-3" required>
                <input id="password" type="password" placeholder="Password" class="w-full border rounded-xl p-3" required>
                <select id="student_type" class="w-full border rounded-xl p-3" required>
                    <option value="">I am a...</option>
                    <option>High School Student</option>
                    <option>College Student</option>
                    <option>Graduate Student</option>
                    <option>Working Professional</option>
                    <option>Other</option>
                </select>
                <button class="cta-button w-full py-3 rounded-xl font-semibold text-white">Create Account 🎉</button>
            </form>
        `;
        const modal = createModal("Join Adhyeta 🚀", content);

        document.getElementById("signupForm").addEventListener("submit", async (e) => {
            e.preventDefault();
            const data = {
                student_name: student_name.value,
                email: email.value,
                phone: phone.value,
                password: password.value,
                student_type: student_type.value
            };
            const res = await fetchJSON(API.signup, "POST", data);
            if (res.ok) {
                showToast("Welcome to Adhyeta 🎓");
                modal.remove();
                loadDashboard();
            } else showToast(res.error, "error");
        });
    });
});

// -------------------------------
// Login
// -------------------------------
document.querySelectorAll('a[href="#login"]').forEach(link => {
    link.addEventListener("click", (e) => {
        e.preventDefault();
        const content = `
            <form id="loginForm" class="space-y-4">
                <input id="login_email" type="email" placeholder="Email" class="w-full border rounded-xl p-3" required>
                <input id="login_password" type="password" placeholder="Password" class="w-full border rounded-xl p-3" required>
                <button class="cta-button w-full py-3 rounded-xl text-white font-semibold">Login 🚀</button>
                <p class="text-center text-sm text-gray-600 mt-2">
                    Forgot your password? <a href="#" id="forgotLink" class="text-purple-600 hover:underline">Reset it 🔑</a>
                </p>
            </form>
        `;
        const modal = createModal("Welcome Back 👋", content);

        document.getElementById("loginForm").addEventListener("submit", async (e) => {
            e.preventDefault();
            const data = {
                email: login_email.value,
                password: login_password.value
            };
            const res = await fetchJSON(API.login, "POST", data);
            if (res.ok) {
                showToast(`Welcome ${res.data.student_name} 🎉`);
                modal.remove();
                loadDashboard();
            } else showToast(res.error, "error");
        });

        document.getElementById("forgotLink").addEventListener("click", (e) => {
            e.preventDefault();
            modal.remove();
            showForgotPassword();
        });
    });
});

// -------------------------------
// Forgot Password + OTP Flow
// -------------------------------
function showForgotPassword() {
    const content = `
        <form id="forgotForm" class="space-y-4">
            <input id="forgot_email" type="email" placeholder="Registered Email" class="w-full border rounded-xl p-3" required>
            <button class="cta-button w-full py-3 rounded-xl text-white font-semibold">Send OTP 📱</button>
        </form>
    `;
    const modal = createModal("Forgot Password 🔑", content);

    document.getElementById("forgotForm").addEventListener("submit", async (e) => {
        e.preventDefault();
        const res = await fetchJSON(API.forgotPassword, "POST", { email: forgot_email.value });
        if (res.ok) {
            showToast(`OTP sent to ${res.data.phone_masked}`);
            modal.remove();
            showOtpVerify(forgot_email.value, res.data.otp_demo);
        } else showToast(res.error, "error");
    });
}

function showOtpVerify(email, otpDemo) {
    const content = `
        <form id="otpForm" class="space-y-4">
            <p class="text-gray-600 text-center text-sm">We sent an OTP to your phone</p>
            <input id="otp_code" maxlength="6" placeholder="Enter OTP" class="w-full border rounded-xl p-3 text-center" required>
            <button class="cta-button w-full py-3 rounded-xl text-white font-semibold">Verify OTP ✅</button>
        </form>
    `;
    const modal = createModal("OTP Verification 📲", content);

    // Auto-fill demo OTP (for testing)
    setTimeout(() => {
        otp_code.value = otpDemo;
        showToast("OTP auto-filled (demo)");
    }, 2000);

    document.getElementById("otpForm").addEventListener("submit", async (e) => {
        e.preventDefault();
        const res = await fetchJSON(API.verifyOtp, "POST", { email, code: otp_code.value });
        if (res.ok) {
            showToast("OTP Verified ✅");
            modal.remove();
            showResetPassword(email, otp_code.value);
        } else showToast(res.error, "error");
    });
}

function showResetPassword(email, code) {
    const content = `
        <form id="resetForm" class="space-y-4">
            <input id="new_password" type="password" placeholder="New Password" class="w-full border rounded-xl p-3" required>
            <input id="confirm_password" type="password" placeholder="Confirm Password" class="w-full border rounded-xl p-3" required>
            <button class="cta-button w-full py-3 rounded-xl text-white font-semibold">Reset Password 🔒</button>
        </form>
    `;
    const modal = createModal("Reset Password 🔐", content);

    document.getElementById("resetForm").addEventListener("submit", async (e) => {
        e.preventDefault();
        if (new_password.value !== confirm_password.value)
            return showToast("Passwords do not match", "error");
        const res = await fetchJSON(API.resetPassword, "POST", {
            email,
            code,
            new_password: new_password.value
        });
        if (res.ok) {
            showToast("Password updated successfully 🎉");
            modal.remove();
        } else showToast(res.error, "error");
    });
}

// -------------------------------
// Dashboard (after login)
// -------------------------------
async function loadDashboard() {
    const res = await fetchJSON(API.me, "GET");
    const dash = document.getElementById("dashboard");
    if (res.ok && dash) {
        const d = res.data;
        document.getElementById("profile-name").textContent = d.student_name;
        document.getElementById("profile-email").textContent = d.email;
        document.getElementById("profile-phone").textContent = d.phone;
        document.getElementById("profile-type").textContent = d.student_type;
        document.getElementById("profile-joined").textContent = d.created_at.split("T")[0];
        document.getElementById("profile-last-login").textContent = d.last_login
            ? d.last_login.split("T")[0]
            : "-";
        dash.classList.remove("hidden");
        window.scrollTo({ top: dash.offsetTop, behavior: "smooth" });
    } else showToast("Please login first", "error");
}

// -------------------------------
// Logout
// -------------------------------
const logoutBtn = document.getElementById("logout-btn");
if (logoutBtn) {
    logoutBtn.addEventListener("click", async () => {
        await fetchJSON(API.logout, "POST");
        showToast("Logged out 👋");
        location.reload();
    });
}
// ========================
// Learn Topics Easily UI
// ========================
const LEARN_API = {
  courses: '/api/courses',
  topics: (courseId) => `/api/topics?course_id=${courseId}`,
  lessons: (topicId) => `/api/lessons?topic_id=${topicId}`,
  mark: '/api/mark-lesson',
  seed: '/api/seed-demo',
  myProgress: '/api/my-progress'
};

function learnModal(content){ 
  const m=document.createElement('div');
  m.className='fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4';
  m.innerHTML = `
    <div class="bg-white rounded-3xl w-full max-w-5xl overflow-hidden">
      <div class="p-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white flex items-center justify-between">
        <h3 class="text-xl font-semibold">Learn Topics Easily</h3>
        <button class="text-2xl leading-none px-2" id="learnClose">&times;</button>
      </div>
      <div class="grid md:grid-cols-[280px,1fr] gap-0">
        <aside id="learnSidebar" class="border-r p-4 space-y-3 max-h-[70vh] overflow-auto"></aside>
        <main id="learnMain" class="p-4 max-h-[70vh] overflow-auto">
          <p class="text-gray-600">Pick a course on the left to begin.</p>
        </main>
      </div>
    </div>`;
  document.body.appendChild(m);
  m.querySelector('#learnClose').onclick=()=>m.remove();
  m.addEventListener('click',e=>{ if(e.target===m) m.remove(); });
  return {root:m, sidebar:m.querySelector('#learnSidebar'), main:m.querySelector('#learnMain')};
}

async function ensureDemoCourses(){
  // Try fetch courses; if empty, seed
  let r = await fetchJSON(LEARN_API.courses, 'GET');
  if (r.ok && r.data.courses.length) return r.data.courses;
  await fetchJSON(LEARN_API.seed, 'POST', {});
  r = await fetchJSON(LEARN_API.courses, 'GET');
  return r.data.courses;
}

async function openLearn(){
  const ui = learnModal();
  const courses = await ensureDemoCourses();

  // Render courses in sidebar
  ui.sidebar.innerHTML = `
    <div class="mb-3">
      <h4 class="font-semibold text-gray-800 mb-2">Courses</h4>
      <div id="courseList" class="space-y-2"></div>
    </div>
    <div id="topicContainer"></div>
  `;
  const courseList = ui.sidebar.querySelector('#courseList');
  courses.forEach(c=>{
    const btn = document.createElement('button');
    btn.className = 'w-full text-left px-3 py-2 rounded-lg hover:bg-purple-50 border';
    btn.innerHTML = `<div class="font-medium">${c.title}</div>
                     <div class="text-xs text-gray-500">${c.topics_count} topics • ${c.lessons_count} lessons</div>`;
    btn.onclick = ()=> loadTopics(c.id, ui);
    courseList.appendChild(btn);
  });
}

async function loadTopics(courseId, ui){
  const r = await fetchJSON(LEARN_API.topics(courseId), 'GET');
  const topics = r.data.topics || [];
  const box = ui.sidebar.querySelector('#topicContainer');
  box.innerHTML = `
    <h4 class="font-semibold text-gray-800 mt-4 mb-2">Topics in ${r.data.course.title}</h4>
    <div id="topicList" class="space-y-2"></div>`;
  const list = box.querySelector('#topicList');
  list.innerHTML = '';
  topics.forEach(t=>{
    const b=document.createElement('button');
    b.className='w-full text-left px-3 py-2 rounded-lg hover:bg-blue-50 border';
    b.textContent = t.title;
    b.onclick = ()=> loadLessons(t.id, ui);
    list.appendChild(b);
  });
  ui.main.innerHTML = `<p class="text-gray-600">Choose a topic to see its lessons.</p>`;
}

async function loadLessons(topicId, ui){
  const r = await fetchJSON(LEARN_API.lessons(topicId), 'GET');
  const lessons = r.data.lessons || [];
  ui.main.innerHTML = `
    <h3 class="text-xl font-semibold mb-3">${r.data.topic.title}</h3>
    <div class="space-y-4" id="lessonList"></div>`;
  const list = ui.main.querySelector('#lessonList');

  lessons.forEach(l=>{
    const card = document.createElement('div');
    card.className='border rounded-xl p-4';
    card.innerHTML = `
      <div class="flex items-start justify-between">
        <div>
          <div class="font-semibold">${l.order}. ${l.title}</div>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-sm ${l.completed?'text-green-600':'text-gray-400'}" id="status-${l.id}">
            ${l.completed ? 'Completed ✔' : 'Not completed'}
          </span>
          <button class="px-3 py-1 rounded-full text-white ${l.completed?'bg-green-500':'bg-purple-600 hover:bg-purple-700'}" id="btn-${l.id}">
            ${l.completed ? 'Done' : 'Mark Complete'}
          </button>
        </div>
      </div>
      <div class="prose max-w-none mt-3">${l.content}</div>
    `;
    list.appendChild(card);

    if (!l.completed){
      card.querySelector(`#btn-${l.id}`).onclick = async ()=>{
        const res = await fetchJSON(LEARN_API.mark, 'POST', { lesson_id: l.id });
        if (res.ok){
          card.querySelector(`#status-${l.id}`).textContent = 'Completed ✔';
          card.querySelector(`#status-${l.id}`).className = 'text-sm text-green-600';
          const btn = card.querySelector(`#btn-${l.id}`);
          btn.textContent = 'Done';
          btn.className = 'px-3 py-1 rounded-full text-white bg-green-500';
        }
      };
    }
  });
}

// Hook the feature card (button) by id
const learnFeature = document.getElementById('feature-learn');
if (learnFeature) {
  learnFeature.addEventListener('click', (e)=>{
    e.preventDefault();
    openLearn();
  });
}
// ========================
// Weekly Progress (last 7 days)
// ========================
const WEEKLY_API = {
  weekly: '/api/progress-weekly',
};

// Tiny helper to draw bars with Tailwind classes
function renderWeeklyBars(days) {
  const max = Math.max(1, ...days.map(d => d.count)); // avoid 0/0
  return `
    <div class="grid grid-cols-7 gap-3 items-end h-40">
      ${days.map(d => {
        const pct = Math.round((d.count / max) * 100);
        return `
          <div class="flex flex-col items-center gap-2">
            <div class="w-6 md:w-8 bg-gradient-to-t from-blue-500 to-purple-600 rounded-md"
                 style="height:${Math.max(6, Math.round(1.2 * pct))}px"
                 title="${d.label} • ${d.count}">
            </div>
            <div class="text-xs text-gray-600">${d.label}</div>
          </div>
        `;
      }).join('')}
    </div>
    <div class="mt-3 text-sm text-gray-600">
      Peak day: <span class="font-medium">${(days.find(d => d.count === Math.max(...days.map(x=>x.count))) || {}).label || '-'}</span>
    </div>
  `;
}

// Re-openable Progress modal with tabs (Overview / Weekly)
function progressTabbedModal() {
  const m = document.createElement('div');
  m.className = 'fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4';
  m.innerHTML = `
    <div class="bg-white rounded-3xl w-full max-w-4xl overflow-hidden">
      <div class="p-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white flex items-center justify-between">
        <div class="flex items-center gap-4">
          <h3 class="text-xl font-semibold">Your Progress</h3>
          <nav class="hidden md:flex items-center gap-2">
            <button id="tabOverview" class="px-3 py-1 rounded-full bg-white/20 hover:bg-white/30">Overview</button>
            <button id="tabWeekly" class="px-3 py-1 rounded-full bg-white/10 hover:bg-white/20">Weekly</button>
          </nav>
        </div>
        <button class="text-2xl leading-none px-2" id="progressClose">&times;</button>
      </div>
      <div class="p-4 max-h-[70vh] overflow-auto" id="progressBody">
        <p class="text-gray-600">Loading…</p>
      </div>
      <div class="md:hidden border-t p-3 flex items-center justify-center gap-3">
        <button id="tabOverviewMobile" class="px-3 py-1 rounded-full bg-gray-100">Overview</button>
        <button id="tabWeeklyMobile" class="px-3 py-1 rounded-full bg-gray-100">Weekly</button>
      </div>
    </div>`;
  document.body.appendChild(m);
  const body = m.querySelector('#progressBody');
  const close = () => m.remove();
  m.querySelector('#progressClose').onclick = close;
  m.addEventListener('click', e => { if (e.target === m) close(); });

  // Tab handlers
  const goOverview = async () => {
    body.innerHTML = '<p class="text-gray-600">Loading…</p>';
    try {
      const res = await fetchJSON('/api/progress-summary', 'GET');
      if (!res.ok) throw new Error(res.error || 'Failed to load progress');
      const d = res.data;
      const per = d.per_course.length
        ? d.per_course.map(c => `
            <div class="border rounded-xl p-3">
              <div class="flex items-center justify-between mb-2">
                <div class="font-medium">${c.title}</div>
                <div class="text-sm text-gray-600">${c.done}/${c.total} (${c.percent}%)</div>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div class="h-2 rounded-full bg-gradient-to-r from-blue-500 to-purple-600" style="width:${c.percent}%;"></div>
              </div>
            </div>`).join('')
        : '<p class="text-gray-600">You are not enrolled in any courses yet.</p>';

      const ach = d.achievements.length
        ? d.achievements.map(a => `<li class="flex items-center gap-2"><span>🏆</span><span>${a}</span></li>`).join('')
        : '<li class="text-gray-500">No achievements yet. Keep learning!</li>';

      body.innerHTML = `
        <div class="grid md:grid-cols-3 gap-4 mb-6">
          <div class="bg-white border rounded-2xl p-4">
            <div class="text-sm text-gray-500">Courses Enrolled</div>
            <div class="text-2xl font-bold text-blue-600">${d.courses_enrolled}</div>
          </div>
          <div class="bg-white border rounded-2xl p-4">
            <div class="text-sm text-gray-500">Lessons Completed</div>
            <div class="text-2xl font-bold text-green-600">${d.lessons_completed}</div>
          </div>
          <div class="bg-white border rounded-2xl p-4">
            <div class="text-sm text-gray-500">Current Streak</div>
            <div class="text-2xl font-bold text-purple-600">${d.streak_days} days</div>
          </div>
        </div>

        <h4 class="font-semibold text-gray-800 mb-2">Per-Course Progress</h4>
        <div class="space-y-3 mb-6">${per}</div>

        <h4 class="font-semibold text-gray-800 mb-2">Achievements</h4>
        <ul class="space-y-1">${ach}</ul>
      `;
    } catch (e) {
      body.innerHTML = `<p class="text-red-600">Error: ${e.message}</p>`;
    }
    selectTab('overview');
  };

  const goWeekly = async () => {
    body.innerHTML = '<p class="text-gray-600">Loading weekly…</p>';
    try {
      const res = await fetchJSON(WEEKLY_API.weekly, 'GET');
      if (!res.ok) throw new Error(res.error || 'Failed to load weekly progress');
      const d = res.data;
      body.innerHTML = `
        <div class="mb-4 grid md:grid-cols-3 gap-4">
          <div class="bg-white border rounded-2xl p-4">
            <div class="text-sm text-gray-500">Total this week</div>
            <div class="text-2xl font-bold text-green-600">${d.total_week}</div>
          </div>
          <div class="bg-white border rounded-2xl p-4 md:col-span-2">
            <div class="text-sm text-gray-500 mb-2">Completions by day (last 7 days)</div>
            ${renderWeeklyBars(d.days)}
          </div>
        </div>
      `;
    } catch (e) {
      body.innerHTML = `<p class="text-red-600">Error: ${e.message}</p>`;
    }
    selectTab('weekly');
  };

  function selectTab(which) {
    const ov = m.querySelector('#tabOverview');
    const wk = m.querySelector('#tabWeekly');
    const ovM = m.querySelector('#tabOverviewMobile');
    const wkM = m.querySelector('#tabWeeklyMobile');

    [[ov, which==='overview'], [wk, which==='weekly'], [ovM, which==='overview'], [wkM, which==='weekly']].forEach(([el, active])=>{
      if (!el) return;
      el.className = 'px-3 py-1 rounded-full ' + (active ? 'bg-white/80 text-gray-800' : 'bg-white/20 text-white');
      if (el.id.endsWith('Mobile')) {
        el.className = 'px-3 py-1 rounded-full ' + (active ? 'bg-purple-100 text-purple-700' : 'bg-gray-100 text-gray-700');
      }
    });
  }

  // Attach tab events
  const ovEls = [m.querySelector('#tabOverview'), m.querySelector('#tabOverviewMobile')].filter(Boolean);
  const wkEls = [m.querySelector('#tabWeekly'), m.querySelector('#tabWeeklyMobile')].filter(Boolean);
  ovEls.forEach(btn => btn.addEventListener('click', goOverview));
  wkEls.forEach(btn => btn.addEventListener('click', goWeekly));

  // Default: Overview first, then user can switch to Weekly
  goOverview();
  return m;
}

// Replace your existing openProgress binding to use the tabbed modal:
const trackBtn2 = document.getElementById('feature-track');
if (trackBtn2) {
  trackBtn2.addEventListener('click', (e) => {
    e.preventDefault();
    progressTabbedModal();
  });
}
// ========================
// Interactive Quizzes (Adaptive to Weekly Progress)
// ========================
const QUIZ_API = {
  generate: (count=6) => `/api/quiz/generate?count=${count}`,
  submit: '/api/quiz/submit',
  history: '/api/quiz/history',
  seed: '/api/quiz/seed',
};

function quizModalSkeleton() {
  const m = document.createElement('div');
  m.className = 'fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4';
  m.innerHTML = `
    <div class="bg-white rounded-3xl w-full max-w-3xl overflow-hidden">
      <div class="p-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white flex items-center justify-between">
        <h3 class="text-xl font-semibold">Interactive Quiz 🎮</h3>
        <button class="text-2xl leading-none px-2" id="quizClose">&times;</button>
      </div>
      <div id="quizBody" class="p-4 max-h-[70vh] overflow-auto">
        <p class="text-gray-600">Loading quiz…</p>
      </div>
    </div>`;
  document.body.appendChild(m);
  m.querySelector('#quizClose').onclick = () => m.remove();
  m.addEventListener('click', e => { if (e.target === m) m.remove(); });
  return {root: m, body: m.querySelector('#quizBody')};
}

async function ensureQuizSeed() {
  // If no questions, seed quickly
  try {
    const r = await fetchJSON(QUIZ_API.history, 'GET');
    return; // history endpoint works, assume DB seeded or fine
  } catch {
    await fetchJSON(QUIZ_API.seed, 'POST', {});
  }
}

async function openQuiz(count = 6) {
  await ensureQuizSeed();
  const ui = quizModalSkeleton();
  try {
    const res = await fetchJSON(QUIZ_API.generate(count), 'GET');
    if (!res.ok) throw new Error(res.error || 'Failed to generate quiz');
    const questions = res.data.questions || [];
    if (!questions.length) {
      ui.body.innerHTML = `<p class="text-gray-600">No quiz questions available yet.</p>`;
      return;
    }

    // Render quiz
    ui.body.innerHTML = `
      <form id="quizForm" class="space-y-5">
        ${questions.map((q, idx) => `
          <div class="border rounded-xl p-4">
            <div class="text-sm text-gray-500 mb-1">${q.topic} • ${q.difficulty.toUpperCase()}</div>
            <div class="font-medium mb-3">${idx+1}. ${q.text}</div>
            <div class="space-y-2">
              ${q.choices.map(c => `
                <label class="flex items-center gap-2">
                  <input type="radio" name="q_${q.id}" value="${c.id}" class="accent-purple-600">
                  <span>${c.text}</span>
                </label>
              `).join('')}
            </div>
          </div>
        `).join('')}

        <div class="flex items-center justify-between">
          <button type="button" id="quizCancel" class="px-4 py-2 rounded-lg border">Cancel</button>
          <button type="submit" class="px-5 py-2 rounded-lg text-white bg-gradient-to-r from-purple-600 to-pink-600">Submit Quiz</button>
        </div>
      </form>
    `;

    ui.body.querySelector('#quizCancel').onclick = () => ui.root.remove();

    ui.body.querySelector('#quizForm').addEventListener('submit', async (e) => {
      e.preventDefault();
      const form = e.currentTarget;
      const formData = new FormData(form);
      const answers = questions.map(q => {
        const choice = formData.get(`q_${q.id}`);
        return { question_id: q.id, choice_id: choice ? parseInt(choice) : null };
      });
      const submitRes = await fetchJSON(QUIZ_API.submit, 'POST', { answers, source: 'weekly' });
      if (!submitRes.ok) {
        ui.body.innerHTML = `<p class="text-red-600">Error: ${submitRes.error}</p>`;
        return;
      }
      const d = submitRes.data;
      ui.body.innerHTML = `
        <div class="mb-4">
          <h4 class="text-xl font-semibold">Your Score: ${d.score}/${d.total}</h4>
          <p class="text-gray-600">Review answers below.</p>
        </div>
        <div class="space-y-4">
          ${d.feedback.map((f,i)=>`
            <div class="border rounded-xl p-4 ${f.correct ? 'border-green-300' : 'border-red-300'}">
              <div class="font-medium mb-2">${i+1}. ${f.question}</div>
              <div class="text-sm"><span class="font-semibold">Your answer:</span> ${f.your_answer ?? '<em>None</em>'}</div>
              <div class="text-sm"><span class="font-semibold">Correct:</span> ${f.correct_answer ?? '-'}</div>
              ${f.explanation ? `<div class="text-sm text-gray-600 mt-2">${f.explanation}</div>` : ''}
            </div>
          `).join('')}
        </div>
        <div class="mt-5 flex justify-end">
          <button id="quizCloseBtn" class="px-5 py-2 rounded-lg border">Close</button>
        </div>
      `;
      ui.body.querySelector('#quizCloseBtn').onclick = () => ui.root.remove();
    });

  } catch (e) {
    ui.body.innerHTML = `<p class="text-red-600">Error: ${e.message}</p>`;
  }
}

// Hook feature 3 card
const quizBtn = document.getElementById('feature-quiz');
if (quizBtn) {
  quizBtn.addEventListener('click', (e)=>{
    e.preventDefault();
    openQuiz(6); // 6 questions mixed (2 easy,2 med,2 hard)
  });
}
// ========================
// AI Assistance (chat)
// ========================
const AI_API = {
  start: '/api/ai/start',
  message: '/api/ai/message',
};

function aiModal() {
  const m = document.createElement('div');
  m.className = 'fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4';
  m.innerHTML = `
    <div class="bg-white rounded-3xl w-full max-w-2xl overflow-hidden">
      <div class="p-4 bg-gradient-to-r from-orange-500 to-pink-600 text-white flex items-center justify-between">
        <h3 class="text-xl font-semibold">Smart AI Assistance 🤖</h3>
        <button id="aiClose" class="text-2xl leading-none px-2">&times;</button>
      </div>
      <div class="p-4 grid gap-3">
        <div id="aiChat" class="border rounded-2xl p-3 h-[50vh] overflow-auto bg-gray-50 space-y-3">
          <div class="text-sm text-gray-600">Say things like:
            <span class="inline-block bg-white border rounded-full px-2 py-0.5 mx-1">next lesson</span>
            <span class="inline-block bg-white border rounded-full px-2 py-0.5 mx-1">explain arrays</span>
            <span class="inline-block bg-white border rounded-full px-2 py-0.5 mx-1">weekly quiz</span>
            <span class="inline-block bg-white border rounded-full px-2 py-0.5 mx-1">my progress</span>
          </div>
        </div>
        <form id="aiForm" class="flex gap-2">
          <input id="aiInput" class="flex-1 border rounded-xl px-3 py-2" placeholder="Ask me anything about your learning…">
          <button class="px-4 py-2 rounded-xl text-white bg-gradient-to-r from-orange-500 to-pink-600">Send</button>
        </form>
      </div>
    </div>`;
  document.body.appendChild(m);
  const chat = m.querySelector('#aiChat');
  const input = m.querySelector('#aiInput');

  const addMsg = (who, text) => {
    const bubble = document.createElement('div');
    const base = 'max-w-[85%] px-3 py-2 rounded-2xl';
    if (who === 'user') {
      bubble.className = `${base} bg-purple-600 text-white ml-auto`;
    } else {
      bubble.className = `${base} bg-white border`;
    }
    bubble.innerHTML = text.replace(/\n/g, '<br>');
    chat.appendChild(bubble);
    chat.scrollTop = chat.scrollHeight;
  };

  let threadId = null;

  // Start thread
  fetchJSON(AI_API.start, 'POST', {}).then(res => {
    if (res.ok) threadId = res.data.thread_id;
  });

  // Send
  m.querySelector('#aiForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = input.value.trim();
    if (!text || !threadId) return;
    addMsg('user', text);
    input.value = '';
    const r = await fetchJSON(AI_API.message, 'POST', { thread_id: threadId, message: text });
    if (r.ok) {
      addMsg('assistant', r.data.reply);
    } else {
      addMsg('assistant', `Error: ${r.error || 'Something went wrong'}`);
    }
  });

  // Close
  m.querySelector('#aiClose').onclick = () => m.remove();
  m.addEventListener('click', e => { if (e.target === m) m.remove(); });

  return m;
}

// Hook the feature 4 card/button
const aiBtn = document.getElementById('feature-ai');
if (aiBtn) {
  aiBtn.addEventListener('click', (e) => {
    e.preventDefault();
    aiModal();
  });
}
// ========================
// Study Hub (Exams → Subjects → Resources + Weightages)
// ========================
const HUB_API = {
  exams: '/api/exams',
  subjects: (slug) => `/api/subjects?exam_slug=${encodeURIComponent(slug)}`,
  resources: (subjectId, kinds='youtube,notes,paper') => `/api/resources?subject_id=${subjectId}&kinds=${kinds}`,
  weights: (slug) => `/api/weightages?exam_slug=${encodeURIComponent(slug)}`,
  seed: '/api/studyhub-seed',
};

// Fallback if fetchJSON wasn't defined earlier
async function fetchJSON(url, method='GET', body) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } };
  if (body) opts.body = JSON.stringify(body);
  const r = await fetch(url, opts);
  const data = await r.json().catch(() => ({}));
  return r.ok ? { ok: true, data } : { ok: false, error: data?.message || r.statusText };
}

function weightBar(pct) {
  return `
    <div class="w-full bg-gray-200 rounded-full h-2">
      <div class="h-2 rounded-full bg-gradient-to-r from-blue-500 to-purple-600" style="width:${Math.min(100, Math.max(0, pct))}%"></div>
    </div>`;
}

async function hubLoadExams() {
  const examSel = document.getElementById('hub-exam');
  if (!examSel) return;

  const res = await fetchJSON(HUB_API.exams, 'GET');
  if (!res.ok) return;

  examSel.innerHTML = res.data.exams.map(e => `<option value="${e.slug}">${e.name}${e.grade ? ' — ' + e.grade : ''}</option>`).join('');

  // If nothing, prompt to seed
  if (!res.data.exams.length) {
    examSel.innerHTML = `<option value="">No exams found. Click "Load demo data".</option>`;
  } else {
    hubOnExamChange();
  }
}

async function hubOnExamChange() {
  const examSel = document.getElementById('hub-exam');
  const slug = examSel.value;
  if (!slug) return;

  // load subjects
  const subWrap = document.getElementById('hub-subjects');
  subWrap.innerHTML = 'Loading subjects…';
  const subs = await fetchJSON(HUB_API.subjects(slug), 'GET');
  if (!subs.ok) { subWrap.innerHTML = 'Failed to load subjects.'; return; }

  subWrap.innerHTML = '';
  subs.data.subjects.forEach(s => {
    const b = document.createElement('button');
    b.className = 'px-3 py-1 rounded-full border hover:bg-purple-50';
    b.textContent = s.name;
    b.dataset.id = s.id;
    b.addEventListener('click', () => hubLoadResourcesForSubject(s.id, b));
    subWrap.appendChild(b);
  });

  // load weightages
  const wres = await fetchJSON(HUB_API.weights(slug), 'GET');
  const wg = document.getElementById('hub-weights');
  if (wres.ok && wres.data.weights.length) {
    wg.innerHTML = wres.data.weights.map(w => `
      <div class="border rounded-xl p-3">
        <div class="flex items-center justify-between mb-2">
          <div class="font-medium">${w.subject}</div>
          <div class="text-sm text-gray-600">${w.weight_percent}%</div>
        </div>
        ${weightBar(w.weight_percent)}
      </div>`).join('');
  } else {
    wg.innerHTML = '<p class="text-gray-600">No weightage data yet.</p>';
  }

  // reset resource columns
  document.getElementById('hub-youtube').innerHTML = '<p class="text-gray-500">Pick a subject above.</p>';
  document.getElementById('hub-notes').innerHTML = '<p class="text-gray-500">Pick a subject above.</p>';
  document.getElementById('hub-papers').innerHTML = '<p class="text-gray-500">Pick a subject above.</p>';
}

async function hubLoadResourcesForSubject(subjectId, btnEl) {
  // visual active state
  [...document.querySelectorAll('#hub-subjects button')].forEach(b => b.classList.remove('bg-purple-100', 'border-purple-400'));
  btnEl.classList.add('bg-purple-100', 'border-purple-400');

  const colYt = document.getElementById('hub-youtube');
  const colNt = document.getElementById('hub-notes');
  const colPp = document.getElementById('hub-papers');
  colYt.innerHTML = 'Loading…'; colNt.innerHTML = 'Loading…'; colPp.innerHTML = 'Loading…';

  const res = await fetchJSON(HUB_API.resources(subjectId), 'GET');
  if (!res.ok) {
    colYt.innerHTML = colNt.innerHTML = colPp.innerHTML = '<p class="text-red-600">Failed to load resources.</p>';
    return;
  }
  const items = res.data.resources || [];

  const yt = items.filter(i => i.kind === 'youtube');
  const nt = items.filter(i => i.kind === 'notes');
  const pp = items.filter(i => i.kind === 'paper');

  colYt.innerHTML = yt.length ? yt.map(i => `
    <a href="${i.url}" target="_blank" class="block border rounded-lg p-2 hover:bg-blue-50">
      <div class="font-medium">${i.title}</div>
      <div class="text-xs text-gray-500">${i.source || 'YouTube'}</div>
    </a>`).join('') : '<p class="text-gray-500">No YouTube links yet.</p>';

  colNt.innerHTML = nt.length ? nt.map(i => `
    <a href="${i.url}" target="_blank" class="block border rounded-lg p-2 hover:bg-green-50">
      <div class="font-medium">${i.title}</div>
      <div class="text-xs text-gray-500">${i.source || 'Notes'}</div>
    </a>`).join('') : '<p class="text-gray-500">No notes yet.</p>';

  colPp.innerHTML = pp.length ? pp.map(i => `
    <div class="border rounded-lg p-2">
      <div class="flex items-center justify-between">
        <div>
          <div class="font-medium">${i.title}${i.year ? ' ('+i.year+')' : ''}</div>
          <div class="text-xs text-gray-500">${i.source || 'Past paper'}</div>
        </div>
        <div class="flex gap-2">
          <a href="${i.url}" target="_blank" class="text-sm underline">Paper</a>
          ${i.solution_url ? `<a href="${i.solution_url}" target="_blank" class="text-sm underline">Solution</a>` : ''}
        </div>
      </div>
    </div>`).join('') : '<p class="text-gray-500">No past papers yet.</p>';
}

// seed button
const hubSeedBtn = document.getElementById('hub-seed');
if (hubSeedBtn) {
  hubSeedBtn.addEventListener('click', async () => {
    const r = await fetchJSON(HUB_API.seed, 'POST', {});
    if (r.ok) {
      // reload exams
      hubLoadExams();
    }
  });
}

// initial load + change handler
const hubExamSel = document.getElementById('hub-exam');
if (hubExamSel) {
  hubExamSel.addEventListener('change', hubOnExamChange);
  hubLoadExams();
}

