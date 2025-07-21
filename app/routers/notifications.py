from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..websocket_manager import manager

# Pastikan variabel 'router' ini ada
router = APIRouter(tags=["Notifications"])

@router.websocket("/ws/notifications")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Biarkan koneksi terbuka untuk menerima pesan dari client jika perlu
            # atau cukup tunggu sampai koneksi terputus.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)