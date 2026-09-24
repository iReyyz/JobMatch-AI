const api = async (url, method = "GET", body) => {
  const r = await fetch(url, { method, headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined });
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(data.error || "Ralat");
  return data;
};
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

const jobCard = (j, extra = "") => `
  <div class="col-md-6"><div class="card job-card h-100"><div class="card-body">
    <h5>${esc(j.title)} ${j.score !== undefined ? `<span class="badge bg-success score-badge">${j.score}% match</span>` : ""}</h5>
    <div class="text-muted small">${esc(j.company)} • ${esc(j.location || "-")} • ${esc(j.salary_range || "-")}</div>
    <p class="mt-2 mb-1 small">${esc(j.description)}</p>
    <div class="small"><b>Skills:</b> ${esc(j.required_skills)}</div>${extra}
  </div></div></div>`;

// ---------- HOME ----------
async function initHome() {
  let mode = "login";
  document.querySelectorAll("[data-mode]").forEach((b) => b.onclick = () => {
    mode = b.dataset.mode;
    document.querySelectorAll("[data-mode]").forEach((x) => x.classList.toggle("active", x === b));
    ["name", "role", "skills"].forEach((id) => $(id).classList.toggle("d-none", mode === "login"));
    $("authBtn").textContent = mode === "login" ? "Login" : "Daftar";
  });
  $("authBtn").onclick = async () => {
    try {
      await api(`/api/auth/${mode}`, "POST", { name: $("name").value, email: $("email").value,
        password: $("password").value, role: $("role").value, skills: $("skills").value });
      location.href = "/dashboard.html";
    } catch (e) { $("authMsg").textContent = e.message; }
  };
  const load = async () => {
    const jobs = await api("/api/jobs?q=" + encodeURIComponent($("search").value));
    $("jobList").innerHTML = jobs.map((j) => jobCard(j)).join("") || "<p>Tiada job.</p>";
  };
  $("search").oninput = load;
  load();
}

// ---------- DASHBOARD ----------
async function initDashboard() {
  let me;
  try { me = await api("/api/auth/me"); } catch { location.href = "/"; return; }
  $("who").textContent = `${me.name} (${me.role})`;
  $("logout").onclick = async () => { await api("/api/auth/logout", "POST"); location.href = "/"; };
  ({ student: studentView, company: companyView, admin: adminView })[me.role](me);
}

async function studentView(me) {
  const [recs, jobs, apps] = await Promise.all([api("/api/recommendations"), api("/api/jobs"), api("/api/my/applications")]);
  const applyBtn = (id) => `<button class="btn btn-sm btn-primary mt-2" onclick="applyJob(${id})">Mohon</button>`;
  $("app").innerHTML = `
    <div class="card p-3 mb-4"><b>Skills saya</b>
      <div class="input-group mt-2"><input id="mySkills" class="form-control" value="${esc(me.skills)}">
      <button class="btn btn-outline-primary" onclick="saveSkills()">Simpan</button></div></div>
    <h4>⭐ Recommended untuk anda</h4>
    <div class="row g-3 mb-4">${recs.map((j) => jobCard(j, applyBtn(j.id))).join("") || "<p class='text-muted'>Tambah skills untuk dapat cadangan.</p>"}</div>
    <h4>Semua Job</h4>
    <div class="row g-3 mb-4">${jobs.map((j) => jobCard(j, applyBtn(j.id))).join("")}</div>
    <h4>Permohonan Saya</h4>
    <ul class="list-group">${apps.map((a) => `<li class="list-group-item d-flex justify-content-between">${esc(a.job)} - ${esc(a.company)}<span class="badge bg-secondary">${a.status}</span></li>`).join("") || "<li class='list-group-item'>Belum ada</li>"}</ul>`;
}
async function applyJob(id) { try { await api(`/api/jobs/${id}/apply`, "POST"); alert("Berjaya dimohon!"); location.reload(); } catch (e) { alert(e.message); } }
async function saveSkills() { await api("/api/auth/skills", "PATCH", { skills: $("mySkills").value }); location.reload(); }

async function companyView() {
  const jobs = await api("/api/company/jobs");
  $("app").innerHTML = `
    <div class="card p-3 mb-4"><h5>Post Job Baru</h5>
      <input id="t" class="form-control mb-2" placeholder="Title">
      <textarea id="d" class="form-control mb-2" placeholder="Description"></textarea>
      <input id="rs" class="form-control mb-2" placeholder="Required skills (comma separated)">
      <div class="row g-2 mb-2"><div class="col"><input id="loc" class="form-control" placeholder="Location"></div>
      <div class="col"><input id="sal" class="form-control" placeholder="Salary range"></div></div>
      <button class="btn btn-primary" onclick="postJob()">Post</button></div>
    <h4>Job Saya</h4>
    <div class="row g-3">${jobs.map((j) => jobCard(j, `<div class="mt-2">
      <button class="btn btn-sm btn-outline-primary" onclick="viewApplicants(${j.id})">Applicants</button>
      <button class="btn btn-sm btn-outline-danger" onclick="delJob(${j.id})">Padam</button></div>`)).join("")}</div>
    <div id="apps" class="mt-4"></div>`;
}
async function postJob() {
  try { await api("/api/jobs", "POST", { title: $("t").value, description: $("d").value, required_skills: $("rs").value, location: $("loc").value, salary_range: $("sal").value }); location.reload(); }
  catch (e) { alert(e.message); }
}
async function delJob(id) { if (confirm("Padam job ini?")) { await api(`/api/jobs/${id}`, "DELETE"); location.reload(); } }
async function viewApplicants(id) {
  const list = await api(`/api/jobs/${id}/applicants`);
  $("apps").innerHTML = `<h4>Applicants</h4><ul class="list-group">${list.map((a) => `
    <li class="list-group-item d-flex justify-content-between align-items-center">
      <span><b>${esc(a.name)}</b> (${esc(a.email)})<br><small>${esc(a.skills)}</small></span>
      <span><span class="badge bg-secondary">${a.status}</span>
      <button class="btn btn-sm btn-success" onclick="setStatus(${a.id},'accepted',${id})">Terima</button>
      <button class="btn btn-sm btn-danger" onclick="setStatus(${a.id},'rejected',${id})">Tolak</button></span></li>`).join("") || "<li class='list-group-item'>Tiada applicant</li>"}</ul>`;
}
async function setStatus(aid, status, jid) { await api(`/api/applications/${aid}`, "PATCH", { status }); viewApplicants(jid); }

async function adminView() {
  const [users, jobs] = await Promise.all([api("/api/admin/users"), api("/api/jobs")]);
  $("app").innerHTML = `<h4>Users</h4><ul class="list-group mb-4">${users.map((u) => `
    <li class="list-group-item d-flex justify-content-between">${esc(u.name)} - ${esc(u.email)} <span class="badge bg-info">${u.role}</span>
    <button class="btn btn-sm btn-outline-danger" onclick="delUser(${u.id})">Padam</button></li>`).join("")}</ul>
    <h4>Jobs</h4><div class="row g-3">${jobs.map((j) => jobCard(j, `<button class="btn btn-sm btn-outline-danger mt-2" onclick="delJob(${j.id})">Padam</button>`)).join("")}</div>`;
}
async function delUser(id) { if (confirm("Padam user ini?")) { await api(`/api/admin/users/${id}`, "DELETE"); location.reload(); } }
