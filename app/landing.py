"""Landing page served at GET / — what a visitor (or a reviewer) sees when
they open the API's URL in a browser. The endpoint list is read from the
app's own OpenAPI schema so it can't drift out of date. Self-contained:
inline CSS/JS, no external assets."""

import html

from fastapi import FastAPI

TAG_ORDER = ["users", "projects", "tasks", "health"]
TAG_BLURB = {
    "users": "Passwords are hashed, never returned",
    "projects": "Each belongs to an existing user",
    "tasks": "todo · in-progress · done",
    "health": "Service and database check",
}


def public_base_url(host: str, scheme: str) -> str:
    """Behind Render's TLS-terminating proxy the app sees plain http, so
    build https links for any non-local host."""
    local = host.split(":")[0] in {"localhost", "127.0.0.1", "0.0.0.0"}
    return f"{scheme if local else 'https'}://{host}"


def _endpoint_groups(app: FastAPI) -> str:
    groups: dict[str, list[tuple[str, str]]] = {}
    for path, methods in app.openapi().get("paths", {}).items():
        for method, op in methods.items():
            tag = (op.get("tags") or ["other"])[0]
            groups.setdefault(tag, []).append((method.upper(), path))

    ordered = [t for t in TAG_ORDER if t in groups] + [t for t in groups if t not in TAG_ORDER]
    sections = []
    for tag in ordered:
        rows = "".join(
            f'<li><span class="m {html.escape(m.lower())}">{html.escape(m)}</span>'
            f"<code>{html.escape(p)}</code></li>"
            for m, p in groups[tag]
        )
        sections.append(
            f"<section><h3>{html.escape(tag.title())}</h3>"
            f"<p>{html.escape(TAG_BLURB.get(tag, ''))}</p><ul>{rows}</ul></section>"
        )
    return "".join(sections)


def _requirements(rows: list[tuple[str, str]]) -> str:
    return "".join(
        f'<tr><th scope="row">{html.escape(req)}</th><td>{html.escape(how)}</td></tr>'
        for req, how in rows
    )


def render_landing(
    app: FastAPI,
    base_url: str,
    environment: str,
    repo_url: str,
    label: str,
    requirements: list[tuple[str, str]],
) -> str:
    replacements = {
        "__TITLE__": html.escape(app.title),
        "__DESC__": html.escape(app.description),
        "__LABEL__": html.escape(label),
        "__VERSION__": html.escape(app.version),
        "__ENV__": html.escape(environment),
        "__REPO__": html.escape(repo_url),
        "__BASE__": html.escape(base_url),
        "__REQS__": _requirements(requirements),
        "__ENDPOINTS__": _endpoint_groups(app),
    }
    page = _TEMPLATE
    for token, value in replacements.items():
        page = page.replace(token, value)
    return page


_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<meta name="description" content="__DESC__">
<style>
:root {
  --bg:#fff; --text:#111827; --muted:#6b7280; --line:#e5e7eb; --accent:#2563eb; --accent-text:#fff;
  --code:#f3f4f6; --ok:#15803d; --warn:#b45309; --bad:#b91c1c;
}
@media (prefers-color-scheme: dark) {
  :root { --bg:#111418; --text:#e7eaee; --muted:#9aa3af; --line:#272c34; --accent:#6ea0ff;
    --accent-text:#0b1220; --code:#1a1f26; --ok:#4ade80; --warn:#fbbf24; --bad:#f87171; }
}
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--text);
  font:16px/1.6 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif; }
a { color:var(--accent); }
code,pre { font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; }
.wrap { max-width:840px; margin:0 auto; padding:56px 20px 40px; }
.eyebrow { color:var(--muted); font-size:.8rem; letter-spacing:.08em; text-transform:uppercase; }
h1 { margin:.4rem 0 .6rem; font-size:clamp(1.6rem,4.5vw,2.2rem); line-height:1.2; letter-spacing:-.01em; }
.lead { margin:0 0 18px; color:var(--muted); max-width:62ch; }
.meta { display:flex; flex-wrap:wrap; gap:16px; align-items:center; margin:0 0 24px; font-size:.9rem; color:var(--muted); }
.status { display:inline-flex; align-items:center; gap:8px; color:var(--text); }
.dot { width:8px; height:8px; border-radius:50%; background:var(--muted); }
.status.ok .dot { background:var(--ok); } .status.warn .dot { background:var(--warn); } .status.bad .dot { background:var(--bad); }
.cta { display:flex; flex-wrap:wrap; gap:14px; align-items:center; }
.btn { display:inline-block; padding:10px 18px; border-radius:8px; border:1px solid var(--accent); background:var(--accent);
  color:var(--accent-text); font:inherit; font-weight:600; text-decoration:none; cursor:pointer; }
