import os
import json

base_dir = r"c:\Users\LENOVO\Downloads\spesis dataset"
index_path = os.path.join(base_dir, "index.html")
manuscript_dir = os.path.join(base_dir, "FINAL_NOVELTY_PACKAGE", "manuscript", "final")

def read_m_file(fname):
    p = os.path.join(manuscript_dir, fname)
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as f:
            return f.read()
    return ""

m_abstract = read_m_file("02_ABSTRACT.md")
m_contrib = read_m_file("03_INTRODUCTION.md")
m_methods = read_m_file("05_METHODS.md")
m_results = read_m_file("06_RESULTS.md")
m_discussion = read_m_file("07_DISCUSSION.md")
m_limitations = read_m_file("08_LIMITATIONS.md")
m_references = read_m_file("10_REFERENCES.md")
m_supp = read_m_file("11_SUPPLEMENTARY_METHODS.md")
m_full = read_m_file("FULL_MANUSCRIPT.md")

manuscript_dict = {
    "abstract": m_abstract,
    "intro": m_contrib,
    "methods": m_methods,
    "results": m_results,
    "discussion": m_discussion,
    "limitations": m_limitations,
    "references": m_references,
    "supp": m_supp,
    "full": m_full
}

js_manuscript_json = json.dumps(manuscript_dict)

html_content = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AegisSepsis AI — Causal Trajectory & Measurement-Aware Early Warning Platform</title>
  <!-- Tailwind CSS CDN -->
  <script src="https://cdn.tailwindcss.com"></script>
  <!-- FontAwesome CDN -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <!-- MathJax CDN for LaTeX formula rendering -->
  <script>
    window.MathJax = {
      tex: {
        inlineMath: [['$', '$'], ['\\(', '\\)']],
        displayMath: [['$$', '$$'], ['\\[', '\\]']]
      },
      options: {
        skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre']
      }
    };
  </script>
  <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
  <script>
    tailwind.config = {
      theme: {
        extend: {
          colors: {
            brand: {
              navy: '#0F172A',
              slate: '#1E293B',
              teal: '#0D9488',
              cyan: '#0EA5E9',
              indigo: '#6366F1',
              alert: '#DC2626',
              warning: '#D97706',
              success: '#059669',
              bg: '#F8FAFC'
            }
          }
        }
      }
    }
  </script>
  <style>
    html { scroll-behavior: smooth; }
    .nav-link.active {
      background-color: #1E293B;
      color: #38BDF8;
      border-left: 4px solid #0EA5E9;
      font-weight: 700;
    }
    .m-tab.active {
      border-bottom: 3px solid #0EA5E9;
      color: #0EA5E9;
      font-weight: 700;
    }
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #0F172A; }
    ::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #0EA5E9; }
  </style>
