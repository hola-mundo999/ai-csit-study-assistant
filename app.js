/* ==========================================================================
   CSIT Pulse
   Three views, one static page. Data comes from data/study.json, answers from
   /api/tutor.
   ========================================================================== */

const LENGTHS = {
  very_short: { label: "Very short", hint: "Under 70 words, the definition and one key fact." },
  short: { label: "Short", hint: "Around 150 words, one clear mechanism." },
  long: { label: "Long", hint: "Around 400 words, exam ready with code and complexity." },
  very_long: { label: "Exam guide", hint: "A full guide with proof, code and practice questions." },
};

const state = {
  length: "short",
  history: [],
  data: null,
  busy: false,
  semIndex: 0,
  qFilter: { text: "", subject: "all" },
};

const dom = {};

/* ---------------------------------------------------------------- helpers */

function el(tag, cls, text) {
  const node = document.createElement(tag);
  if (cls) node.className = cls;
  if (text != null) node.textContent = text;
  return node;
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

/* A small markdown renderer: code fences, headings, lists, bold, inline code.
   Everything is escaped first, so model output cannot inject markup. */
function renderMarkdown(source) {
  const text = String(source || "").replace(/\r\n/g, "\n");
  const fence = /```([a-zA-Z0-9+#.-]*)\n?([\s\S]*?)```/g;
  const blocks = [];
  let body = text.replace(fence, (_, lang, code) => {
    blocks.push(
      `<pre><code data-lang="${escapeHtml(lang)}">${escapeHtml(code.replace(/\n$/, ""))}</code></pre>`
    );
    return `\u0000BLOCK${blocks.length - 1}\u0000`;
  });

  body = escapeHtml(body)
    .replace(/\*\*([^*\n]+)\*\*/g, "<strong>$1</strong>")
    .replace(/(^|[\s(])\*([^*\n]+)\*(?=[\s).,;:!?]|$)/g, "$1<em>$2</em>")
    .replace(/`([^`\n]+)`/g, "<code>$1</code>");

  const lines = body.split("\n");
  const out = [];
  let list = null;
  let para = [];

  const flushPara = () => {
    if (para.length) {
      out.push(`<p>${para.join(" ").trim()}</p>`);
      para = [];
    }
  };
  const flushList = () => {
    if (list) {
      out.push(`<${list.tag}>${list.items.map((i) => `<li>${i}</li>`).join("")}</${list.tag}>`);
      list = null;
    }
  };

  for (const raw of lines) {
    const line = raw.trimEnd();
    if (!line.trim()) {
      flushPara();
      flushList();
      continue;
    }
    if (/^\u0000BLOCK\d+\u0000$/.test(line.trim())) {
      flushPara();
      flushList();
      out.push(line.trim());
      continue;
    }
    const heading = line.match(/^(#{1,6})\s+(.*)$/);
    if (heading) {
      flushPara();
      flushList();
      const level = Math.min(4, Math.max(3, heading[1].length + 1));
      out.push(`<h${level}>${heading[2]}</h${level}>`);
      continue;
    }
    const bullet = line.match(/^\s*[-*+]\s+(.*)$/);
    const numbered = line.match(/^\s*\d+[.)]\s+(.*)$/);
    if (bullet || numbered) {
      flushPara();
      const tag = bullet ? "ul" : "ol";
      if (!list || list.tag !== tag) {
        flushList();
        list = { tag, items: [] };
      }
      list.items.push((bullet || numbered)[1]);
      continue;
    }
    flushList();
    para.push(line.trim());
  }
  flushPara();
  flushList();

  return out
    .join("\n")
    .replace(/\u0000BLOCK(\d+)\u0000/g, (_, i) => blocks[Number(i)]);
}

/* -------------------------------------------------------------------- api */

async function askTutor(question) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 55000);
  try {
    const response = await fetch("api/tutor", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question,
        length: state.length,
        history: state.history.slice(-6),
      }),
      signal: controller.signal,
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(payload.error || `Request failed (${response.status})`);
    }
    return payload;
  } finally {
    clearTimeout(timer);
  }
}

/* ------------------------------------------------------------------ views */

function showView(name) {
  const target = document.getElementById(`view-${name}`);
  if (!target) return;
  document.querySelectorAll(".view").forEach((v) => v.classList.toggle("is-active", v === target));
  document.querySelectorAll(".tab").forEach((t) => {
    const on = t.dataset.view === name;
    t.classList.toggle("is-active", on);
    t.setAttribute("aria-selected", String(on));
  });
  if (name !== "tutor" && location.hash !== `#${name}`) {
    history.replaceState(null, "", `#${name}`);
  } else if (name === "tutor" && location.hash !== "#tutor") {
    history.replaceState(null, "", "#tutor");
  }
  window.scrollTo({ top: 0, behavior: "smooth" });
}