.btn.ghost { background:transparent; color:var(--accent); }
.btn[disabled] { opacity:.6; cursor:progress; }
a:focus-visible,button:focus-visible { outline:2px solid var(--accent); outline-offset:2px; }
h2 { margin:44px 0 10px; font-size:.8rem; letter-spacing:.08em; text-transform:uppercase; color:var(--muted); font-weight:600; }
.sub { margin:0 0 12px; color:var(--muted); font-size:.92rem; }
table { width:100%; border-collapse:collapse; font-size:.92rem; }
th,td { text-align:left; vertical-align:top; padding:9px 12px 9px 0; border-top:1px solid var(--line); }
th { width:34%; font-weight:600; }
td { color:var(--muted); }
td code,.sub code { font-size:.82rem; color:var(--text); }
#checks { list-style:none; margin:0; padding:0; }
#checks li { display:grid; grid-template-columns:1.2em 1fr auto; gap:0 10px; align-items:baseline; padding:7px 0; border-top:1px solid var(--line); font-size:.92rem; }
#checks .mark { font-weight:700; color:var(--muted); }
#checks .pass .mark { color:var(--ok); } #checks .fail .mark { color:var(--bad); }
#checks .why { color:var(--muted); font-size:.82rem; text-align:right; }
#summary { margin:12px 0 0; font-size:.92rem; min-height:1.5em; }
.snip { background:var(--code); border-radius:8px; }
.snip .bar { display:flex; justify-content:flex-end; padding:8px 8px 0; }
.snip button { padding:3px 10px; font-size:.75rem; border-radius:6px; border:1px solid var(--line);
  background:var(--bg); color:var(--text); cursor:pointer; }
