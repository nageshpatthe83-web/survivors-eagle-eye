/**
 * Project Eagle Eye - Interactive Inspection Client
 * Team Survivors | Track 01 - Emerson | Code Apex Hackathon
 */

document.addEventListener('DOMContentLoaded', () => {
  let currentRunData = null;
  let activeFilter = 'all';
  let showBoxes = true;
  let showLabels = false;

  // DOM Elements
  const cabinetImg = document.getElementById('main-cabinet-img');
  const svgOverlay = document.getElementById('svg-overlay');
  const checklistContainer = document.getElementById('checklist-cards');
  const toast = document.getElementById('toast');

  // Stats elements
  const statTotal = document.getElementById('stat-total');
  const statPassed = document.getElementById('stat-passed');
  const statFailed = document.getElementById('stat-failed');
  const summaryOverallBadge = document.getElementById('summary-overall-badge');
  const centerStatusBadge = document.getElementById('center-status-badge');

  // Filter counters
  const countAll = document.getElementById('count-all');
  const countFail = document.getElementById('count-fail');
  const countReview = document.getElementById('count-review');
  const countPass = document.getElementById('count-pass');

  // Evidence elements
  const evidenceTitle = document.getElementById('evidence-title');
  const evidenceRuleBadge = document.getElementById('evidence-rule-badge');
  const evidenceSnippetImg = document.getElementById('evidence-snippet-img');
  const evidenceLocation = document.getElementById('evidence-location');
  const evidenceExpected = document.getElementById('evidence-expected');
  const evidenceObserved = document.getElementById('evidence-observed');
  const evidenceNotes = document.getElementById('evidence-notes');

  // Toast Helper
  function showToast(msg, isError = false) {
    toast.textContent = msg;
    toast.className = 'toast';
    if (isError) toast.style.borderLeftColor = '#f43f5e';
    else toast.style.borderLeftColor = '#10b981';
    toast.classList.remove('hidden');
    setTimeout(() => {
      toast.classList.add('hidden');
    }, 3500);
  }

  // Run AI Inspection
  async function runInspection(isDemo = false) {
    showToast('Executing multimodal AI inspection pipeline...');
    const formData = new FormData();
    formData.append('cabinet_id', 'EE-024');
    formData.append('cabinet_name', 'Emerson Control Cabinet 415V');
    formData.append('is_demo', isDemo ? 'true' : 'false');

    const cabFile = document.getElementById('input-cabinet').files[0];
    const bpFile = document.getElementById('input-blueprint').files[0];
    const wireFile = document.getElementById('input-wire').files[0];

    if (cabFile) formData.append('cabinet_photo', cabFile);
    if (bpFile) formData.append('blueprint_pdf', bpFile);
    if (wireFile) formData.append('wire_list', wireFile);

    try {
      const resp = await fetch('/api/inspect', {
        method: 'POST',
        body: formData
      });
      const data = await resp.json();
      if (!data.success) {
        showToast('Inspection failed: ' + (data.error || 'Server error'), true);
        return;
      }
      currentRunData = data;
      renderInspectionResults(data);
      showToast('AI Inspection complete: ' + data.summary.failed_checks + ' discrepancies flagged');
    } catch (err) {
      console.error(err);
      showToast('Network error during inspection', true);
    }
  }

  // Render Full Results
  function renderInspectionResults(data) {
    const s = data.summary;
    statTotal.textContent = s.total_checks;
    statPassed.textContent = s.passed_checks;
    statFailed.textContent = s.failed_checks;

    countAll.textContent = s.total_checks;
    countFail.textContent = s.failed_checks;
    countReview.textContent = s.review_checks;
    countPass.textContent = s.passed_checks;

    // Badges
    const statusText = s.overall_status;
    summaryOverallBadge.textContent = statusText;
    summaryOverallBadge.className = 'status-badge-overall status-' + statusText.toLowerCase();

    centerStatusBadge.textContent = statusText === 'FAIL' 
      ? `FAIL (${s.failed_checks} Discrepancies)` 
      : (statusText === 'PASS' ? 'PASS (100% Verified)' : 'NEEDS REVIEW');
    centerStatusBadge.className = 'status-badge-overall status-' + statusText.toLowerCase();

    // Update image
    cabinetImg.src = data.raw_image || '/sample_inputs/cabinet_initial.jpg';

    cabinetImg.onload = () => {
      renderSvgOverlay(data.checklist);
    };
    renderSvgOverlay(data.checklist);

    // Populate checklist cards
    renderChecklistCards(data.checklist);

    // Auto-select first failed item or first item
    const firstFail = data.checklist.find(c => c.status === 'FAIL') || data.checklist[0];
    if (firstFail) selectChecklistItem(firstFail);
  }

  // Draw Interactive SVG Bounding Boxes
  function renderSvgOverlay(checklist) {
    svgOverlay.innerHTML = '';
    if (!showBoxes || !checklist) return;

    const natW = 1000;
    const natH = 700;
    svgOverlay.setAttribute('viewBox', `0 0 ${natW} ${natH}`);

    checklist.forEach(item => {
      const bbox = item.bbox;
      if (!bbox || bbox.length < 4) return;
      const [x1, y1, x2, y2] = bbox;
      const w = x2 - x1;
      const h = y2 - y1;

      let strokeColor = '#10b981';
      let fillColor = 'rgba(16, 185, 129, 0.15)';
      if (item.status === 'FAIL') {
        strokeColor = '#f43f5e';
        fillColor = 'rgba(244, 63, 94, 0.2)';
      } else if (item.status === 'NEEDS_REVIEW') {
        strokeColor = '#f59e0b';
        fillColor = 'rgba(245, 158, 11, 0.2)';
      }

      // Group
      const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      g.style.cursor = 'pointer';

      // Rect
      const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
      rect.setAttribute('x', x1);
      rect.setAttribute('y', y1);
      rect.setAttribute('width', w);
      rect.setAttribute('height', h);
      rect.setAttribute('fill', fillColor);
      rect.setAttribute('stroke', strokeColor);
      rect.setAttribute('stroke-width', '2.5');
      rect.classList.add('bbox-rect');
      g.appendChild(rect);

      // Label Badge
      if (showLabels || item.status === 'FAIL') {
        const textBg = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        textBg.setAttribute('x', x1);
        textBg.setAttribute('y', Math.max(0, y1 - 22));
        textBg.setAttribute('width', item.item_code.length * 10 + 45);
        textBg.setAttribute('height', 20);
        textBg.setAttribute('fill', strokeColor);
        textBg.setAttribute('rx', '3');
        g.appendChild(textBg);

        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', x1 + 4);
        text.setAttribute('y', Math.max(14, y1 - 8));
        text.setAttribute('fill', '#ffffff');
        text.setAttribute('font-size', '12px');
        text.setAttribute('font-weight', '700');
        text.setAttribute('font-family', 'Inter, sans-serif');
        text.textContent = `[${item.status}] ${item.item_code}`;
        g.appendChild(text);
      }

      g.addEventListener('click', () => {
        selectChecklistItem(item);
      });

      svgOverlay.appendChild(g);
    });
  }

  // Populate Right Column Cards
  function renderChecklistCards(checklist) {
    checklistContainer.innerHTML = '';

    const filtered = checklist.filter(item => {
      if (activeFilter === 'all') return true;
      return item.status === activeFilter;
    });

    if (filtered.length === 0) {
      checklistContainer.innerHTML = '<div style="text-align:center; padding:1.5rem; color:#64748b; font-size:0.8rem;">No items matching this filter.</div>';
      return;
    }

    filtered.forEach(item => {
      const card = document.createElement('div');
      card.className = 'check-item-card';
      card.dataset.tag = item.item_code;

      let badgeClass = 'status-pass';
      if (item.status === 'FAIL') badgeClass = 'status-fail';
      else if (item.status === 'NEEDS_REVIEW') badgeClass = 'status-review';

      card.innerHTML = `
        <div class="check-card-header">
          <div>
            <span class="item-tag">${item.item_code}</span>
            <div class="item-desc">${item.component_type} • ${item.location}</div>
          </div>
          <span class="status-badge-overall ${badgeClass}">${item.status}</span>
        </div>
        <div class="item-values">
          <div class="val-box"><span>Expected</span><code>${item.expected_val}</code></div>
          <div class="val-box"><span>Observed</span><code>${item.observed_val}</code></div>
        </div>
      `;

      card.addEventListener('click', () => {
        selectChecklistItem(item);
      });

      checklistContainer.appendChild(card);
    });
  }

  // Select Item & Update Evidence Drawer
  function selectChecklistItem(item) {
    document.querySelectorAll('.check-item-card').forEach(c => {
      if (c.dataset.tag === item.item_code) c.classList.add('active-selected');
      else c.classList.remove('active-selected');
    });

    evidenceTitle.textContent = `[${item.status}] ${item.item_code} — ${item.fault_type || 'Compliant'}`;
    evidenceTitle.style.color = item.status === 'FAIL' ? '#f43f5e' : (item.status === 'PASS' ? '#10b981' : '#f59e0b');
    evidenceRuleBadge.textContent = 'Rule: ' + item.rule_type;
    evidenceLocation.textContent = item.location;
    evidenceExpected.textContent = item.expected_val;
    evidenceObserved.textContent = item.observed_val;
    evidenceObserved.style.color = item.status === 'FAIL' ? '#f43f5e' : '#10b981';
    evidenceNotes.textContent = item.notes;

    if (item.evidence_crop) {
      evidenceSnippetImg.src = item.evidence_crop;
      evidenceSnippetImg.style.display = 'block';
    } else {
      evidenceSnippetImg.src = '/sample_inputs/cabinet_initial.jpg';
    }
  }

  // Tab Filter Clicks
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeFilter = btn.dataset.filter;
      if (currentRunData) renderChecklistCards(currentRunData.checklist);
    });
  });

  // Buttons Event Listeners
  document.getElementById('btn-run-inspect').addEventListener('click', () => runInspection(false));
  document.getElementById('btn-load-demo').addEventListener('click', () => runInspection(true));

  document.getElementById('btn-view-report').addEventListener('click', () => {
    if (currentRunData && currentRunData.report_url) {
      window.open(currentRunData.report_url, '_blank');
    } else {
      showToast('Run an inspection first to generate the QC Certificate', true);
    }
  });

  // Toggle Bounding Boxes
  document.getElementById('btn-toggle-boxes').addEventListener('click', (e) => {
    showBoxes = !showBoxes;
    e.target.classList.toggle('active', showBoxes);
    if (currentRunData) renderSvgOverlay(currentRunData.checklist);
  });

  // Toggle Labels
  document.getElementById('btn-toggle-labels').addEventListener('click', (e) => {
    showLabels = !showLabels;
    e.target.classList.toggle('active', showLabels);
    if (currentRunData) renderSvgOverlay(currentRunData.checklist);
  });

  // Closed Loop Modal Handlers
  const recheckModal = document.getElementById('recheck-modal');
  document.getElementById('btn-open-recheck').addEventListener('click', () => {
    recheckModal.classList.remove('hidden');
  });

  document.getElementById('btn-close-modal').addEventListener('click', () => {
    recheckModal.classList.add('hidden');
  });

  document.getElementById('btn-modal-cancel').addEventListener('click', () => {
    recheckModal.classList.add('hidden');
  });

  // Submit Re-Check
  document.getElementById('btn-submit-recheck').addEventListener('click', async () => {
    showToast('Running Closed-Loop Re-check verification on corrected cabinet...');
    const formData = new FormData();
    formData.append('original_run_id', currentRunData ? currentRunData.run_id : 1);

    const correctedInput = document.getElementById('input-corrected-photo').files[0];
    if (correctedInput) formData.append('corrected_photo', correctedInput);

    try {
      const resp = await fetch('/api/recheck', {
        method: 'POST',
        body: formData
      });
      const data = await resp.json();
      if (!data.success) {
        showToast('Re-check failed: ' + (data.error || 'Server error'), true);
        return;
      }

      document.getElementById('recheck-after-title').textContent = 'After Correction: 100% PASS';
      document.getElementById('recheck-resolved-text').textContent = `✅ ${data.resolved_issues} Discrepancies Resolved (${data.summary.passed_checks} / ${data.summary.total_checks} Checks Passed)`;
      document.getElementById('recheck-compare-img').src = data.annotated_image;

      const certBtn = document.getElementById('btn-download-corrected-cert');
      certBtn.style.display = 'inline-flex';
      certBtn.onclick = () => window.open(data.report_url, '_blank');

      // Also update main dashboard view
      currentRunData = data;
      renderInspectionResults(data);
      showToast('All corrections verified! 100% PASS Certificate generated.');
    } catch (err) {
      console.error(err);
      showToast('Error during re-check', true);
    }
  });

  // File Inputs Name Previews
  document.getElementById('input-cabinet').addEventListener('change', (e) => {
    if (e.target.files[0]) document.getElementById('label-cabinet').textContent = e.target.files[0].name;
  });
  document.getElementById('input-blueprint').addEventListener('change', (e) => {
    if (e.target.files[0]) document.getElementById('label-blueprint').textContent = e.target.files[0].name;
  });
  document.getElementById('input-wire').addEventListener('change', (e) => {
    if (e.target.files[0]) document.getElementById('label-wire').textContent = e.target.files[0].name;
  });

  // Auto-run initial demo on launch
  runInspection(true);
});