/* ------------------------------------------------------------------ chat */

function messageNode(role) {
  const wrap = el("div", `msg ${role}`);
  const avatar = el("div", "msg-avatar", role === "user" ? "You" : "AI");
  avatar.setAttribute("aria-hidden", "true");
  const body = el("div", "msg-body");
  const label = el("div", "msg-role", role === "user" ? "You" : "Tutor");
  body.appendChild(label);
  wrap.append(avatar, body);
  return { wrap, body };
}

function scrollChat() {
  if (dom.chatLog) dom.chatLog.scrollTop = dom.chatLog.scrollHeight;
}

function addUserMessage(text) {
  const node = messageNode("user").wrap;
  node.querySelector(".msg-body").appendChild(el("p", null, text));
  dom.chatLog.appendChild(node);
  scrollChat();
}

function addTyping() {
  const { wrap, body } = messageNode("bot");
  const p = el("p", "answer");
  const dots = el("span", "typing");
  dots.append(el("span"), el("span"), el("span"));
  dots.setAttribute("aria-label", "Thinking");
  p.appendChild(dots);
  body.appendChild(p);
  wrap.dataset.typing = "true";
  dom.chatLog.appendChild(wrap);
  scrollChat();
  return wrap;
}

function addBotMessage({ answer, source, engine }) {
  const { wrap, body } = messageNode("bot");
  const answerEl = el("div", "answer");
  answerEl.innerHTML = renderMarkdown(answer);
  body.appendChild(answerEl);

  const meta = el("div", "answer-meta");
  const tag = el("span", "tag" + (source === "online" ? " online" : ""), source === "online" ? "Online model" : "Local engine");
  meta.appendChild(tag);
  if (engine) meta.appendChild(el("span", "tag", engine));
  const copy = el("button", null, "Copy");
  copy.type = "button";
  copy.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(answer);
      copy.textContent = "Copied";
      setTimeout(() => (copy.textContent = "Copy"), 1600);
    } catch {
      copy.textContent = "Select and copy";
    }
  });
  meta.appendChild(copy);
  body.appendChild(meta);

  dom.chatLog.appendChild(wrap);
  scrollChat();
}

function addErrorMessage(message) {
  const { wrap, body } = messageNode("bot");
  const p = el("p", "answer", message);
  body.appendChild(p);
  dom.chatLog.appendChild(wrap);
  scrollChat();
}

function welcome() {
  dom.chatLog.innerHTML = "";
  const { wrap, body } = messageNode("bot");
  const answer = el("div", "answer");
  answer.innerHTML = renderMarkdown(
    "Ask me anything from the TU BSc CSIT programme. I can explain a concept, compare two techniques, walk through a past board question, or write and read back code.\n\n" +
      "Try *Explain the working of a relational join*, *Derive the worst case of quick sort*, or paste a question from your exam paper."
  );
  body.appendChild(answer);
  dom.chatLog.appendChild(wrap);
}

async function submitQuestion(text) {
  const question = String(text || "").trim();
  if (!question || state.busy) return;

  state.busy = true;
  dom.sendBtn.disabled = true;
  dom.suggest.hidden = true;

  addUserMessage(question);
  state.history.push({ role: "user", content: question });
  const typing = addTyping();

  try {
    const result = await askTutor(question);
    typing.remove();
    addBotMessage(result);
    state.history.push({ role: "assistant", content: result.answer });
  } catch (error) {
    typing.remove();
    const message =
      error.name === "AbortError"
        ? "That answer took too long to come back. Try again, or ask a narrower question."
        : "The tutor could not answer that one. Check your connection and try again.";
    addErrorMessage(message);
  } finally {
    state.busy = false;
    dom.sendBtn.disabled = false;
  }
}

/* -------------------------------------------------------------- curriculum */

function renderSemesters() {
  const { semesters } = state.data;
  dom.semList.innerHTML = "";
  semesters.forEach((sem, index) => {
    const btn = el("button", "sem" + (index === state.semIndex ? " is-active" : ""));
    btn.type = "button";
    btn.setAttribute("role", "tab");
    btn.setAttribute("aria-selected", String(index === state.semIndex));
    btn.append(
      el("span", "sem-num", String(index + 1).padStart(2, "0")),
      el("span", null, sem.title.replace(/ Semester$/, "")),
      el("span", "sem-count", String(sem.subjects.length))
    );
    btn.addEventListener("click", () => {
      state.semIndex = index;
      renderSemesters();
      renderCourses();
    });
    dom.semList.appendChild(btn);
  });
}

