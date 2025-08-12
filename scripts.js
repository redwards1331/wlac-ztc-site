document.addEventListener('DOMContentLoaded', () => {
  const RESULTS = document.getElementById('results');
  const search = document.getElementById('search');
  const dept = document.getElementById('department');
  const term = document.getElementById('term');
  const refresh = document.getElementById('refresh');
  let data = [];

  function load() {
    Papa.parse('ztc_live.csv', {
      download: true,
      header: true,
      skipEmptyLines: true,
      complete: (res) => {
        data = res.data.filter(r => r.Course || r.Description);
        populateFilters();
        render();
      },
      error: (err) => {
        RESULTS.innerHTML = '<p class="card">Error loading CSV. Ensure <code>ztc_live.csv</code> is present at repository root.</p>';
        console.error(err);
      }
    });
  }

  function populateFilters() {
    const depts = Array.from(new Set(data.map(d => d.Department).filter(Boolean))).sort();
    const terms = Array.from(new Set(data.map(d => d.Term).filter(Boolean))).sort();
    dept.innerHTML = '<option value="">All Departments</option>' + depts.map(d => `<option value="${d}">${d}</option>`).join('');
    term.innerHTML = '<option value="">All Terms</option>' + terms.map(t => `<option value="${t}">${t}</option>`).join('');
  }

  function render() {
    const q = search.value.trim().toLowerCase();
    const d = dept.value;
    const t = term.value;
    const filtered = data.filter(item => {
      const text = ((item.Course||'') + ' ' + (item.Description||'') + ' ' + (item.Instructor||'')).toLowerCase();
      if (q && !text.includes(q)) return false;
      if (d && item.Department !== d) return false;
      if (t && item.Term !== t) return false;
      return true;
    });
    if (!filtered.length) {
      RESULTS.innerHTML = '<p class="card">No courses found.</p>';
      return;
    }
    RESULTS.innerHTML = filtered.map(c => `
      <article class="card">
        <h3>${escapeHtml(c.Course)}</h3>
        <p>${escapeHtml(c.Description)}</p>
        <p><strong>Dept:</strong> ${escapeHtml(c.Department)} · <strong>Term:</strong> ${escapeHtml(c.Term)}</p>
        <p><strong>Instructor:</strong> ${escapeHtml(c.Instructor||'TBA')}</p>
        ${c.Link ? `<p><a href="${c.Link}" target="_blank">Course Link</a></p>` : ''}
      </article>
    `).join('');
  }

  function escapeHtml(s){ return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

  search.addEventListener('input', render);
  dept.addEventListener('change', render);
  term.addEventListener('change', render);
  refresh.addEventListener('click', load);

  load();
});
