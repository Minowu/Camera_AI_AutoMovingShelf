# Graph Report - Camera_AI_AutoMovingShelf  (2026-11-09)

## Corpus Check
- Corpus is ~8,885 words - fits in a single context window. You may not need a graph.

## Summary
- 221 nodes · 404 edges · 16 communities (7 shown, 9 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 7 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- External Dependencies & Imports
- MongoDB Database Layer
- Async HTTP Networking
- Camera Orchestrator & Multi-Processing
- Centralized Logging Utilities
- Shelf Position Management Logic
- Application Settings & Config
- DCC AF3 AF4 Shelf Logic
- YOLO Object Detection Engine
- Server-Sent Events (SSE) Streaming
- PA Area Shelf Logic
- Robot Tracking & Zone Safety
- SSE Realtime API Endpoints
- Task Tracking & Locking Service

## God Nodes (most connected - your core abstractions)
1. `Position_Manager` - 16 edges
2. `YoloDetector` - 13 edges
3. `request_RCS()` - 11 edges
4. `CameraOrchestratorService` - 9 edges
5. `lifespan()` - 8 edges
6. `request_RCS()` - 8 edges
7. `process_auto()` - 8 edges
8. `CameraThread` - 7 edges
9. `active_process()` - 7 edges
10. `start_camera_threads()` - 6 edges

## Surprising Connections (you probably didn't know these)
- `CameraOrchestratorService` --uses--> `YoloDetector`  [INFERRED]
  ai_service/services/camera_orchestrator_service.py → ai_service/services/yolo_detector.py
- `lifespan()` --uses--> `CameraOrchestratorService`  [INFERRED]
  ai_service/main.py → ai_service/services/camera_orchestrator_service.py
- `lifespan()` --calls--> `connect_to_mongo()`  [EXTRACTED]
  ai_service/main.py → ai_service/core/database.py
- `lifespan()` --calls--> `close_mongo_connection()`  [EXTRACTED]
  ai_service/main.py → ai_service/core/database.py
- `start_camera_threads()` --calls--> `CameraThread`  [EXTRACTED]
  ai_service/services/camera_process_worker.py → ai_service/services/camera_thread_worker.py

## Import Cycles
- None detected.

## Communities (16 total, 9 thin omitted)

### Community 0 - "External Dependencies & Imports"
Cohesion: 0.09
Nodes (7): receive_data(), active_proc(), receive_data(), receive_task_status(), health_check(), lifespan(), root()

### Community 1 - "MongoDB Database Layer"
Cohesion: 0.09
Nodes (9): close_mongo_connection(), connect_to_mongo(), Database, get_collection(), get_database(), health_check(), lifespan(), root() (+1 more)

### Community 2 - "Async HTTP Networking"
Cohesion: 0.20
Nodes (13): add_task(), handle_logic_1(), handle_logic_2(), handle_logic_2_1(), handle_logic_2_2(), process_auto(), request_RCS(), active_process() (+5 more)

### Community 4 - "Centralized Logging Utilities"
Cohesion: 0.17
Nodes (4): get_logger(), setup_logger(), get_logger(), setup_logger()

### Community 6 - "Application Settings & Config"
Cohesion: 0.15
Nodes (4): Settings, Config, Settings, Config

### Community 7 - "DCC AF3 AF4 Shelf Logic"
Cohesion: 0.35
Nodes (10): add_task(), handle_logic_1(), handle_logic_2(), handle_logic_2_1(), handle_logic_2_2(), handle_logic_3(), handle_logic_3_2(), handle_logic_4() (+2 more)

### Community 10 - "PA Area Shelf Logic"
Cohesion: 0.39
Nodes (4): handle_logic_5(), handle_logic_6(), process_auto(), request_RCS()

## Knowledge Gaps
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Position_Manager` connect `Shelf Position Management Logic` to `External Dependencies & Imports`?**
  _High betweenness centrality (0.125) - this node is a cross-community bridge._
- **Should `External Dependencies & Imports` be split into smaller, more focused modules?**
  _Cohesion score 0.09388335704125178 - nodes in this community are weakly interconnected._
- **Why does `YoloDetector` connect `YOLO Object Detection Engine` to `MongoDB Database Layer`, `Camera Orchestrator & Multi-Processing`?**
  _High betweenness centrality (0.089) - this node is a cross-community bridge._
- **Should `MongoDB Database Layer` be split into smaller, more focused modules?**
  _Cohesion score 0.09032258064516129 - nodes in this community are weakly interconnected._
- **Why does `RawSSEManager` connect `Server-Sent Events (SSE) Streaming` to `External Dependencies & Imports`?**
  _High betweenness centrality (0.071) - this node is a cross-community bridge._
- **Should `Camera Orchestrator & Multi-Processing` be split into smaller, more focused modules?**
  _Cohesion score 0.11462450592885376 - nodes in this community are weakly interconnected._