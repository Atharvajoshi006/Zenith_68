// ====== KEEP YOUR EXISTING MAPPINGS ======
// Exams and subjects mapping
const examsByGrade = {
  8: ["School Finals", "NSTSE"],
  10: ["Board Exams", "NTSE"],
  12: ["NEET", "CET", "JEE Advanced"]
};

const subjectsByExam = {
  "School Finals": ["Maths", "Science"],
  "NSTSE": ["Maths", "Reasoning"],
  "Board Exams": ["Maths", "Science"],
  "NTSE": ["Maths", "Reasoning"],
  "NEET": ["Biology", "Chemistry"],
  "JEE Advanced": ["Physics", "Maths"]
};

// Resources by State, Grade & Exam
const resourcesByState = {
  karnataka: {
    8: { "School Finals": ["Maths (Kannada)", "Science (Kannada)"], "NSTSE": ["Maths (Kannada)", "Reasoning (Kannada)"] },
    10: { "Board Exams": ["Maths (Kannada)", "Science (Kannada)"], "NTSE": ["Maths (Kannada)", "Reasoning (Kannada)"] }
  },
  maharashtra: {
    8: { "School Finals": ["Maths (Marathi)", "Science (Marathi)"], "NSTSE": ["Maths (Marathi)", "Reasoning (Marathi)"] },
    10: { "Board Exams": ["Maths (Marathi)", "Science (Marathi)"], "NTSE": ["Maths (Marathi)", "Reasoning (Marathi)"] }
  },
  tamilnadu: {
    8: { "School Finals": ["Maths (Tamil)", "Science (Tamil)"], "NSTSE": ["Maths (Tamil)", "Reasoning (Tamil)"] },
    10: { "Board Exams": ["Maths (Tamil)", "Science (Tamil)"], "NTSE": ["Maths (Tamil)", "Reasoning (Tamil)"] }
  },
  telangana: {
    8: { "School Finals": ["Maths (Telugu)", "Science (Telugu)"], "NSTSE": ["Maths (Telugu)", "Reasoning (Telugu)"] },
    10: { "Board Exams": ["Maths (Telugu)", "Science (Telugu)"], "NTSE": ["Maths (Telugu)", "Reasoning (Telugu)"] }
  }
};

// ====== DOM ======
const gradeSelect = document.getElementById("gradeSelect");
const examSelect = document.getElementById("examSelect");
const subjectSelect = document.getElementById("subjectSelect");
const examSection = document.getElementById("examSection");
const subjectSection = document.getElementById("subjectSection");
const continueBtn = document.getElementById("continueBtn");
const stateSelect = document.getElementById("stateSelect");

const user = new URLSearchParams(window.location.search).get("user");
const welcome = document.getElementById("welcomeMsg");
if (welcome) welcome.textContent = `Welcome, ${user || "Student"}!`;

// ====== Helpers ======
const backendSubjectsCache = new Map(); // gradeId -> [{id, name}, ...]

function normalizeBaseSubject(displayName) {
  // "Maths (Kannada)" -> "maths"
  return displayName.split("(")[0].trim().toLowerCase();
}

function byNameMap(list) {
  const m = new Map();
  list.forEach(s => m.set(String(s.name).trim().toLowerCase(), s));
  return m;
}

async function getBackendSubjectsForGrade(gradeId) {
  if (!backendSubjectsCache.has(gradeId)) {
    const subs = await API.listSubjects(gradeId);
    backendSubjectsCache.set(gradeId, subs || []);
  }
  return backendSubjectsCache.get(gradeId);
}

// ====== Initial load: Grades from backend ======
document.addEventListener("DOMContentLoaded", async () => {
  try {
    const grades = await API.listGrades();
    // Populate gradeSelect from backend
    gradeSelect.innerHTML = `<option value="">--Select Grade--</option>` +
      grades.map(g => `<option value="${g.id}">${g.name}</option>`).join("");

    // If you want default selection, pick the first grade:
    if (grades.length) {
      gradeSelect.value = grades[0].id;
      updateForm(); // populate exams for that grade
    }
  } catch (e) {
    console.error(e);
    alert("Failed to load grades. Is the backend running at http://127.0.0.1:8000?");
  }
});

// ====== Events ======
stateSelect.addEventListener("change", updateForm);
gradeSelect.addEventListener("change", updateForm);
examSelect.addEventListener("change", updateSubjects);
subjectSelect.addEventListener("change", () => {
  // Only allow continue if this option maps to a valid backend subject id
  const opt = subjectSelect.options[subjectSelect.selectedIndex];
  continueBtn.style.display = opt && opt.dataset && opt.dataset.subjectId ? "inline-block" : "none";
});

