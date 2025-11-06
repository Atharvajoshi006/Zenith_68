// Centralized API for frontend <-> Django
(function () {
  const API_BASE = 'http://127.0.0.1:8000/api'; // change if your port/host differs

  async function apiGet(path, params = {}) {
    const qs = new URLSearchParams(params).toString();
    const url = `${API_BASE}${path}${qs ? `?${qs}` : ''}`;
    const res = await fetch(url, { credentials: 'include' });
    if (!res.ok) throw new Error(`GET ${path} failed: ${res.status}`);
    return res.json();
  }

  async function apiPost(path, body = {}) {
    const res = await fetch(`${API_BASE}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      let detail = '';
      try { detail = (await res.json()).detail || ''; } catch {}
      throw new Error(`POST ${path} failed: ${res.status} ${detail}`);
    }
    return res.json();
  }

  window.API = {
    listGrades:     () => apiGet('/grades/'),
    listSubjects:   (gradeId)   => apiGet('/subjects/',  { grade: gradeId }),
    listTopics:     (subjectId) => apiGet('/topics/',    { subject: subjectId }),
    listResources:  (topicId)   => apiGet('/resources/', { topic: topicId }),
    listPapers:     (subjectId) => apiGet('/papers/',    { subject: subjectId }),
    personalize:    (subjectId, hours, weak=[]) => apiPost('/personalize/', {
                        subject_id: subjectId, hours, weak_topics: weak }),
    login:          (username, password) => apiPost('/login/', { username, password }),
  };
})();
