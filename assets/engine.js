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

async function initExamEngine() {
  const titleEl = document.getElementById('test-title');
  try {
    const res = await fetch('./test.json');
    if (!res.ok) throw new Error(`HTTP ${res.status}: Could not load ./test.json (Check file path & local server)`);
    
    testData = await res.json();

    if (!testData.sections || !Array.isArray(testData.sections)) {
      throw new Error("Invalid test.json structure: 'sections' array missing.");
    }

    let rawQuestions = [];
    testData.sections.forEach(sec => {
      (sec.questions || []).forEach(q => rawQuestions.push({ ...q, subject: sec.subject }));
    });

    if (rawQuestions.length === 0) {
      throw new Error("No questions found in test.json.");
    }

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
    console.error("Exam load error:", err);
    document.body.innerHTML = `
      <div class="min-h-screen flex items-center justify-center p-6 bg-slate-100 dark:bg-slate-950">
        <div class="max-w-md w-full bg-white dark:bg-slate-900 border border-rose-200 dark:border-rose-900/50 p-6 rounded-2xl shadow-lg space-y-4">
          <div class="text-rose-500 font-bold text-lg">⚠️ Failed to Load Test</div>
          <p class="text-sm text-slate-600 dark:text-slate-400 font-mono bg-slate-50 dark:bg-slate-800 p-3 rounded-lg break-words">
            ${err.message}
          </p>
          <div class="text-xs text-slate-500 space-y-1">
            <p><strong>Common Fixes:</strong></p>
            <p>1. Make sure you are serving via a web server (e.g. VS Code Live Server or python -m http.server), not opening the raw file.</p>
            <p>2. Verify that <code>test.json</code> exists inside this test folder.</p>
          </div>
          <a href="../../index.html" class="inline-block w-full text-center px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-semibold">
            Return to Portal Home
          </a>
        </div>
      </div>`;
  }
}

function renderMath() {
  if (window.renderMathInElement) {
    try {
      renderMathInElement(document.body, {
        delimiters: [
          { left: '$$', right: '$$', display: true },
          { left: '$', right: '$', display: false }
        ],
        throwOnError: false
      });
    } catch (e) {
      console.warn("KaTeX render error:", e);
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
      <div class="my-4 max-w-lg">
        <img src="${q.image}" alt="Question Diagram" 
             class="rounded-xl border border-slate-200 dark:border-slate-800 bg-white p-2 shadow-sm max-h-72 object-contain w-auto"
             onerror="this.style.display='none'" />
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
        <label class="flex items-center gap-3 p-3.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-800/60">
          <input type="radio" name="opt" value="${idx}" ${isChecked} onchange="recordChoice(${idx})" class="w-4 h-4 text-indigo-600">
          <span class="text-sm font-medium">(${String.fromCharCode(65 + idx)}) ${opt}</span>
        </label>`;
    });
  } else if (q.type === 'multiple_choice' && Array.isArray(q.options)) {
    const checkedArr = Array.isArray(resp) ? resp : [];
    q.options.forEach((opt, idx) => {
      const isChecked = checkedArr.includes(idx) ? 'checked' : '';
      container.innerHTML += `
        <label class="flex items-center gap-3 p-3.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-800/60">
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
  setTimeout(renderMath, 20);
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