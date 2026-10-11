import os
import re

index_path = r"c:\Users\LENOVO\Downloads\spesis dataset\index.html"
with open(index_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update Header Buttons to include Word Manuscript Download
header_old = r"""      <a href="/download/monograph-pdf" class="bg-teal-600 hover:bg-teal-500 text-white text-xs font-semibold px-3 py-1.5 rounded transition flex items-center gap-1.5 shadow">
        <i class="fa-solid fa-file-pdf"></i> Master PDF Monograph
      </a>"""

header_new = r"""      <a href="/download/manuscript-docx" class="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold px-3 py-1.5 rounded transition flex items-center gap-1.5 shadow">
        <i class="fa-solid fa-file-word"></i> Word Manuscript (.docx)
      </a>
      <a href="/download/monograph-pdf" class="bg-teal-600 hover:bg-teal-500 text-white text-xs font-semibold px-3 py-1.5 rounded transition flex items-center gap-1.5 shadow">
        <i class="fa-solid fa-file-pdf"></i> Master PDF Monograph
      </a>"""

content = content.replace(header_old, header_new)

# 2. Add Published Figures & Novelty Explorer logic
script_addon = r"""
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
              <div class="bg-slate-900/5 p-2 rounded flex justify-center items-center min-h-[200px]">
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

    window.addEventListener('DOMContentLoaded', () => {
      loadDynamicTables();
      loadFiguresGallery();
    });
"""

content = content.replace("window.addEventListener('DOMContentLoaded', () => {\n      loadDynamicTables();\n    });", script_addon)

with open(index_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated index.html header download button and dynamic script.")
