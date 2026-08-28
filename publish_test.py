import os
import sys
import json
import datetime

# --- HTML Template: Self-Contained Test Engine ---
TEST_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
  <title>Online Assessment | SMA Test Portal</title>
  <meta name="robots" content="noindex, nofollow" />

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'media',
      theme: { extend: { fontFamily: { sans: ['Inter', 'sans-serif'] } } }
    }
  </script>

  <!-- KaTeX -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js"></script>

  <style>
    .katex-display { overflow-x: auto; overflow-y: hidden; padding: 4px 0; }
    .safe-bottom { padding-bottom: max(1rem, env(safe-area-inset-bottom)); }
  </style>
</head>
<body class="bg-slate-100 dark:bg-slate-950 text-slate-900 dark:text-slate-100 min-h-screen flex flex-col select-none antialiased">

  <header class="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 px-3 md:px-4 py-2.5 flex items-center justify-between sticky top-0 z-20 shadow-xs">
    <div class="flex items-center space-x-2">
      <a href="../../index.html" class="text-xs md:text-sm font-bold text-indigo-600 dark:text-indigo-400 p-1">← Exit</a>
      <span class="text-slate-300 dark:text-slate-700">|</span>
      <h1 id="test-title" class="font-bold text-xs md:text-base truncate max-w-[140px] sm:max-w-xs md:max-w-md">Loading...</h1>
    </div>
    
    <div class="flex items-center space-x-2 md:space-x-3">
      <button onclick="toggleMobilePalette()" class="lg:hidden px-2.5 py-1.5 rounded-lg border border-slate-300 dark:border-slate-700 text-xs font-bold bg-slate-50 dark:bg-slate-800">
        📑 Qs
      </button>
      <div class="bg-indigo-50 dark:bg-slate-800 px-2.5 py-1.5 rounded-lg border border-indigo-100 dark:border-slate-700 font-mono font-bold text-xs md:text-sm text-indigo-700 dark:text-indigo-400">
        ⏱ <span id="timer-display">--:--</span>
      </div>
      <button onclick="confirmSubmit()" class="bg-emerald-600 hover:bg-emerald-500 active:scale-95 text-white text-xs md:text-sm font-bold px-3 py-1.5 md:px-4 md:py-2 rounded-lg shadow-sm">
        Submit
      </button>
    </div>
  </header>

  <div class="flex-1 flex flex-col lg:flex-row overflow-hidden pb-20 lg:pb-0">
    <main class="flex-1 flex flex-col justify-between p-4 md:p-6 overflow-y-auto">
      <div class="space-y-4 md:space-y-6 max-w-3xl">
        <div class="flex items-center justify-between text-xs font-bold text-slate-500 dark:text-slate-400 border-b border-slate-200 dark:border-slate-800 pb-2">
          <span id="question-meta">Subject: -- | Question --</span>
          <span id="marking-scheme" class="text-indigo-600 dark:text-indigo-400">Marks: +4, -1</span>
        </div>

        <div id="question-text" class="text-sm md:text-lg text-slate-900 dark:text-slate-100 leading-relaxed font-normal">
          <div class="p-8 text-center text-slate-400 animate-pulse">Loading question...</div>
        </div>
        
        <div id="options-container" class="space-y-2.5 pt-2"></div>
      </div>

      <div class="hidden lg:flex mt-8 pt-4 border-t border-slate-200 dark:border-slate-800 flex-wrap gap-3 items-center justify-between">
        <div class="flex gap-2">
          <button onclick="saveAndNext()" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-semibold">Save & Next</button>
          <button onclick="markForReviewAndNext()" class="px-4 py-2 bg-amber-500 hover:bg-amber-400 text-white rounded-lg text-sm font-semibold">Mark for Review</button>
          <button onclick="clearResponse()" class="px-3 py-2 bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300 rounded-lg text-sm font-medium">Clear</button>
        </div>
        <div class="flex gap-2">
          <button onclick="prevQuestion()" class="px-3 py-2 bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-lg text-sm font-medium">Previous</button>
          <button onclick="nextQuestion()" class="px-3 py-2 bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-lg text-sm font-medium">Next</button>
        </div>
      </div>
    </main>

    <aside id="palette-drawer" class="fixed lg:static inset-x-0 bottom-0 z-40 bg-white dark:bg-slate-900 border-t lg:border-t-0 lg:border-l border-slate-200 dark:border-slate-800 p-4 w-full lg:w-80 transform translate-y-full lg:translate-y-0 transition-transform duration-200 ease-in-out shadow-2xl lg:shadow-none max-h-[75vh] lg:max-h-none flex flex-col justify-between rounded-t-2xl lg:rounded-none">
      <div>
        <div class="flex items-center justify-between mb-3">
          <h3 class="font-bold text-sm">Question Palette</h3>
          <button onclick="toggleMobilePalette()" class="lg:hidden text-slate-400 p-1 font-bold text-base">✕</button>
        </div>
        <div id="palette-grid" class="grid grid-cols-5 gap-2 max-h-52 lg:max-h-96 overflow-y-auto p-1"></div>
      </div>

      <div class="mt-4 pt-3 border-t border-slate-200 dark:border-slate-800 grid grid-cols-2 gap-2 text-[11px] text-slate-600 dark:text-slate-400">
        <div class="flex items-center gap-1.5"><span class="w-3 h-3 rounded bg-emerald-500 shrink-0"></span> Answered</div>
        <div class="flex items-center gap-1.5"><span class="w-3 h-3 rounded bg-amber-500 shrink-0"></span> Marked</div>
        <div class="flex items-center gap-1.5"><span class="w-3 h-3 rounded bg-rose-500 shrink-0"></span> Unanswered</div>
        <div class="flex items-center gap-1.5"><span class="w-3 h-3 rounded bg-slate-200 dark:bg-slate-700 shrink-0"></span> Not Visited</div>
      </div>
    </aside>
  </div>

  <div class="lg:hidden fixed bottom-0 inset-x-0 bg-white/95 dark:bg-slate-900/95 backdrop-blur-md border-t border-slate-200 dark:border-slate-800 p-2.5 z-30 flex items-center justify-between safe-bottom">
    <div class="flex gap-1.5">
      <button onclick="prevQuestion()" class="p-2.5 bg-slate-100 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg text-xs font-bold">◀</button>
      <button onclick="nextQuestion()" class="p-2.5 bg-slate-100 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg text-xs font-bold">▶</button>
      <button onclick="clearResponse()" class="px-2.5 py-2 bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300 rounded-lg text-xs font-semibold">Clear</button>
    </div>
    <div class="flex gap-1.5">
      <button onclick="markForReviewAndNext()" class="px-3 py-2 bg-amber-500 text-white rounded-lg text-xs font-bold">Review</button>
      <button onclick="saveAndNext()" class="px-4 py-2 bg-indigo-600 text-white rounded-lg text-xs font-bold shadow-sm">Save & Next</button>
    </div>
  </div>

  <script>
    let testData = null;
    let questions = [];
    let currentIndex = 0;
    let userResponses = {};
    let timerInterval = null;
    let timeRemaining = 0;

    function shuffle(array) {
      for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
      }
      return array;
    }

    function processAndShuffleOptions(q) {
      if (!q.options || q.type === 'numerical') return q;
      const mapped = q.options.map((text, idx) => ({ text, originalIndex: idx }));
      shuffle(mapped);
      const newOptions = mapped.map(o => o.text);

      if (q.type === 'single_choice') {
        const newCorrect = mapped.findIndex(o => o.originalIndex === q.correctOption);
        return { ...q, options: newOptions, correctOption: newCorrect };
      }
      if (q.type === 'multiple_choice') {
        const newCorrect = (q.correctOptions || []).map(orig => mapped.findIndex(o => o.originalIndex === orig)).sort();
        return { ...q, options: newOptions, correctOptions: newCorrect };
      }
      return q;
    }

    async function startTestEngine() {
      const titleEl = document.getElementById('test-title');
      try {
        const res = await fetch('./test.json');
        if (!res.ok) throw new Error("HTTP " + res.status + ": Could not find test.json");
        testData = await res.json();

        let rawQuestions = [];
        (testData.sections || []).forEach(sec => {
          (sec.questions || []).forEach(q => rawQuestions.push({ ...q, subject: sec.subject || 'General' }));
        });

        if (rawQuestions.length === 0) throw new Error("No questions found in test.json.");

        questions = shuffle(rawQuestions).map(q => processAndShuffleOptions(q));
        questions.forEach(q => {
          userResponses[q.id] = { value: null, status: 'not_visited' };
        });

        if (titleEl) titleEl.innerText = testData.title || "Assessment";
        timeRemaining = (testData.durationMinutes || 60) * 60;

        startTimer();
        renderPalette();
        loadQuestion(0);
      } catch (err) {
        console.error("Critical Engine Error:", err);
        document.body.innerHTML = `
          <div class="min-h-screen flex items-center justify-center p-6 bg-slate-100 dark:bg-slate-950">
            <div class="max-w-md w-full bg-white dark:bg-slate-900 border border-rose-200 dark:border-rose-900/50 p-6 rounded-2xl shadow-lg space-y-4">
              <div class="text-rose-500 font-bold text-lg">⚠️ Unable to Load Test</div>
              <p class="text-xs text-slate-600 dark:text-slate-400 font-mono bg-slate-50 dark:bg-slate-800 p-3 rounded-lg break-words">
                ${err.message}
              </p>
              <a href="../../index.html" class="inline-block w-full text-center px-4 py-2.5 bg-indigo-600 text-white rounded-xl text-sm font-semibold">
                Return to Portal Home
              </a>
            </div>
          </div>`;
      }
    }

    function renderMathSafe() {
      if (typeof window.renderMathInElement === 'function') {
        try {
          window.renderMathInElement(document.body, {
            delimiters: [
              { left: '$$', right: '$$', display: true },
              { left: '$', right: '$', display: false }
            ],
            throwOnError: false
          });
        } catch (e) {
          console.warn("KaTeX render note:", e);
        }
      }
    }

    function loadQuestion(index) {
      if (index < 0 || index >= questions.length) return;
      currentIndex = index;
      const q = questions[index];

      if (userResponses[q.id].status === 'not_visited') {
        userResponses[q.id].status = 'not_answered';
      }

      const metaEl = document.getElementById('question-meta');
      if (metaEl) metaEl.innerText = `Subject: ${q.subject} | Question ${index + 1} of ${questions.length}`;

      const marks = q.marking?.correct || q.marking?.full || 4;
      const neg = q.marking?.incorrect !== undefined ? q.marking.incorrect : 0;
      const markingEl = document.getElementById('marking-scheme');
      if (markingEl) markingEl.innerText = `Marks: +${marks}, ${neg}`;

      let questionHTML = `<div class="mb-3">${q.question || ''}</div>`;
      if (q.image) {
        questionHTML += `
          <div class="my-3 max-w-lg">
            <div class="inline-block rounded-xl border border-slate-200 dark:border-slate-800 bg-white p-2 shadow-xs">
              <img src="${q.image}" alt="Question Diagram" class="max-h-56 sm:max-h-72 w-auto object-contain rounded-lg" onerror="this.parentElement.style.display='none'" />
            </div>
          </div>`;
      }
      
      const qTextEl = document.getElementById('question-text');
      if (qTextEl) qTextEl.innerHTML = questionHTML;

      const container = document.getElementById('options-container');
      if (!container) return;
      container.innerHTML = '';
      const resp = userResponses[q.id].value;

      if (q.type === 'single_choice' && Array.isArray(q.options)) {
        q.options.forEach((opt, idx) => {
          const isChecked = resp === idx ? 'checked' : '';
          container.innerHTML += `
            <label class="flex items-center gap-3 p-3.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-800/60 transition-colors">
              <input type="radio" name="opt" value="${idx}" ${isChecked} onchange="recordChoice(${idx})" class="w-4 h-4 text-indigo-600">
              <span class="text-sm font-medium">(${String.fromCharCode(65 + idx)}) ${opt}</span>
            </label>`;
        });
      } else if (q.type === 'multiple_choice' && Array.isArray(q.options)) {
        const checkedArr = Array.isArray(resp) ? resp : [];
        q.options.forEach((opt, idx) => {
          const isChecked = checkedArr.includes(idx) ? 'checked' : '';
          container.innerHTML += `
            <label class="flex items-center gap-3 p-3.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-800/60 transition-colors">
              <input type="checkbox" value="${idx}" ${isChecked} onchange="recordMultiChoice(${idx})" class="w-4 h-4 text-indigo-600 rounded">
              <span class="text-sm font-medium">(${String.fromCharCode(65 + idx)}) ${opt}</span>
            </label>`;
        });
      } else if (q.type === 'numerical') {
        const val = resp !== null && resp !== undefined ? resp : '';
        container.innerHTML = `
          <div class="max-w-xs pt-2">
            <input type="number" step="any" placeholder="Enter numerical answer" value="${val}" oninput="recordNumerical(this.value)"
              class="w-full px-4 py-2.5 border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500">
          </div>`;
      }

      renderPalette();
      setTimeout(renderMathSafe, 40);
    }

    function recordChoice(val) { userResponses[questions[currentIndex].id].value = val; }
    function recordMultiChoice(idx) {
      const qId = questions[currentIndex].id;
      let curr = userResponses[qId].value || [];
      curr = curr.includes(idx) ? curr.filter(i => i !== idx) : [...curr, idx];
      userResponses[qId].value = curr;
    }
    function recordNumerical(val) { userResponses[questions[currentIndex].id].value = val === '' ? null : Number(val); }

    function saveAndNext() {
      const qId = questions[currentIndex].id;
      const resp = userResponses[qId].value;
      userResponses[qId].status = (resp !== null && (!Array.isArray(resp) || resp.length > 0)) ? 'answered' : 'not_answered';
      nextQuestion();
    }

    function markForReviewAndNext() {
      userResponses[questions[currentIndex].id].status = 'marked';
      nextQuestion();
    }

    function clearResponse() {
      const qId = questions[currentIndex].id;
      userResponses[qId].value = null;
      userResponses[qId].status = 'not_answered';
      loadQuestion(currentIndex);
    }

    function nextQuestion() {
      if (currentIndex < questions.length - 1) loadQuestion(currentIndex + 1);
      else renderPalette();
    }

    function prevQuestion() {
      if (currentIndex > 0) loadQuestion(currentIndex - 1);
    }

    function renderPalette() {
      const palette = document.getElementById('palette-grid');
      if (!palette) return;
      palette.innerHTML = '';
      questions.forEach((q, idx) => {
        const st = userResponses[q.id].status;
        let color = 'bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300';
        if (st === 'answered') color = 'bg-emerald-500 text-white';
        else if (st === 'marked') color = 'bg-amber-500 text-white';
        else if (st === 'not_answered') color = 'bg-rose-500 text-white';
        const isCurrent = idx === currentIndex ? 'ring-2 ring-indigo-500 ring-offset-2 dark:ring-offset-slate-900 font-black' : '';
        palette.innerHTML += `
          <button onclick="loadQuestion(${idx})" class="h-9 w-9 rounded-lg font-semibold text-xs flex items-center justify-center ${color} ${isCurrent}">
            ${idx + 1}
          </button>`;
      });
    }

    function startTimer() {
      const display = document.getElementById('timer-display');
      if (!display) return;
      timerInterval = setInterval(() => {
        if (timeRemaining <= 0) {
          clearInterval(timerInterval);
          submitTest();
          return;
        }
        timeRemaining--;
        const m = Math.floor(timeRemaining / 60);
        const s = timeRemaining % 60;
        display.innerText = `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
      }, 1000);
    }

    function confirmSubmit() {
      if (confirm("Are you sure you want to submit the test?")) submitTest();
    }

    function submitTest() {
      clearInterval(timerInterval);
      const resultData = {
        testId: testData.testId,
        testTitle: testData.title,
        exam: testData.exam,
        totalMarks: testData.totalMarks || (questions.length * 4),
        questions: questions,
        userResponses: userResponses,
        submittedAt: new Date().toLocaleString()
      };
      sessionStorage.setItem(`sma_result_${testData.testId}`, JSON.stringify(resultData));
      window.location.href = 'result.html';
    }

    function toggleMobilePalette() {
      document.getElementById('palette-drawer').classList.toggle('translate-y-full');
    }

    window.addEventListener('DOMContentLoaded', startTestEngine);
  </script>
</body>
</html>"""

# --- HTML Template: Self-Contained Result Engine ---
RESULT_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Scorecard & Solutions | SMA Test Portal</title>
  <meta name="robots" content="noindex, follow" />

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'media',
      theme: { extend: { fontFamily: { sans: ['Inter', 'sans-serif'] } } }
    }
  </script>

  <!-- KaTeX -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js"></script>

  <style>
    .katex-display { overflow-x: auto; overflow-y: hidden; padding: 4px 0; }
  </style>
</head>
<body class="bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 min-h-screen flex flex-col antialiased">

  <header class="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 sticky top-0 z-10 shadow-xs">
    <div class="max-w-4xl mx-auto px-4 h-14 md:h-16 flex items-center justify-between">
      <div class="flex items-center space-x-2">
        <a href="../../index.html" class="flex items-center space-x-2 focus:outline-none">
          <div class="w-8 h-8 rounded-lg bg-indigo-600 text-white flex items-center justify-center font-extrabold text-xs">SMA</div>
          <span class="font-bold text-base md:text-lg tracking-tight">Performance Summary</span>
        </a>
      </div>
      <a href="../../index.html" class="text-xs md:text-sm font-bold px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white transition-colors">
        Back Home
      </a>
    </div>
  </header>

  <main id="result-main" class="max-w-4xl mx-auto px-4 py-6 md:py-8 flex-1 w-full space-y-6 md:space-y-8">
    <div class="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-5 md:p-8 shadow-sm">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-100 dark:border-slate-800 pb-5">
        <div>
          <span class="text-[11px] font-bold uppercase tracking-wider text-indigo-600 dark:text-indigo-400">Scorecard</span>
          <h2 id="res-test-title" class="text-xl md:text-2xl font-bold mt-0.5 text-slate-900 dark:text-white">Calculating Result...</h2>
          <p id="res-submitted-at" class="text-xs text-slate-500 dark:text-slate-400 mt-1"></p>
        </div>
        <div class="flex items-baseline gap-2 bg-indigo-50 dark:bg-indigo-950/50 border border-indigo-100 dark:border-indigo-900/50 px-5 py-3 rounded-xl self-start sm:self-auto">
          <span class="text-3xl font-black text-indigo-600 dark:text-indigo-400" id="res-score">0</span>
          <span class="text-slate-400 font-bold text-sm" id="res-total-marks">/ 0</span>
        </div>
      </div>

      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-5">
        <div class="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800 text-center">
          <span class="text-[11px] text-slate-500">Accuracy</span>
          <div class="text-lg font-bold mt-0.5" id="res-accuracy">0%</div>
        </div>
        <div class="p-3 rounded-xl bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-100 dark:border-emerald-900/30 text-center">
          <span class="text-[11px] text-emerald-600 dark:text-emerald-400 font-semibold">Correct</span>
          <div class="text-lg font-bold mt-0.5 text-emerald-600 dark:text-emerald-400" id="res-correct-count">0</div>
        </div>
        <div class="p-3 rounded-xl bg-rose-50 dark:bg-rose-950/30 border border-rose-100 dark:border-rose-900/30 text-center">
          <span class="text-[11px] text-rose-600 dark:text-rose-400 font-semibold">Incorrect</span>
          <div class="text-lg font-bold mt-0.5 text-rose-600 dark:text-rose-400" id="res-incorrect-count">0</div>
        </div>
        <div class="p-3 rounded-xl bg-amber-50 dark:bg-amber-950/30 border border-amber-100 dark:border-amber-900/30 text-center">
          <span class="text-[11px] text-amber-600 dark:text-amber-400 font-semibold">Skipped</span>
          <div class="text-lg font-bold mt-0.5 text-amber-600 dark:text-amber-400" id="res-unattempted-count">0</div>
        </div>
      </div>
    </div>

    <section class="space-y-4">
      <h3 class="text-lg md:text-xl font-bold">Solutions & Step-by-Step Analysis</h3>
      <div id="questions-review-container" class="space-y-4 md:space-y-6">
        <div class="p-8 text-center text-slate-400 animate-pulse">Loading solutions...</div>
      </div>
    </section>
  </main>

  <script>
    function renderMathSafe() {
      if (typeof window.renderMathInElement === 'function') {
        try {
          window.renderMathInElement(document.body, {
            delimiters: [
              { left: '$$', right: '$$', display: true },
              { left: '$', right: '$', display: false }
            ],
            throwOnError: false
          });
        } catch (e) {
          console.warn("KaTeX render note:", e);
        }
      }
    }

    async function loadResultPage() {
      try {
        const res = await fetch('./test.json');
        if (!res.ok) throw new Error("HTTP " + res.status + ": test.json not found");
        const localTestData = await res.json();

        const storageKey = `sma_result_${localTestData.testId}`;
        let rawData = sessionStorage.getItem(storageKey);

        let sessionData;
        let isPracticeMode = false;

        if (rawData) {
          sessionData = JSON.parse(rawData);
        } else {
          isPracticeMode = true;
          let rawQuestions = [];
          (localTestData.sections || []).forEach(sec => {
            (sec.questions || []).forEach(q => rawQuestions.push({ ...q, subject: sec.subject || 'General' }));
          });

          sessionData = {
            testId: localTestData.testId,
            testTitle: localTestData.title,
            exam: localTestData.exam,
            totalMarks: localTestData.totalMarks || (rawQuestions.length * 4),
            questions: rawQuestions,
            userResponses: {},
            submittedAt: 'Solutions / Practice Mode'
          };
        }

        evaluateAndRender(sessionData, isPracticeMode);
      } catch (err) {
        console.error("Result Engine Error:", err);
        const container = document.getElementById('result-main');
        if (container) {
          container.innerHTML = `
            <div class="p-8 text-center bg-white dark:bg-slate-900 rounded-2xl border border-rose-200 dark:border-rose-900/50 shadow-sm space-y-3">
              <div class="text-rose-500 font-bold text-lg">⚠️ Unable to Load Results</div>
              <p class="text-xs text-slate-500 font-mono">${err.message}</p>
              <a href="../../index.html" class="inline-block mt-3 px-4 py-2 bg-indigo-600 text-white rounded-lg text-xs font-semibold">
                Return to Portal Home
              </a>
            </div>`;
        }
      }
    }

    function evaluateAndRender(data, isPracticeMode) {
      let totalScore = 0;
      let correct = 0;
      let incorrect = 0;
      let unattempted = 0;

      const evaluated = (data.questions || []).map((q, idx) => {
        const userResp = data.userResponses[q.id]?.value;
        let status = 'unattempted';
        let marksScored = 0;
        let formattedUserAnswer = 'Not Answered';
        let formattedCorrectAnswer = '';

        const pos = q.marking?.correct || q.marking?.full || 4;
        const neg = q.marking?.incorrect !== undefined ? q.marking.incorrect : 0;

        if (q.type === 'single_choice') {
          const correctIdx = q.correctOption !== undefined ? q.correctOption : 0;
          formattedCorrectAnswer = q.options && q.options[correctIdx] 
            ? `(${String.fromCharCode(65 + correctIdx)}) ${q.options[correctIdx]}` 
            : 'N/A';

          if (userResp !== null && userResp !== undefined) {
            formattedUserAnswer = q.options && q.options[userResp] 
              ? `(${String.fromCharCode(65 + userResp)}) ${q.options[userResp]}` 
              : 'Selected';
            if (userResp === correctIdx) {
              status = 'correct';
              marksScored = pos;
              correct++;
            } else {
              status = 'incorrect';
              marksScored = neg;
              incorrect++;
            }
          } else {
            unattempted++;
          }
        } else if (q.type === 'multiple_choice') {
          const correctArr = q.correctOptions || [];
          const sortedCorrect = [...correctArr].sort();
          formattedCorrectAnswer = sortedCorrect
            .map(i => `(${String.fromCharCode(65 + i)}) ${q.options ? q.options[i] : ''}`)
            .join(', ');

          if (Array.isArray(userResp) && userResp.length > 0) {
            const sortedUser = [...userResp].sort();
            formattedUserAnswer = sortedUser
              .map(i => `(${String.fromCharCode(65 + i)}) ${q.options ? q.options[i] : ''}`)
              .join(', ');

            if (JSON.stringify(sortedUser) === JSON.stringify(sortedCorrect)) {
              status = 'correct';
              marksScored = pos;
              correct++;
            } else {
              status = 'incorrect';
              marksScored = neg;
              incorrect++;
            }
          } else {
            unattempted++;
          }
        } else if (q.type === 'numerical') {
          formattedCorrectAnswer = `${q.correctValue}`;
          if (userResp !== null && userResp !== undefined && userResp !== '') {
            formattedUserAnswer = `${userResp}`;
            if (Number(userResp) === Number(q.correctValue)) {
              status = 'correct';
              marksScored = pos;
              correct++;
            } else {
              status = 'incorrect';
              marksScored = neg;
              incorrect++;
            }
          } else {
            unattempted++;
          }
        }

        totalScore += marksScored;

        return {
          ...q,
          index: idx + 1,
          status,
          marksScored,
          formattedUserAnswer,
          formattedCorrectAnswer
        };
      });

      const attempted = correct + incorrect;
      const accuracy = attempted > 0 ? Math.round((correct / attempted) * 100) : 0;

      document.getElementById('res-test-title').innerText = data.testTitle || 'Assessment Results';
      document.getElementById('res-submitted-at').innerText = isPracticeMode ? 'Mode: Complete Solutions & Answer Key' : `Submitted on ${data.submittedAt}`;
      document.getElementById('res-score').innerText = isPracticeMode ? '--' : totalScore;
      document.getElementById('res-total-marks').innerText = `/ ${data.totalMarks}`;
      document.getElementById('res-accuracy').innerText = isPracticeMode ? '--' : `${accuracy}%`;
      document.getElementById('res-correct-count').innerText = isPracticeMode ? '--' : correct;
      document.getElementById('res-incorrect-count').innerText = isPracticeMode ? '--' : incorrect;
      document.getElementById('res-unattempted-count').innerText = isPracticeMode ? evaluated.length : unattempted;

      const container = document.getElementById('questions-review-container');
      if (!container) return;
      container.innerHTML = '';

      evaluated.forEach(q => {
        let badge = '';
        let border = 'border-l-4 border-l-slate-400';

        if (!isPracticeMode) {
          if (q.status === 'correct') {
            badge = `<span class="px-2.5 py-1 bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-400 font-bold text-xs rounded-full border border-emerald-200 dark:border-emerald-800">Correct (+${q.marksScored})</span>`;
            border = 'border-l-4 border-l-emerald-500';
          } else if (q.status === 'incorrect') {
            badge = `<span class="px-2.5 py-1 bg-rose-100 dark:bg-rose-950 text-rose-700 dark:text-rose-400 font-bold text-xs rounded-full border border-rose-200 dark:border-rose-800">Incorrect (${q.marksScored})</span>`;
            border = 'border-l-4 border-l-rose-500';
          } else {
            badge = `<span class="px-2.5 py-1 bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 font-bold text-xs rounded-full border border-slate-200 dark:border-slate-700">Unattempted (0)</span>`;
          }
        } else {
          badge = `<span class="px-2.5 py-1 bg-indigo-50 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-400 font-bold text-xs rounded-full border border-indigo-200 dark:border-indigo-800">Answer Key</span>`;
          border = 'border-l-4 border-l-indigo-500';
        }

        const card = document.createElement('div');
        card.className = `bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-4 md:p-6 shadow-xs ${border} space-y-4`;

        let questionContent = `<div class="text-slate-900 dark:text-slate-100 text-sm md:text-base leading-relaxed">${q.question || ''}</div>`;
        if (q.image) {
          questionContent += `
            <div class="my-3 max-w-md">
              <div class="inline-block rounded-xl border border-slate-200 dark:border-slate-800 bg-white p-2 shadow-xs">
                <img src="${q.image}" alt="Question Diagram" class="max-h-52 w-auto object-contain rounded-lg" onerror="this.parentElement.style.display='none'" />
              </div>
            </div>`;
        }

        card.innerHTML = `
          <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
            <span class="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">${q.subject} • Question ${q.index}</span>
            ${badge}
          </div>

          ${questionContent}

          <div class="grid grid-cols-1 ${!isPracticeMode ? 'sm:grid-cols-2' : ''} gap-3 pt-2 text-xs md:text-sm">
            ${!isPracticeMode ? `
              <div class="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800">
                <span class="text-[11px] font-semibold text-slate-400 block mb-1">Your Answer</span>
                <div class="font-medium ${q.status === 'correct' ? 'text-emerald-600 dark:text-emerald-400' : q.status === 'incorrect' ? 'text-rose-600 dark:text-rose-400' : 'text-slate-500'}">
                  ${q.formattedUserAnswer}
                </div>
              </div>
            ` : ''}

            <div class="p-3 rounded-lg bg-emerald-50/50 dark:bg-emerald-950/20 border border-emerald-100 dark:border-emerald-900/40">
              <span class="text-[11px] font-semibold text-emerald-600 dark:text-emerald-400 block mb-1">Correct Answer</span>
              <div class="font-medium text-emerald-700 dark:text-emerald-300">
                ${q.formattedCorrectAnswer}
              </div>
            </div>
          </div>

          ${(q.solution || q.solutionImage) ? `
            <div class="mt-4 p-4 rounded-xl bg-indigo-50/40 dark:bg-indigo-950/20 border border-indigo-100 dark:border-indigo-900/40 text-xs md:text-sm space-y-2">
              <span class="font-bold text-indigo-600 dark:text-indigo-400 block">Explanation & Solution:</span>
              ${q.solution ? `<div class="text-slate-700 dark:text-slate-300 leading-relaxed">${q.solution}</div>` : ''}
              ${q.solutionImage ? `
                <div class="pt-2 max-w-md">
                  <div class="inline-block rounded-lg border border-slate-200 dark:border-slate-800 bg-white p-1.5">
                    <img src="${q.solutionImage}" alt="Solution Diagram" class="max-h-48 w-auto object-contain rounded" onerror="this.parentElement.style.display='none'" />
                  </div>
                </div>` : ''}
            </div>` : ''}
        `;

        container.appendChild(card);
      });

      setTimeout(renderMathSafe, 40);
    }

    window.addEventListener('DOMContentLoaded', loadResultPage);
  </script>
</body>
</html>"""


def sync_test_folder(folder_name):
    """
    Looks inside tests/<folder_name>/test.json, builds HTML files, and updates manifest.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    test_dir = os.path.join(base_dir, 'tests', folder_name)
    test_json_path = os.path.join(test_dir, 'test.json')
    manifest_path = os.path.join(base_dir, 'assets', 'tests-manifest.json')

    if not os.path.exists(test_json_path):
        print(f"❌ Error: {test_json_path} does not exist.")
        return False

    with open(test_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    test_id = data.get('testId', folder_name)
    title = data.get('title', 'Untitled Test')
    exam_badge = data.get('exam', 'JEE Main')
    duration_mins = data.get('durationMinutes', 60)
    
    # Auto-detect exam category for filtering (jee-main, jee-adv, neet)
    badge_lower = exam_badge.lower()
    if 'adv' in badge_lower:
        exam_cat = 'jee-adv'
    elif 'neet' in badge_lower:
        exam_cat = 'neet'
    else:
        exam_cat = 'jee-main'

    # Compute total questions
    total_questions = sum(len(sec.get('questions', [])) for sec in data.get('sections', []))

    # 1. Write index.html into the test folder
    with open(os.path.join(test_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(TEST_HTML_TEMPLATE)

    # 2. Write result.html into the test folder
    with open(os.path.join(test_dir, 'result.html'), 'w', encoding='utf-8') as f:
        f.write(RESULT_HTML_TEMPLATE)

    # 3. Update tests-manifest.json
    manifest = []
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
        except Exception:
            manifest = []

    # Remove existing entry if re-publishing the same test
    manifest = [item for item in manifest if item.get('id') != test_id and item.get('testUrl') != f"tests/{folder_name}/index.html"]

    # Demote older tests
    for item in manifest:
        item['isLatest'] = False

    # Prepend new test
    new_entry = {
        "id": test_id,
        "title": title,
        "exam": exam_cat,
        "badge": exam_badge,
        "date": datetime.date.today().strftime("%Y-%m-%d"),
        "duration": f"{duration_mins} mins",
        "questionsCount": total_questions,
        "testUrl": f"tests/{folder_name}/index.html",
        "resultUrl": f"tests/{folder_name}/result.html",
        "isLatest": True
    }
    manifest.insert(0, new_entry)

    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"✅ Successfully registered and deployed test: '{title}'")
    print(f"📁 Folder: tests/{folder_name}/")
    print(f"📝 Questions: {total_questions} | ⏱ Duration: {duration_mins} mins")
    print(f"📑 Manifest updated with {len(manifest)} total tests.")
    return True


if __name__ == '__main__':
    if len(sys.argv) > 1:
        target_folder = sys.argv[1]
    else:
        target_folder = input("Enter test folder name under tests/ (e.g. jee-adv-02): ").strip()

    sync_test_folder(target_folder)