// ====== Update exams based on Grade and State (state only affects the labels you show) ======
function updateForm() {
  const state = stateSelect.value;
  const gradeId = gradeSelect.value; // backend grade id

  // Reset UI
  examSelect.innerHTML = "<option value=''>--Select Exam--</option>";
  subjectSelect.innerHTML = "<option value=''>--Select Subject--</option>";
  examSection.style.display = "none";
  subjectSection.style.display = "none";
  continueBtn.style.display = "none";

  // We pick exam list purely from your examsByGrade, but key by "grade label".
  // If your backend grade "name" is like "8", "10", etc., you can store a mapping.
  // Simpler: derive 'grade label' from a handful of common names:
  // Try to find a number in the grade's text option to map to examsByGrade.
  const gradeOption = gradeSelect.options[gradeSelect.selectedIndex];
  const gradeLabel = gradeOption ? (gradeOption.textContent.match(/\d+/)?.[0] || "") : "";
  const examList = examsByGrade[gradeLabel];

  if (state && gradeId && examList && examList.length) {
    examList.forEach(exam => {
      const opt = document.createElement("option");
      opt.value = exam;
      opt.textContent = exam;
      examSelect.appendChild(opt);
    });
    examSection.style.display = "block";
  }
}

// ====== Update subjects for State + Grade + Exam, but map each display subject to backend subject id ======
async function updateSubjects() {
  const state = stateSelect.value;
  const gradeId = gradeSelect.value;      // backend grade id
  const exam = examSelect.value;

  subjectSelect.innerHTML = "<option value=''>--Select Subject--</option>";
  continueBtn.style.display = "none";
  subjectSection.style.display = "none";

  if (!state || !gradeId || !exam) return;

  // Your display subjects (localized labels)
  const displaySubjects = resourcesByState[state]?.[extractGradeLabel()]?.[exam] || [];

  // Pull subjects from backend for this grade (to find the subject IDs)
  let backendSubjects = [];
  try {
    backendSubjects = await getBackendSubjectsForGrade(gradeId);
  } catch (e) {
    console.error(e);
    alert("Could not load subjects from backend.");
    return;
  }

  const backendByName = byNameMap(backendSubjects); // lowercased name -> subject obj

  displaySubjects.forEach(sub => {
    const opt = document.createElement("option");
    opt.value = sub; // keep your label
    opt.textContent = sub;

    // Try to map "Maths (Kannada)" -> backend subject "Maths"
    const base = normalizeBaseSubject(sub);
    const match = backendByName.get(base);

    if (match) {
      opt.dataset.subjectId = match.id; // this is what we’ll send to resource.html
      opt.title = `Maps to backend subject: ${match.name}`;
    } else {
      // If not found in backend, keep it selectable but mark as missing
      opt.disabled = true;
      opt.textContent = `${sub} (add in backend)`;
      opt.title = "This subject name doesn't exist in backend yet.";
    }

    subjectSelect.appendChild(opt);
  });

  if (displaySubjects.length > 0) subjectSection.style.display = "block";
}

function extractGradeLabel() {
  // Pull "8", "10", "12" from the visible grade option text (e.g., "Grade 8")
  const gradeOption = gradeSelect.options[gradeSelect.selectedIndex];
  return gradeOption ? (gradeOption.textContent.match(/\d+/)?.[0] || "") : "";
}

// ====== Continue: go to resource.html with the BACKEND subject id ======
continueBtn.addEventListener("click", () => {
  const state = stateSelect.value;
  const exam = examSelect.value;
  const gradeLabel = extractGradeLabel(); // for your own query string

  const opt = subjectSelect.options[subjectSelect.selectedIndex];
  if (!opt || !opt.dataset.subjectId) {
    alert("This subject isn’t available in the backend yet. Add it in Django admin.");
    return;
  }

  const subjectId = opt.dataset.subjectId; // backend subject id
  const subjectDisplay = opt.value;        // your display text (kept for info)

  // Redirect with subjectId (backend) so resource.html can call /api/topics/?subject=<id>
  window.location.href =
    `./resource.html?state=${encodeURIComponent(state)}` +
    `&grade=${encodeURIComponent(gradeLabel)}` +
    `&exam=${encodeURIComponent(exam)}` +
    `&subject=${encodeURIComponent(subjectDisplay)}` +
    `&subject_id=${encodeURIComponent(subjectId)}`;
});

