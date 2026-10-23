/* ==========================================================================
   CSIT Pulse
   Static study desk. Answers stream from a free, keyless, OpenAI compatible
   endpoint straight to the browser, so each visitor gets their own quota and
   there is no server round trip before the first token.
   ========================================================================== */

const MODEL_ENDPOINT = "https://text.pollinations.ai/openai";
const MODEL_NAME = "openai";
const CACHE_PREFIX = "csitpulse.answer.v1";
const CACHE_TTL = 7 * 24 * 60 * 60 * 1000;

const LENGTHS = {
  very_short: {
    hint: "Under 70 words: the definition and one key fact.",
    budget: 160,
    rule: "Answer in under 70 words. Give the direct definition, the key formula or complexity, and nothing else.",
  },
  short: {
    hint: "Around 150 words, one clear mechanism.",
    budget: 420,
    rule: "Answer in about 150 words: definition, how it works, and the essential formula or complexity.",
  },
  long: {
    hint: "Around 400 words with a worked example.",
    budget: 950,
    rule: "Answer in about 400 words with short sections: definition, step by step mechanism, one worked example or code block, and complexity.",
  },
  very_long: {
    hint: "A full guide with code and practice questions.",
    budget: 1800,
    rule: "Write a study guide of about 800 words: theory, step by step mechanism, runnable code or pseudocode, complexity, common mistakes, and three practice questions with short answers.",
  },
};

const SYSTEM_PROMPT = [
  "You are a precise computer science professor for Tribhuvan University BSc CSIT students.",
  "Answer the exact question you are given, starting with the answer itself in the first sentence.",
  "Never answer a different topic, never pad with unrelated background, and never invent citations or exam dates.",
  "Use GitHub flavoured Markdown: short paragraphs, bold for key terms, and fenced code blocks with a language tag.",
  "Draw diagrams as plain text inside a fenced code block, never as mermaid.",
  "Never use em dashes or en dashes. Use a comma, a colon, or the word 'to' instead.",
  "If the question is outside computer science, still answer it accurately and briefly.",
].join(" ");

const state = {
  length: "short",
  history: [],
  busy: false,
  controller: null,
  data: null,
  topics: [],
  semIndex: 0,
  qFilter: { text: "", subject: "all" },
};

const dom = {};

/* ------------------------------------------------------------------ utils */

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

function plainDashes(text) {
  return String(text || "")
    .replace(/\s*[\u2014\u2013]\s*/g, ", ")
    .replace(/[\u2010\u2011\u2012\u2015\u2212\u2043]/g, "-");
}

function hash(text) {
  let h = 5381;
  for (let i = 0; i < text.length; i++) h = (h * 33) ^ text.charCodeAt(i);
  return (h >>> 0).toString(36);
}

function readCache(key) {
  try {
    const raw = localStorage.getItem(key);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (!parsed || typeof parsed.answer !== "string") return null;
    if (Date.now() - (parsed.ts || 0) > CACHE_TTL) {
      localStorage.removeItem(key);
      return null;
    }
    return parsed.answer;
  } catch {
    return null;
  }
}

function writeCache(key, answer) {
  try {
    localStorage.setItem(key, JSON.stringify({ answer, ts: Date.now() }));
  } catch {
    /* storage full or blocked, answer still renders */
  }
}

