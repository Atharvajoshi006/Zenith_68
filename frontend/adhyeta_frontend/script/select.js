const examsByGrade = {
  8: ["School Finals", "NSTSE"],
  10: ["Board Exams", "NTSE"],
  12: ["NEET", "JEE Advanced"]
};

const subjectsByExam = {
  "School Finals": ["Maths", "Science"],
  "NSTSE": ["Maths", "Reasoning"],
  "Board Exams": ["Maths", "Science"],
  "NTSE": ["Maths", "Reasoning"],
  "NEET": ["Biology", "Chemistry"],
  "JEE Advanced": ["Physics", "Maths"]
};

const gradeSelect = document.getElementById("gradeSelect");
const examSelect = document.getElementById("examSelect");
const subjectSelect = document.getElementById("subjectSelect");
const examSection = document.getElementById("examSection");
const subjectSection = document.getElementById("subjectSection");
const continueBtn = document.getElementById("continueBtn");

const user = new URLSearchParams(window.location.search).get("user");
document.getElementById("welcomeMsg").textContent = `Welcome, ${user || "Student"}!`;

gradeSelect.addEventListener("change", () => {
  const selectedGrade = gradeSelect.value;
  examSelect.innerHTML = "<option value=''>--Select Exam--</option>";

  if (selectedGrade) {
    examsByGrade[selectedGrade].forEach(exam => {
      const opt = document.createElement("option");
      opt.value = exam;
      opt.textContent = exam;
      examSelect.appendChild(opt);
    });
    examSection.style.display = "block";
  } else {
    examSection.style.display = "none";
    subjectSection.style.display = "none";
    continueBtn.style.display = "none";
  }
});

examSelect.addEventListener("change", () => {
  const selectedExam = examSelect.value;
  subjectSelect.innerHTML = "<option value=''>--Select Subject--</option>";

  if (selectedExam) {
    subjectsByExam[selectedExam].forEach(sub => {
      const opt = document.createElement("option");
      opt.value = sub;
      opt.textContent = sub;
      subjectSelect.appendChild(opt);
    });
    subjectSection.style.display = "block";
  } else {
    subjectSection.style.display = "none";
    continueBtn.style.display = "none";
  }
});

subjectSelect.addEventListener("change", () => {
  continueBtn.style.display = subjectSelect.value ? "inline-block" : "none";
});

continueBtn.addEventListener("click", () => {
  const grade = gradeSelect.value;
  const exam = examSelect.value;
  const subject = subjectSelect.value;
  window.location.href = `./resource.html?grade=${grade}&exam=${exam}&subject=${subject}`;

});
