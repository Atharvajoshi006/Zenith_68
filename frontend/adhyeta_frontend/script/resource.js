// DOM Elements
const pageHeading = document.getElementById("pageHeading");
const resourceGrid = document.getElementById("resourceGrid");
const backBtn = document.getElementById("backBtn");

// Get query params from previous page
const urlParams = new URLSearchParams(window.location.search);
const state = urlParams.get("state");
const grade = urlParams.get("grade");
const exam = urlParams.get("exam");
const subject = urlParams.get("subject");

// Back button functionality
backBtn.addEventListener("click", () => {
  window.history.back();
});

// Mocked resources (can be replaced with API or database later)
const resources = {
  karnataka: {
    8: {
      "School Finals": {
        "Maths (Kannada)": [
          { title: "Kannada Maths Notes", type: "PDF", link: "#" },
          { title: "Math Practice Videos", type: "Video", link: "#" }
        ],
        "Science (Kannada)": [
          { title: "Science Workbook", type: "PDF", link: "#" },
          { title: "Experiments Video", type: "Video", link: "#" }
        ]
      },
      "NSTSE": {
        "Maths (Kannada)": [
          { title: "NSTSE Maths Guide", type: "PDF", link: "#" }
        ]
      }
    },
    10: {
      "Board Exams": {
        "Maths (Kannada)": [
          { title: "Grade 10 Maths Notes", type: "PDF", link: "#" }
        ]
      }
    }
  },
  maharashtra: {
    8: {
      "School Finals": {
        "Maths (Marathi)": [
          { title: "Maths Notes (Marathi)", type: "PDF", link: "#" }
        ]
      }
    }
  }
  // Add other states/grades/subjects as needed
};

// Humanized heading
pageHeading.textContent = `Resources for ${subject || ""} | ${exam || ""} | Grade ${grade || ""} | ${state || ""}`;

// Fetch resources based on query
function displayResources() {
  resourceGrid.innerHTML = "";

  if (!state || !grade || !exam || !subject) {
    resourceGrid.innerHTML = "<p>Please select a valid State, Grade, Exam, and Subject from the previous page.</p>";
    return;
  }

  const stateData = resources[state];
  if (!stateData) return;

  const gradeData = stateData[grade];
  if (!gradeData) return;

  const examData = gradeData[exam];
  if (!examData) return;

  const subjectResources = examData[subject];
  if (!subjectResources || subjectResources.length === 0) {
    resourceGrid.innerHTML = "<p>No resources available for this selection.</p>";
    return;
  }

  // Render each resource card
  subjectResources.forEach(res => {
    const card = document.createElement("div");
    card.className = "resource-card fade-in";
    card.innerHTML = `
      <h3>${res.title}</h3>
      <p>Type: ${res.type}</p>
      <a href="${res.link}" target="_blank">View Resource</a>
    `;
    resourceGrid.appendChild(card);
  });
}

// Initialize
displayResources();
