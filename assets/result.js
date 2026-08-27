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
      console.warn("KaTeX rendering note:", e);
    }
  }
}

async function initResultView() {
  try {
    const res = await fetch('./test.json');
    if (!res.ok) throw new Error("Could not load test.json from this folder.");
    const localTestData = await res.json();

    // Check for saved session responses
    const storageKey = `sma_result_${localTestData.testId}`;
    let rawData = sessionStorage.getItem(storageKey);

    let sessionData;
    let isPracticeMode = false;

    if (rawData) {
      sessionData = JSON.parse(rawData);
    } else {
      // Fallback: If accessed directly as a solutions sheet
      isPracticeMode = true;
      let rawQuestions = [];
      (localTestData.sections || []).forEach(sec => {
        (sec.questions || []).forEach(q => rawQuestions.push({ ...q, subject: sec.subject }));
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
    console.error("Result view failed to initialize:", err);
    const container = document.getElementById('result-main');
    if (container) {
      container.innerHTML = `
        <div class="p-8 text-center bg-white dark:bg-slate-900 rounded-2xl border border-rose-200 dark:border-rose-900/50 shadow-sm space-y-3">
          <div class="text-rose-500 font-bold text-lg">⚠️ Unable to Load Results</div>
          <p class="text-sm text-slate-500">${err.message}</p>
          <a href="../../index.html" class="inline-block mt-3 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-semibold">
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

  const evaluated = data.questions.map((q, idx) => {
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
        formattedUserAnswer = `(${String.fromCharCode(65 + userResp)}) ${q.options[userResp]}`;
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
        .map(i => `(${String.fromCharCode(65 + i)}) ${q.options[i]}`)
        .join(', ');

      if (Array.isArray(userResp) && userResp.length > 0) {
        const sortedUser = [...userResp].sort();
        formattedUserAnswer = sortedUser
          .map(i => `(${String.fromCharCode(65 + i)}) ${q.options[i]}`)
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

  // Safe DOM population
  const titleEl = document.getElementById('res-test-title');
  const subEl = document.getElementById('res-submitted-at');
  const scoreEl = document.getElementById('res-score');
  const totalMarksEl = document.getElementById('res-total-marks');
  const accEl = document.getElementById('res-accuracy');
  const corrEl = document.getElementById('res-correct-count');
  const incorrEl = document.getElementById('res-incorrect-count');
  const unattEl = document.getElementById('res-unattempted-count');

  if (titleEl) titleEl.innerText = data.testTitle || 'Test Solutions';
  if (subEl) subEl.innerText = isPracticeMode ? 'Viewing Solutions Sheet' : `Submitted on ${data.submittedAt}`;
  if (scoreEl) scoreEl.innerText = isPracticeMode ? '--' : totalScore;
  if (totalMarksEl) totalMarksEl.innerText = `/ ${data.totalMarks}`;
  if (accEl) accEl.innerText = isPracticeMode ? '--' : `${accuracy}%`;
  if (corrEl) corrEl.innerText = isPracticeMode ? '--' : correct;
  if (incorrEl) incorrEl.innerText = isPracticeMode ? '--' : incorrect;
  if (unattEl) unattEl.innerText = isPracticeMode ? evaluated.length : unattempted;

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
    card.className = `bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-5 md:p-6 shadow-sm ${border} space-y-4`;

    let questionContent = `<div class="text-slate-800 dark:text-slate-100 text-base leading-relaxed">${q.question || ''}</div>`;
    if (q.image) {
      questionContent += `
        <div class="my-3 max-w-md">
          <img src="${q.image}" alt="Question Diagram" class="rounded-xl border border-slate-200 dark:border-slate-800 bg-white p-2 max-h-60 object-contain w-auto" onerror="this.style.display='none'" />
        </div>`;
    }

    card.innerHTML = `
      <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
        <span class="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">${q.subject} • Question ${q.index}</span>
        ${badge}
      </div>

      ${questionContent}

      <div class="grid grid-cols-1 ${!isPracticeMode ? 'md:grid-cols-2' : ''} gap-3 pt-2 text-sm">
        ${!isPracticeMode ? `
          <div class="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800">
            <span class="text-xs font-semibold text-slate-400 block mb-1">Your Answer</span>
            <div class="font-medium ${q.status === 'correct' ? 'text-emerald-600 dark:text-emerald-400' : q.status === 'incorrect' ? 'text-rose-600 dark:text-rose-400' : 'text-slate-500'}">
              ${q.formattedUserAnswer}
            </div>
          </div>
        ` : ''}

        <div class="p-3 rounded-lg bg-emerald-50/50 dark:bg-emerald-950/20 border border-emerald-100 dark:border-emerald-900/40">
          <span class="text-xs font-semibold text-emerald-600 dark:text-emerald-400 block mb-1">Correct Answer</span>
          <div class="font-medium text-emerald-700 dark:text-emerald-300">
            ${q.formattedCorrectAnswer}
          </div>
        </div>
      </div>

      ${(q.solution || q.solutionImage) ? `
        <div class="mt-4 p-4 rounded-xl bg-indigo-50/40 dark:bg-indigo-950/20 border border-indigo-100 dark:border-indigo-900/40 text-sm space-y-2">
          <span class="text-xs font-bold text-indigo-600 dark:text-indigo-400 block">Explanation & Solution:</span>
          ${q.solution ? `<div class="text-slate-700 dark:text-slate-300 leading-relaxed">${q.solution}</div>` : ''}
          ${q.solutionImage ? `
            <div class="pt-2 max-w-md">
              <img src="${q.solutionImage}" alt="Solution Diagram" class="rounded-lg border border-slate-200 dark:border-slate-800 bg-white p-1.5 max-h-52 object-contain w-auto" onerror="this.style.display='none'" />
            </div>` : ''}
        </div>` : ''}
    `;

    container.appendChild(card);
  });

  setTimeout(renderMath, 20);
}