.snip pre { margin:0; padding:2px 16px 14px; overflow-x:auto; font-size:.85rem; }
.eps { display:grid; gap:24px; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); }
.eps h3 { margin:0; font-size:.95rem; } .eps p { margin:0 0 8px; color:var(--muted); font-size:.8rem; }
.eps ul { list-style:none; margin:0; padding:0; }
.eps li { display:flex; align-items:baseline; gap:8px; padding:4px 0; }
.eps li code { font-size:.8rem; overflow-wrap:break-word; min-width:0; }
.m { flex:none; font:700 .62rem ui-monospace,Menlo,monospace; padding:2px 0; border-radius:4px; width:48px; text-align:center;
  color:#fff; background:#64748b; }
.m.get { background:#2563eb; } .m.post { background:#15803d; } .m.patch { background:#b45309; }
.m.delete { background:#b91c1c; } .m.put { background:#7c3aed; }
footer { margin-top:48px; padding-top:16px; border-top:1px solid var(--line); color:var(--muted); font-size:.85rem; }
footer p { margin:0 0 6px; }
@media (max-width:600px) {
  th,td { display:block; width:auto; padding:0; border:0; }
  tr { display:block; padding:9px 0; border-top:1px solid var(--line); }
  th { padding-bottom:2px; }
  #checks .why { grid-column:2 / -1; text-align:left; }
}
</style>
</head>
<body>
<main class="wrap">
  <div class="eyebrow">__LABEL__ · Innovation Hacks Full Stack Internship</div>
  <h1>__TITLE__</h1>
  <p class="lead">REST API for users, projects and tasks, persisted in PostgreSQL. Built to the Task 3 brief. Every requirement below can be verified live, from this page.</p>
  <div class="meta">
    <span id="status" class="status" role="status"><span class="dot"></span><span id="status-text">Checking status…</span></span>
    <span>v__VERSION__ · __ENV__</span>
  </div>
  <div class="cta">
    <a class="btn" href="/docs">Open API docs</a>
    <button class="btn ghost" id="run" type="button">Run live checks</button>
    <a href="/redoc">ReDoc</a>
    <a href="__REPO__">GitHub</a>
  </div>

  <h2>Requirements coverage</h2>
  <table><tbody>__REQS__</tbody></table>

  <h2>Live verification</h2>
  <p class="sub">Runs real requests against this server and shows the result of each. It writes to the PostgreSQL database: it creates a temporary user with projects and tasks, then deletes them.</p>
  <ul id="checks" aria-live="polite"></ul>
  <p id="summary" role="status"></p>

  <h2>Quick start</h2>
  <p class="sub">Create a user, then use the returned <code>id</code> as <code>owner_id</code> in <code>POST /projects</code>, and the project's <code>id</code> in <code>POST /tasks</code>.</p>
  <div class="snip"><div class="bar"><button type="button" id="copy">Copy</button></div><pre id="cmd">curl -X POST __BASE__/users \\
  -H "Content-Type: application/json" \\
  -d '{"name":"Ada Lovelace","email":"ada@example.com","password":"supersecret1"}'</pre></div>

  <h2>Endpoints</h2>
  <div class="eps">__ENDPOINTS__</div>

  <footer>
    <p>Spec: <a href="/openapi.json">/openapi.json</a> · Free tier: the first request after inactivity can take up to a minute. Data is stored in PostgreSQL and survives restarts; Render's free database instances are time-limited.</p>
  </footer>
</main>
<script>
(function () {
  var box = document.getElementById("status"), text = document.getElementById("status-text");
  function set(cls, msg) { box.className = "status " + cls; text.textContent = msg; }
  var t0 = performance.now(), slow = setTimeout(function () { set("warn", "Waking up…"); }, 3000);
  fetch("/health", { cache: "no-store" }).then(function (r) {
    return r.json().catch(function () { return {}; }).then(function (body) { return { r: r, body: body }; });
  }).then(function (x) {
    clearTimeout(slow);
    var ms = Math.round(performance.now() - t0);
    var db = x.body && x.body.database === "ok" ? " · PostgreSQL connected" : "";
    set(x.r.ok ? "ok" : "bad", x.r.ok ? "Operational · " + ms + " ms" + db : "Unhealthy · database " + (x.body.database || "unknown"));
  }).catch(function () { clearTimeout(slow); set("bad", "Unreachable"); });

  var copy = document.getElementById("copy");
  copy.addEventListener("click", function () {
    var code = document.getElementById("cmd").textContent;
    (navigator.clipboard ? navigator.clipboard.writeText(code) : Promise.reject()).then(function () {
      copy.textContent = "Copied"; setTimeout(function () { copy.textContent = "Copy"; }, 1500);
    }).catch(function () { copy.textContent = "Ctrl+C"; });
  });

  async function api(method, path, body) {
    var res = await fetch(path, { method: method, headers: { "Content-Type": "application/json" },
      body: body === undefined ? undefined : JSON.stringify(body) });
    var raw = await res.text(), json = null;
    try { json = JSON.parse(raw); } catch (e) {}
    return { status: res.status, body: json };
  }
  function code(r) { return r.body && r.body.error ? r.body.error.code : undefined; }

  var NIL = "00000000-0000-0000-0000-000000000000";
  var steps = [
    ["Create a user", async function (c) {
      var r = await api("POST", "/users", { name: "Live Check", email: c.email, password: "supersecret1" });
      c.user = r.body;
      return [r.status === 201 && !("password" in r.body) && !("password_hash" in r.body), "201 · password never returned"];
    }],
    ["Read it back from the database", async function (c) {
      var r = await api("GET", "/users/" + c.user.id);
      return [r.status === 200 && r.body.email === c.email, "200 · same record"];
    }],
    ["Update the user", async function (c) {
      var r = await api("PATCH", "/users/" + c.user.id, { name: "Renamed" });
      return [r.status === 200 && r.body.name === "Renamed", "200 · name changed"];
    }],
    ["Reject a duplicate email", async function (c) {
      var r = await api("POST", "/users", { name: "Dup", email: c.email, password: "supersecret1" });
      return [r.status === 409 && code(r) === "conflict", "409 · unique index"];
    }],
    ["Reject invalid input", async function () {
      var r = await api("POST", "/users", { name: "", email: "not-an-email", password: "x" });
      return [r.status === 422 && code(r) === "validation_error", "422 validation_error"];
    }],
    ["Reject a project with an unknown owner", async function () {
      var r = await api("POST", "/projects", { name: "P", owner_id: NIL });
      return [r.status === 404, "404 · foreign key"];
    }],
    ["Create, rename and read a project", async function (c) {
      var p = await api("POST", "/projects", { name: "Live Project", owner_id: c.user.id });
      c.project = p.body;
      var u = await api("PATCH", "/projects/" + c.project.id, { name: "Renamed Project" });
      var g = await api("GET", "/projects/" + c.project.id);
      return [p.status === 201 && u.status === 200 && g.body.name === "Renamed Project", "201 · 200 · renamed"];
    }],
    ["Create a task and change its status", async function (c) {
      var t = await api("POST", "/tasks", { title: "Live Task", project_id: c.project.id });
      c.task = t.body;
      var u = await api("PATCH", "/tasks/" + c.task.id + "/status", { status: "done" });
      return [t.status === 201 && t.body.status === "todo" && u.status === 200 && u.body.status === "done", "todo → done"];
    }],
    ["Deleting a project removes its tasks", async function (c) {
      var p2 = await api("POST", "/projects", { name: "Doomed", owner_id: c.user.id });
      var t2 = await api("POST", "/tasks", { title: "Doomed task", project_id: p2.body.id });
      var d = await api("DELETE", "/projects/" + p2.body.id);
      var g = await api("GET", "/tasks/" + t2.body.id);
      return [d.status === 204 && g.status === 404, "204 · task now 404"];
    }],
    ["Deleting a user removes their projects and tasks", async function (c) {
      var d = await api("DELETE", "/users/" + c.user.id);
      c.user = null;
      var p = await api("GET", "/projects/" + c.project.id), t = await api("GET", "/tasks/" + c.task.id);
      return [d.status === 204 && p.status === 404 && t.status === 404, "204 · project and task now 404"];
    }],
    ["Unknown routes use the same error format", async function () {
      var r = await api("GET", "/no-such-route");
      return [r.status === 404 && code(r) === "not_found", "404 not_found"];
    }]
  ];

  var run = document.getElementById("run"), list = document.getElementById("checks"), summary = document.getElementById("summary");
  run.addEventListener("click", async function () {
    run.disabled = true; run.textContent = "Running…"; list.textContent = ""; summary.textContent = "";
    var ctx = { email: "live-check-" + Date.now() + "@example.com" }, passed = 0, t0 = performance.now();
    list.scrollIntoView({ behavior: "smooth", block: "center" });
    for (var i = 0; i < steps.length; i++) {
      var li = document.createElement("li"), mark = document.createElement("span"), name = document.createElement("span"), why = document.createElement("span");
      mark.className = "mark"; name.textContent = steps[i][0]; why.className = "why";
      li.append(mark, name, why); list.append(li);
      var ok = false, detail = "";
      try { var out = await steps[i][1](ctx); ok = !!out[0]; detail = out[1]; }
      catch (e) { detail = "request failed"; }
      li.className = ok ? "pass" : "fail"; mark.textContent = ok ? "✓" : "✗"; why.textContent = ok ? detail : "unexpected result";
      if (ok) passed++;
    }
    if (ctx.user) { try { await api("DELETE", "/users/" + ctx.user.id); } catch (e) {} }
    var secs = ((performance.now() - t0) / 1000).toFixed(1);
    summary.textContent = passed + " of " + steps.length + " checks passed · " + secs + " s";
    summary.style.color = passed === steps.length ? "var(--ok)" : "var(--bad)";
    run.disabled = false; run.textContent = "Run again";
  });
})();
</script>
</body>
</html>
"""