function renderCourses() {
  const sem = state.data.semesters[state.semIndex];
  if (!sem) return;

  dom.semEyebrow.textContent = sem.title;
  dom.semTitle.textContent = sem.title;
  dom.semSummary.textContent = sem.description || "";
  dom.semSummary.hidden = !sem.description;
  const chapters = sem.subjects.reduce((sum, s) => sum + s.chapters.length, 0);
  dom.courseCount.textContent = `${sem.subjects.length} subjects`;
  dom.creditCount.textContent = `${chapters} chapters`;
  dom.courseList.innerHTML = "";

  sem.subjects.forEach((subject) => {
    const card = el("article", "course");
    const head = el("button", "course-head");
    head.type = "button";
    head.setAttribute("aria-expanded", "false");

    const caret = el("span", "course-caret");
    caret.innerHTML =
      '<svg viewBox="0 0 16 16" width="12" height="12" aria-hidden="true"><path d="M6 3l5 5-5 5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>';

    head.append(
      el("span", "course-code", subject.code || "CSIT"),
      el("span", "course-name", subject.name),
      el("span", "course-sub", `${subject.chapters.length} chapters`),
      caret
    );

    const bodyEl = el("div", "course-body");
    if (subject.chapters.length) {
      const list = el("div", "chapters");
      subject.chapters.forEach((chapter) => {
        const chip = el("button", "chapter");
        chip.type = "button";
        chip.append(el("span", null, "\u203a"), document.createTextNode(chapter.title));
        chip.title = `Ask the tutor about ${chapter.title}`;
        chip.addEventListener("click", () => {
          showView("tutor");
          submitQuestion(`Explain ${chapter.title} in the context of ${subject.name} (${subject.code}).`);
        });
        list.appendChild(chip);
      });
      bodyEl.appendChild(list);
    } else {
      bodyEl.appendChild(el("p", "course-desc", "Project and internship work, assessed by your college."));
    }

    head.addEventListener("click", () => {
      const open = card.classList.toggle("is-open");
      head.setAttribute("aria-expanded", String(open));
    });

    card.append(head, bodyEl);
    dom.courseList.appendChild(card);
  });
}

/* --------------------------------------------------------------- questions */

function renderQuestions() {
  const all = state.data.questions;
  const subjects = [...new Set(all.map((q) => q.subject))].sort();

  dom.qSubject.innerHTML = "";
  const allOption = el("option", null, `All subjects (${all.length})`);
  allOption.value = "all";
  dom.qSubject.appendChild(allOption);
  subjects.forEach((subject) => {
    const option = el("option", null, subject);
    option.value = subject;
    dom.qSubject.appendChild(option);
  });
  dom.qSubject.value = state.qFilter.subject;

  drawQuestionList();
}

function drawQuestionList() {
  const needle = state.qFilter.text.trim().toLowerCase();
  const rows = state.data.questions.filter((q) => {
    if (state.qFilter.subject !== "all" && q.subject !== state.qFilter.subject) return false;
    if (!needle) return true;
    return `${q.title} ${q.subject} ${q.code} ${q.year}`.toLowerCase().includes(needle);
  });

  dom.qList.innerHTML = "";
  if (!rows.length) {
    const empty = el("div", "empty");
    empty.append(el("strong", null, "Nothing matches that search"), document.createTextNode("Try a shorter phrase, or clear the subject filter."));
    dom.qList.appendChild(empty);
    return;
  }

  rows.slice(0, 120).forEach((q) => {
    const card = el("article", "q-card");
    const top = el("div", "q-top");
    top.append(el("span", "q-subject", q.code ? `${q.subject} · ${q.code}` : q.subject));
    if (q.year) top.append(el("span", "q-year", q.year));
    card.appendChild(top);
    card.appendChild(el("p", "q-text", q.title));

    const actions = el("div", "q-actions");
    const toggle = el("button", "q-toggle", "Show solution");
    toggle.type = "button";
    const ask = el("button", "q-ask", "Ask tutor");
    ask.type = "button";
    const solution = el("div", "q-solution");
    card.append(actions, solution);
    actions.append(toggle, ask);

    toggle.addEventListener("click", async () => {
      const open = card.classList.toggle("is-open");
      toggle.textContent = open ? "Hide solution" : "Show solution";
      if (!open || solution.dataset.loaded) return;
      solution.dataset.loaded = "1";
      solution.innerHTML = '<p class="typing"><span></span><span></span><span></span></p>';
      try {
        const result = await askTutor(q.title);
        solution.innerHTML = `<div class="answer">${renderMarkdown(result.answer)}</div>`;
      } catch {
        delete solution.dataset.loaded;
        solution.innerHTML =
          '<div class="answer"><p>The solution could not load. Check your connection and try again.</p></div>';
      }
    });

    ask.addEventListener("click", () => {
      showView("tutor");
      submitQuestion(`Solve this past TU board question step by step: ${q.title}`);
    });

    dom.qList.appendChild(card);
  });

  if (rows.length > 120) {
    const more = el("p", "empty", `Showing the first 120 of ${rows.length} matches. Narrow the search to see the rest.`);
    dom.qList.appendChild(more);
  }
}

