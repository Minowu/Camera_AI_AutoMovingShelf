from typing import Dict, Any, List, Optional
import os
import json
import time
from shared.logger import get_logger
from fastapi import APIRouter, Request, Body, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from services.POS_manager import pos_manager
from services.Task_manager import task_service

logger = get_logger("logic_service")
router = APIRouter()


def extract_points(payload: Any) -> List[str]:
    """Trích xuất mảng pos_id từ nhiều định dạng payload khác nhau."""
    if isinstance(payload, list):
        return [str(p).strip() for p in payload if p is not None and str(p).strip()]
    elif isinstance(payload, dict):
        if "points" in payload:
            pts = payload["points"]
            if isinstance(pts, list):
                return [str(p).strip() for p in pts if p is not None and str(p).strip()]
            return [str(pts).strip()] if str(pts).strip() else []
        elif "point" in payload:
            pts = payload["point"]
            if isinstance(pts, list):
                return [str(p).strip() for p in pts if p is not None and str(p).strip()]
            return [str(pts).strip()] if str(pts).strip() else []
        elif "position" in payload:
            pts = payload["position"]
            if isinstance(pts, list):
                return [str(p).strip() for p in pts if p is not None and str(p).strip()]
            return [str(pts).strip()] if str(pts).strip() else []
        # Trường hợp dict là dạng {pos_id: ...} (bỏ qua các key cờ điều khiển như clear_task)
        return [str(k).strip() for k in payload.keys() if k not in ("clear_task",) and str(k).strip()]
    elif isinstance(payload, (str, int)):
        val = str(payload).strip()
        return [val] if val else []
    return []


