// 未來若由 Java 提供網頁並直連 Python API，只需修改此處網址
const API_URL = '/api/stt/transcribe';

let mediaRecorder;
let audioChunks = [];
let audioCtx, analyser, animationId;

// 綁定 DOM 事件
document.addEventListener('DOMContentLoaded', () => {
    const minSilenceInput = document.getElementById('minSilence');
    const thresholdInput = document.getElementById('threshold');
    const recordBtn = document.getElementById('recordBtn');
    const stopBtn = document.getElementById('stopBtn');

    minSilenceInput.addEventListener('input', (e) => {
        document.getElementById('silenceVal').innerText = e.target.value;
    });

    thresholdInput.addEventListener('input', (e) => {
        const val = e.target.value;
        document.getElementById('threshVal').innerText = val;
        document.getElementById('thresholdLine').style.left = (val * 100) + '%';
    });

    recordBtn.addEventListener('click', startRecording);
    stopBtn.addEventListener('click', stopRecording);
});

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        
        // Web Audio API 即時計算麥克風能量
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const source = audioCtx.createMediaStreamSource(stream);
        analyser = audioCtx.createAnalyser();
        analyser.fftSize = 512;
        source.connect(analyser);
        monitorEnergy();

        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) audioChunks.push(event.data);
        };

        mediaRecorder.onstop = async () => {
            cancelAnimationFrame(animationId);
            if (audioCtx) audioCtx.close();
            document.getElementById('meterBar').style.width = '0%';
            document.getElementById('energyText').innerText = '即時能量：0.00';

            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            const playback = document.getElementById('audioPlayback');
            playback.src = URL.createObjectURL(audioBlob);
            playback.style.display = 'block';

            await sendAudioToApi(audioBlob);
            stream.getTracks().forEach(track => track.stop());
        };

        mediaRecorder.start();
        document.getElementById('recordBtn').classList.add('recording');
        document.getElementById('recordBtn').disabled = true;
        document.getElementById('stopBtn').disabled = false;
        document.getElementById('status').innerText = "狀態：🔴 錄音中... 請說話";
    } catch (err) {
        alert("無法存取麥克風：" + err);
    }
}

function monitorEnergy() {
    const dataArray = new Uint8Array(analyser.fftSize);
    analyser.getByteTimeDomainData(dataArray);
    
    let sumSquares = 0;
    for (let i = 0; i < dataArray.length; i++) {
        const normalized = (dataArray[i] - 128) / 128;
        sumSquares += normalized * normalized;
    }
    const rms = Math.sqrt(sumSquares / dataArray.length);
    const displayEnergy = Math.min(1.0, rms * 4); 
    const threshold = parseFloat(document.getElementById('threshold').value);

    const meterBar = document.getElementById('meterBar');
    meterBar.style.width = (displayEnergy * 100) + '%';
    meterBar.style.backgroundColor = displayEnergy >= threshold ? '#28a745' : '#6c757d';
    document.getElementById('energyText').innerText = `即時能量：${displayEnergy.toFixed(2)} (門檻: ${threshold})`;

    animationId = requestAnimationFrame(monitorEnergy);
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
        document.getElementById('recordBtn').classList.remove('recording');
        document.getElementById('recordBtn').disabled = false;
        document.getElementById('stopBtn').disabled = true;
        document.getElementById('status').innerText = "狀態：⏳ 計算 VAD 能量與辨識中...";
    }
}

async function sendAudioToApi(audioBlob) {
    const formData = new FormData();
    formData.append("file", audioBlob, "recording.webm");
    formData.append("vad_filter", document.getElementById('vadFilter').checked);
    formData.append("min_silence_duration_ms", document.getElementById('minSilence').value);
    formData.append("threshold", document.getElementById('threshold').value);

    try {
        const response = await fetch(API_URL, { method: 'POST', body: formData });
        const data = await response.json();
        
        document.getElementById('status').innerText = "狀態：✅ 辨識完成！";
        document.getElementById('fullText').innerText = data.full_text || "(未偵測到語音)";
        
        const m = data.vad_metrics;
        document.getElementById('vadStats').innerHTML = 
            `設定 Threshold：<strong>${m.threshold}</strong> ｜ ` +
            `最高語音機率：<strong>${m.max_speech_prob}</strong> ｜ ` +
            `平均語音機率：<strong>${m.avg_speech_prob}</strong>`;

        drawVadChart(m.timeline, m.threshold);
        
        const displayData = { 
            ...data, 
            vad_metrics: { ...m, timeline: `[共 ${m.timeline.length} 筆時間點數據]` } 
        };
        document.getElementById('jsonResult').innerText = JSON.stringify(displayData, null, 2);
    } catch (err) {
        document.getElementById('status').innerText = "狀態：❌ 發生錯誤：" + err;
    }
}

function drawVadChart(timeline, threshold) {
    const canvas = document.getElementById('vadChart');
    const ctx = canvas.getContext('2d');
    const w = canvas.width;
    const h = canvas.height;
    ctx.clearRect(0, 0, w, h);

    if (!timeline || timeline.length === 0) return;

    // 1. 繪製 VAD 語音機率曲線 (綠色)
    ctx.beginPath();
    ctx.strokeStyle = '#00ff88';
    ctx.lineWidth = 2;
    timeline.forEach((pt, idx) => {
        const x = (idx / Math.max(1, timeline.length - 1)) * w;
        const y = h - (pt.speech_prob * h);
        if (idx === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    });
    ctx.stroke();

    // 2. 繪製 Threshold 門檻線 (紅色虛線)
    const threshY = h - (threshold * h);
    ctx.beginPath();
    ctx.setLineDash();
    ctx.strokeStyle = '#ff4444';
    ctx.lineWidth = 2;
    ctx.moveTo(0, threshY);
    ctx.lineTo(w, threshY);
    ctx.stroke();
    ctx.setLineDash([]);

    // 標示文字
    ctx.fillStyle = '#ff6666';
    ctx.font = '12px sans-serif';
    ctx.fillText(`Threshold: ${threshold}`, 10, Math.max(14, threshY - 5));
}
