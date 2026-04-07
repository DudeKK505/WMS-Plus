// ... Twoje zmienne na początku bez zmian ...

function showTab(tabId) {
    document.getElementById('tourTab').style.display = tabId === 'tourTab' ? 'block' : 'none';
    document.getElementById('cptTab').style.display = tabId === 'cptTab' ? 'block' : 'none';
    document.getElementById('btnTour').style.backgroundColor = tabId === 'tourTab' ? '#2d3748' : '#718096';
    document.getElementById('btnCpt').style.backgroundColor = tabId === 'cptTab' ? '#2d3748' : '#718096';
}

function addRow() {
    const container = document.getElementById('cptRows');
    const lastDate = document.querySelector('.cpt-date:last-of-type')?.value || "";
    const div = document.createElement('div');
    div.className = 'cpt-row';
    div.style = "display: flex; gap: 4px; margin-bottom: 5px;";
    div.innerHTML = `<input type="date" class="cpt-date" value="${lastDate}" style="flex: 2; font-size: 0.8rem; padding: 5px;">
                     <input type="time" class="cpt-time" style="flex: 1.5; font-size: 0.8rem; padding: 5px;">
                     <button onclick="removeRow(this)" style="background: #e53e3e; padding: 5px 10px;">X</button>`;
    container.appendChild(div);
}

function removeRow(btn) { btn.parentElement.remove(); }

async function initiateCptScrape() {
    const schedule = Array.from(document.querySelectorAll('.cpt-row')).map(row => ({
        date: row.querySelector('.cpt-date').value,
        time: row.querySelector('.cpt-time').value
    })).filter(r => r.date && r.time);

    if (schedule.length === 0) return;
    prepareUI("Zliczam CPT...");

    const response = await fetch('/start_cpt_scrape', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ schedule: schedule })
    });
    const data = await response.json();
    currentTaskId = data.task_id;
    pollInterval = setInterval(checkStatus, 1000);
}

function prepareUI(text) {
    document.getElementById('statusBox').style.display = 'flex';
    document.getElementById('loadingElement').style.display = 'flex';
    document.getElementById('resultContainer').style.display = 'none';
    document.getElementById('statusText').innerText = text;
    startTime = Date.now();
}

async function checkStatus() {
    const response = await fetch(`/check_status/${currentTaskId}`);
    const data = await response.json();

    if (data.status === 'completed') {
        clearInterval(pollInterval);
        document.getElementById('loadingElement').style.display = 'none';
        if (data.result.type === 'cpt') {
            showCptResult(data.result);
        } else {
            showResult("QL TOTAL", data.result);
        }
    } else if (data.status === 'error') {
        clearInterval(pollInterval);
        showError(data.result);
    }
}

function showCptResult(res) {
    document.getElementById('resultContainer').style.display = 'block';
    document.getElementById('resultLabel').innerText = "WYNIKI ZAMÓWIEŃ";
    let html = res.details.map(d => `<div style="display:flex; justify-content:space-between; font-size:0.8rem; border-bottom:1px solid #eee;"><span>Tura ${d.time}:</span><b>${d.count}</b></div>`).join('');
    html += `<div style="margin-top:10px; font-size:0.7rem; color:#777;">SUMA:</div><div style="font-size:2rem; color:#27ae60; font-weight:800;">${res.total}</div>`;
    document.getElementById('resultValue').innerHTML = html;
}
// ... Reszta Twoich funkcji (showResult, showError) bez zmian ...
