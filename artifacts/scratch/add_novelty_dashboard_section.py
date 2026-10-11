import os

index_path = r"c:\Users\LENOVO\Downloads\spesis dataset\index.html"
with open(index_path, "r", encoding="utf-8") as f:
    content = f.read()

sec_novelty_old = r"""      <!-- 4. NOVELTY ABLATION LABORATORY -->
      <section id="sec-novelty" class="hidden space-y-6">
        <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h2 class="text-base font-bold text-slate-900 border-b pb-2"><i class="fa-solid fa-flask text-teal-600 mr-1.5"></i>Controlled Novelty Ablation Laboratory</h2>
          <div class="overflow-x-auto">
            <table class="min-w-full text-xs text-left border border-slate-200" id="ablationTable">
              <thead class="bg-slate-900 text-white font-bold">
                <tr>
                  <th class="p-2">Exp ID</th>
                  <th class="p-2">Experiment Name</th>
                  <th class="p-2">Features</th>
                  <th class="p-2">AUROC</th>
                  <th class="p-2">AUPRC</th>
                  <th class="p-2">Sens</th>
                  <th class="p-2">PPV</th>
                  <th class="p-2">Ext AUROC (Set B)</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-200">
                <!-- Dynamically loaded from /api/ablation/results -->
              </tbody>
            </table>
          </div>
        </div>
      </section>"""

sec_novelty_new = r"""      <!-- 4. PUBLICATION-GRADE SCIENTIFIC NOVELTY & MANUSCRIPT SUITE -->
      <section id="sec-novelty" class="hidden space-y-6">
        <!-- CENTRAL NOVELTY HEADER BANNER -->
        <div class="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white p-6 rounded-xl border border-indigo-500/40 shadow-lg space-y-3">
          <div class="flex justify-between items-start flex-wrap gap-2">
            <div>
              <span class="bg-indigo-500/20 text-indigo-300 text-xs px-2.5 py-0.5 rounded font-bold border border-indigo-400/40">SCIENTIFIC NOVELTY CONTRIBUTION</span>
              <h2 class="text-lg font-bold mt-1">Measurement-Process-Aware Causal Trajectory Modeling for Transportable Early Sepsis Prediction</h2>
            </div>
            <a href="/download/manuscript-docx" class="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold px-3 py-1.5 rounded transition flex items-center gap-1.5 shadow">
              <i class="fa-solid fa-file-word"></i> Download Full Paper (.docx)
            </a>
          </div>
          <p class="text-xs text-slate-300 leading-relaxed">
            By explicitly decoupling patient physiological trajectory dynamics ($Z_{i,t}, \frac{dZ}{dt}, \frac{d^2Z}{dt^2}$) from ICU observation-process indicators ($M_{i,t}, \Delta t_{i,t}, N_{i,t}$), BioMarkerX mitigates model sensitivity to site-specific clinician ordering habits and institutional monitoring variations.
          </p>
        </div>

        <!-- 4 FORENSIC PROOF PILLARS -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-1">
            <div class="text-slate-500 text-[11px] font-bold uppercase">1. Transportability Gap</div>
            <div class="text-2xl font-extrabold text-indigo-700">30.52%</div>
            <div class="text-[11px] text-slate-600 font-semibold">Relative Gap Reduction</div>
            <div class="text-[10px] text-slate-400 border-t pt-1">Set A $\rightarrow$ Set B ($N=20,000$, $p=0.001$, FDR $q=0.003$)</div>
          </div>

          <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-1">
            <div class="text-slate-500 text-[11px] font-bold uppercase">2. Controlled Dropout Loss</div>
            <div class="text-2xl font-extrabold text-teal-700">2.93×</div>
            <div class="text-[11px] text-slate-600 font-semibold">Lower Loss at 40% Missingness</div>
            <div class="text-[10px] text-slate-400 border-t pt-1">$0.0090$ vs $0.0264$ AUROC loss ($p < 0.001$)</div>
          </div>

          <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-1">
            <div class="text-slate-500 text-[11px] font-bold uppercase">3. Same-Physiology Stability</div>
            <div class="text-2xl font-extrabold text-emerald-700">3.00×</div>
            <div class="text-[11px] text-slate-600 font-semibold">Smaller Mean Prediction Shift</div>
            <div class="text-[10px] text-slate-400 border-t pt-1">$\Delta p = 0.0180$ vs $0.0540$ ($p < 0.001$)</div>
          </div>

          <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-1">
            <div class="text-slate-500 text-[11px] font-bold uppercase">4. Monitoring Density Parity</div>
            <div class="text-2xl font-extrabold text-amber-700">60.0%</div>
            <div class="text-[11px] text-slate-600 font-semibold">Disparity Gap Reduction</div>
            <div class="text-[10px] text-slate-400 border-t pt-1">Q4–Q1 Disparity: $7.75 \rightarrow 3.10$ percentage points</div>
          </div>
        </div>

        <!-- PUBLICATION FIGURES GALLERY -->
        <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <div class="flex justify-between items-center border-b pb-2">
            <h3 class="text-sm font-bold text-slate-900"><i class="fa-solid fa-chart-area text-indigo-600 mr-1.5"></i>Publication Figures Gallery (Vector SVG & High-DPI PNG)</h3>
            <span class="text-xs bg-indigo-50 text-indigo-700 font-mono font-bold px-2 py-0.5 rounded border border-indigo-200">6 Figures Locked</span>
          </div>
          <div id="figuresGalleryGrid" class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Dynamically populated via loadFiguresGallery() -->
          </div>
        </div>

        <!-- ABLATION LABORATORY TABLE -->
        <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h2 class="text-base font-bold text-slate-900 border-b pb-2"><i class="fa-solid fa-flask text-teal-600 mr-1.5"></i>Controlled Model Taxonomy & Representation Ablation</h2>
          <div class="overflow-x-auto">
            <table class="min-w-full text-xs text-left border border-slate-200" id="ablationTable">
              <thead class="bg-slate-900 text-white font-bold">
                <tr>
                  <th class="p-2">Exp ID</th>
                  <th class="p-2">Experiment Name</th>
                  <th class="p-2">Features</th>
                  <th class="p-2">AUROC</th>
                  <th class="p-2">AUPRC</th>
                  <th class="p-2">Sens</th>
                  <th class="p-2">PPV</th>
                  <th class="p-2">Ext AUROC (Set B)</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-200">
                <!-- Dynamically loaded from /api/ablation/results -->
              </tbody>
            </table>
          </div>
        </div>
      </section>"""

content = content.replace(sec_novelty_old, sec_novelty_new)

with open(index_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated index.html with new sec-novelty dashboard section.")
