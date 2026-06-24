'use client';

import { useEffect, useRef, useCallback } from 'react';

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'wss://backend-production-40db.up.railway.app/ws';

export function useRealtime(onDataChanged?: () => void) {
  const ws = useRef<WebSocket | null>(null);
  const cb = useRef(onDataChanged);
  cb.current = onDataChanged;

  useEffect(() => {
    let retryTimer: ReturnType<typeof setTimeout>;

    function connect() {
      const socket = new WebSocket(WS_URL);
      ws.current = socket;

      socket.onopen = () => console.log('[WS] Connected');

      socket.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          if (msg.event === 'data_changed') {
            cb.current?.();
          }
        } catch { /* ignore */ }
      };

      socket.onclose = () => {
        retryTimer = setTimeout(connect, 3000);
      };

      socket.onerror = () => socket.close();
    }

    connect();

    return () => {
      clearTimeout(retryTimer);
      ws.current?.close();
    };
  }, []);
}