@router.post("/block_point")
async def block_point(payload: Any = Body(...)):
    """Khóa một hoặc nhiều điểm thủ công."""
    try:
        pts = extract_points(payload)
        if not pts:
            raise HTTPException(status_code=400, detail="Không tìm thấy danh sách điểm cần block")
        await pos_manager.block_point(pts)
        return {
            "status": "success",
            "message": f"Đã khóa thành công {len(pts)} điểm",
            "points": pts
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error blocking points: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/unblock_point")
async def unblock_point(payload: Any = Body(...)):
    """Mở khóa một hoặc nhiều điểm thủ công, tùy chọn gỡ đơn kẹt trong tracking_task."""
    try:
        pts = extract_points(payload)
        if not pts:
            raise HTTPException(status_code=400, detail="Không tìm thấy danh sách điểm cần mở khóa")
        await pos_manager.un_block_point(pts)

        # Mặc định gỡ đơn kẹt trong tracking_task nếu có chứa ô được mở khóa thủ công
        clear_task = True
        if isinstance(payload, dict) and "clear_task" in payload:
            clear_task = bool(payload["clear_task"])

        cleared_orders = []
        if clear_task:
            for oid, tdata in list(task_service.tracking_task.items()):
                pos = tdata.get("position")
                t_positions = pos if isinstance(pos, list) else [pos]
                t_positions_str = [str(p).strip() for p in t_positions if p is not None]
                if any(p in t_positions_str for p in pts):
                    task_service.tracking_task.pop(oid, None)
                    cleared_orders.append(oid)
                    logger.info(f"🧹 [MANUAL UNBLOCK] Gỡ đơn kẹt {oid} khỏi tracking_task do mở khóa ô {pts}")

        return {
            "status": "success",
            "message": f"Đã mở khóa thành công {len(pts)} điểm",
            "points": pts,
            "cleared_orders": cleared_orders
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unblocking points: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def load_ui_zones() -> Dict[str, Any]:
    """Đọc cấu hình phân chia khu vực hiển thị từ file ui_zones.json."""
    candidates = [
        os.path.join(os.path.dirname(__file__), "..", "config", "ui_zones.json"),
        os.path.join("config", "ui_zones.json"),
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading ui_zones.json: {e}")
    return {}


@router.get("/api/ui-zones")
async def get_ui_zones():
    """API trả về danh sách các khu vực giao diện định nghĩa trong ui_zones.json."""
    return load_ui_zones()


def get_hanam_positions_catalog() -> Dict[str, Dict[str, Any]]:
    """Đọc cấu hình Hà Nam và tổng hợp đầy đủ 205 ô (110 nguồn + 95 đích)."""
    cfg = pos_manager.data_configs.get("HaNam_config.json")
    if not cfg:
        candidates = [
            os.path.join(os.path.dirname(__file__), "..", "config", "map_config", "HaNam_config.json"),
            os.path.join("config", "map_config", "HaNam_config.json"),
        ]
        for p in candidates:
            if os.path.exists(p):
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        cfg = json.load(f)
                        pos_manager.data_configs["HaNam_config.json"] = cfg
                        break
                except Exception as e:
                    logger.error(f"Error loading HaNam_config.json: {e}")
    if not cfg:
        cfg = {}

    catalog = {}
    # 1. 110 ô nguồn
    for pos_id, info in cfg.items():
        pos_id_str = str(pos_id).strip()
        catalog[pos_id_str] = {
            "pos_id": pos_id_str,
            "is_source": True,
            "group_id": info.get("group_id", 1),
            "logic_path": info.get("logic_path", "auto"),
            "matching": [str(x).strip() for x in info.get("matching", [])],
            "process_code": info.get("process_code", "")
        }

    # 2. 95 ô đích
    for pos_id, info in cfg.items():
        matching = info.get("matching", [])
        dest_candidates = matching[1:] if len(matching) > 1 else matching
        for dest in dest_candidates:
            dest_str = str(dest).strip()
            if dest_str not in catalog:
                catalog[dest_str] = {
                    "pos_id": dest_str,
                    "is_source": False,
                    "group_id": 1,
                    "logic_path": "DESTINATION",
                    "matching": [],
                    "process_code": "Ô Đích / Bãi đệm"
                }

    return catalog


@router.get("/api/positions")
async def get_positions():
    """API trả về trạng thái thời gian thực của toàn bộ 205 ô Hà Nam kèm phân khu UI."""
    catalog = get_hanam_positions_catalog()
    ui_zones = load_ui_zones()
    now = time.time()

    # Xây dựng bảng tra cứu pos_id -> zone
    point_to_zone = {}
    zone_stats = {}
    for zkey, zdata in ui_zones.items():
        zname = zdata.get("name", zkey)
        zdesc = zdata.get("description", "")
        pts = [str(x).strip() for x in zdata.get("points", [])]
        zone_stats[zkey] = {
            "key": zkey,
            "name": zname,
            "description": zdesc,
            "total": len(pts),
            "hang": 0,
            "trong": 0,
            "block": 0,
            "failed": 0,
            "points": pts
        }
        for pid in pts:
            point_to_zone[pid] = zkey

    positions_list = []
    hang_count = 0
    trong_count = 0
    block_count = 0
    failed_count = 0

    # Lập bản đồ pos_id -> active order_id trong tracking_task
    pos_to_order = {}
    for oid, tdata in task_service.tracking_task.items():
        pos = tdata.get("position")
        t_positions = pos if isinstance(pos, list) else [pos]
        for p in t_positions:
            if p is not None:
                pos_to_order[str(p).strip()] = oid

    for pos_id_str, item in catalog.items():
        confirmed_info = pos_manager._position_state.get(pos_id_str, {})
        confirmed_label = confirmed_info.get("label", "chua_xac_nhan")
        is_blocked = (confirmed_label == "block")
        is_failed = (pos_id_str in pos_manager._failed_points)
        is_dispatching = (pos_id_str in pos_manager._dispatching)

        if confirmed_label == "hang":
            hang_count += 1
        elif confirmed_label == "trong":
            trong_count += 1
        if is_blocked:
            block_count += 1
        if is_failed:
            failed_count += 1

        pending_info = pos_manager._pending_state.get(pos_id_str)
        pending_label = pending_info.get("label") if pending_info else None
        pending_elapsed = round(now - pending_info.get("start_ts", now), 1) if pending_info else 0

        active_order_id = pos_to_order.get(pos_id_str)

        zkey = point_to_zone.get(pos_id_str, "OTHER")
        zname = zone_stats[zkey]["name"] if zkey in zone_stats else "Chưa phân khu"

        # Cộng dồn thống kê cho từng khu
        if zkey in zone_stats:
            if confirmed_label == "hang":
                zone_stats[zkey]["hang"] += 1
            elif confirmed_label == "trong":
                zone_stats[zkey]["trong"] += 1
            if is_blocked:
                zone_stats[zkey]["block"] += 1
            if is_failed:
                zone_stats[zkey]["failed"] += 1

        positions_list.append({
            "pos_id": pos_id_str,
            "zone": zkey,
            "zone_name": zname,
            "is_source": item["is_source"],
            "logic_path": item["logic_path"],
            "matching": item["matching"],
            "process_code": item["process_code"],
            "confirmed_label": confirmed_label,
            "is_blocked": is_blocked,
            "is_failed": is_failed,
            "is_dispatching": is_dispatching,
            "pending_label": pending_label,
            "pending_elapsed": pending_elapsed,
            "active_order_id": active_order_id
        })

    # Sắp xếp danh sách: Ô nguồn trước, rồi theo mã ô
    positions_list.sort(key=lambda x: (0 if x["is_source"] else 1, x["pos_id"]))

    return {
        "summary": {
            "total": len(positions_list),
            "hang": hang_count,
            "trong": trong_count,
            "block": block_count,
            "failed": failed_count,
            "active_tasks": len(task_service.tracking_task)
        },
        "zones": zone_stats,
        "positions": positions_list
    }


@router.get("/ui", response_class=HTMLResponse)
async def serve_control_ui():
    """Giao diện điều khiển Block/Unblock siêu tối giản, mật độ cao (Ultra-compact)."""
    html_content = """<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Quản Lý Block/Unblock - Hà Nam</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@600;700&display=swap" rel="stylesheet">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #0b1120;
      color: #f1f5f9;
      padding: 4px 8px;
      font-size: 12px;
    }
    
    /* Top Bar cực gọn */
    .topbar {
      display: flex;
      align-items: center;
      gap: 8px;
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 6px;
      padding: 4px 8px;
      margin-bottom: 6px;
      flex-wrap: wrap;
      position: sticky;
      top: 0;
      z-index: 50;
      box-shadow: 0 2px 6px rgba(0,0,0,0.3);
    }
    
    .stats {
      display: flex;
      gap: 8px;
      font-weight: 600;
      font-size: 11.5px;
      white-space: nowrap;
      background: #0f172a;
      padding: 3px 8px;
      border-radius: 4px;
      border: 1px solid #334155;
    }
    .stats span { color: #94a3b8; }
    .stats b { color: #f8fafc; }
    .stat-hang b { color: #fbbf24; }
    .stat-trong b { color: #34d399; }
    .stat-block b { color: #fb923c; }
    .stat-failed b { color: #f87171; }

    .filters {
      display: flex;
      gap: 4px;
      flex-wrap: wrap;
      align-items: center;
    }
    .btn-filter {
      background: #334155;
      border: 1px solid #475569;
      color: #cbd5e1;
      padding: 3px 8px;
      border-radius: 4px;
      font-size: 11.5px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.1s ease;
      white-space: nowrap;
    }
    .btn-filter:hover { background: #475569; color: #fff; }
    .btn-filter.active { background: #2563eb; border-color: #3b82f6; color: #fff; font-weight: 600; }
    .btn-filter.alert-filter.active { background: #dc2626; border-color: #ef4444; }

    .search-box {
      margin-left: auto;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .search-box input {
      background: #0f172a;
      border: 1px solid #475569;
      color: #fff;
      padding: 3px 8px;
      border-radius: 4px;
      font-size: 11.5px;
      width: 120px;
      outline: none;
      transition: width 0.15s;
    }
    .search-box input:focus { border-color: #38bdf8; width: 150px; }

    .btn-unblock-all {
      background: #7f1d1d;
      border: 1px solid #ef4444;
      color: #fecaca;
      padding: 3px 8px;
      border-radius: 4px;
      font-size: 11.5px;
      font-weight: 600;
      cursor: pointer;
      white-space: nowrap;
    }
    .btn-unblock-all:hover { background: #dc2626; color: #fff; }

    /* Zone Section Container */
    #zonesContainer {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .zone-section {
      background: #131d31;
      border: 1px solid #23354d;
      border-radius: 5px;
      padding: 5px 8px 7px 8px;
    }

    .zone-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 5px;
      padding-bottom: 3px;
      border-bottom: 1px solid #1e293b;
      user-select: none;
    }
    .zone-header-left {
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .zone-badge-tag {
      background: #1e3a8a;
      color: #93c5fd;
      font-size: 10px;
      font-weight: 700;
      padding: 1px 6px;
      border-radius: 3px;
      letter-spacing: 0.3px;
      text-transform: uppercase;
      border: 1px solid #2563eb;
    }
    .zone-title {
      font-size: 13px;
      font-weight: 700;
      color: #f8fafc;
    }
    .zone-count {
      font-size: 11px;
      color: #94a3b8;
    }

    .zone-mini-stats {
      display: flex;
      gap: 6px;
      font-size: 11px;
      font-weight: 600;
    }
    .z-badge {
      padding: 1px 6px;
      border-radius: 3px;
      background: #0f172a;
      border: 1px solid #334155;
    }
    .z-badge.z-hang { color: #fbbf24; border-color: #78350f; background: rgba(245, 158, 11, 0.1); }
    .z-badge.z-trong { color: #34d399; border-color: #064e3b; background: rgba(16, 185, 129, 0.1); }
    .z-badge.z-block { color: #fb923c; border-color: #7c2d12; background: rgba(249, 115, 22, 0.15); font-weight: 700; }
    .z-badge.z-failed { color: #f87171; border-color: #7f1d1d; background: rgba(239, 68, 68, 0.15); font-weight: 700; }

    /* High Density Grid - Mật độ siêu cao */
    .zone-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(115px, 1fr));
      gap: 4px;
    }
    
    .cell {
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 4px;
      padding: 4px 6px;
      display: flex;
      flex-direction: column;
      gap: 2px;
    }
    .cell:hover {
      border-color: #64748b;
    }
    .cell.is-block {
      background: #2e1809;
      border-color: #f97316;
    }
    .cell.is-failed {
      background: #350c0c;
      border-color: #ef4444;
    }
    .cell.is-hang {
      border-color: #b45309;
      background: rgba(180, 83, 9, 0.15);
    }

    .cell-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      line-height: 1;
    }
    .cell-id {
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      font-weight: 700;
      color: #fff;
    }
    .cell-tag {
      font-size: 9px;
      font-weight: 700;
      padding: 1px 3px;
      border-radius: 2px;
      line-height: 1;
      text-transform: uppercase;
    }
    .tag-block { background: #ea580c; color: #fff; }
    .tag-failed { background: #dc2626; color: #fff; }
    .tag-hang { background: #d97706; color: #fff; }
    .tag-trong { background: #059669; color: #fff; }
    .tag-none { background: #475569; color: #94a3b8; }

    .cell-sub {
      display: flex;
      justify-content: space-between;
      font-size: 9.5px;
      color: #94a3b8;
      line-height: 1.1;
    }
    .cell-type {
      font-size: 8.5px;
      font-weight: 600;
      text-transform: uppercase;
      padding: 0 2px;
      border-radius: 2px;
    }
    .type-src { color: #38bdf8; background: rgba(56, 189, 248, 0.15); }
    .type-dest { color: #c084fc; background: rgba(192, 132, 252, 0.15); }

    .cell-actions {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 3px;
      margin-top: 1px;
    }
    .cell-btn {
      padding: 2px 0;
      font-size: 10px;
      font-weight: 600;
      border-radius: 3px;
      cursor: pointer;
      text-align: center;
      border: 1px solid #475569;
      background: #334155;
      transition: background 0.1s;
    }
    .btn-b { color: #fca5a5; }
    .btn-b:hover { background: #b91c1c; color: #fff; border-color: #ef4444; }
    .btn-u { color: #86efac; }
    .btn-u:hover { background: #15803d; color: #fff; border-color: #22c55e; }

    /* Toast */
    #toast {
      position: fixed;
      bottom: 10px;
      right: 10px;
      background: #1e293b;
      border: 1px solid #38bdf8;
      color: #fff;
      padding: 6px 12px;
      border-radius: 4px;
      font-size: 12px;
      display: none;
      z-index: 100;
    }
  </style>
</head>
<body>

  <!-- Top 1-row bar -->
  <div class="topbar">
    <div class="stats">
      <span>Tổng: <b id="sTotal">205</b></span>
      <span class="stat-hang">H: <b id="sHang">0</b></span>
      <span class="stat-trong">T: <b id="sTrong">0</b></span>
      <span class="stat-block">B: <b id="sBlock">0</b></span>
      <span class="stat-failed">Lỗi: <b id="sFailed">0</b></span>
    </div>

    <div class="filters" id="filterBar">
      <button class="btn-filter active" data-filter="all" onclick="setFilter('all')">Tất cả (205)</button>
      <button class="btn-filter alert-filter" data-filter="alert" onclick="setFilter('alert')">⚠️ Block/Lỗi</button>
      <button class="btn-filter" data-filter="hang" onclick="setFilter('hang')">📦 Có hàng</button>
    </div>

    <div class="search-box">
      <input type="text" id="searchInput" placeholder="🔍 Tìm mã ô...">
      <button class="btn-unblock-all" onclick="unlockAll()">Mở hết Block/Lỗi</button>
    </div>
  </div>

  <!-- Container hiển thị các Khối Khu Vực -->
  <div id="zonesContainer"></div>
  <div id="toast"></div>

  <script>
    let rawPositions = [];
    let zonesConfig = {};
    let currentFilter = 'all';
    let searchQuery = '';
    let isFetching = false;
    let initialFilterButtonsBuilt = false;

    function showToast(msg) {
      const t = document.getElementById('toast');
      t.textContent = msg;
      t.style.display = 'block';
      setTimeout(() => { t.style.display = 'none'; }, 2000);
    }

    function setFilter(f) {
      currentFilter = f;
      document.querySelectorAll('.btn-filter').forEach(b => {
        b.classList.toggle('active', b.getAttribute('data-filter') === f);
      });
      render();
    }

    document.getElementById('searchInput').addEventListener('input', (e) => {
      searchQuery = e.target.value.trim().toLowerCase();
      render();
    });

    async function sendBlock(id) {
      try {
        const res = await fetch('/block_point', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(id)
        });
        if (res.ok) {
          showToast(`Đã Block ${id}`);
          fetchData();
        }
      } catch (e) { showToast(`Lỗi: ${e.message}`); }
    }

    async function sendUnblock(id) {
      try {
        const res = await fetch('/unblock_point', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({points: [id], clear_task: true})
        });
        if (res.ok) {
          showToast(`Đã Mở ${id}`);
          fetchData();
        }
      } catch (e) { showToast(`Lỗi: ${e.message}`); }
    }

    async function unlockAll() {
      const ids = rawPositions.filter(p => p.is_blocked || p.is_failed).map(p => p.pos_id);
      if (!ids.length) { showToast('Không có ô nào bị Block/Lỗi'); return; }
      if (!confirm(`Mở khóa ${ids.length} ô?`)) return;
      try {
        await fetch('/unblock_point', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({points: ids, clear_task: true})
        });
        showToast(`Đã mở ${ids.length} ô`);
        fetchData();
      } catch (e) { showToast(`Lỗi: ${e.message}`); }
    }

    function buildFilterButtons(zones) {
      if (initialFilterButtonsBuilt) return;
      const bar = document.getElementById('filterBar');
      
      for (const [zkey, zdata] of Object.entries(zones)) {
        const btn = document.createElement('button');
        btn.className = 'btn-filter';
        btn.setAttribute('data-filter', zkey);
        btn.textContent = `${zkey} (${zdata.total})`;
        btn.onclick = () => setFilter(zkey);
        bar.appendChild(btn);
      }
      initialFilterButtonsBuilt = true;
    }

    async function fetchData() {
      if (isFetching) return;
      isFetching = true;
      try {
        const res = await fetch('/api/positions');
        if (!res.ok) return;
        const data = await res.json();
        
        const s = data.summary || {};
        document.getElementById('sTotal').textContent = s.total || 0;
        document.getElementById('sHang').textContent = s.hang || 0;
        document.getElementById('sTrong').textContent = s.trong || 0;
        document.getElementById('sBlock').textContent = s.block || 0;
        document.getElementById('sFailed').textContent = s.failed || 0;

        rawPositions = data.positions || [];
        zonesConfig = data.zones || {};

        buildFilterButtons(zonesConfig);
        render();
      } finally {
        isFetching = false;
      }
    }

    function renderCell(p) {
      let tag = '-';
      let tagCls = 'tag-none';
      let cellCls = 'cell';

      if (p.is_failed) {
        tag = 'LỖI';
        tagCls = 'tag-failed';
        cellCls += ' is-failed';
      } else if (p.is_blocked) {
        tag = 'BLOCK';
        tagCls = 'tag-block';
        cellCls += ' is-block';
      } else if (p.confirmed_label === 'hang') {
        tag = 'HÀNG';
        tagCls = 'tag-hang';
        cellCls += ' is-hang';
      } else if (p.confirmed_label === 'trong') {
        tag = 'TRỐNG';
        tagCls = 'tag-trong';
      }

      const pcode = p.process_code ? p.process_code.replace('SingleGroup', '').replace('SEGroup', '') : '';

      return `
        <div class="${cellCls}">
          <div class="cell-header">
            <span class="cell-id">${p.pos_id}</span>
            <span class="cell-tag ${tagCls}">${tag}</span>
          </div>
          <div class="cell-sub">
            <span class="cell-type ${p.is_source ? 'type-src' : 'type-dest'}">${p.is_source ? 'NGUỒN' : 'ĐÍCH'}</span>
            <span>${pcode}</span>
          </div>
          <div class="cell-actions">
            <button class="cell-btn btn-b" onclick="sendBlock('${p.pos_id}')">Block</button>
            <button class="cell-btn btn-u" onclick="sendUnblock('${p.pos_id}')">Unblock</button>
          </div>
        </div>
      `;
    }

    function render() {
      const container = document.getElementById('zonesContainer');
      
      const activePositions = rawPositions.filter(p => {
        if (searchQuery && !p.pos_id.toLowerCase().includes(searchQuery)) return false;
        if (currentFilter === 'alert') return p.is_blocked || p.is_failed;
        if (currentFilter === 'hang') return p.confirmed_label === 'hang';
        if (currentFilter !== 'all' && currentFilter !== 'alert' && currentFilter !== 'hang') {
          return p.zone === currentFilter;
        }
        return true;
      });

      const groupedByZone = {};
      for (const [zkey, zdata] of Object.entries(zonesConfig)) {
        groupedByZone[zkey] = {
          info: zdata,
          positions: []
        };
      }
      groupedByZone['OTHER'] = {
        info: { name: 'Chưa phân khu', total: 0 },
        positions: []
      };

      for (const p of activePositions) {
        const zk = p.zone in groupedByZone ? p.zone : 'OTHER';
        groupedByZone[zk].positions.push(p);
      }

      let html = '';
      for (const [zkey, zgroup] of Object.entries(groupedByZone)) {
        if (zgroup.positions.length === 0) continue;

        const zInfo = zgroup.info || {};
        const zHang = zgroup.positions.filter(p => p.confirmed_label === 'hang').length;
        const zTrong = zgroup.positions.filter(p => p.confirmed_label === 'trong').length;
        const zBlock = zgroup.positions.filter(p => p.is_blocked).length;
        const zFailed = zgroup.positions.filter(p => p.is_failed).length;

        html += `
          <div class="zone-section" id="section-${zkey}">
            <div class="zone-header">
              <div class="zone-header-left">
                <span class="zone-badge-tag">${zkey}</span>
                <span class="zone-title">${zInfo.name || zkey}</span>
                <span class="zone-count">(${zgroup.positions.length})</span>
              </div>
              <div class="zone-mini-stats">
                <span class="z-badge z-hang">H: ${zHang}</span>
                <span class="z-badge z-trong">T: ${zTrong}</span>
                ${zBlock > 0 ? `<span class="z-badge z-block">B: ${zBlock}</span>` : ''}
                ${zFailed > 0 ? `<span class="z-badge z-failed">Lỗi: ${zFailed}</span>` : ''}
              </div>
            </div>
            <div class="zone-grid">
              ${zgroup.positions.map(renderCell).join('')}
            </div>
          </div>
        `;
      }

      if (!html) {
        html = '<div style="text-align:center; padding: 20px; color:#94a3b8;">Không tìm thấy vị trí nào.</div>';
      }

      container.innerHTML = html;
    }

    fetchData();
    setInterval(fetchData, 1000);
  </script>
</body>
</html>
"""
    return HTMLResponse(content=html_content)
