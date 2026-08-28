import os
import sys
import json
import datetime

# --- HTML Templates for new test folders ---
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
  <script>tailwind.config = { darkMode: 'media', theme: { extend: { fontFamily: { sans: ['Inter', 'sans-serif'] } } } }</script>
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
          <span id="question-meta">Subject: -- | Q--</span>
          <span id="marking-scheme" class="text-indigo-600 dark:text-indigo-400">Marks: +4, -1</span>
        </div>
        <div id="question-text" class="text-sm md:text-lg text-slate-900 dark:text-slate-100 leading-relaxed font-normal"></div>
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

  <script src="../../assets/engine.js"></script>
  <script>
    function toggleMobilePalette() {
      document.getElementById('palette-drawer').classList.toggle('translate-y-full');
    }
    window.addEventListener('DOMContentLoaded', initExamEngine);
  </script>
</body>
</html>"""

RESULT_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Scorecard & Solutions | SMA Test Portal</title>
  <meta name="robots" content="noindex, follow" />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <script src="https://cdn.tailwindcss.com"></script>
  <script>tailwind.config = { darkMode: 'media', theme: { extend: { fontFamily: { sans: ['Inter', 'sans-serif'] } } } }</script>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js"></script>
  <style>.katex-display { overflow-x: auto; overflow-y: hidden; padding: 4px 0; }</style>
</head>
<body class="bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 min-h-screen flex flex-col antialiased">
  <header class="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 sticky top-0 z-10">
    <div class="max-w-4xl mx-auto px-4 h-14 md:h-16 flex items-center justify-between">
      <div class="flex items-center space-x-2">
        <div class="w-8 h-8 rounded-lg bg-indigo-600 text-white flex items-center justify-center font-extrabold text-xs">SMA</div>
        <span class="font-bold text-base md:text-lg tracking-tight">Performance Summary</span>
      </div>
      <a href="../../index.html" class="text-xs md:text-sm font-bold px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white">Back Home</a>
    </div>
  </header>
  <main id="result-main" class="max-w-4xl mx-auto px-4 py-6 md:py-8 flex-1 w-full space-y-6 md:space-y-8">
    <div class="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-5 md:p-8 shadow-sm">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-100 dark:border-slate-800 pb-5">
        <div>
          <span class="text-[11px] font-bold uppercase tracking-wider text-indigo-600 dark:text-indigo-400">Scorecard</span>
          <h2 id="res-test-title" class="text-xl md:text-2xl font-bold mt-0.5 text-slate-900 dark:text-white">Test Results</h2>
          <p id="res-submitted-at" class="text-xs text-slate-500 dark:text-slate-400 mt-1"></p>
        </div>
        <div class="flex items-baseline gap-2 bg-indigo-50 dark:bg-indigo-950/50 border border-indigo-100 dark:border-indigo-900/50 px-5 py-3 rounded-xl">
          <span class="text-3xl font-black text-indigo-600 dark:text-indigo-400" id="res-score">0</span>
          <span class="text-slate-400 font-bold text-sm" id="res-total-marks">/ 0</span>
        </div>
      </div>
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-5">
        <div class="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 text-center"><span class="text-[11px] text-slate-500">Accuracy</span><div class="text-lg font-bold mt-0.5" id="res-accuracy">0%</div></div>
        <div class="p-3 rounded-xl bg-emerald-50 dark:bg-emerald-950/30 text-center"><span class="text-[11px] text-emerald-600">Correct</span><div class="text-lg font-bold mt-0.5 text-emerald-600" id="res-correct-count">0</div></div>
        <div class="p-3 rounded-xl bg-rose-50 dark:bg-rose-950/30 text-center"><span class="text-[11px] text-rose-600">Incorrect</span><div class="text-lg font-bold mt-0.5 text-rose-600" id="res-incorrect-count">0</div></div>
        <div class="p-3 rounded-xl bg-amber-50 dark:bg-amber-950/30 text-center"><span class="text-[11px] text-amber-600">Skipped</span><div class="text-lg font-bold mt-0.5 text-amber-600" id="res-unattempted-count">0</div></div>
      </div>
    </div>
    <section class="space-y-4">
      <h3 class="text-lg md:text-xl font-bold">Solutions & Step-by-Step Analysis</h3>
      <div id="questions-review-container" class="space-y-4 md:space-y-6"></div>
    </section>
  </main>
  <script src="../../assets/result.js"></script>
  <script>window.addEventListener('DOMContentLoaded', initResultView);</script>
</body>
</html>"""


def publish_test_from_file(json_file_path):
    """
    Reads a JSON test specification, prepares the test folder, and updates the manifest.
    """
    if not os.path.exists(json_file_path):
        print(f"❌ Error: File not found -> {json_file_path}")
        return False

    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    test_id = data['testId']
    title = data['title']
    exam_category = data.get('examCategory', 'jee-main')  # 'jee-main', 'jee-adv', 'neet'
    badge_name = data.get('badgeName', 'JEE Main')
    duration_mins = data.get('durationMinutes', 60)
    sections = data.get('sections', [])

    base_dir = os.path.dirname(os.path.abspath(__file__))
    tests_dir = os.path.join(base_dir, 'tests')
    manifest_path = os.path.join(base_dir, 'assets', 'tests-manifest.json')
    test_folder = os.path.join(tests_dir, test_id)

    # 1. Create test and images directory
    os.makedirs(test_folder, exist_ok=True)
    os.makedirs(os.path.join(test_folder, 'images'), exist_ok=True)

    # 2. Compute total questions and marks
    total_questions = sum(len(sec.get('questions', [])) for sec in sections)
    total_marks = data.get('totalMarks', total_questions * 4)

    # 3. Create test.json
    final_test_json = {
        "testId": test_id,
        "title": title,
        "exam": badge_name,
        "durationMinutes": duration_mins,
        "totalMarks": total_marks,
        "sections": sections
    }

    with open(os.path.join(test_folder, 'test.json'), 'w', encoding='utf-8') as f:
        json.dump(final_test_json, f, indent=2, ensure_ascii=False)

    # 4. Write HTML wrappers
    with open(os.path.join(test_folder, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(TEST_HTML_TEMPLATE)

    with open(os.path.join(test_folder, 'result.html'), 'w', encoding='utf-8') as f:
        f.write(RESULT_HTML_TEMPLATE)

    # 5. Update assets/tests-manifest.json
    manifest = []
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
        except Exception:
            manifest = []

    # Demote previous tests
    for item in manifest:
        item['isLatest'] = False

    # Prepend new test
    new_entry = {
        "id": test_id,
        "title": title,
        "exam": exam_category,
        "badge": badge_name,
        "date": datetime.date.today().strftime("%Y-%m-%d"),
        "duration": f"{duration_mins} mins",
        "questionsCount": total_questions,
        "testUrl": f"tests/{test_id}/index.html",
        "resultUrl": f"tests/{test_id}/result.html",
        "isLatest": True
    }
    manifest.insert(0, new_entry)

    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"✅ Successfully published '{title}'")
    print(f"📁 Target Folder: {test_folder}")
    print(f"📑 Total Tests in Manifest: {len(manifest)}")
    return True


if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
    else:
        # Fallback to a default filename if none provided in CLI
        input_path = "sample_input_test.json"
        
    publish_test_from_file(input_path)