"""
simulator_service/main.py
Bộ giả lập tín hiệu Camera AI toàn diện cho Honda Hà Nam.
- Quản lý và cho phép bật/tắt HÀNG hoặc TRỐNG cho TẤT CẢ 205 vị trí (110 ô nguồn + 95 ô đích).
- Vòng lặp ngầm: Phát dữ liệu toàn bộ 205 ô sang POST http://127.0.0.1:8000/ai-data mỗi 1.0 giây.
- Bảng nhật ký Real-time: Hiển thị tín hiệu gửi đi và phản hồi nhận về từ logic_service.
"""

import os
import json
import time
import asyncio
from typing import Dict, Any, List
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import uvicorn

CONFIG_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "logic_service", "config", "map_config", "HaNam_config.json")
)
LOGIC_SERVICE_URL = "http://127.0.0.1:8000"

# Bộ nhớ 205 vị trí trong RAM
# pos_id: {"pos_id": ..., "label": "trong", "type": "source" / "dest", "details": ...}
simulated_positions: Dict[str, Dict[str, Any]] = {}
signal_logs: List[Dict[str, Any]] = []

def load_all_hanam_points():
    global simulated_positions
    if not os.path.exists(CONFIG_PATH):
        print(f"[ERROR] Không tìm thấy file: {CONFIG_PATH}")
        return

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    # 1. Nạp tất cả 110 ô nguồn
    for pos_id, info in cfg.items():
        simulated_positions[pos_id] = {
            "pos_id": pos_id,
            "label": "trong",  # Mặc định TRỐNG
            "is_source": True,
            "group_id": info.get("group_id", 1),
            "logic_path": info.get("logic_path", "auto"),
            "matching": info.get("matching", []),
            "process_code": info.get("process_code", "")
        }

    # 2. Quét mảng matching để gom tiếp toàn bộ 95 ô đích
    dest_count = 0
    for pos_id, info in cfg.items():
        matching = info.get("matching", [])
        # Từ phần tử thứ 1 trở đi là ô đích (hoặc phần tử duy nhất trong empty_one_place cũ)
        dest_candidates = matching[1:] if len(matching) > 1 else matching
        for dest in dest_candidates:
            if dest not in simulated_positions:
                simulated_positions[dest] = {
                    "pos_id": dest,
                    "label": "trong",  # Mặc định TRỐNG
                    "is_source": False,
                    "group_id": 1,
                    "logic_path": "DESTINATION",
                    "matching": [],
                    "process_code": "Ô Đích / Bãi đệm"
                }
                dest_count += 1

    print(f"✅ Đã nạp đầy đủ: {len(simulated_positions)} vị trí ({len(cfg)} ô nguồn + {dest_count} ô đích)")

