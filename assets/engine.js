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

  // Question Prompt + Image Builder
  let questionHTML = `<div class="mb-3 text-slate-900 dark:text-slate-100 font-normal leading-relaxed">${q.question || ''}</div>`;
  
  if (q.image) {
    questionHTML += `
      <div class="my-3 max-w-lg">
        <div class="inline-block rounded-xl border border-slate-200 dark:border-slate-800 bg-white p-2 shadow-xs cursor-zoom-in" onclick="openImageModal('${q.image}')">
          <img src="${q.image}" alt="Question Diagram" 
               class="max-h-56 sm:max-h-72 w-auto object-contain rounded-lg hover:opacity-95 transition-opacity" 
               loading="lazy" 
               onerror="this.parentElement.style.display='none'" />
        </div>
        <span class="block text-[11px] text-slate-400 mt-1">Tap image to expand</span>
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
          <input type="radio" name="opt" value="${idx}" ${isChecked} onchange="recordChoice(${idx})" class="w-4 h-4 text-indigo-600 focus:ring-indigo-500">
          <span class="text-sm font-medium">(${String.fromCharCode(65 + idx)}) ${opt}</span>
        </label>`;
    });
  } else if (q.type === 'multiple_choice' && Array.isArray(q.options)) {
    const checkedArr = Array.isArray(resp) ? resp : [];
    q.options.forEach((opt, idx) => {
      const isChecked = checkedArr.includes(idx) ? 'checked' : '';
      container.innerHTML += `
        <label class="flex items-center gap-3 p-3.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-800/60 transition-colors">
          <input type="checkbox" value="${idx}" ${isChecked} onchange="recordMultiChoice(${idx})" class="w-4 h-4 text-indigo-600 rounded focus:ring-indigo-500">
          <span class="text-sm font-medium">(${String.fromCharCode(65 + idx)}) ${opt}</span>
        </label>`;
    });
  } else if (q.type === 'numerical') {
    const val = resp !== null && resp !== undefined ? resp : '';
    container.innerHTML = `
      <div class="max-w-xs pt-2">
        <input type="number" step="any" placeholder="Enter numerical answer" value="${val}" oninput="recordNumerical(this.value)"
          class="w-full px-4 py-2.5 border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm md:text-base">
      </div>`;
  }

  renderPalette();
  setTimeout(renderMath, 20);
}

// Modal zoom helper
function openImageModal(src) {
  let modal = document.getElementById('image-modal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'image-modal';
    modal.className = 'fixed inset-0 z-50 bg-black/80 backdrop-blur-xs flex items-center justify-center p-4 cursor-zoom-out';
    modal.onclick = () => modal.remove();
    document.body.appendChild(modal);
  }
  modal.innerHTML = `
    <div class="relative max-w-4xl max-h-[90vh] bg-white p-2 rounded-2xl shadow-2xl">
      <img src="${src}" class="max-h-[85vh] max-w-full object-contain rounded-xl" />
    </div>`;
}