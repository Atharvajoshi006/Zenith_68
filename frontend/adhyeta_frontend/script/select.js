// Exams and subjects mapping
const examsByGrade = {
  8: ["School Finals", "NSTSE"],
  10: ["Board Exams", "NTSE"],
  12: ["NEET","CET","JEE Advanced"]
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

// DOM elements
const gradeSelect = document.getElementById("gradeSelect");
const examSelect = document.getElementById("examSelect");
const subjectSelect = document.getElementById("subjectSelect");
const examSection = document.getElementById("examSection");
const subjectSection = document.getElementById("subjectSection");
const continueBtn = document.getElementById("continueBtn");
const stateSelect = document.getElementById("stateSelect");

const user = new URLSearchParams(window.location.search).get("user");
document.getElementById("welcomeMsg").textContent = `Welcome, ${user || "Student"}!`;

// Event listeners
stateSelect.addEventListener("change", updateForm);
gradeSelect.addEventListener("change", updateForm);
examSelect.addEventListener("change", updateSubjects);
subjectSelect.addEventListener("change", () => {
  continueBtn.style.display = subjectSelect.value ? "inline-block" : "none";
});

// Update exams based on Grade and State
function updateForm() {
  const state = stateSelect.value;
  const grade = gradeSelect.value;

  // Reset exam and subject sections
  examSelect.innerHTML = "<option value=''>--Select Exam--</option>";
  subjectSelect.innerHTML = "<option value=''>--Select Subject--</option>";
  examSection.style.display = "none";
  subjectSection.style.display = "none";
  continueBtn.style.display = "none";

  if (state && grade && examsByGrade[grade]) {
    examsByGrade[grade].forEach(exam => {
      const opt = document.createElement("option");
      opt.value = exam;
      opt.textContent = exam;
      examSelect.appendChild(opt);
    });
    examSection.style.display = "block";
  }
}

// Update subjects based on State + Grade + Exam
function updateSubjects() {
  const state = stateSelect.value;
  const grade = gradeSelect.value;
  const exam = examSelect.value;

  subjectSelect.innerHTML = "<option value=''>--Select Subject--</option>";
  continueBtn.style.display = "none";

  if (state && grade && exam) {
    const subjects = resourcesByState[state]?.[grade]?.[exam] || [];
    subjects.forEach(sub => {
      const opt = document.createElement("option");
      opt.value = sub;
      opt.textContent = sub;
      subjectSelect.appendChild(opt);
    });
    if (subjects.length > 0) subjectSection.style.display = "block";
  }
}

// Continue button redirects with query params
continueBtn.addEventListener("click", () => {
  const state = stateSelect.value;
  const grade = gradeSelect.value;
  const exam = examSelect.value;
  const subject = subjectSelect.value;
  window.location.href = `./resource.html?state=${state}&grade=${grade}&exam=${exam}&subject=${subject}`;
});
