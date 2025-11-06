/* ============================================================
   ADHYETA – Online Resource Loader
   Dynamically displays study materials based on grade, exam,
   and subject using online resource links.
============================================================ */

// --- Capture parameters from URL ---
const params = new URLSearchParams(window.location.search);
const grade = params.get("grade");
const exam = params.get("exam");
const subject = params.get("subject");

// --- Update heading dynamically ---
const heading = document.getElementById("pageHeading");
heading.textContent = `Resources for ${subject} – ${exam} (Grade ${grade})`;

// --- Back Button ---
document.getElementById("backBtn").addEventListener("click", () => {
  window.history.back();
});

// --- Define Online Resources (EDIT HERE) ---
const resourceBank = {
  "Grade 8": {
    "School Finals": {
      Maths: [
        { name: "Algebra Basics", type: "YouTube", link: "https://www.youtube.com/watch?v=6xvW4b9QmWw" },
        { name: "Geometry Concepts", type: "YouTube", link: "https://www.youtube.com/watch?v=KQ_q5XoQfVY" }
      ],
      Science: [
        { name: "Science Revision Crash Course", type: "YouTube", link: "https://www.youtube.com/watch?v=p6zS2H5ZKkA" },
        { name: "Science Quiz Practice", type: "Website", link: "https://quizizz.com/admin/quiz/5f87ddee4be582001f4cbb28" }
      ]
    },
    "NSTSE": {
      Maths: [
        { name: "NSTSE Maths Practice", type: "YouTube", link: "https://www.youtube.com/watch?v=w12Dxl0FrfE" },
        { name: "NSTSE Sample Paper", type: "Website", link: "https://www.unifiedcouncil.com/nstse/study-material" }
      ],
      Reasoning: [
        { name: "Reasoning Practice Set", type: "Website", link: "https://www.indiabix.com/logical-reasoning/questions-and-answers/" }
      ]
    }
  },

  "Grade 10": {
    "Board Exams": {
      Maths: [
        { name: "Quadratic Equations – Crash Course", type: "YouTube", link: "https://www.youtube.com/watch?v=Qe6JrZL2x1E" },
        { name: "Sample Papers 2024", type: "Website", link: "https://cbseacademic.nic.in/SQP_CLASSX_2024.html" }
      ],
      Science: [
        { name: "Physics Full Chapter", type: "YouTube", link: "https://www.youtube.com/watch?v=t2fUxfJ0IY4" },
        { name: "Chemistry Notes", type: "Website", link: "https://byjus.com/cbse-notes/class-10-chemistry-notes/" }
      ]
    },
    "NTSE": {
      Maths: [
        { name: "NTSE Important Topics", type: "YouTube", link: "https://www.youtube.com/watch?v=FrzMuN9hOq0" },
        { name: "NTSE Free Mock Test", type: "Website", link: "https://ntseguru.in/" }
      ]
    }
  },

  "Grade 12": {
    "NEET": {
      Biology: [
        { name: "NEET Biology 2025 Revision", type: "YouTube", link: "https://youtube.com/playlist?list=PLVdpygJig6T3uInasUeUm4NxJc6yImr6w&si=VIxUyOB_dVnDDwIc"},
        { name: "NCERT Summary Notes", type: "Website", link: "https://www.selfstudys.com/books/neet/biology/ncert-notes" }
      ],
      Chemistry: [
        { name: "Organic Chemistry Practice", type: "YouTube", link: "https://youtube.com/playlist?list=PLVdpygJig6T12-StN9weAVwZhgTpW0R5c&si=zxnkg6O6ItLWc51G" }
      ]
    },
    "JEE": {
      Physics: [
        { name: "JEE Physics – Concepts", type: "YouTube", link: "https://youtube.com/playlist?list=PLxyGaR3hEy3jUUtmhkX54XuTXejaqQUXa&si=T7N3U_bHdtfPzsKf" },
        { name: "JEE PYQs", type: "Website", link: "https://questions.examside.com/past-years/jee/jee-main" }
      ]
    }
  }
};

// --- DOM container ---
const grid = document.getElementById("resourceGrid");

// --- Load Resources Function ---
function loadResources() {
  const selectedResources =
    resourceBank[`Grade ${grade}`]?.[exam]?.[subject];

  if (!selectedResources) {
    grid.innerHTML = `<p>No resources found for this combination yet.</p>`;
    return;
  }

  selectedResources.forEach(res => {
    const card = document.createElement("div");
    card.classList.add("card", "fade-in");

    card.innerHTML = `
      <h3>${res.name}</h3>
      <p>Type: ${res.type}</p>
      <a href="${res.link}" target="_blank">Open Resource</a>
    `;

    grid.appendChild(card);
  });
}

// --- Load automatically ---
window.addEventListener("DOMContentLoaded", loadResources);