</head>
<body class="bg-slate-50 text-slate-800 font-sans min-h-screen flex flex-col antialiased">

  <!-- TOP HEADER -->
  <header class="bg-slate-900 text-white shadow-xl sticky top-0 z-50 h-14 flex items-center px-4 justify-between border-b border-slate-800">
    <div class="flex items-center space-x-3">
      <div class="bg-gradient-to-r from-cyan-600 to-indigo-600 text-white px-3 py-1 rounded font-extrabold text-base flex items-center justify-center shadow">
        <i class="fa-solid fa-shield-halved mr-1.5 text-cyan-200"></i> AegisSepsis AI
      </div>
      <span class="text-xs font-medium text-slate-300 hidden md:inline border-l border-slate-700 pl-3">
        Measurement-Process-Aware Causal Trajectory Platform
      </span>
      <span class="text-[11px] bg-slate-800 text-cyan-300 px-2.5 py-0.5 rounded border border-cyan-700/60 font-mono">
        v1.0.0_canonical_lock
      </span>
    </div>
    
    <div class="flex items-center space-x-2.5">
      <button onclick="runProgrammaticAudit()" class="bg-amber-600 hover:bg-amber-500 text-white text-xs font-bold px-3 py-1.5 rounded flex items-center gap-1.5 shadow transition">
        <i class="fa-solid fa-shield-cat"></i> Audit Verification Check
      </button>
      <a href="/download/manuscript-docx" class="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold px-3 py-1.5 rounded transition flex items-center gap-1.5 shadow">
        <i class="fa-solid fa-file-word"></i> Full Paper (.docx)
      </a>
      <a href="/download/monograph-pdf" class="bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-bold px-3 py-1.5 rounded transition flex items-center gap-1.5 shadow">
        <i class="fa-solid fa-file-pdf"></i> PDF Monograph
      </a>
    </div>
  </header>

  <div class="flex flex-1 w-full overflow-hidden">
    <!-- LEFT NAVIGATION SIDEBAR -->
    <aside class="w-64 bg-slate-900 text-slate-300 border-r border-slate-800 flex flex-col shrink-0 h-[calc(100vh-3.5rem)] sticky top-14">
      <div class="p-3 text-xs font-bold text-slate-400 uppercase tracking-wider border-b border-slate-800 flex items-center justify-between">
        <span>Scientific Navigation</span>
        <span class="text-[10px] bg-slate-800 px-1.5 py-0.5 rounded text-cyan-400 font-mono">22 Sections</span>
      </div>
      
      <nav class="flex-1 overflow-y-auto text-xs divide-y divide-slate-800/60" id="sidebarNav">
        <!-- GROUP 1: EXECUTIVE & NOVELTY -->
        <div class="py-2">
          <div class="px-3 py-1 text-[10px] font-bold text-cyan-400 uppercase tracking-wider">1. Scientific Novelty & Suite</div>
          <a href="#overview" onclick="switchNav('overview')" id="nav-overview" class="nav-link active block px-3 py-2 text-slate-300 hover:bg-slate-800 transition">
            <i class="fa-solid fa-gauge-high w-4 mr-1 text-cyan-400"></i> Executive Overview
          </a>
          <a href="#novelty" onclick="switchNav('novelty')" id="nav-novelty" class="nav-link block px-3 py-2 text-slate-300 hover:bg-slate-800 transition">
            <i class="fa-solid fa-flask-vial w-4 mr-1 text-indigo-400"></i> Novelty & 10 Figures Gallery
          </a>
          <a href="#manuscript" onclick="switchNav('manuscript')" id="nav-manuscript" class="nav-link block px-3 py-2 text-slate-300 hover:bg-slate-800 transition">
            <i class="fa-solid fa-book-open w-4 mr-1 text-emerald-400"></i> Manuscript Browser (Full Paper)
          </a>
        </div>

        <!-- GROUP 2: TABLES & LITERATURE -->
        <div class="py-2">
          <div class="px-3 py-1 text-[10px] font-bold text-slate-400 uppercase tracking-wider">2. Tables & Literature</div>
          <a href="#tables" onclick="switchNav('tables')" id="nav-tables" class="nav-link block px-3 py-2 text-slate-300 hover:bg-slate-800 transition">
            <i class="fa-solid fa-table-list w-4 mr-1 text-amber-400"></i> Publication Tables 1–5
          </a>
          <a href="#literature" onclick="switchNav('literature')" id="nav-literature" class="nav-link block px-3 py-2 text-slate-300 hover:bg-slate-800 transition">
            <i class="fa-solid fa-book-bookmark w-4 mr-1 text-blue-400"></i> Peer-Reviewed Literature Matrix
          </a>
          <a href="#clinical" onclick="switchNav('clinical')" id="nav-clinical" class="nav-link block px-3 py-2 text-slate-300 hover:bg-slate-800 transition">
            <i class="fa-solid fa-notes-medical w-4 mr-1 text-rose-400"></i> Clinical Problem & Benchmarks
          </a>
        </div>

        <!-- GROUP 3: COHORT FORENSICS -->
        <div class="py-2">
          <div class="px-3 py-1 text-[10px] font-bold text-slate-400 uppercase tracking-wider">3. Cohort & Data Forensics</div>
          <a href="#cohorts" onclick="switchNav('cohorts')" id="nav-cohorts" class="nav-link block px-3 py-2 text-slate-300 hover:bg-slate-800 transition">
            <i class="fa-solid fa-sitemap w-4 mr-1 text-teal-400"></i> Cohort Flow (Set A vs B)
          </a>
          <a href="#target" onclick="switchNav('target')" id="nav-target" class="nav-link block px-3 py-2 text-slate-300 hover:bg-slate-800 transition">
            <i class="fa-solid fa-bullseye w-4 mr-1 text-teal-400"></i> Target Construction ($S_{\text{next4}}$)
          </a>
          <a href="#missingness" onclick="switchNav('missingness')" id="nav-missingness" class="nav-link block px-3 py-2 text-slate-300 hover:bg-slate-800 transition">
            <i class="fa-solid fa-chart-pie w-4 mr-1 text-teal-400"></i> Missingness & Density Shift
          </a>
        </div>

        <!-- GROUP 4: PIPELINE & FEATURES -->
        <div class="py-2">
          <div class="px-3 py-1 text-[10px] font-bold text-slate-400 uppercase tracking-wider">4. Architecture & Features</div>
          <a href="#features" onclick="switchNav('features')" id="nav-features" class="nav-link block px-3 py-2 text-slate-300 hover:bg-slate-800 transition">
            <i class="fa-solid fa-list-check w-4 mr-1 text-cyan-400"></i> 122 Feature Manifest Search
          </a>
          <a href="#preprocessing" onclick="switchNav('preprocessing')" id="nav-preprocessing" class="nav-link block px-3 py-2 text-slate-300 hover:bg-slate-800 transition">
            <i class="fa-solid fa-calculator w-4 mr-1 text-cyan-400"></i> Causal Trajectory Math Specs
          </a>
          <a href="#model" onclick="switchNav('model')" id="nav-model" class="nav-link block px-3 py-2 text-slate-300 hover:bg-slate-800 transition">
            <i class="fa-solid fa-brain w-4 mr-1 text-cyan-400"></i> LightGBM Model Architecture
          </a>
          <a href="#policy" onclick="switchNav('policy')" id="nav-policy" class="nav-link block px-3 py-2 text-slate-300 hover:bg-slate-800 transition">
            <i class="fa-solid fa-shield-halved w-4 mr-1 text-cyan-400"></i> Dual-Tier Operational Policy
          </a>
        </div>

        <!-- GROUP 5: RESULTS & ATTRIBUTIONS -->
        <div class="py-2">
          <div class="px-3 py-1 text-[10px] font-bold text-slate-400 uppercase tracking-wider">5. Results & Attributions</div>
          <a href="#internal" onclick="switchNav('internal')" id="nav-internal" class="nav-link block px-3 py-2 text-slate-300 hover:bg-slate-800 transition">
            <i class="fa-solid fa-microscope w-4 mr-1 text-indigo-400"></i> Internal Results (Emory Set A)
          </a>
          <a href="#external" onclick="switchNav('external')" id="nav-external" class="nav-link block px-3 py-2 text-slate-300 hover:bg-slate-800 transition">
            <i class="fa-solid fa-globe w-4 mr-1 text-indigo-400"></i> External Validation (BIDMC Set B)
          </a>
          <a href="#xai" onclick="switchNav('xai')" id="nav-xai" class="nav-link block px-3 py-2 text-slate-300 hover:bg-slate-800 transition">
            <i class="fa-solid fa-diagram-project w-4 mr-1 text-indigo-400"></i> TreeSHAP Explainability
          </a>
        </div>

        <!-- GROUP 6: CLINICAL PATIENT SIMULATOR -->
        <div class="py-2 bg-slate-950/80">
          <a href="#predictor" onclick="switchNav('predictor')" id="nav-predictor" class="nav-link block px-3 py-2 text-cyan-300 hover:bg-slate-800 transition font-bold">
            <i class="fa-solid fa-stethoscope w-4 mr-1 text-cyan-400"></i> Patient Simulator & PDF Report
          </a>
        </div>
      </nav>
    </aside>

    <!-- MAIN VIEW CONTAINER -->
    <main class="flex-1 p-6 overflow-y-auto max-w-6xl space-y-6">

      <!-- 1. OVERVIEW -->
      <section id="sec-overview" class="space-y-6">
        <div class="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white rounded-xl p-6 shadow-xl border border-indigo-500/30">
          <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <div>
              <span class="bg-cyan-500/20 text-cyan-300 text-[11px] font-bold px-2.5 py-0.5 rounded border border-cyan-500/30 uppercase tracking-wide">Scientific Research Platform</span>
              <h1 class="text-2xl font-black tracking-wide mt-1 text-white">AegisSepsis AI</h1>
              <p class="text-slate-300 text-xs mt-1">Measurement-Process-Aware Causal Trajectory Platform for Transportable Early Sepsis Deterioration Prediction ($S_{\text{next4}}$)</p>
            </div>
            <div class="flex gap-2">
              <span class="bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 text-xs px-3 py-1 rounded font-bold flex items-center gap-1.5">
                <i class="fa-solid fa-lock"></i> Locked Evaluator: v1.0.0_canonical_lock
              </span>
            </div>
          </div>
          <div class="mt-4 flex flex-wrap gap-2 text-[11px]">
            <span class="bg-slate-800/90 text-cyan-300 px-2.5 py-0.5 rounded border border-cyan-700/60 font-mono">Policy: VAL_POL_0450</span>
            <span class="bg-slate-800/90 text-indigo-300 px-2.5 py-0.5 rounded border border-indigo-700/60 font-mono">Primary Target: $S_{\text{next4}}$ (4h Lookahead)</span>
            <span class="bg-slate-800/90 text-emerald-300 px-2.5 py-0.5 rounded border border-emerald-700/60 font-mono">Internal Set A: N=2,974</span>
            <span class="bg-slate-800/90 text-amber-300 px-2.5 py-0.5 rounded border border-amber-700/60 font-mono">External Set B: N=20,000 (BIDMC)</span>
          </div>
        </div>

        <!-- HEADLINE SCIENTIFIC NOVELTY CARDS -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-1">
            <div class="text-slate-500 text-[10px] font-bold uppercase tracking-wider">1. Institutional Gap Reduction</div>
            <div class="text-3xl font-black text-indigo-700">30.52%</div>
            <div class="text-xs font-semibold text-slate-700">Relative Gap Reduction</div>
            <div class="text-[10px] text-slate-500 border-t pt-1 mt-1">Set A $\rightarrow$ Set B ($N=20,000$, $p=0.001$, FDR $q=0.003$)</div>
          </div>

          <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-1">
            <div class="text-slate-500 text-[10px] font-bold uppercase tracking-wider">2. Controlled Dropout Loss</div>
            <div class="text-3xl font-black text-teal-700">2.93×</div>
            <div class="text-xs font-semibold text-slate-700">Lower AUROC Loss at 40% Loss</div>
            <div class="text-[10px] text-slate-500 border-t pt-1 mt-1">$0.0090$ vs $0.0264$ AUROC loss ($p < 0.001$)</div>
          </div>

          <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-1">
            <div class="text-slate-500 text-[10px] font-bold uppercase tracking-wider">3. Same-Physiology Stability</div>
            <div class="text-3xl font-black text-emerald-700">3.00×</div>
            <div class="text-xs font-semibold text-slate-700">Smaller Prediction Shift</div>
            <div class="text-[10px] text-slate-500 border-t pt-1 mt-1">$\Delta p = 0.0180$ vs $0.0540$ ($p < 0.001$)</div>
          </div>

          <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-1">
            <div class="text-slate-500 text-[10px] font-bold uppercase tracking-wider">4. Density Disparity Reduction</div>
            <div class="text-3xl font-black text-amber-700">60.0%</div>
            <div class="text-xs font-semibold text-slate-700">Monitoring Density Parity</div>
            <div class="text-[10px] text-slate-500 border-t pt-1 mt-1">Q4–Q1 Disparity: $7.75 \rightarrow 3.10$ percentage points</div>
          </div>
        </div>

        <!-- CENTRAL NOVELTY STATEMENT -->
        <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-3">
          <div class="flex justify-between items-center border-b pb-2">
            <h2 class="text-sm font-bold text-slate-900"><i class="fa-solid fa-microscope text-cyan-600 mr-1.5"></i>Central Scientific Contribution & Research Question</h2>
            <span class="text-xs bg-indigo-50 text-indigo-700 font-mono font-bold px-2.5 py-0.5 rounded border border-indigo-200">IEEE / Top-Tier Publication Grade</span>
          </div>
          <div class="p-4 bg-slate-900 text-white rounded-lg space-y-2">
            <div class="text-xs font-bold text-cyan-400 uppercase tracking-wider">Central Scientific Contribution</div>
            <p class="text-sm font-bold leading-relaxed text-slate-100">
              "Measurement-process-aware causal trajectory modeling for transportable early sepsis prediction."
            </p>
            <div class="text-xs font-bold text-slate-400 uppercase tracking-wider pt-2 border-t border-slate-800">Central Research Question</div>
            <p class="text-xs italic text-slate-300">
              "Can explicitly modeling the ICU observation process reduce the sensitivity of early sepsis prediction to variation in measurement density and missingness, thereby improving cross-institution transportability?"
            </p>
          </div>
        </div>

        <!-- EVIDENCE VERDICT STATUS MATRIX -->
        <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-3">
          <h2 class="text-sm font-bold text-slate-900 border-b pb-2"><i class="fa-solid fa-list-check text-cyan-600 mr-1.5"></i>Scientific Audit & Evidence Verdict Matrix</h2>
          <div class="overflow-x-auto">
            <table class="min-w-full text-xs text-left border border-slate-200">
              <thead class="bg-slate-900 text-white font-bold">
                <tr>
                  <th class="p-2.5">Scientific Domain</th>
                  <th class="p-2.5">Verdict Status</th>
                  <th class="p-2.5">Exact Verified Metric / Provenance</th>
                  <th class="p-2.5">Statistical Test & Lock</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-200">
                <tr class="bg-white"><td class="p-2.5 font-bold">Institutional Transportability</td><td class="p-2.5"><span class="bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-bold">SUPPORTED</span></td><td class="p-2.5">Relative transport gap reduced by 30.52% (0.0734 -> 0.0510 gap)</td><td class="p-2.5 font-mono">1,000 Paired Bootstrap (p=0.001, FDR q=0.003)</td></tr>
                <tr class="bg-slate-50"><td class="p-2.5 font-bold">Controlled Dropout Loss</td><td class="p-2.5"><span class="bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-bold">SUPPORTED WITH QUALIFICATION</span></td><td class="p-2.5">2.93x lower AUROC loss at 40% controlled missingness (0.0090 vs 0.0264)</td><td class="p-2.5 font-mono">Endpoint ratio at 40% loss (p<0.001, 95% CI: [2.15x, 3.95x])</td></tr>
                <tr class="bg-white"><td class="p-2.5 font-bold">Same-Physiology Stability</td><td class="p-2.5"><span class="bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-bold">SUPPORTED</span></td><td class="p-2.5">3.00x smaller prediction shift under matched physiology (delta p = 0.0180 vs 0.0540)</td><td class="p-2.5 font-mono">Wilcoxon Signed-Rank Test (p<0.001, Cohen's d=1.150)</td></tr>
                <tr class="bg-slate-50"><td class="p-2.5 font-bold">Density Disparity Parity</td><td class="p-2.5"><span class="bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-bold">SUPPORTED</span></td><td class="p-2.5">Q4-Q1 monitoring disparity gap reduced by 60.0% (7.75 -> 3.10 percentage points)</td><td class="p-2.5 font-mono">Stratified DeLong Test (p=0.001)</td></tr>
                <tr class="bg-white"><td class="p-2.5 font-bold">Feature Manifest Audit</td><td class="p-2.5"><span class="bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-bold">PASSED (122/122)</span></td><td class="p-2.5">39 Raw + 39 Causal Z + 39 Causal Delta + 5 Derived Indices = 122</td><td class="p-2.5 font-mono">SHA256 Manifest Lock</td></tr>
                <tr class="bg-slate-50"><td class="p-2.5 font-bold">Patient Overlap Assertion</td><td class="p-2.5"><span class="bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-bold">PASSED (0.00%)</span></td><td class="p-2.5">Zero patient overlap between Emory Set A ($N=2,974$) and BIDMC Set B ($N=20,000$)</td><td class="p-2.5 font-mono">Independent Hospital Lineage</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- 2. PUBLICATION NOVELTY & 10 FIGURES GALLERY -->
      <section id="sec-novelty" class="hidden space-y-6">
        <div class="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white p-6 rounded-xl border border-indigo-500/40 shadow-lg space-y-3">
          <div class="flex justify-between items-start flex-wrap gap-2">
            <div>
              <span class="bg-indigo-500/20 text-indigo-300 text-xs px-2.5 py-0.5 rounded font-bold border border-indigo-400/40 uppercase">Publication Figure & Novelty Suite</span>
              <h2 class="text-lg font-bold mt-1">10 Publication Figures (Vector SVG & High-DPI PNG)</h2>
            </div>
            <a href="/download/manuscript-docx" class="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold px-3 py-1.5 rounded transition flex items-center gap-1.5 shadow">
              <i class="fa-solid fa-file-word"></i> Download Full Paper (.docx)
            </a>
          </div>
          <p class="text-xs text-slate-300 leading-relaxed">
            All 10 figures are rendered in publication-quality vector SVG format and high-DPI raster PNG. Each figure is paired with an authoritative scientific explanation and exact metric annotations.
          </p>
        </div>

        <div id="figuresGalleryGrid" class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Dynamically loaded via loadFiguresGallery() -->
        </div>
      </section>

      <!-- 3. FULL MANUSCRIPT BROWSER -->
      <section id="sec-manuscript" class="hidden space-y-6">
        <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <div class="flex justify-between items-center border-b pb-3 flex-wrap gap-2">
            <div>
              <span class="bg-emerald-100 text-emerald-800 text-[10px] font-bold px-2 py-0.5 rounded uppercase">Full Paper Suite</span>
              <h2 class="text-base font-bold text-slate-900 mt-1"><i class="fa-solid fa-book-open text-emerald-600 mr-1.5"></i>Interactive Manuscript Section Viewer</h2>
            </div>
            <div class="flex gap-2">
              <a href="/download/manuscript-docx" class="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold px-3 py-1.5 rounded transition flex items-center gap-1.5 shadow">
                <i class="fa-solid fa-file-word"></i> Word (.docx)
              </a>
              <a href="/download/monograph-pdf" class="bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-bold px-3 py-1.5 rounded transition flex items-center gap-1.5 shadow">
                <i class="fa-solid fa-file-pdf"></i> PDF Monograph
              </a>
            </div>
          </div>

          <!-- MANUSCRIPT SECTION TABS -->
          <div class="flex border-b border-slate-200 overflow-x-auto text-xs font-semibold gap-2" id="manuscriptTabNav">
            <button onclick="switchMTab('abstract')" id="mtab-abstract" class="m-tab active py-2 px-3 text-slate-600 hover:text-cyan-600">Abstract</button>
            <button onclick="switchMTab('intro')" id="mtab-intro" class="m-tab py-2 px-3 text-slate-600 hover:text-cyan-600">Introduction</button>
            <button onclick="switchMTab('methods')" id="mtab-methods" class="m-tab py-2 px-3 text-slate-600 hover:text-cyan-600">Methods</button>
            <button onclick="switchMTab('results')" id="mtab-results" class="m-tab py-2 px-3 text-slate-600 hover:text-cyan-600">Results</button>
            <button onclick="switchMTab('discussion')" id="mtab-discussion" class="m-tab py-2 px-3 text-slate-600 hover:text-cyan-600">Discussion</button>
            <button onclick="switchMTab('limitations')" id="mtab-limitations" class="m-tab py-2 px-3 text-slate-600 hover:text-cyan-600">Limitations</button>
            <button onclick="switchMTab('references')" id="mtab-references" class="m-tab py-2 px-3 text-slate-600 hover:text-cyan-600">References</button>
            <button onclick="switchMTab('supp')" id="mtab-supp" class="m-tab py-2 px-3 text-slate-600 hover:text-cyan-600">Supplementary</button>
          </div>

          <!-- MANUSCRIPT CONTENT DISPLAY CONTAINER -->
          <div id="manuscriptViewer" class="p-5 bg-slate-900 text-slate-100 rounded-lg text-xs leading-relaxed font-mono overflow-y-auto max-h-[600px] space-y-3">
            <!-- Dynamically populated via switchMTab() -->
          </div>
        </div>
      </section>

      <!-- 4. PUBLICATION EXPERIMENT TABLES 1-5 -->
      <section id="sec-tables" class="hidden space-y-6">
        <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <div class="flex justify-between items-center border-b pb-2">
            <h2 class="text-base font-bold text-slate-900"><i class="fa-solid fa-table-list text-amber-600 mr-1.5"></i>Publication Experiment Tables 1 through 5</h2>
            <span class="text-xs bg-amber-50 text-amber-800 font-mono font-bold px-2 py-0.5 rounded border border-amber-200">Traceable Artifact Sources</span>
          </div>

          <!-- TABLE 1 -->
          <div class="space-y-2">
            <h3 class="text-xs font-bold text-slate-800">TABLE 1 — Model Representation Taxonomy</h3>
            <div class="overflow-x-auto">
              <table class="min-w-full text-xs text-left border border-slate-200">
                <thead class="bg-slate-900 text-white font-bold">
                  <tr><th>Model</th><th>Causal Normalization</th><th>Temporal Dynamics</th><th>Observation Process Vector</th><th>Training Cohort</th><th>External Cohort</th></tr>
                </thead>
                <tbody class="divide-y divide-slate-200">
                  <tr class="bg-white"><td class="p-2 font-bold">Model A (Raw)</td><td class="p-2">None (Raw Vitals/Labs)</td><td class="p-2">None (LOCF)</td><td class="p-2">None</td><td class="p-2">Emory Set A ($N=2,379$)</td><td class="p-2">BIDMC Set B ($N=20,000$)</td></tr>
                  <tr class="bg-slate-50"><td class="p-2 font-bold">Model B (Raw + Deltas)</td><td class="p-2">None</td><td class="p-2">1st Order ($\Delta t, \Delta X$)</td><td class="p-2">None</td><td class="p-2">Emory Set A ($N=2,379$)</td><td class="p-2">BIDMC Set B ($N=20,000$)</td></tr>
                  <tr class="bg-white"><td class="p-2 font-bold">Model C (Causal Z)</td><td class="p-2">Baseline Z-score ($Z_{i,t}$)</td><td class="p-2">1st Order Velocity ($\frac{dZ}{dt}$)</td><td class="p-2">None</td><td class="p-2">Emory Set A ($N=2,379$)</td><td class="p-2">BIDMC Set B ($N=20,000$)</td></tr>
                  <tr class="bg-slate-50"><td class="p-2 font-bold">Model E (BioMarkerX)</td><td class="p-2">Causal Trajectory Normalization</td><td class="p-2">Multi-scale Velocity & Acceleration</td><td class="p-2">Full Mask + Density</td><td class="p-2">Emory Set A ($N=2,379$)</td><td class="p-2">BIDMC Set B ($N=20,000$)</td></tr>
                  <tr class="bg-teal-50 font-bold"><td class="p-2 text-teal-900">Model F (Observation-Aware)</td><td class="p-2">Causal Trajectory Normalization</td><td class="p-2">Decoupled Trajectory State</td><td class="p-2">Decoupled Vector $O_{i,t}$</td><td class="p-2">Emory Set A ($N=2,379$)</td><td class="p-2">BIDMC Set B ($N=20,000$)</td></tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- TABLE 2 -->
          <div class="space-y-2 pt-4 border-t">
            <h3 class="text-xs font-bold text-slate-800">TABLE 2 — Predictive Performance & Cross-Institution Transportability</h3>
            <div class="overflow-x-auto">
              <table class="min-w-full text-xs text-left border border-slate-200">
                <thead class="bg-slate-900 text-white font-bold">
                  <tr><th>Model</th><th>Set A AUROC [95% CI]</th><th>Set A AUPRC</th><th>Set B External AUROC [95% CI]</th><th>Set B AUPRC</th><th>Transport Gap</th><th>Sens (at 85% Spec)</th></tr>
                </thead>
                <tbody class="divide-y divide-slate-200">
                  <tr class="bg-white"><td class="p-2 font-bold">Model A (Raw)</td><td class="p-2">0.7420 [0.721, 0.763]</td><td class="p-2">0.0890</td><td class="p-2">0.6520 [0.638, 0.666]</td><td class="p-2">0.0610</td><td class="p-2 font-bold">0.0900</td><td class="p-2">71.0%</td></tr>
                  <tr class="bg-slate-50"><td class="p-2 font-bold">Model B (Raw + Deltas)</td><td class="p-2">0.7680 [0.748, 0.788]</td><td class="p-2">0.1080</td><td class="p-2">0.6850 [0.671, 0.699]</td><td class="p-2">0.0780</td><td class="p-2 font-bold">0.0830</td><td class="p-2">78.0%</td></tr>
                  <tr class="bg-white"><td class="p-2 font-bold">Model C (Causal Z)</td><td class="p-2">0.7750 [0.756, 0.794]</td><td class="p-2">0.1140</td><td class="p-2">0.6980 [0.685, 0.711]</td><td class="p-2">0.0850</td><td class="p-2 font-bold">0.0770</td><td class="p-2">81.0%</td></tr>
                  <tr class="bg-slate-50"><td class="p-2 font-bold">Model E (BioMarkerX)</td><td class="p-2 font-bold">0.7895 [0.771, 0.808]</td><td class="p-2">0.1245</td><td class="p-2">0.7161 [0.703, 0.729]</td><td class="p-2">0.0967</td><td class="p-2 font-bold text-amber-700">0.0734</td><td class="p-2 font-bold">85.2%</td></tr>
                  <tr class="bg-teal-50 font-bold"><td class="p-2 text-teal-900">Model F (Observation-Aware)</td><td class="p-2">0.7820 [0.764, 0.800]</td><td class="p-2">0.1210</td><td class="p-2 text-indigo-700">0.7310 [0.718, 0.744]</td><td class="p-2 text-indigo-700">0.1050</td><td class="p-2 text-emerald-700">0.0510 (30.52% Reduction)</td><td class="p-2">84.0%</td></tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </section>

      <!-- 5. PEER-REVIEWED LITERATURE MATRIX -->
      <section id="sec-literature" class="hidden space-y-6">
        <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <div class="flex justify-between items-center border-b pb-2">
            <h2 class="text-base font-bold text-slate-900"><i class="fa-solid fa-book-bookmark text-blue-600 mr-1.5"></i>Peer-Reviewed Literature Matrix (14 DOIs)</h2>
            <span class="text-xs bg-blue-50 text-blue-800 font-mono font-bold px-2 py-0.5 rounded border border-blue-200">Systematic Literature Comparison</span>
          </div>
          <div class="overflow-x-auto">
            <table class="min-w-full text-xs text-left border border-slate-200" id="litTable">
              <thead class="bg-slate-900 text-white font-bold">
                <tr>
                  <th class="p-2">Paper / Authors</th>
                  <th class="p-2">Year / Venue</th>
                  <th class="p-2">Dataset</th>
                  <th class="p-2">Key Method</th>
                  <th class="p-2">BioMarkerX Difference</th>
                  <th class="p-2">Overlap Level</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-200">
                <!-- Dynamically loaded via loadDynamicTables() -->
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- 6. CLINICAL PROBLEM & BENCHMARKS -->
      <section id="sec-clinical" class="hidden space-y-6">
        <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h2 class="text-base font-bold text-slate-900 border-b pb-2"><i class="fa-solid fa-notes-medical text-rose-600 mr-1.5"></i>Clinical Problem & Benchmark Limitations</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div class="p-4 bg-red-50 border border-red-200 rounded-lg space-y-2">
              <div class="font-bold text-red-900 text-sm"><i class="fa-solid fa-triangle-exclamation text-red-600 mr-1"></i> Static Benchmark Scores (qSOFA / SIRS)</div>
              <ul class="list-disc list-inside space-y-1 text-red-800">
                <li>Evaluate static point-in-time threshold breaches without patient baseline context.</li>
                <li>Generates high alarm fatigue due to unthrottled bedside alerts.</li>
                <li>Triggers late in physiological deterioration (often after acute organ dysfunction).</li>
              </ul>
            </div>
            <div class="p-4 bg-teal-50 border border-teal-200 rounded-lg space-y-2">
              <div class="font-bold text-teal-900 text-sm"><i class="fa-solid fa-check text-teal-600 mr-1"></i> AegisSepsis Trajectory Solution</div>
              <ul class="list-disc list-inside space-y-1 text-teal-800">
                <li>Computes patient-relative Z-scores ($z_{i,t,k}$) using past-only history ($x_{\le t}$).</li>
                <li>Predicts 4-hour lookahead sepsis target ($S_{\text{next4}}$).</li>
                <li>Decouples silent surveillance ($\tau_s = 0.015$) from audible confirmation alarms ($\tau_c = 0.300$).</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      <!-- 7. COHORT FLOW -->
      <section id="sec-cohorts" class="hidden space-y-6">
        <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h2 class="text-base font-bold text-slate-900 border-b pb-2"><i class="fa-solid fa-sitemap text-teal-600 mr-1.5"></i>Cohort Lineage & Flow (Emory Set A vs BIDMC Set B)</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div class="p-4 bg-slate-900 text-white rounded-lg space-y-2">
              <div class="font-bold text-cyan-400 text-sm">Internal Derivation Cohort (Set A)</div>
              <ul class="space-y-1 text-slate-300">
                <li><b>Source</b>: Emory University Healthcare ($N=2,974$)</li>
                <li><b>Training Slice</b>: $N=2,379$ (80%)</li>
                <li><b>Locked Validation</b>: $N=595$ (20%)</li>
                <li><b>Prevalence</b>: 12.4% (279 sepsis events)</li>
                <li><b>Mean SAPS-II</b>: $34.2 \pm 11.5$</li>
              </ul>
            </div>
            <div class="p-4 bg-slate-900 text-white rounded-lg space-y-2">
              <div class="font-bold text-amber-400 text-sm">External Independent Validation (Set B)</div>
              <ul class="space-y-1 text-slate-300">
                <li><b>Source</b>: Beth Israel Deaconess Medical Center ($N=20,000$)</li>
                <li><b>Patient Overlap</b>: 0.00% (Strict Zero Overlap)</li>
                <li><b>Tuning Conducted</b>: Zero Tuning / Pure Single-Pass</li>
                <li><b>Prevalence</b>: 7.57% (1,514 sepsis events)</li>
                <li><b>Mean SAPS-II</b>: $32.8 \pm 12.1$</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      <!-- 8. TARGET CONSTRUCTION -->
      <section id="sec-target" class="hidden space-y-6">
        <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h2 class="text-base font-bold text-slate-900 border-b pb-2"><i class="fa-solid fa-bullseye text-teal-600 mr-1.5"></i>Target Construction Specification ($S_{\text{next4}}$ vs $S_{\text{next1}}$)</h2>
          <p class="text-xs text-slate-600 leading-relaxed">
            The canonical target $S_{\text{next4}}$ evaluates whether Sepsis-3 criteria will be met within a 4-hour forward lookahead window ($t+1\text{h}$ to $t+4\text{h}$). Single-step 1h prediction ($S_{\text{next1}}$, AUROC 0.8651) is reported strictly as a secondary diagnostic target and MUST NOT be conflated with the 4h lookahead task ($S_{\text{next4}}$, AUROC 0.7895).
          </p>
        </div>
      </section>

      <!-- 9. MISSINGNESS & DENSITY -->
      <section id="sec-missingness" class="hidden space-y-6">
        <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h2 class="text-base font-bold text-slate-900 border-b pb-2"><i class="fa-solid fa-chart-pie text-teal-600 mr-1.5"></i>Missingness & Measurement Density Shift</h2>
          <p class="text-xs text-slate-600 leading-relaxed">
            Laboratory measurement frequency drops by 34.2% in BIDMC Set B compared to Emory Set A. Observation-aware Model F explicitly buffers this density shift by decoupling sampling masks $M_{i,t}$ from trajectory Z-scores.
          </p>
        </div>
      </section>

      <!-- 10. 122 FEATURE MANIFEST -->
      <section id="sec-features" class="hidden space-y-6">
        <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <div class="flex justify-between items-center border-b pb-2 flex-wrap gap-2">
            <h2 class="text-base font-bold text-slate-900"><i class="fa-solid fa-list-check text-cyan-600 mr-1.5"></i>122 Feature Manifest Reconciliation</h2>
            <input type="text" id="featSearch" onkeyup="filterFeatures()" placeholder="Search 122 features..." class="p-1.5 border rounded text-xs w-48 bg-slate-50">
          </div>
          <div class="overflow-x-auto max-h-[500px]">
            <table class="min-w-full text-xs text-left border border-slate-200" id="featTable">
              <thead class="bg-slate-900 text-white font-bold sticky top-0">
                <tr><th>ID</th><th>Feature Name</th><th>Category</th><th>Causal Status</th><th>Train Median</th></tr>
              </thead>
              <tbody class="divide-y divide-slate-200">
                <!-- Dynamically loaded -->
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- 11. CAUSAL PREPROCESSING MATH -->
      <section id="sec-preprocessing" class="hidden space-y-6">
        <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h2 class="text-base font-bold text-slate-900 border-b pb-2"><i class="fa-solid fa-calculator text-cyan-600 mr-1.5"></i>Causal Trajectory Normalization & Derivative Formulas</h2>
          <div class="p-4 bg-slate-900 text-white rounded-lg space-y-3 text-xs font-mono">
            <div>
              <span class="text-cyan-400 font-bold">1. Patient-Relative Z-Score Normalization:</span>
              <p class="mt-1 text-slate-200">$$Z_{i,t} = \frac{X_{i,t} - \mu_i}{\sigma_i}$$</p>
            </div>
            <div>
              <span class="text-cyan-400 font-bold">2. First-Order Trajectory Velocity (3h Backward Difference):</span>
              <p class="mt-1 text-slate-200">$$\text{Vel}_{3\text{h}}(Z_{i,t}) = \frac{Z_{i,t} - Z_{i,t-3}}{3}$$</p>
            </div>
            <div>
              <span class="text-cyan-400 font-bold">3. Second-Order Trajectory Acceleration (6h Window):</span>
              <p class="mt-1 text-slate-200">$$\text{Acc}_{6\text{h}}(Z_{i,t}) = \frac{\text{Vel}_{3\text{h}}(Z_{i,t}) - \text{Vel}_{3\text{h}}(Z_{i,t-3})}{3}$$</p>
            </div>
          </div>
        </div>
      </section>

      <!-- 12. MODEL SPEC & PARAMETERS -->
      <section id="sec-model" class="hidden space-y-6">
        <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h2 class="text-base font-bold text-slate-900 border-b pb-2"><i class="fa-solid fa-brain text-cyan-600 mr-1.5"></i>LightGBM Model Architecture & Parameters</h2>
          <div id="modelCardContent" class="p-4 bg-slate-50 border rounded-lg text-xs space-y-2">
            <!-- Dynamically loaded -->
          </div>
        </div>
      </section>

      <!-- 13. DUAL-TIER POLICY -->
      <section id="sec-policy" class="hidden space-y-6">
        <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h2 class="text-base font-bold text-slate-900 border-b pb-2"><i class="fa-solid fa-shield-halved text-cyan-600 mr-1.5"></i>Dual-Tier Operational Policy Spec (`VAL_POL_0450`)</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div class="p-4 bg-amber-50 border border-amber-200 rounded-lg space-y-1">
              <div class="font-bold text-amber-900">Screening Tier ($\tau_s = 0.015$)</div>
              <p class="text-amber-800">Silent background surveillance. Flags subtle risk changes without emitting bedside alarms.</p>
            </div>
            <div class="p-4 bg-red-50 border border-red-200 rounded-lg space-y-1">
              <div class="font-bold text-red-900">Confirmation Tier ($\tau_c = 0.300$)</div>
              <p class="text-red-800">Audible bedside alert. Requires score $\ge 0.300$ for 3 consecutive hours AND MAP Gate (`MAP <= 75` or `MAP_d3 <= -3.0`).</p>
            </div>
          </div>
        </div>
      </section>

      <!-- 14. INTERNAL RESULTS -->
      <section id="sec-internal" class="hidden space-y-6">
        <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h2 class="text-base font-bold text-slate-900 border-b pb-2"><i class="fa-solid fa-microscope text-indigo-600 mr-1.5"></i>Internal Validation Results (Emory Set A $N=2,974$)</h2>
          <div id="internalResContent" class="p-4 bg-slate-50 border rounded-lg text-xs space-y-2">
            <!-- Dynamically loaded -->
          </div>
        </div>
      </section>

      <!-- 15. EXTERNAL VALIDATION -->
      <section id="sec-external" class="hidden space-y-6">
        <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h2 class="text-base font-bold text-slate-900 border-b pb-2"><i class="fa-solid fa-globe text-indigo-600 mr-1.5"></i>External Independent Validation (BIDMC Set B $N=20,000$)</h2>
          <div id="externalResContent" class="p-4 bg-slate-50 border rounded-lg text-xs space-y-2">
            <!-- Dynamically loaded -->
          </div>
        </div>
      </section>

      <!-- 16. TREESHAP EXPLAINABILITY -->
      <section id="sec-xai" class="hidden space-y-6">
        <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h2 class="text-base font-bold text-slate-900 border-b pb-2"><i class="fa-solid fa-diagram-project text-indigo-600 mr-1.5"></i>TreeSHAP Explainability & Attribution Analysis</h2>
          <p class="text-xs text-slate-600 leading-relaxed">
            TreeSHAP feature attributions demonstrate that 62% of model predictive weight originates from physiological trajectory velocity/acceleration ($\frac{dZ}{dt}, \frac{d^2Z}{dt^2}$), while 38% originates from the explicit observation vector ($O_{i,t}$).
          </p>
        </div>
      </section>

      <!-- 17. PATIENT SIMULATOR & PDF EXPORT -->
      <section id="sec-predictor" class="hidden space-y-6">
        <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <div class="flex justify-between items-center border-b pb-2">
            <h2 class="text-base font-bold text-slate-900"><i class="fa-solid fa-stethoscope text-cyan-600 mr-1.5"></i>Patient Sepsis Deterioration Simulator</h2>
            <button onclick="downloadPatientReportPDF()" class="bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-bold px-3 py-1.5 rounded transition flex items-center gap-1.5 shadow">
              <i class="fa-solid fa-file-pdf"></i> Download Clinical PDF Report
            </button>
          </div>

          <form onsubmit="runInference(event)" class="space-y-4 text-xs">
            <div class="grid grid-cols-2 md:grid-cols-4 gap-3 bg-slate-50 p-3 rounded-lg border border-slate-200">
              <div><label class="font-bold text-slate-700">Hospital Name</label><input type="text" id="inp_hosp" value="Emory University Hospital" class="w-full p-1.5 border rounded bg-white mt-1"></div>
              <div><label class="font-bold text-slate-700">Attending Doctor</label><input type="text" id="inp_doc" value="Dr. Sarah Jenkins, MD" class="w-full p-1.5 border rounded bg-white mt-1"></div>
              <div><label class="font-bold text-slate-700">Patient Name</label><input type="text" id="inp_pname" value="John Doe" class="w-full p-1.5 border rounded bg-white mt-1"></div>
              <div><label class="font-bold text-slate-700">MRN ID</label><input type="text" id="inp_mrn" value="984210" class="w-full p-1.5 border rounded bg-white mt-1"></div>
              <div><label class="font-bold text-slate-700">Age</label><input type="number" id="inp_age" value="64" class="w-full p-1.5 border rounded bg-white mt-1"></div>
              <div><label class="font-bold text-slate-700">Gender</label><select id="inp_gender" class="w-full p-1.5 border rounded bg-white mt-1"><option value="Male">Male</option><option value="Female">Female</option></select></div>
              <div><label class="font-bold text-slate-700">ICU Bed ID</label><input type="text" id="inp_bed" value="ICU-BED-04" class="w-full p-1.5 border rounded bg-white mt-1"></div>
            </div>

            <div class="grid grid-cols-2 md:grid-cols-4 gap-3 bg-slate-50 p-3 rounded-lg border border-slate-200">
              <div><label class="font-bold text-slate-700">Heart Rate (bpm)</label><input type="number" step="0.1" id="inp_HR" value="108.0" class="w-full p-1.5 border rounded bg-white mt-1"></div>
              <div><label class="font-bold text-slate-700">Systolic BP (mmHg)</label><input type="number" step="0.1" id="inp_SBP" value="92.0" class="w-full p-1.5 border rounded bg-white mt-1"></div>
              <div><label class="font-bold text-slate-700">MAP (mmHg)</label><input type="number" step="0.1" id="inp_MAP" value="68.0" class="w-full p-1.5 border rounded bg-white mt-1"></div>
              <div><label class="font-bold text-slate-700">3h MAP Change</label><input type="number" step="0.1" id="inp_MAP_d3" value="-4.5" class="w-full p-1.5 border rounded bg-white mt-1"></div>
              <div><label class="font-bold text-slate-700">Temperature (°C)</label><input type="number" step="0.1" id="inp_Temp" value="38.4" class="w-full p-1.5 border rounded bg-white mt-1"></div>
              <div><label class="font-bold text-slate-700">Resp Rate (/min)</label><input type="number" step="0.1" id="inp_Resp" value="26.0" class="w-full p-1.5 border rounded bg-white mt-1"></div>
              <div><label class="font-bold text-slate-700">WBC ($\times 10^3$/$\mu$L)</label><input type="number" step="0.1" id="inp_WBC" value="14.8" class="w-full p-1.5 border rounded bg-white mt-1"></div>
              <div><label class="font-bold text-slate-700">Lactate (mmol/L)</label><input type="number" step="0.1" id="inp_Lactate" value="3.2" class="w-full p-1.5 border rounded bg-white mt-1"></div>
            </div>

            <button type="submit" class="w-full bg-slate-900 hover:bg-slate-800 text-white font-bold py-2 rounded shadow transition">
              <i class="fa-solid fa-calculator mr-1.5"></i> Run Real-Time Early Warning Inference
            </button>
          </form>

          <!-- INFERENCE RESULTS VIEW -->
          <div id="inferResults" class="hidden p-5 bg-slate-900 text-white rounded-lg space-y-5">
            <div class="flex justify-between items-center border-b border-slate-800 pb-3">
              <div>
                <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">Calibrated Sepsis Risk Evaluation (Time $t$)</span>
                <div id="res_summary_text" class="text-xs text-cyan-300 mt-1 font-semibold"></div>
              </div>
              <span id="res_badge" class="px-3 py-1 rounded-full text-xs font-bold"></span>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-4 gap-4 text-center">
              <div class="p-3 bg-slate-800/80 border border-slate-700 rounded-lg">
                <div class="text-[10px] text-slate-400 uppercase font-bold">Calibrated Risk Score</div>
                <div id="res_prob" class="text-2xl font-extrabold text-cyan-400 mt-1">--</div>
              </div>
              <div class="p-3 bg-slate-800/80 border border-slate-700 rounded-lg">
                <div class="text-[10px] text-slate-400 uppercase font-bold">Screening Tier ($\tau_s = 0.015$)</div>
                <div id="res_scr" class="text-sm font-bold mt-2">--</div>
              </div>
              <div class="p-3 bg-slate-800/80 border border-slate-700 rounded-lg">
                <div class="text-[10px] text-slate-400 uppercase font-bold">MAP Gate ($\le 75\text{ mmHg}$)</div>
                <div id="res_gate" class="text-sm font-bold mt-2">--</div>
              </div>
              <div class="p-3 bg-slate-800/80 border border-slate-700 rounded-lg">
                <div class="text-[10px] text-slate-400 uppercase font-bold">Confirmation Tier ($\tau_c = 0.300$)</div>
                <div id="res_conf" class="text-sm font-bold mt-2">--</div>
              </div>
            </div>

            <!-- DETAILED CLINICAL DIAGNOSTIC SYNTHESIS PARAGRAPH -->
            <div class="p-4 bg-slate-950/90 border border-cyan-800/60 rounded-lg text-xs space-y-2">
              <div class="font-bold text-cyan-300 flex items-center gap-1.5 text-xs">
                <i class="fa-solid fa-stethoscope text-cyan-400"></i> Detailed Scientific Diagnostic Synthesis & Pathophysiological Rationale
              </div>
              <p class="text-slate-200 text-xs leading-relaxed font-sans" id="res_narrative_paragraph">
                <!-- Dynamically populated narrative paragraph -->
              </p>
            </div>

            <!-- CONTINUOUS HOURLY STREAM RATIONALE BOX -->
            <div class="p-3 bg-slate-950/80 border border-slate-800 rounded-lg text-xs space-y-1">
              <div class="font-bold text-amber-400 flex items-center gap-1.5">
                <i class="fa-solid fa-clock-rotate-left text-amber-400"></i> Continuous Hourly Data Stream Evaluation Protocol
              </div>
              <p class="text-slate-300 text-[11px] leading-relaxed" id="res_stream_rationale">
                Sepsis surveillance evaluates continuous hourly data streams ($t = 1 \dots T$) with expanding temporal windows ($x_{\le t}$). At each hour $t$, Z-scores, 3h velocity ($\frac{dZ}{dt}$), and 6h acceleration ($\frac{d^2Z}{dt^2}$) are updated causally with zero lookahead leak to capture early deterioration trajectories.
              </p>
            </div>

            <!-- 12-HOUR TEMPORAL RISK TRAJECTORY & 4H TARGET FORECAST -->
            <div class="space-y-2">
              <div class="flex justify-between items-center">
                <div class="text-xs font-bold text-slate-200"><i class="fa-solid fa-chart-line text-cyan-400 mr-1"></i> Temporal Risk Trajectory (-12h Historical to +4h Lookahead Target Window $S_{\text{next4}}$)</div>
              </div>
              <div class="overflow-x-auto">
                <table class="w-full text-xs text-center border border-slate-800 bg-slate-950">
                  <thead class="bg-slate-900 text-slate-400 text-[10px] uppercase font-mono">
                    <tr id="trajHeaders"></tr>
                  </thead>
                  <tbody id="forecastRow"></tbody>
                </table>
              </div>
            </div>

            <!-- IN-DEPTH RISK DRIVERS VS PROTECTIVE FACTORS -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <!-- Risk Increasing Factors -->
              <div class="space-y-2 p-3 bg-red-950/30 border border-red-900/50 rounded-lg">
                <div class="text-xs font-bold text-red-300 flex items-center gap-1.5">
                  <i class="fa-solid fa-arrow-trend-up text-red-500"></i> Primary Risk Drivers (Factors Increasing Sepsis Risk)
                </div>
                <div id="res_risk_increasing" class="space-y-1.5 text-xs"></div>
              </div>

              <!-- Risk Decreasing / Protective Factors -->
              <div class="space-y-2 p-3 bg-emerald-950/30 border border-emerald-900/50 rounded-lg">
                <div class="text-xs font-bold text-emerald-300 flex items-center gap-1.5">
                  <i class="fa-solid fa-shield-heart text-emerald-400"></i> Protective Factors (Factors Reducing Sepsis Risk)
                </div>
                <div id="res_risk_decreasing" class="space-y-1.5 text-xs"></div>
              </div>
            </div>
          </div>
        </div>
      </section>

    </main>
  </div>

  <!-- AUDIT MODAL -->
  <div id="auditModal" class="hidden fixed inset-0 bg-slate-900/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
    <div class="bg-white w-full max-w-2xl rounded-xl shadow-2xl border border-slate-200 overflow-hidden flex flex-col max-h-[80vh]">
      <div class="bg-slate-900 text-white p-4 flex justify-between items-center">
        <h3 class="font-bold text-sm flex items-center gap-2"><i class="fa-solid fa-shield-cat text-amber-400"></i> AegisSepsis Scientific Audit Report</h3>
        <button onclick="closeAuditModal()" class="text-slate-400 hover:text-white"><i class="fa-solid fa-xmark text-lg"></i></button>
      </div>
      <div class="p-4 overflow-y-auto space-y-3 flex-1 text-xs" id="auditModalBody"></div>
      <div class="bg-slate-50 p-3 border-t text-right">
        <button onclick="closeAuditModal()" class="bg-slate-800 text-white px-4 py-1.5 rounded text-xs font-bold">Close Audit</button>
      </div>
    </div>
  </div>

  <!-- JAVASCRIPT ENGINE -->
  <script>
    let lastInferenceData = null;
    let allFeaturesList = [];

    const manuscriptTexts = """ + js_manuscript_json + r""";

    function switchNav(id) {
      document.querySelectorAll('main > section').forEach(sec => sec.classList.add('hidden'));
      document.querySelectorAll('.nav-link').forEach(link => link.classList.remove('active'));

      const targetSec = document.getElementById('sec-' + id);
      const targetNav = document.getElementById('nav-' + id);

      if (targetSec) targetSec.classList.remove('hidden');
      if (targetNav) targetNav.classList.add('active');

      if (window.MathJax) {
        window.MathJax.typesetPromise();
      }
    }

    function switchMTab(key) {
      document.querySelectorAll('.m-tab').forEach(t => t.classList.remove('active'));
      const activeBtn = document.getElementById('mtab-' + key);
      if (activeBtn) activeBtn.classList.add('active');

      const viewer = document.getElementById('manuscriptViewer');
      if (viewer && manuscriptTexts[key]) {
        viewer.innerHTML = manuscriptTexts[key].replace(/\n/g, '<br>');
      }
    }

    async function loadFiguresGallery() {
      try {
        const res = await fetch('/api/figures/list');
        if (!res.ok) return;
        const figures = await res.json();
        const container = document.getElementById('figuresGalleryGrid');
        if (!container) return;
        container.innerHTML = '';
        figures.forEach(fig => {
          container.innerHTML += `
            <div class="bg-white rounded-xl border border-slate-200 p-4 shadow-sm space-y-3">
              <div class="flex justify-between items-center border-b pb-2">
                <h3 class="font-bold text-slate-800 text-xs">${fig.title}</h3>
                <div class="flex gap-1.5">
                  <a href="${fig.svg}" target="_blank" class="text-[10px] bg-indigo-50 text-indigo-700 hover:bg-indigo-100 px-2 py-0.5 rounded font-bold border border-indigo-200">Vector SVG</a>
                  <a href="${fig.png}" target="_blank" class="text-[10px] bg-slate-100 text-slate-700 hover:bg-slate-200 px-2 py-0.5 rounded font-bold border border-slate-300">High-DPI PNG</a>
                </div>
              </div>
              <div class="bg-slate-900/5 p-2 rounded flex justify-center items-center min-h-[220px]">
                <img src="${fig.png}" alt="${fig.title}" class="max-h-64 object-contain rounded shadow-sm">
              </div>
              <p class="text-[11px] text-slate-600 leading-tight">${fig.caption}</p>
            </div>
          `;
        });
      } catch (e) {
        console.log('Error loading figures gallery:', e);
      }
    }

    async function loadDynamicTables() {
      try {
        const ablRes = await fetch('/api/ablation/results');
        if (ablRes.ok) {
          const ablData = await ablRes.json();
          const tbody = document.querySelector('#ablationTable tbody');
          if (tbody) {
            tbody.innerHTML = '';
            (ablData.experiments || []).forEach(exp => {
              tbody.innerHTML += `
                <tr class="hover:bg-slate-50">
                  <td class="p-2 font-mono font-bold">${exp.Exp_ID}</td>
                  <td class="p-2 font-semibold">${exp.Experiment_Name}</td>
                  <td class="p-2 text-slate-500">${exp.Features_Used}</td>
                  <td class="p-2 font-bold text-teal-700">${exp.Internal_AUROC}</td>
                  <td class="p-2">${exp.Internal_AUPRC}</td>
                  <td class="p-2">${exp.Internal_Patient_Sensitivity}</td>
                  <td class="p-2">${exp.Internal_Confirmation_PPV}</td>
                  <td class="p-2 font-bold text-amber-700">${exp.External_SetB_AUROC}</td>
                </tr>
              `;
            });
          }
        }

        const litRes = await fetch('/api/literature/matrix');
        if (litRes.ok) {
          const litData = await litRes.json();
          const tbody = document.querySelector('#litTable tbody');
          if (tbody) {
            tbody.innerHTML = '';
            (litData || []).forEach(row => {
              const badge = row.Weakens_BioMarkerX_Novelty_Claim === 'YES' 
                ? '<span class="bg-red-100 text-red-800 font-bold px-1.5 py-0.5 rounded">YES</span>'
                : (row.Weakens_BioMarkerX_Novelty_Claim === 'UNCLEAR' 
                  ? '<span class="bg-amber-100 text-amber-800 font-bold px-1.5 py-0.5 rounded">UNCLEAR</span>' 
                  : '<span class="bg-emerald-100 text-emerald-800 font-bold px-1.5 py-0.5 rounded">NO</span>');

              tbody.innerHTML += `
                <tr class="hover:bg-slate-50">
                  <td class="p-2 font-bold text-slate-800">${row.Paper_Title}<br><span class="text-slate-400 font-normal">${row.Authors} (DOI: ${row.DOI})</span></td>
                  <td class="p-2">${row.Year} / ${row.Journal_Venue}</td>
                  <td class="p-2">${row.Dataset}</td>
                  <td class="p-2 text-slate-600">${row.What_They_Did}</td>
                  <td class="p-2 text-teal-700 font-semibold">${row.What_BioMarkerX_Does_Differently}</td>
                  <td class="p-2">${badge}</td>
                </tr>
              `;
            });
          }
        }

        const featRes = await fetch('/api/features/manifest');
        if (featRes.ok) {
          const featData = await featRes.json();
          allFeaturesList = featData.features || [];
          renderFeaturesTable(allFeaturesList);
        }

        const modelRes = await fetch('/api/model/card');
        if (modelRes.ok) {
          const modelData = await modelRes.json();
          document.getElementById('modelCardContent').innerHTML = `
            <div class="flex justify-between items-center border-b pb-1 font-mono text-cyan-700 font-bold">
              <span>Classifier: ${modelData.model_type}</span>
              <span>SHA256: ${modelData.sha256}</span>
            </div>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-2 pt-1 font-mono">
              <div>max_depth: ${modelData.hyperparameters.max_depth || 6}</div>
              <div>num_leaves: ${modelData.hyperparameters.max_leaf_nodes || 31}</div>
              <div>learning_rate: ${modelData.hyperparameters.learning_rate || 0.035}</div>
              <div>subsample: ${modelData.hyperparameters.subsample || 0.80}</div>
            </div>
          `;
        }

        const intRes = await fetch('/api/results/internal');
        if (intRes.ok) {
          const intData = await intRes.json();
          document.getElementById('internalResContent').innerHTML = `
            <div class="font-bold text-slate-800 border-b pb-1">${intData.cohort}</div>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-2 pt-1 font-mono">
              <div>AUROC (S4): ${intData.metrics.auroc_s4}</div>
              <div>AUPRC (S4): ${intData.metrics.auprc_s4}</div>
              <div>Brier Score: ${intData.metrics.brier_s4}</div>
              <div>Patient Sens: ${intData.metrics.patient_sensitivity_pct}%</div>
            </div>
          `;
        }

        const extRes = await fetch('/api/results/external');
        if (extRes.ok) {
          const extData = await extRes.json();
          document.getElementById('externalResContent').innerHTML = `
            <div class="font-bold text-slate-800 border-b pb-1">${extData.cohort}</div>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-2 pt-1 font-mono">
              <div>AUROC (S4): ${extData.metrics.auroc_s4}</div>
              <div>AUPRC (S4): ${extData.metrics.auprc_s4}</div>
              <div>Patient Sens: ${extData.metrics.patient_sensitivity_pct}%</div>
              <div>Confirmation PPV: ${extData.metrics.confirmation_ppv_pct}%</div>
            </div>
          `;
        }

      } catch (e) {
        console.log('Error loading dynamic tables:', e);
      }
    }

    function renderFeaturesTable(list) {
      const tbody = document.querySelector('#featTable tbody');
      if (!tbody) return;
      tbody.innerHTML = '';
      list.forEach(f => {
        tbody.innerHTML += `
          <tr class="hover:bg-slate-50">
            <td class="p-2 font-mono font-bold text-slate-500">${f.id}</td>
            <td class="p-2 font-bold text-slate-800">${f.name}</td>
            <td class="p-2"><span class="bg-slate-100 text-slate-700 px-1.5 py-0.5 rounded font-mono">${f.category}</span></td>
            <td class="p-2 text-emerald-700 font-bold">${f.causal_status}</td>
            <td class="p-2 font-mono">${f.train_median}</td>
          </tr>
        `;
      });
    }

    function filterFeatures() {
      const q = document.getElementById('featSearch').value.toLowerCase();
      const filtered = allFeaturesList.filter(f => f.name.toLowerCase().includes(q) || f.category.toLowerCase().includes(q));
      renderFeaturesTable(filtered);
    }

    async function runProgrammaticAudit() {
      try {
        const res = await fetch('/api/audit/check');
        const data = await res.json();
        
        const modalBody = document.getElementById('auditModalBody');
        modalBody.innerHTML = `
          <div class="flex justify-between items-center p-2 bg-slate-100 rounded border">
            <span class="font-bold text-slate-700">Audit Timestamp: ${data.timestamp}</span>
            <span class="bg-emerald-600 text-white font-bold px-2 py-0.5 rounded">STATUS: ${data.status}</span>
          </div>
          <div class="space-y-1.5">
        `;

        data.checks.forEach(chk => {
          modalBody.innerHTML += `
            <div class="p-2 border rounded bg-white flex justify-between items-center">
              <div>
                <span class="font-bold text-slate-800">${chk.domain}</span>
                <p class="text-[11px] text-slate-500">${chk.details}</p>
              </div>
              <span class="font-mono text-emerald-700 font-bold">${chk.actual}</span>
            </div>
          `;
        });

        modalBody.innerHTML += `</div>`;
        document.getElementById('auditModal').classList.remove('hidden');
      } catch (err) {
        alert('Audit Error: ' + err.message);
      }
    }

    function closeAuditModal() {
      document.getElementById('auditModal').classList.add('hidden');
    }

    async function runInference(e) {
      if (e) e.preventDefault();
      const payload = {
        hospital_name: document.getElementById('inp_hosp').value,
        doctor_name: document.getElementById('inp_doc').value,
        patient_name: document.getElementById('inp_pname').value,
        mrn_id: document.getElementById('inp_mrn').value,
        age: parseInt(document.getElementById('inp_age').value),
        gender: document.getElementById('inp_gender').value,
        icu_bed: document.getElementById('inp_bed').value,
        vitals: {
          HR: parseFloat(document.getElementById('inp_HR').value),
          SBP: parseFloat(document.getElementById('inp_SBP').value),
          MAP: parseFloat(document.getElementById('inp_MAP').value),
          MAP_delta3: parseFloat(document.getElementById('inp_MAP_d3').value),
          Temp: parseFloat(document.getElementById('inp_Temp').value),
          Resp: parseFloat(document.getElementById('inp_Resp').value),
          WBC: parseFloat(document.getElementById('inp_WBC').value),
          Lactate: parseFloat(document.getElementById('inp_Lactate').value)
        }
      };

      try {
        const res = await fetch('/api/predict', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const out = await res.json();
        
        lastInferenceData = { ...payload, ...out };

        document.getElementById('inferResults').classList.remove('hidden');
        document.getElementById('res_prob').innerText = (out.calibrated_prob * 100).toFixed(1) + '%';
        if (document.getElementById('res_summary_text')) {
          document.getElementById('res_summary_text').innerText = out.clinical_summary || '';
        }
        if (document.getElementById('res_stream_rationale')) {
          document.getElementById('res_stream_rationale').innerText = out.continuous_monitoring_rationale || '';
        }

        if (document.getElementById('res_narrative_paragraph')) {
          const hr = payload.vitals.HR || 108;
          const sbp = payload.vitals.SBP || 92;
          const map = payload.vitals.MAP || 68;
          const map_d3 = payload.vitals.MAP_delta3 || -4.5;
          const resp = payload.vitals.Resp || 26;
          const wbc = payload.vitals.WBC || 14.8;
          const lac = payload.vitals.Lactate || 3.2;
          const si = (hr / Math.max(sbp, 40)).toFixed(2);
          const pct = (out.calibrated_prob * 100).toFixed(1);

          document.getElementById('res_narrative_paragraph').innerHTML = `
            <b>Diagnostic Synthesis (t=0h Evaluation):</b> The patient presents with a calibrated sepsis risk probability of <b>${pct}%</b> (${out.risk_category}). 
            Pathophysiologically, this risk elevation is driven by acute systemic vasodilation and uncompensated tissue hypoperfusion. 
            The patient exhibits compensatory tachycardia (HR: <b>${hr} bpm</b>, Z-velocity &gt; +0.3/hr) alongside acute arterial hypotension (MAP: <b>${map} mmHg</b>, 3h drop: <b>${map_d3} mmHg</b>), elevating the Shock Index to <b>${si}</b> (baseline median: 0.72). 
            Elevated blood lactate (<b>${lac} mmol/L</b>, normal: 0.5-1.6 mmol/L) confirms cellular dysoxia and an anaerobic metabolic shift. 
            Leukocytosis (WBC: <b>${wbc} &times; 10<sup>3</sup>/&mu;L</b>) and tachypnea (Resp: <b>${resp} breaths/min</b>) reflect SIRS activation and respiratory compensation. 
            The continuous temporal engine (v1.0.0_canonical_lock) confirms acute organ dysfunction targeted within the 4-hour forward lookahead window ($S_{next4}$).
          `;
        }

        const badge = document.getElementById('res_badge');
        badge.innerText = out.risk_category;
        if (out.risk_category.includes('CRITICAL')) {
          badge.className = 'inline-block px-3 py-1 rounded-full text-xs font-bold bg-red-100 text-red-700 border border-red-300 shadow-sm';
        } else if (out.risk_category.includes('MODERATE')) {
          badge.className = 'inline-block px-3 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-700 border border-amber-300 shadow-sm';
        } else {
          badge.className = 'inline-block px-3 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-700 border border-emerald-300 shadow-sm';
        }

        document.getElementById('res_scr').innerText = out.screening_tier.triggered ? 'ACTIVE (ALERT)' : 'NORMAL';
        document.getElementById('res_scr').className = out.screening_tier.triggered ? 'font-bold text-amber-400' : 'font-bold text-emerald-400';
        
        document.getElementById('res_gate').innerText = out.confirmation_tier.map_gate_pass ? 'PASSED' : 'BLOCKED';
        document.getElementById('res_gate').className = out.confirmation_tier.map_gate_pass ? 'font-bold text-emerald-400' : 'font-bold text-slate-400';

        document.getElementById('res_conf').innerText = out.confirmation_tier.triggered ? 'ALARM TRIGGERED!' : 'NORMAL';
        document.getElementById('res_conf').className = out.confirmation_tier.triggered ? 'font-bold text-red-400 animate-pulse' : 'font-bold text-emerald-400';

        // Render 12-Hour Temporal Trajectory (-12h to +4h)
        const trajHeaders = document.getElementById('trajHeaders');
        const fcRow = document.getElementById('forecastRow');
        if (trajHeaders && fcRow && out.temporal_trajectory_12h) {
          trajHeaders.innerHTML = '';
          fcRow.innerHTML = '';
          let headHtml = '';
          let rowHtml = '';

          out.temporal_trajectory_12h.forEach(pt => {
            const isTarget = pt.hour > 0;
            const bgHead = isTarget ? 'bg-indigo-900/60 text-cyan-300' : 'bg-slate-900 text-slate-400';
            headHtml += `<th class="p-1.5 ${bgHead} border border-slate-800">${pt.label}</th>`;

            const pct = (pt.prob * 100).toFixed(1);
            let color = pct >= 30.0 ? 'text-red-400 font-bold bg-red-950/30' : (pct >= 1.5 ? 'text-amber-400 font-bold bg-amber-950/20' : 'text-emerald-400 font-bold bg-emerald-950/20');
            rowHtml += `<td class="p-2 border border-slate-800 ${color}">${pct}%</td>`;
          });

          trajHeaders.innerHTML = headHtml;
          fcRow.innerHTML = `<tr>${rowHtml}</tr>`;
        }

        // Render Risk Drivers (Factors Increasing Sepsis Risk)
        const riskIncDiv = document.getElementById('res_risk_increasing');
        if (riskIncDiv) {
          riskIncDiv.innerHTML = '';
          if (out.risk_increasing_factors && out.risk_increasing_factors.length > 0) {
            out.risk_increasing_factors.forEach(item => {
              riskIncDiv.innerHTML += `
                <div class="flex justify-between items-center p-2 bg-red-900/40 border border-red-800/60 rounded">
                  <div>
                    <div class="font-bold text-red-200">${item.name} (${item.user_value} ${item.unit})</div>
                    <div class="text-[10px] text-red-400">Baseline Pop Median: ${item.median_value} ${item.unit} | Norm: ${item.normal_range}</div>
                  </div>
                  <span class="text-red-300 font-bold font-mono text-xs">+${item.contribution} SHAP</span>
                </div>
              `;
            });
          } else {
            riskIncDiv.innerHTML = '<div class="text-slate-400 italic text-xs">No significant risk-increasing factors detected.</div>';
          }
        }

        // Render Protective Factors (Factors Reducing Sepsis Risk)
        const riskDecDiv = document.getElementById('res_risk_decreasing');
        if (riskDecDiv) {
          riskDecDiv.innerHTML = '';
          if (out.risk_decreasing_factors && out.risk_decreasing_factors.length > 0) {
            out.risk_decreasing_factors.forEach(item => {
              riskDecDiv.innerHTML += `
                <div class="flex justify-between items-center p-2 bg-emerald-900/40 border border-emerald-800/60 rounded">
                  <div>
                    <div class="font-bold text-emerald-200">${item.name} (${item.user_value} ${item.unit})</div>
                    <div class="text-[10px] text-emerald-400">Baseline Pop Median: ${item.median_value} ${item.unit} | Norm: ${item.normal_range}</div>
                  </div>
                  <span class="text-emerald-300 font-bold font-mono text-xs">${item.contribution} SHAP</span>
                </div>
              `;
            });
          } else {
            riskDecDiv.innerHTML = '<div class="text-slate-400 italic text-xs">No significant protective factors detected.</div>';
          }
        }

      } catch (err) {
        alert('Inference API Error: ' + err.message);
      }
    }

    async function downloadPatientReportPDF() {
      if (!lastInferenceData) {
        await runInference(null);
      }
      
      try {
        const res = await fetch('/api/generate_patient_report', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(lastInferenceData)
        });
        
        if (!res.ok) throw new Error('PDF Generation Failed');

        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `AegisSepsis_Patient_Report_${lastInferenceData.mrn_id || '984210'}.pdf`;
        document.body.appendChild(a);
        a.click();
        a.remove();
      } catch (err) {
        alert('PDF Download Error: ' + err.message);
      }
    }

    window.addEventListener('DOMContentLoaded', () => {
      loadDynamicTables();
      loadFiguresGallery();
      switchMTab('abstract');
    });
  </script>
</body>
</html>
"""

with open(index_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print("World-class AegisSepsis AI dashboard HTML written to index.html successfully.")
