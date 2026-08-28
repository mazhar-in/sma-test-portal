// Inside evaluateAndRender() in assets/result.js:
evaluated.forEach(q => {
  let badge = '', border = 'border-l-4 border-l-slate-400';

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