/* Markdown: escape first, then apply a small, predictable subset. */
function renderMarkdown(source) {
  const text = plainDashes(source).replace(/\r\n/g, "\n");
  const blocks = [];
  const body = text.replace(/```([a-zA-Z0-9+#.-]*)\n?([\s\S]*?)```/g, (_, lang, code) => {
    blocks.push(
      `<pre><code data-lang="${escapeHtml(lang)}">${escapeHtml(code.replace(/\n$/, ""))}</code></pre>`
    );
    return `\u0000B${blocks.length - 1}\u0000`;
  });

  const escaped = escapeHtml(body)
    .replace(/\*\*([^*\n]+)\*\*/g, "<strong>$1</strong>")
    .replace(/(^|[\s(])\*([^*\n]+)\*(?=[\s).,;:!?]|$)/g, "$1<em>$2</em>")
    .replace(/`([^`\n]+)`/g, "<code>$1</code>");

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

  for (const raw of escaped.split("\n")) {
    const line = raw.trimEnd();
    if (!line.trim()) {
      flushPara();
      flushList();
      continue;
    }
    if (/^\u0000B\d+\u0000$/.test(line.trim())) {
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
    .replace(/\u0000B(\d+)\u0000/g, (_, i) => blocks[Number(i)]);
}

/* -------------------------------------------------------------- topic refs */

function topicFor(question) {
  const q = question.toLowerCase();
  let best = null;
  let bestScore = 0;
  for (const topic of state.topics) {
    let score = 0;
    const title = topic.title.toLowerCase();
    const words = title.split(/[^a-z0-9+*]+/).filter((w) => w.length > 2);
    if (q.includes(title)) score += 10;
    for (const word of words) if (q.includes(word)) score += 3;
    if (q.includes(topic.slug.replace(/-/g, " "))) score += 6;
    if (score > bestScore) {
      bestScore = score;
      best = topic;
    }
  }
  return bestScore >= 9 ? best : null;
}

function referenceBlock(topic) {
  if (!topic) return "";
  const parts = [
    `Reference notes for ${topic.title} (${topic.subject}). Use them only if they answer the question:`,
    topic.definition,
  ];
  if (topic.how && topic.how.length) parts.push(`How it works: ${topic.how.slice(0, 4).join(" ")}`);
  if (topic.complexity && Object.keys(topic.complexity).length) {
    parts.push(
      `Complexity: ${Object.entries(topic.complexity)
        .map(([k, v]) => `${k}: ${v}`)
        .join("; ")}`
    );
  }
  return parts.join("\n");
}

/* ------------------------------------------------------------- streaming */

function sseContent(line) {
  if (!line.startsWith("data:")) return "";
  const payload = line.slice(5).trim();
  if (!payload || payload === "[DONE]") return "";
  try {
    const json = JSON.parse(payload);
    const delta = json.choices && json.choices[0] && json.choices[0].delta;
    return (delta && delta.content) || "";
  } catch {
    return "";
  }
}

function rateLimitSeconds(message) {
  const match = String(message || "").match(/wait\s+(\d+)\s+seconds/i);
  return match ? Number(match[1]) : 20;
}

/* Open the event stream through our edge proxy. A local file server has no
   /api route, so fall back to calling the provider directly while developing. */
async function openStream(messages, signal) {
  const budget = LENGTHS[state.length].budget;
  let response = await fetch("api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages, max_tokens: budget }),
    signal,
  });

  if (response.status === 404 || response.status === 405) {
    response = await fetch(MODEL_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model: MODEL_NAME,
        stream: true,
        temperature: 0.35,
        max_tokens: budget,
        messages,
      }),
      signal,
    });
  }
  return response;
}

async function streamAnswer(question, { signal, onDelta, onStatus }) {
  const topic = topicFor(question);
  const reference = referenceBlock(topic);
  const messages = [
    { role: "system", content: `${SYSTEM_PROMPT} ${LENGTHS[state.length].rule}` },
    ...state.history.slice(-4).map((m) => ({ role: m.role, content: m.content })),
    {
      role: "user",
      content: reference ? `${question}\n\n${reference}` : question,
    },
  ];

  let response = await openStream(messages, signal);

  if (!response.ok) {
    const text = await response.text().catch(() => "");
    if (response.status === 402 || response.status === 429) {
      const seconds = rateLimitSeconds(text);
      onStatus({ waiting: seconds });
      await new Promise((resolve) => setTimeout(resolve, (seconds + 1) * 1000));
      response = await openStream(messages, signal);
      if (!response.ok) throw new Error("busy");
    } else {
      throw new Error("http");
    }
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let answer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";
    for (const line of lines) {
      const delta = sseContent(line.trim());
      if (!delta) continue;
      answer += delta;
      onDelta(answer);
    }
  }
  if (buffer.trim()) {
    const delta = sseContent(buffer.trim());
    if (delta) {
      answer += delta;
      onDelta(answer);
    }
  }
  return answer.trim();
}

/* ---------------------------------------------------------------- answers */

function answerCacheKey(question) {
  return `${CACHE_PREFIX}.${state.length}.${hash(question.toLowerCase().trim())}`;
}

/* A bot bubble that can stream text and finish with a meta line. */
function createAnswerBubble(placeholder) {
  const wrap = el("div", "msg bot");
  const avatar = el("div", "msg-avatar", "AI");
  avatar.setAttribute("aria-hidden", "true");
  const body = el("div", "msg-body");
  body.appendChild(el("div", "msg-role", "Tutor"));
  const answer = el("div", "answer");
  const text = el("div", "answer-text");
  answer.appendChild(text);
  body.appendChild(answer);
  wrap.append(avatar, body);
  dom.chatLog.appendChild(wrap);

  if (placeholder) {
    const dots = el("span", "typing");
    dots.append(el("span"), el("span"), el("span"));
    dots.setAttribute("aria-label", "Thinking");
    text.appendChild(dots);
  }

  return {
    wrap,
    text,
    setStatus(message) {
      text.innerHTML = "";
      text.appendChild(el("p", "status-line", message));
    },
    setText(value) {
      text.innerHTML = renderMarkdown(value);
    },
    finish({ seconds, cached, onRetry }) {
      text.classList.remove("is-streaming");
      const meta = el("div", "answer-meta");
      meta.appendChild(el("span", "tag", cached ? "Saved answer" : `${seconds}s`));
      meta.appendChild(el("span", "tag", LENGTHS[state.length].label));
      const copy = el("button", null, "Copy");
      copy.type = "button";
      copy.addEventListener("click", async () => {
        try {
          await navigator.clipboard.writeText(text.innerText);
          copy.textContent = "Copied";
          setTimeout(() => (copy.textContent = "Copy"), 1600);
        } catch {
          copy.textContent = "Select and copy";
        }
      });
      meta.appendChild(copy);
      if (onRetry) {
        const retry = el("button", null, "Try again");
        retry.type = "button";
        retry.addEventListener("click", onRetry);
        meta.appendChild(retry);
      }
      body.appendChild(meta);
      scrollChat();
    },
    fail(message, onRetry) {
      text.innerHTML = "";
      const p = el("p", "answer-error", message);
      text.appendChild(p);
      const retry = el("button", "retry-btn", "Try again");
      retry.type = "button";
      retry.addEventListener("click", onRetry);
      text.appendChild(retry);
      scrollChat();
    },
  };
}

function scrollChat(force) {
  if (!dom.chatLog) return;
  const nearBottom =
    dom.chatLog.scrollHeight - dom.chatLog.scrollTop - dom.chatLog.clientHeight < 120;
  if (force || nearBottom) dom.chatLog.scrollTop = dom.chatLog.scrollHeight;
}

function addUserMessage(text) {
  const wrap = el("div", "msg user");
  const avatar = el("div", "msg-avatar", "You");
  avatar.setAttribute("aria-hidden", "true");
  const body = el("div", "msg-body");
  body.appendChild(el("p", null, text));
  wrap.append(avatar, body);
  dom.chatLog.appendChild(wrap);
  scrollChat(true);
}

async function submitQuestion(raw) {
  const question = String(raw || "").trim();
  if (!question || state.busy) return;

  state.busy = true;
  state.controller = new AbortController();
  dom.sendBtn.classList.add("is-stop");
  dom.sendBtn.setAttribute("aria-label", "Stop answering");
  dom.suggest.hidden = true;

  addUserMessage(question);
  const bubble = createAnswerBubble(true);
  const started = Date.now();
  let received = false;

  const cached = readCache(answerCacheKey(question));
  const render = (value) => {
    if (!value) return;
    if (!received) {
      received = true;
      bubble.text.innerHTML = "";
      bubble.text.classList.add("is-streaming");
    }
    bubble.setText(value);
    scrollChat();
  };

  if (cached) {
    render(cached);
    bubble.finish({ seconds: 0, cached: true });
    state.history.push({ role: "user", content: question });
    state.history.push({ role: "assistant", content: cached });
    finishBusy();
    return;
  }

  try {
    const answer = await streamAnswer(question, {
      signal: state.controller.signal,
      onDelta: render,
      onStatus: ({ waiting }) =>
        bubble.setStatus(`The free model is busy, retrying in ${waiting} seconds.`),
    });
    if (!answer) throw new Error("empty");
    bubble.setText(answer);
    writeCache(answerCacheKey(question), answer);
    bubble.finish({ seconds: Math.max(1, Math.round((Date.now() - started) / 1000)) });
    state.history.push({ role: "user", content: question });
    state.history.push({ role: "assistant", content: answer });
  } catch (error) {
    if (error.name === "AbortError") {
      bubble.setText("Stopped. Ask again whenever you are ready.");
    } else if (error.message === "busy") {
      bubble.fail("The free model is still busy. Wait a few seconds and try again.", () =>
        retry(question, bubble)
      );
    } else {
      bubble.fail("The answer could not load. Check your connection and try again.", () =>
        retry(question, bubble)
      );
    }
  } finally {
    finishBusy();
  }
}

function retry(question, bubble) {
  bubble.wrap.remove();
  const lastUser = state.history[state.history.length - 1];
  if (lastUser && lastUser.role === "user" && lastUser.content === question) state.history.pop();
  if (state.history[state.history.length - 1]?.role === "assistant") state.history.pop();
  if (dom.chatLog.lastElementChild && dom.chatLog.lastElementChild.classList.contains("user")) {
    dom.chatLog.lastElementChild.remove();
  }
  submitQuestion(question);
}

function finishBusy() {
  state.busy = false;
  state.controller = null;
  dom.sendBtn.classList.remove("is-stop");
  dom.sendBtn.setAttribute("aria-label", "Send question");
}

/* ------------------------------------------------------------ chapter notes */

const STOPWORDS = new Set([
  "and", "the", "for", "with", "from", "into", "over", "under", "basic", "basics",
  "introduction", "concept", "concepts", "advanced", "using", "types", "type", "other",
  "data", "computer", "system", "network", "fundamental", "fundamentals", "method", "methods",
  "programming", "language", "representation", "structure", "structures", "technology",
  "application", "applications", "management", "information", "theory", "analysis",
]);

function stem(word) {
  if (word.length > 5 && word.endsWith("ing")) return word.slice(0, -3);
  if (word.length > 5 && word.endsWith("ies")) return `${word.slice(0, -3)}y`;
  if (word.length > 4 && word.endsWith("es")) return word.slice(0, -2);
  if (word.length > 3 && word.endsWith("s")) return word.slice(0, -1);
  return word;
}

function words(text) {
  return String(text || "")
    .toLowerCase()
    .split(/[^a-z0-9+*]+/)
    .map(stem)
    .filter((w) => w.length > 3 && !STOPWORDS.has(w));
}

/* Chapters are broad ("Sorting", "Trees And Graphs"), so match any saved note
   that shares a real keyword with the chapter title. */
function topicsForChapter(chapterTitle) {
  const chapterWords = new Set(words(chapterTitle));
  if (!chapterWords.size) return [];
  const scored = [];
  for (const topic of state.topics) {
    const titleWords = words(topic.title);
    const slugWords = words(topic.slug);
    let score = 0;
    for (const word of [...titleWords, ...slugWords]) {
      if (chapterWords.has(word)) score += 1;
    }
    if (score) scored.push({ topic, score });
  }
  scored.sort((a, b) => b.score - a.score);
  return scored.slice(0, 2).map((item) => item.topic);
}

function chapterNote(subject, chapterTitle) {
  const matches = topicsForChapter(chapterTitle);
  const panel = el("div", "chapter-panel");

  const head = el("div", "chapter-panel__head");
  head.append(
    el("span", "chapter-panel__code", subject.code || "CSIT"),
    el("strong", null, chapterTitle)
  );
  panel.appendChild(head);

  if (matches.length) {
    panel.appendChild(
      el("p", "chapter-panel__def", "Related saved notes for this chapter. Read the summary here, then ask the tutor for a full worked example.")
    );
    for (const topic of matches) {
      const note = el("div", "topic-note");
      note.appendChild(el("h3", "topic-note__title", topic.title));
      note.appendChild(el("p", null, topic.definition));
      if (topic.how && topic.how.length) {
        const list = el("ul", "chapter-panel__list");
        topic.how.slice(0, 3).forEach((line) => list.appendChild(el("li", null, line)));
        note.appendChild(list);
      }
      if (topic.complexity && Object.keys(topic.complexity).length) {
        const bits = Object.entries(topic.complexity)
          .map(([k, v]) => `${k}: ${v}`)
          .join(" | ");
        note.appendChild(el("p", "chapter-panel__meta", bits));
      }
      panel.appendChild(note);
    }
  } else {
    panel.appendChild(
      el(
        "p",
        "chapter-panel__def",
        `This chapter is best explained live. The tutor will walk through ${chapterTitle} with an example tailored to ${subject.name}.`
      )
    );
  }

  const actions = el("div", "chapter-panel__actions");
  const ask = el("button", "btn-inline", "Ask about this chapter");
  ask.type = "button";
  ask.addEventListener("click", () => {
    openTutor(`Explain ${chapterTitle} for ${subject.name} (${subject.code}) with a worked example.`);
  });
  actions.appendChild(ask);
  const needs = el("button", "btn-inline btn-inline--ghost", "Type my own question");
  needs.type = "button";
  needs.addEventListener("click", () => openTutor(""));
  actions.appendChild(needs);
  panel.appendChild(actions);
  return panel;
}

/* ------------------------------------------------------------------- views */

function showView(name) {
  const target = document.getElementById(`view-${name}`);
  if (!target) return;
  document.querySelectorAll(".view").forEach((v) => v.classList.toggle("is-active", v === target));
  document.querySelectorAll(".tab").forEach((t) => {
    const on = t.dataset.view === name;
    t.classList.toggle("is-active", on);
    t.setAttribute("aria-selected", String(on));
  });
  history.replaceState(null, "", `#${name}`);
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function openTutor(question) {
  showView("tutor");
  dom.askInput.value = question;
  dom.askInput.focus();
  dom.askInput.dispatchEvent(new Event("input"));
  if (!question) dom.askInput.scrollIntoView({ block: "center", behavior: "smooth" });
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
    const noteSlot = el("div", "chapter-slot");

    if (subject.chapters.length) {
      const list = el("div", "chapters");
      subject.chapters.forEach((chapter) => {
        const chip = el("button", "chapter");
        chip.type = "button";
        chip.append(el("span", null, "\u203a"), document.createTextNode(chapter.title));
        chip.addEventListener("click", () => {
          const existing = noteSlot.querySelector(".chapter-panel");
          const alreadyOpen = existing && existing.dataset.title === chapter.title;
          noteSlot.innerHTML = "";
          list.querySelectorAll(".chapter").forEach((c) => c.classList.remove("is-open"));
          if (alreadyOpen) return;
          chip.classList.add("is-open");
          const panel = chapterNote(subject, chapter.title);
          panel.dataset.title = chapter.title;
          noteSlot.appendChild(panel);
        });
        list.appendChild(chip);
      });
      bodyEl.append(list, noteSlot);
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
    empty.append(
      el("strong", null, "Nothing matches that search"),
      document.createTextNode("Try a shorter phrase, or clear the subject filter.")
    );
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
      const started = Date.now();
      let text = "";
      const target = el("div", "answer");
      try {
        const answer = await streamAnswer(`Solve this past TU BSc CSIT board question step by step, then give the final answer:\n\n${q.title}`, {
          signal: new AbortController().signal,
          onDelta: (value) => {
            text = value;
            target.innerHTML = renderMarkdown(value);
            if (!target.isConnected) {
              solution.innerHTML = "";
              solution.appendChild(target);
            }
          },
          onStatus: () => {},
        });
        target.innerHTML = renderMarkdown(answer);
        solution.innerHTML = "";
        solution.appendChild(target);
        const meta = el("div", "answer-meta");
        meta.appendChild(el("span", "tag", `${Math.max(1, Math.round((Date.now() - started) / 1000))}s`));
        meta.appendChild(el("span", "tag", q.code || q.subject));
        solution.appendChild(meta);
      } catch {
        delete solution.dataset.loaded;
        solution.innerHTML =
          '<div class="answer"><p class="answer-error">The solution could not load. Check your connection and try again.</p></div>';
        toggle.textContent = "Show solution";
        card.classList.remove("is-open");
        solution.dataset.loaded = "";
      }
    });

    ask.addEventListener("click", () => {
      openTutor(`Solve this past TU board question step by step: ${q.title}`);
    });

    dom.qList.appendChild(card);
  });

  if (rows.length > 120) {
    dom.qList.appendChild(
      el("p", "empty", `Showing the first 120 of ${rows.length} matches. Narrow the search to see the rest.`)
    );
  }
}

