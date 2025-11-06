// resource.js (paste-ready)

// DOM Elements
const pageHeading = document.getElementById("pageHeading");
const resourceGrid = document.getElementById("resourceGrid");
const backBtn = document.getElementById("backBtn");

// Get query params from previous page
const urlParams = new URLSearchParams(window.location.search);
const state = urlParams.get("state");
const grade = urlParams.get("grade");
const exam = urlParams.get("exam");
const subject = urlParams.get("subject");     // display label (e.g., "Maths (Kannada)")
const subjectId = urlParams.get("subject_id"); // BACKEND subject id (important)

// Back button
if (backBtn) {
  backBtn.addEventListener("click", () => window.history.back());
}

// Heading
if (pageHeading) {
  pageHeading.textContent = `Resources for ${subject || ""} | ${exam || ""} | Grade ${grade || ""} | ${state || ""}`;
}

// Utility: create a card node
function makeCard({ title, type, link }) {
  const card = document.createElement("div");
  card.className = "resource-card fade-in";
  card.innerHTML = `
    <h3>${title}</h3>
    <p>Type: ${type}</p>
    <a href="${link}" target="_blank" rel="noopener">View Resource</a>
  `;
  return card;
}

// Main loader
async function displayResources() {
  resourceGrid.innerHTML = "";

  if (!subjectId) {
    resourceGrid.innerHTML = "<p>Missing subject_id. Please reselect a subject.</p>";
    return;
  }

  try {
    // 1) Get topics for the chosen subject
    const topics = await API.listTopics(subjectId); // [{id, title, weight, subject}, ...]
    if (!topics || topics.length === 0) {
      resourceGrid.innerHTML = "<p>No topics found for this subject.</p>";
      return;
    }

    // 2) For each topic, fetch its resources and render cards
    let totalCards = 0;

    for (const t of topics) {
      const topicResources = await API.listResources(t.id); // [{id,title,type,url,topic}, ...]

      if (topicResources && topicResources.length) {
        // Topic header card (optional: comment this out if you don't want headers)
        const header = document.createElement("div");
        header.className = "resource-card fade-in";
        header.innerHTML = `<h3 style="margin-bottom:8px;">Topic: ${t.title}</h3>`;
        resourceGrid.appendChild(header);

        topicResources.forEach(r => {
          const card = makeCard({
            title: r.title,
            type: r.type || "Link",
            link: r.url || "#"
          });
          resourceGrid.appendChild(card);
          totalCards++;
        });
      }
    }

    // 3) Question papers for this subject (optional but useful)
    try {
      const papers = await API.listPapers(subjectId); // [{year,pdf_url,solution_url,...}]
      if (papers && papers.length) {
        const header = document.createElement("div");
        header.className = "resource-card fade-in";
        header.innerHTML = `<h3 style="margin-bottom:8px;">Question Papers</h3>`;
        resourceGrid.appendChild(header);

        papers.forEach(p => {
          const card = document.createElement("div");
          card.className = "resource-card fade-in";
          card.innerHTML = `
            <h3>Paper ${p.year || ""}</h3>
            <p>Type: Question Paper</p>
            <a href="${p.pdf_url}" target="_blank" rel="noopener">View Paper</a>
            ${p.solution_url ? `<br/><a href="${p.solution_url}" target="_blank" rel="noopener">View Solution</a>` : ""}
          `;
          resourceGrid.appendChild(card);
          totalCards++;
        });
      }
    } catch (e) {
      // Papers are optional; log and continue
      console.warn("Could not load papers:", e);
    }

    if (totalCards === 0) {
      resourceGrid.innerHTML = "<p>No resources available for this selection yet.</p>";
    }
  } catch (err) {
    console.error(err);
    resourceGrid.innerHTML = "<p>Failed to load resources. Make sure the backend is running.</p>";
  }
}

// Init
displayResources();