app = FastAPI(title="Honda Ha Nam - Comprehensive Mock AI Service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    html_content = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Honda Hà Nam - Bảng Giả Lập Tín Hiệu Camera AI (205 Vị Trí)</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #0f172a; --card: #1e293b; --border: #334155;
            --text: #f8fafc; --text-dim: #94a3b8;
            --green: #22c55e; --red: #ef4444; --accent: #38bdf8; --purple: #c084fc;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }
        body { background: var(--bg); color: var(--text); padding: 20px; }
        
        header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding-bottom: 16px; border-bottom: 1px solid var(--border); }
        h1 { font-size: 20px; font-weight: 700; color: #fff; }
        p.sub { font-size: 13px; color: var(--text-dim); margin-top: 4px; }

        .header-badges { display: flex; gap: 12px; align-items: center; }
        .badge-live { display: flex; align-items: center; gap: 8px; background: rgba(34, 197, 94, 0.15); border: 1px solid var(--green); padding: 6px 14px; border-radius: 999px; font-size: 13px; font-weight: 600; color: #4ade80; }
        .dot { width: 8px; height: 8px; border-radius: 50%; background: var(--green); animation: pulse 1.5s infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }

        .layout-grid { display: grid; grid-template-columns: 1fr 360px; gap: 20px; }

        .controls { display: flex; gap: 10px; margin-bottom: 16px; align-items: center; flex-wrap: wrap; }
        .search-box { flex: 1; max-width: 300px; }
        .search-box input { width: 100%; background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 9px 14px; color: #fff; font-size: 14px; outline: none; }
        .search-box input:focus { border-color: var(--accent); }

        .btn { background: var(--card); border: 1px solid var(--border); color: #fff; padding: 8px 14px; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer; transition: 0.2s; }
        .btn:hover { background: #334155; }
        .btn.active { background: #334155; border-color: var(--accent); color: var(--accent); }

        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 12px; max-height: calc(100vh - 160px); overflow-y: auto; padding-right: 6px; }
        .card { background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 14px; transition: 0.2s; }
        .card.is-hang { border-color: var(--red); background: rgba(239, 68, 68, 0.1); }
        .card.is-trong { border-color: rgba(34, 197, 94, 0.3); }

        .card-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
        .pos-id { font-family: 'JetBrains Mono', monospace; font-size: 16px; font-weight: 700; color: #fff; }
        .tag-source { font-size: 10px; font-weight: 700; padding: 2px 8px; border-radius: 4px; text-transform: uppercase; background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); }
        .tag-dest { font-size: 10px; font-weight: 700; padding: 2px 8px; border-radius: 4px; text-transform: uppercase; background: rgba(168, 85, 247, 0.15); color: var(--purple); border: 1px solid rgba(168, 85, 247, 0.3); }

        .info { font-size: 12px; color: var(--text-dim); margin-bottom: 12px; min-height: 36px; }
        .info span { font-family: 'JetBrains Mono', monospace; color: #cbd5e1; }

        .btn-toggle { width: 100%; padding: 9px; border-radius: 8px; font-size: 12px; font-weight: 700; cursor: pointer; border: none; transition: 0.2s; }
        .btn-hang { background: var(--red); color: #fff; }
        .btn-hang:hover { background: #dc2626; }
        .btn-trong { background: #14532d; color: #4ade80; border: 1px solid var(--green); }
        .btn-trong:hover { background: #166534; }

        /* Log Panel */
        .log-panel { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 16px; display: flex; flex-direction: column; height: calc(100vh - 120px); }
        .log-panel h3 { font-size: 15px; font-weight: 700; color: #fff; margin-bottom: 6px; }
        .log-sub { font-size: 12px; color: var(--text-dim); margin-bottom: 12px; border-bottom: 1px solid var(--border); padding-bottom: 8px; }
        .log-box { flex: 1; overflow-y: auto; background: #0a0f1d; border-radius: 8px; padding: 10px; font-family: 'JetBrains Mono', monospace; font-size: 11px; line-height: 1.6; }
        .log-item { margin-bottom: 8px; padding-bottom: 6px; border-bottom: 1px solid #1e293b; }
        .log-time { color: var(--accent); }
        .log-hang { color: var(--red); font-weight: 700; }
        .log-ok { color: var(--green); }
        .log-err { color: #f87171; }
    </style>
</head>
<body>

<header>
    <div>
        <h1>📡 Giả Lập Tín Hiệu Camera AI — Quản Lý Toàn Bộ 205 Vị Trí (Hà Nam)</h1>
        <p class="sub">110 Ô Nguồn Cấp + 95 Ô Đích Đệm | Cho phép Bật/Tắt HÀNG hoặc TRỐNG cho từng vị trí</p>
    </div>
    <div class="header-badges">
        <div class="badge-live">
            <span class="dot"></span>
            <span>Phát 205 ô sang Logic Service (Cổng 8000) mỗi 1s</span>
        </div>
    </div>
</header>

<div class="layout-grid">
    <!-- CỘT TRÁI: 205 VỊ TRÍ -->
    <div>
        <div class="controls">
            <div class="search-box">
                <input type="text" id="searchInput" placeholder="🔍 Tìm mã ô (VD: 10001762, 10001546)..." onkeyup="renderPoints()">
            </div>
            <button class="btn active" onclick="setFilter('all', this)">Tất Cả (<span id="count-all">0</span>)</button>
            <button class="btn" onclick="setFilter('source', this)">Ô Nguồn (110)</button>
            <button class="btn" onclick="setFilter('dest', this)">Ô Đích (95)</button>
            <button class="btn" onclick="setFilter('hang', this)">🔴 Đang Có Hàng (<span id="count-hang">0</span>)</button>
            <button class="btn" style="margin-left: auto;" onclick="resetAll()">🔄 Đặt Tất Cả Về TRỐNG</button>
        </div>

        <div class="grid" id="gridContainer"></div>
    </div>

    <!-- CỘT PHẢI: NHẬT KÝ PHÁT TÍN HIỆU & PHẢN HỒI -->
    <div class="log-panel">
        <h3>📋 Nhật Ký Gửi Tín Hiệu & Phản Hồi</h3>
        <p class="log-sub">Xem tín hiệu phát đi và giá trị logic_service phản hồi về theo thời gian thực:</p>
        <div class="log-box" id="logContainer">
            <div style="color: var(--text-dim);">Đang chờ phát tín hiệu...</div>
        </div>
    </div>
</div>

<script>
    let points = [];
    let currentFilter = 'all';

    async function loadPoints() {
        const res = await fetch('/api/points');
        points = await res.json();
        updateCounts();
        renderPoints();
    }

    async function fetchLogs() {
        const res = await fetch('/api/signal-logs');
        const logs = await res.json();
        renderLogs(logs);
    }

    function updateCounts() {
        document.getElementById('count-all').innerText = points.length;
        const hangCount = points.filter(p => p.label === 'hang').length;
        document.getElementById('count-hang').innerText = hangCount;
    }

    function renderPoints() {
        const container = document.getElementById('gridContainer');
        const search = document.getElementById('searchInput').value.trim().toLowerCase();

        const filtered = points.filter(p => {
            const matchSearch = p.pos_id.toLowerCase().includes(search) || (p.matching && p.matching.join(',').includes(search));
            let matchType = true;
            if (currentFilter === 'source') matchType = p.is_source === true;
            if (currentFilter === 'dest') matchType = p.is_source === false;
            if (currentFilter === 'hang') matchType = p.label === 'hang';
            return matchSearch && matchType;
        });

        container.innerHTML = filtered.map(p => {
            const isHang = p.label === 'hang';
            const targets = (p.matching && p.matching.length > 1) ? p.matching.slice(1).join(', ') : (p.matching ? p.matching[0] : '-');

            return `
                <div class="card ${isHang ? 'is-hang' : 'is-trong'}">
                    <div class="card-top">
                        <span class="pos-id">📍 ${p.pos_id}</span>
                        ${p.is_source ? `
                            <span class="tag-source">NGUỒN (${p.logic_path})</span>
                        ` : `
                            <span class="tag-dest">Ô ĐÍCH / BÃI</span>
                        `}
                    </div>
                    <div class="info">
                        ${p.is_source ? `
                            Mã: <span>${p.process_code || '-'}</span> | Đích: <span>${targets}</span>
                        ` : `
                            <span>Bãi trả hàng / Ô đệm</span>
                        `}
                    </div>
                    ${isHang ? `
                        <button class="btn-toggle btn-hang" onclick="toggle('${p.pos_id}', 'trong')">
                            🔴 ĐANG CÓ HÀNG (Bấm để TRỐNG)
                        </button>
                    ` : `
                        <button class="btn-toggle btn-trong" onclick="toggle('${p.pos_id}', 'hang')">
                            🟢 ĐANG TRỐNG (Bấm để CÓ HÀNG)
                        </button>
                    `}
                </div>
            `;
        }).join('');
    }

    function renderLogs(logs) {
        const container = document.getElementById('logContainer');
        if (!logs || logs.length === 0) return;

        container.innerHTML = logs.map(l => {
            const isOk = l.status_code === 200;
            return `
                <div class="log-item">
                    <span class="log-time">[${l.time}]</span> 
                    Gửi 205 ô: <span class="${l.hang_count > 0 ? 'log-hang' : ''}">[${l.hang_count} ô HÀNG: ${l.hang_list.join(', ') || 'Không có'}]</span><br>
                    ➔ Phản hồi Logic Service: <span class="${isOk ? 'log-ok' : 'log-err'}">${l.status_code} (${l.response_text})</span>
                </div>
            `;
        }).join('');
    }

    async function toggle(posId, newLabel) {
        await fetch('/api/set-state', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({pos_id: posId, label: newLabel})
        });
        loadPoints();
    }

    async function resetAll() {
        if (!confirm('Đặt tất cả 205 ô về trạng thái TRỐNG?')) return;
        await fetch('/api/set-all', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({label: 'trong'})
        });
        loadPoints();
    }

    function setFilter(type, btn) {
        currentFilter = type;
        document.querySelectorAll('.controls .btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        renderPoints();
    }

    loadPoints();
    fetchLogs();
    setInterval(fetchLogs, 1500);
</script>

</body>
</html>
    """
    return HTMLResponse(content=html_content)

@app.get("/api/points")
async def get_points():
    return list(simulated_positions.values())

@app.post("/api/set-state")
async def set_point_state(req: Request):
    body = await req.json()
    pos_id = str(body.get("pos_id"))
    new_label = body.get("label", "trong")

    if pos_id in simulated_positions:
        simulated_positions[pos_id]["label"] = new_label
        return {"status": "success", "pos_id": pos_id, "new_label": new_label}
    return JSONResponse(status_code=404, content={"status": "not_found"})

@app.post("/api/set-all")
async def set_all_states(req: Request):
    body = await req.json()
    label = body.get("label", "trong")
    for pos_id in simulated_positions:
        simulated_positions[pos_id]["label"] = label
    return {"status": "success", "count": len(simulated_positions), "label": label}

@app.get("/api/signal-logs")
async def get_signal_logs():
    return list(reversed(signal_logs[-25:]))

async def background_ai_broadcaster():
    """
    Vòng lặp phát tín hiệu ngầm mỗi 1.0 giây sang logic_service (POST /ai-data)
    và lưu lại log phản hồi trả về
    """
    await asyncio.sleep(1)
    print(f"🚀 Bắt đầu phát tín hiệu 205 ô sang {LOGIC_SERVICE_URL}/ai-data mỗi 1s...")

    async with httpx.AsyncClient(timeout=3) as client:
        while True:
            try:
                payload = {}
                hang_list = []
                for pos_id, info in simulated_positions.items():
                    lbl = info["label"]
                    payload[pos_id] = {
                        "label": lbl,
                        "group_id": info.get("group_id", 1)
                    }
                    if lbl == "hang":
                        hang_list.append(pos_id)

                # Gửi sang POST /ai-data
                res = await client.post(f"{LOGIC_SERVICE_URL}/ai-data", json=payload)
                
                # Ghi nhận log phản hồi trả về
                cur_time = time.strftime("%H:%M:%S")
                signal_logs.append({
                    "time": cur_time,
                    "hang_count": len(hang_list),
                    "hang_list": hang_list,
                    "status_code": res.status_code,
                    "response_text": res.text
                })
                # Giữ tối đa 50 log gần nhất
                if len(signal_logs) > 50:
                    signal_logs.pop(0)

            except Exception as e:
                cur_time = time.strftime("%H:%M:%S")
                signal_logs.append({
                    "time": cur_time,
                    "hang_count": len(hang_list),
                    "hang_list": hang_list,
                    "status_code": 0,
                    "response_text": f"Lỗi kết nối logic_service: {e}"
                })
                if len(signal_logs) > 50:
                    signal_logs.pop(0)

            await asyncio.sleep(1.0)

async def main():
    load_all_hanam_points()

    config = uvicorn.Config(app, host="0.0.0.0", port=8080, log_level="warning")
    server = uvicorn.Server(config)

    print("\n" + "="*75)
    print("🎉 BỘ GIẢ LẬP TÍN HIỆU CAMERA AI (205 VỊ TRÍ) ĐÃ SẴN SÀNG!")
    print("👉 Mở trình duyệt để bật/tắt HÀNG hoặc TRỐNG: http://localhost:8080")
    print("👉 Dữ liệu tự động phát sang logic_service (Cổng 8000)")
    print("="*75 + "\n")

    await asyncio.gather(
        server.serve(),
        background_ai_broadcaster()
    )

if __name__ == "__main__":
    asyncio.run(main())