/* -------------------------------------------------------------------- init */

function bindTutor() {
  dom.askForm.addEventListener("submit", (event) => {
    event.preventDefault();
    if (state.busy) {
      state.controller?.abort();
      return;
    }
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
    state.controller?.abort();
    state.history = [];
    dom.suggest.hidden = false;
    welcome();
  });

  dom.lenHint.textContent = LENGTHS[state.length].hint;
}

function welcome() {
  dom.chatLog.innerHTML = "";
  const wrap = el("div", "msg bot");
  const avatar = el("div", "msg-avatar", "AI");
  avatar.setAttribute("aria-hidden", "true");
  const body = el("div", "msg-body");
  body.appendChild(el("div", "msg-role", "Tutor"));
  const answer = el("div", "answer");
  answer.innerHTML = renderMarkdown(
    "Ask me anything from the TU BSc CSIT programme. I answer the question you actually asked, with code and complexity where they matter.\n\n" +
      "Try *Explain the working of a relational join*, *Derive the worst case of quick sort*, or paste a question from your exam paper."
  );
  body.appendChild(answer);
  wrap.append(avatar, body);
  dom.chatLog.appendChild(wrap);
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
    const [studyRes, topicsRes] = await Promise.all([
      fetch("data/study.json"),
      fetch("data/topics.json").catch(() => null),
    ]);
    if (!studyRes.ok) throw new Error(String(studyRes.status));
    state.data = await studyRes.json();
    if (topicsRes && topicsRes.ok) state.topics = await topicsRes.json();
    renderSemesters();
    renderCourses();
    renderQuestions();
    setStatus(`${state.data.totals.subjects} subjects, ${state.data.totals.chapters} chapters`, "live");
  } catch {
    setStatus("Syllabus unavailable", "warn");
    dom.courseList.innerHTML = "";
    const empty = el("div", "empty");
    empty.append(
      el("strong", null, "The syllabus could not load"),
      document.createTextNode("Refresh the page. The tutor still works.")
    );
    dom.courseList.appendChild(empty);
  }
}

document.addEventListener("DOMContentLoaded", boot);
