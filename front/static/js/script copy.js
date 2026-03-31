let currentTaskId = null;
let pollInterval = null;
let startTime = null;

async function initiateScrape() {
    const tourIdInput = document.getElementById('tourId');
    const tourId = tourIdInput.value.trim();
    if (!tourId) return;

    document.getElementById('startBtn').disabled = true;
    document.getElementById('statusBox').style.display = 'flex';
    document.getElementById('loadingElement').style.display = 'flex';
    document.getElementById('loadingElement').style.flexDirection = 'column';
    document.getElementById('loadingElement').style.alignItems = 'center';
    document.getElementById('resultContainer').style.display = 'none';
    document.getElementById('statusText').innerText = `Analizuję Tour: ${tourId}`;
    
    startTime = Date.now();

    try {
        const response = await fetch('/start_scrape', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tour_id: tourId })
        });
        const data = await response.json();
        currentTaskId = data.task_id;
        pollInterval = setInterval(checkStatus, 1000);
    } catch (error) {
        showError("Błąd inicjalizacji.");
    }
}

async function checkStatus() {
    const response = await fetch(`/check_status/${currentTaskId}`);
    const data = await response.json();

    if (data.status === 'completed') {
        stopPolling();
        const sec = ((Date.now() - startTime) / 1000).toFixed(1);
        showResult(`QL TOTAL (${sec}s)`, data.result);
    } else if (data.status === 'error') {
        stopPolling();
        showError(data.result);
    }
}

function stopPolling() {
    clearInterval(pollInterval);
    document.getElementById('startBtn').disabled = false;
    document.getElementById('loadingElement').style.display = 'none';
}

function showResult(label, value) {
    document.getElementById('resultContainer').style.display = 'block';
    document.getElementById('resultLabel').innerText = label;
    document.getElementById('resultValue').className = 'result-value';
    document.getElementById('resultValue').innerText = value;
}

function showError(msg) {
    document.getElementById('resultContainer').style.display = 'block';
    document.getElementById('resultLabel').innerText = "Błąd:";
    document.getElementById('resultValue').className = 'error-value';
    document.getElementById('resultValue').innerText = msg;
}

// Obsługa Entera
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('tourId').addEventListener('keypress', e => { 
        if (e.key === 'Enter') initiateScrape(); 
    });
});