/* ------------------------------------------------------------------- init */

function bindTutor() {
  dom.askForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const value = dom.askInput.value;
    dom.askInput.value = "";
    dom.askInput.style.height = "auto";
    submitQuestion(value);
  });

  dom.askInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      dom.askForm.requestSubmit();
    }
  });

  dom.askInput.addEventListener("input", () => {
    dom.askInput.style.height = "auto";
    dom.askInput.style.height = `${Math.min(dom.askInput.scrollHeight, 180)}px`;
  });

  dom.lenChips.addEventListener("click", (event) => {
    const chip = event.target.closest(".chip");
    if (!chip) return;
    state.length = chip.dataset.len;
    dom.lenChips.querySelectorAll(".chip").forEach((c) => {
      const on = c === chip;
      c.classList.toggle("is-on", on);
      c.setAttribute("aria-checked", String(on));
    });
    dom.lenHint.textContent = LENGTHS[state.length].hint;
  });

  dom.suggest.addEventListener("click", (event) => {
    const item = event.target.closest(".suggest-item");
    if (!item) return;
    submitQuestion(item.textContent);
  });

  dom.clearChat.addEventListener("click", () => {
    state.history = [];
    dom.suggest.hidden = false;
    welcome();
  });

  dom.lenHint.textContent = LENGTHS[state.length].hint;
}

function bindNav() {
  document.querySelectorAll(".tab").forEach((tab) => {
    tab.addEventListener("click", () => showView(tab.dataset.view));
  });
  window.addEventListener("hashchange", () => {
    const name = location.hash.replace("#", "") || "tutor";
    if (document.getElementById(`view-${name}`)) showView(name);
  });
}

function setStatus(text, kind) {
  dom.statusText.textContent = text;
  dom.statusDot.className = `dot${kind ? ` is-${kind}` : ""}`;
}

async function boot() {
  Object.assign(dom, {
    chatLog: document.getElementById("chatLog"),
    suggest: document.getElementById("suggest"),
    askForm: document.getElementById("askForm"),
    askInput: document.getElementById("askInput"),
    sendBtn: document.getElementById("sendBtn"),
    clearChat: document.getElementById("clearChat"),
    lenChips: document.getElementById("lenChips"),
    lenHint: document.getElementById("lenHint"),
    semList: document.getElementById("semList"),
    semEyebrow: document.getElementById("semEyebrow"),
    semTitle: document.getElementById("semTitle"),
    semSummary: document.getElementById("semSummary"),
    courseCount: document.getElementById("courseCount"),
    creditCount: document.getElementById("creditCount"),
    courseList: document.getElementById("courseList"),
    qList: document.getElementById("qList"),
    qSearch: document.getElementById("qSearch"),
    qSubject: document.getElementById("qSubject"),
    statusDot: document.getElementById("statusDot"),
    statusText: document.getElementById("statusText"),
  });

  bindNav();
  bindTutor();
  welcome();

  dom.qSearch.addEventListener("input", () => {
    state.qFilter.text = dom.qSearch.value;
    if (state.data) drawQuestionList();
  });
  dom.qSubject.addEventListener("change", () => {
    state.qFilter.subject = dom.qSubject.value;
    if (state.data) drawQuestionList();
  });

  const hash = location.hash.replace("#", "");
  if (["courses", "questions", "tutor"].includes(hash)) showView(hash);

  setStatus("Loading syllabus", null);
  try {
    const response = await fetch("data/study.json");
    if (!response.ok) throw new Error(String(response.status));
    state.data = await response.json();
    renderSemesters();
    renderCourses();
    renderQuestions();
    setStatus(`${state.data.totals.subjects} subjects, ${state.data.totals.chapters} chapters`, "live");
  } catch {
    setStatus("Syllabus unavailable", "warn");
    dom.courseList.innerHTML = "";
    const empty = el("div", "empty");
    empty.append(el("strong", null, "The syllabus could not load"), document.createTextNode("Refresh the page. The tutor still works."));
    dom.courseList.appendChild(empty);
  }
}

document.addEventListener("DOMContentLoaded", boot);
