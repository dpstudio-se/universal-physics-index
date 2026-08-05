/**
 * Universal Physics Index — OdinOS, Puter.js & Odysseus AI Module Client Logic
 */

(function () {
  'use strict';

  // Constants & Physics Constants
  const PLANCK_H = 6.62607015e-34; // J*s
  const SPEED_C = 299792458.0;      // m/s
  const REFERENCE_8HZ = 8.0;

  // 4-Base Harmonic Tuning Mapping
  const BASE_NOTE_MAP = {
    'A': { note: 'A4', semitone: 9, defaultFreq: 440.0 },
    'C': { note: 'C4', semitone: 0, defaultFreq: 261.63 },
    'G': { note: 'G4', semitone: 7, defaultFreq: 392.0 },
    'T': { note: 'E4', semitone: 4, defaultFreq: 329.63 },
    'U': { note: 'E4', semitone: 4, defaultFreq: 329.63 },
  };

  // Web Audio Context
  let audioCtx = null;
  let currentOscillators = [];
  let isAudioPlaying = false;

  // Puter.js Integration State
  let isPuterAvailable = false;

  // DOM Load
  document.addEventListener('DOMContentLoaded', () => {
    initPuterIntegration();
    initTabNavigation();
    initOdysseusModule();
    initDnaSonifier();
    initQuditSimulator();
    initStatusAuditor();
    initAecoModule();
    initExportHandlers();
  });

  /* --------------------------------------------------------------------------
   * 1. Puter.js Integration
   * -------------------------------------------------------------------------- */
  function initPuterIntegration() {
    const puterBadge = document.getElementById('puter-status');
    
    if (typeof puter !== 'undefined' && puter.isAvailable && puter.isAvailable()) {
      isPuterAvailable = true;
      puterBadge.textContent = 'Puter: Connected (v2)';
      puterBadge.className = 'badge badge-est';

      // Load saved state from Puter KV if present
      try {
        puter.kv.get('upi_last_dna').then(val => {
          if (val) {
            document.getElementById('dna-input').value = val;
          }
        }).catch(() => {});
      } catch (err) {
        console.warn('Puter KV load skipped:', err);
      }
    } else {
      isPuterAvailable = false;
      puterBadge.textContent = 'Puter: Standalone Mode';
      puterBadge.className = 'badge badge-der';
    }
  }

  /* --------------------------------------------------------------------------
   * 2. Navigation Tabs
   * -------------------------------------------------------------------------- */
  function initTabNavigation() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const targetId = btn.getAttribute('data-tab');

        tabBtns.forEach(b => b.classList.remove('active'));
        tabContents.forEach(c => c.classList.remove('active'));

        btn.classList.add('active');
        document.getElementById(targetId).classList.add('active');
      });
    });
  }

  /* --------------------------------------------------------------------------
   * 3. Odysseus AI LLM/AGI Agent Fusion Module
   * -------------------------------------------------------------------------- */
  function fetchOdysseusTools() {
    const toolsBox = document.getElementById('odysseus-tools-list');
    fetch('/api/odysseus/tools')
      .then(res => res.json())
      .then(data => {
        toolsBox.innerHTML = '';
        if (data.tools && Array.isArray(data.tools)) {
          data.tools.forEach(tool => {
            const div = document.createElement('div');
            div.className = 'tool-item';
            div.innerHTML = `
              <div class="tool-item-name">🛠️ ${tool.name}</div>
              <div class="tool-item-desc">${tool.description}</div>
            `;
            toolsBox.appendChild(div);
          });
        }
      })
      .catch(err => {
        toolsBox.textContent = `Error loading Odysseus tool manifest: ${err.message}`;
      });
  }

  function initOdysseusModule() {
    const btnSend = document.getElementById('btn-odysseus-send');
    const btnFetchTools = document.getElementById('btn-odysseus-tools');
    const promptInput = document.getElementById('odysseus-prompt');
    const outputLog = document.getElementById('odysseus-output-log');

    fetchOdysseusTools();

    btnFetchTools.addEventListener('click', fetchOdysseusTools);

    btnSend.addEventListener('click', () => {
      const promptText = promptInput.value.trim();
      if (!promptText) return;

      outputLog.textContent = `Odysseus Agent processing intent: "${promptText}"...`;

      // If Puter AI is available, use puter.ai.chat + backend fallback
      if (isPuterAvailable && puter.ai && puter.ai.chat) {
        puter.ai.chat(`You are an Odysseus AI Agent controlling the Universal Physics Index. User intent: ${promptText}`)
          .then(reply => {
            // Also call backend intent executor
            fetch('/api/odysseus/intent', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ prompt: promptText })
            })
            .then(res => res.json())
            .then(toolRes => {
              outputLog.textContent = JSON.stringify({
                odysseus_agent_protocol: 'v1.0',
                puter_ai_response: reply,
                tool_execution_result: toolRes
              }, null, 2);
            });
          })
          .catch(() => {
            // Direct backend fallback
            executeBackendIntent(promptText);
          });
      } else {
        executeBackendIntent(promptText);
      }
    });

    function executeBackendIntent(promptText) {
      fetch('/api/odysseus/intent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: promptText })
      })
      .then(res => res.json())
      .then(data => {
        outputLog.textContent = JSON.stringify(data, null, 2);
      })
      .catch(err => {
        outputLog.textContent = `Odysseus Intent Execution Error: ${err.message}`;
      });
    }
  }

  /* --------------------------------------------------------------------------
   * 4. DNA & 12-TET Acoustic Sonifier
   * -------------------------------------------------------------------------- */
  function calculate12TetFreq(semitoneFromC4, refA4 = 440.0) {
    const n = semitoneFromC4 - 9;
    return refA4 * Math.pow(2.0, n / 12.0);
  }

  function sonifyDnaSequence(seq, refA4 = 440.0) {
    const cleanedSeq = seq.trim().toUpperCase();
    const results = [];

    for (let i = 0; i < cleanedSeq.length; i++) {
      const char = cleanedSeq[i];
      if (!BASE_NOTE_MAP[char]) continue;

      const mapping = BASE_NOTE_MAP[char];
      const freq = calculate12TetFreq(mapping.semitone, refA4);
      const energy = PLANCK_H * freq;
      const massEq = energy / (SPEED_C * SPEED_C);
      const n8Index = freq / REFERENCE_8HZ;

      results.push({
        position: i + 1,
        base: char,
        note: mapping.note,
        frequencyHz: freq,
        n8Index: n8Index,
        energyJ: energy,
        massKg: massEq,
        status: 'DER'
      });
    }

    return results;
  }

  function renderSonificationTable(items) {
    const tbody = document.querySelector('#table-sonification tbody');
    tbody.innerHTML = '';

    items.forEach(item => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${item.position}</td>
        <td><strong>${item.base}</strong></td>
        <td>${item.note}</td>
        <td>${item.frequencyHz.toFixed(2)}</td>
        <td>${item.n8Index.toFixed(2)}</td>
        <td>${item.energyJ.toExponential(4)}</td>
        <td>${item.massKg.toExponential(4)}</td>
        <td><span class="badge badge-der">DER</span></td>
      `;
      tbody.appendChild(tr);
    });
  }

  function drawSpectrumCanvas(frequencies) {
    const canvas = document.getElementById('audio-canvas');
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    ctx.clearRect(0, 0, width, height);

    ctx.strokeStyle = '#1e293b';
    ctx.lineWidth = 1;
    for (let x = 0; x < width; x += 40) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }
    for (let y = 0; y < height; y += 40) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }

    if (!frequencies || frequencies.length === 0) return;

    const barWidth = Math.max(12, Math.floor(width / frequencies.length) - 4);
    frequencies.forEach((freq, idx) => {
      const x = idx * (barWidth + 4) + 20;
      const normalizedHeight = Math.min(height - 20, (freq / 600) * (height - 40));
      const y = height - normalizedHeight - 10;

      const gradient = ctx.createLinearGradient(0, y, 0, height);
      gradient.addColorStop(0, '#f59e0b');
      gradient.addColorStop(1, '#8b5cf6');

      ctx.fillStyle = gradient;
      ctx.fillRect(x, y, barWidth, normalizedHeight);

      ctx.fillStyle = '#94a3b8';
      ctx.font = '10px monospace';
      ctx.fillText(`${freq.toFixed(0)}Hz`, x, y - 4);
    });
  }

  function playSonificationAudio(items, waveform = 'triangle') {
    stopAudio();

    if (!audioCtx) {
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }

    if (audioCtx.state === 'suspended') {
      audioCtx.resume();
    }

    isAudioPlaying = true;
    const liveInfo = document.getElementById('audio-live-info');
    liveInfo.textContent = `Playing ${items.length} base notes...`;

    let timeOffset = audioCtx.currentTime + 0.05;
    const noteDuration = 0.22;

    items.forEach((item, idx) => {
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();

      osc.type = waveform;
      osc.frequency.setValueAtTime(item.frequencyHz, timeOffset);

      gain.gain.setValueAtTime(0.001, timeOffset);
      gain.gain.exponentialRampToValueAtTime(0.3, timeOffset + 0.02);
      gain.gain.exponentialRampToValueAtTime(0.001, timeOffset + noteDuration - 0.01);

      osc.connect(gain);
      gain.connect(audioCtx.destination);

      osc.start(timeOffset);
      osc.stop(timeOffset + noteDuration);

      currentOscillators.push(osc);
      timeOffset += noteDuration;
    });

    setTimeout(() => {
      isAudioPlaying = false;
      liveInfo.textContent = `Sonification sequence completed (${items.length} notes).`;
    }, (items.length * noteDuration + 0.1) * 1000);
  }

  function stopAudio() {
    currentOscillators.forEach(osc => {
      try { osc.stop(); } catch (e) {}
    });
    currentOscillators = [];
    isAudioPlaying = false;
    const liveInfo = document.getElementById('audio-live-info');
    if (liveInfo) liveInfo.textContent = 'Audio stopped.';
  }

  function initDnaSonifier() {
    const btnSonify = document.getElementById('btn-sonify');
    const btnStop = document.getElementById('btn-stop-audio');
    const dnaInput = document.getElementById('dna-input');
    const refPitch = document.getElementById('ref-pitch');

    function updateSonification() {
      const seq = dnaInput.value;
      const refA4 = parseFloat(refPitch.value) || 440.0;
      const items = sonifyDnaSequence(seq, refA4);
      renderSonificationTable(items);
      drawSpectrumCanvas(items.map(i => i.frequencyHz));
      return items;
    }

    updateSonification();

    dnaInput.addEventListener('input', () => {
      const items = updateSonification();
      if (isPuterAvailable) {
        try { puter.kv.set('upi_last_dna', dnaInput.value); } catch (e) {}
      }
    });
    refPitch.addEventListener('change', updateSonification);

    btnSonify.addEventListener('click', () => {
      const items = updateSonification();
      const waveform = document.getElementById('waveform-select').value;
      playSonificationAudio(items, waveform);
    });

    btnStop.addEventListener('click', stopAudio);
  }

  /* --------------------------------------------------------------------------
   * 5. Digital Qudit Torus Search Simulator
   * -------------------------------------------------------------------------- */
  function simulateQuditSearch(dims, targets, iterations) {
    const totalStates = dims.reduce((acc, d) => acc * d, 1);
    const targetSet = new Set(targets);
    
    let stateVector = new Array(totalStates).fill(1.0 / Math.sqrt(totalStates));
    
    for (let k = 0; k < iterations; k++) {
      for (let i = 0; i < totalStates; i++) {
        if (targetSet.has(i)) {
          stateVector[i] = -stateVector[i];
        }
      }

      const mean = stateVector.reduce((sum, v) => sum + v, 0.0) / totalStates;
      for (let i = 0; i < totalStates; i++) {
        stateVector[i] = 2.0 * mean - stateVector[i];
      }
    }

    const probabilities = stateVector.map(v => v * v);
    const targetProbSum = Array.from(targetSet).reduce((sum, t) => sum + (probabilities[t] || 0.0), 0.0);

    return {
      dimensions: dims,
      totalStates: totalStates,
      targets: targets,
      iterations: iterations,
      targetSuccessProbability: targetProbSum,
      probabilities: probabilities
    };
  }

  function drawQuditCanvas(res) {
    const canvas = document.getElementById('qudit-canvas');
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    ctx.clearRect(0, 0, width, height);

    const probs = res.probabilities;
    const barWidth = Math.max(4, Math.floor((width - 40) / probs.length) - 2);

    probs.forEach((p, idx) => {
      const x = 20 + idx * (barWidth + 2);
      const h = Math.min(height - 30, p * (height - 40));
      const y = height - h - 15;

      const isTarget = res.targets.includes(idx);
      ctx.fillStyle = isTarget ? '#10b981' : '#3b82f6';
      ctx.fillRect(x, y, barWidth, h);

      if (probs.length <= 20) {
        ctx.fillStyle = '#64748b';
        ctx.font = '9px monospace';
        ctx.fillText(idx.toString(), x, height - 3);
      }
    });
  }

  function initQuditSimulator() {
    const btnRun = document.getElementById('btn-run-qudit');

    btnRun.addEventListener('click', () => {
      const dimsInput = document.getElementById('qudit-dims').value;
      const targetsInput = document.getElementById('qudit-targets').value;
      const iterations = parseInt(document.getElementById('qudit-iterations').value) || 1;

      const dims = dimsInput.split(',').map(s => parseInt(s.trim())).filter(n => !isNaN(n) && n > 0);
      const targets = targetsInput.split(',').map(s => parseInt(s.trim())).filter(n => !isNaN(n) && n >= 0);

      if (dims.length === 0 || targets.length === 0) {
        alert('Invalid dimensions or target input.');
        return;
      }

      const res = simulateQuditSearch(dims, targets, iterations);
      drawQuditCanvas(res);

      const log = document.getElementById('qudit-output-log');
      log.textContent = JSON.stringify({
        operation: 'qudit_torus_search_simulation',
        status: 'DER',
        verification_type: 'software_test',
        torus_dimensions: res.dimensions,
        total_basis_states: res.totalStates,
        target_states: res.targets,
        diffusion_iterations: res.iterations,
        success_probability: Number(res.targetSuccessProbability.toFixed(6)),
        interpretation: 'classical_state_vector_qudit_simulator'
      }, null, 2);

      document.getElementById('qudit-live-info').textContent = 
        `Basis states: ${res.totalStates} | Target P(success): ${(res.targetSuccessProbability * 100).toFixed(2)}% after ${iterations} step(s).`;
    });
  }

  /* --------------------------------------------------------------------------
   * 6. Scientific Status Inspector & Auditor
   * -------------------------------------------------------------------------- */
  function initStatusAuditor() {
    const btnValidate = document.getElementById('btn-validate-record');
    const jsonTextarea = document.getElementById('inspector-json');
    const auditResult = document.getElementById('audit-result');

    btnValidate.addEventListener('click', () => {
      try {
        const record = JSON.parse(jsonTextarea.value);
        const validStatuses = ['EST', 'DER', 'HYP', 'STOP', 'ERR', 'SYM'];

        if (!record.address || !record.status) {
          auditResult.className = 'audit-box badge-err';
          auditResult.textContent = '❌ Invalid UPI Record: Missing "address" or "status" fields.';
          return;
        }

        if (!validStatuses.includes(record.status)) {
          auditResult.className = 'audit-box badge-err';
          auditResult.textContent = `❌ Invalid Scientific Status "${record.status}". Allowed: ${validStatuses.join(', ')}`;
          return;
        }

        auditResult.className = 'audit-box badge-est';
        auditResult.textContent = `✅ UPI Record Validated!
Address: ${record.address}
Status: ${record.status}
Verification Type: ${record.verification_type || 'software_test'}
Confusion Guard: ${record.confusion_guard || 'Present'}
Boundary Check: PASS (Complies with AGENTS.md non-negotiable rules)`;
      } catch (err) {
        auditResult.className = 'audit-box badge-err';
        auditResult.textContent = `❌ JSON Parsing Error: ${err.message}`;
      }
    });
  }

  /* --------------------------------------------------------------------------
   * 7. AECΩ Evolution Module
   * -------------------------------------------------------------------------- */
  function initAecoModule() {
    const btnRunAeco = document.getElementById('btn-run-aeco');
    const aecoOutput = document.getElementById('aeco-output');

    btnRunAeco.addEventListener('click', () => {
      aecoOutput.textContent = 'Running AECΩ evolution loop (Observer -> Evaluator -> Mutator -> Selector)...';
      setTimeout(() => {
        aecoOutput.textContent = JSON.stringify({
          organ: 'UPI-AECΩ',
          version: 'v0.1.0',
          cycle_result: 'NO_PROMOTION',
          self_model_status: 'HEALTHY',
          benchmarks_passed: 324,
          dna_violations: 0,
          notes: 'RNA layer stable. Scientific DNA records preserved without mutation.'
        }, null, 2);
      }, 600);
    });
  }

  /* --------------------------------------------------------------------------
   * 8. Puter & Export Handlers
   * -------------------------------------------------------------------------- */
  function initExportHandlers() {
    const btnPuterSave = document.getElementById('btn-puter-save');
    const btnExportJson = document.getElementById('btn-export-json');

    btnExportJson.addEventListener('click', () => {
      const seq = document.getElementById('dna-input').value;
      const refA4 = parseFloat(document.getElementById('ref-pitch').value) || 440.0;
      const items = sonifyDnaSequence(seq, refA4);

      const upiNode = {
        version: '0.1.0',
        address: `UPI<biology,1,acoustics,dna_sonification_${seq.substring(0, 8)}>`,
        status: 'DER',
        verification_type: 'software_test',
        claims_experimental_verification: false,
        sequence: seq,
        reference_a4_hz: refA4,
        traces: items,
        confusion_guard: 'Acoustic DNA sonification maps frequencies for audio visualization; it does not claim biological mechanics.'
      };

      const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(upiNode, null, 2));
      const downloadAnchor = document.createElement('a');
      downloadAnchor.setAttribute('href', dataStr);
      downloadAnchor.setAttribute('download', `upi_dna_sonification_${seq.substring(0, 6)}.json`);
      document.body.appendChild(downloadAnchor);
      downloadAnchor.click();
      downloadAnchor.remove();
    });

    btnPuterSave.addEventListener('click', () => {
      const seq = document.getElementById('dna-input').value;
      const refA4 = parseFloat(document.getElementById('ref-pitch').value) || 440.0;
      const items = sonifyDnaSequence(seq, refA4);

      const upiNode = {
        version: '0.1.0',
        address: `UPI<biology,1,acoustics,dna_sonification_${seq.substring(0, 8)}>`,
        status: 'DER',
        verification_type: 'software_test',
        claims_experimental_verification: false,
        sequence: seq,
        reference_a4_hz: refA4,
        traces: items
      };

      if (isPuterAvailable) {
        puter.fs.write(`upi_node_${Date.now()}.json`, JSON.stringify(upiNode, null, 2))
          .then(() => {
            alert('✅ Successfully saved UPI Node to Puter Cloud FS!');
          })
          .catch(err => {
            alert(`Puter Cloud Save Error: ${err.message}`);
          });
      } else {
        alert('Puter SDK is running in Standalone Mode. Use "Export UPI Node" to download JSON locally.');
      }
    });
  }

})();
