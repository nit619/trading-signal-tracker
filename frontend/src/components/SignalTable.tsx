import { useEffect, useState } from "react";
import axios from "axios";

type Signal = {
  id: number;
  symbol: string;
  direction: "BUY" | "SELL";
  entry_price: number;
  stop_loss: number;
  target_price: number;
  entry_time: string; // ISO
  expiry_time: string;
  created_at: string;
  status:
    | "OPEN"
    | "TARGET_HIT"
    | "STOPLOSS_HIT"
    | "EXPIRED";
  realized_roi: number | null;
  current_price: number;
  time_left_seconds: number;
};

export default function SignalTable() {
  const [signals, setSignals] = useState<Signal[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchSignals = async () => {
    setLoading(true);
    try {
      const resp = await axios.get<Signal[]>("http://localhost:8000/api/signals");
      setSignals(resp.data);
    } catch (e) {
      console.error("Failed to fetch signals", e);
    } finally {
      setLoading(false);
    }
  };

  // Auto‑refresh every 15 seconds (Req 9.2)
  useEffect(() => {
    fetchSignals();
    const timer = setInterval(fetchSignals, 15_000);
    return () => clearInterval(timer);
  }, []);

  const formatTime = (sec: number) => {
    if (sec <= 0) return "Expired";
    const h = Math.floor(sec / 3600);
    const m = Math.floor((sec % 3600) / 60);
    const s = sec % 60;
    return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
  };

  if (loading) return <p>Loading…</p>;
  if (signals.length === 0) return <p>No signals yet.</p>;

  return (
    <table
      style={{
        width: "100%",
        borderCollapse: "collapse",
        marginTop: 24,
      }}
    >
      <thead>
        <tr>
          <th>Symbol</th>
          <th>Dir</th>
          <th>Entry</th>
          <th>Target</th>
          <th>SL</th>
          <th>Price</th>
          <th>Status</th>
          <th>ROI %</th>
          <th>Time Left</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {signals.map((s) => (
          <tr key={s.id} style={{ borderBottom: "1px solid #eee" }}>
            <td>{s.symbol}</td>
            <td>{s.direction}</td>
            <td>{s.entry_price.toFixed(2)}</td>
            <td>{s.target_price.toFixed(2)}</td>
            <td>{s.stop_loss.toFixed(2)}</td>
            <td>{s.current_price.toFixed(2)}</td>
            <td>{s.status}</td>
            <td>
              {s.realized_roi !== null
                ? s.realized_roi.toFixed(2)
                : "-"}
            </td>
            <td>{formatTime(s.time_left_seconds)}</td>
            <td>
              <button
                onClick={() => {
                  if (
                    window.confirm(
                      `Delete signal ${s.id}? This cannot be undone.`
                    )
                  ) {
                    axios
                      .delete(`http://localhost:8000/api/signals/${s.id}`)
                      .then(() => fetchSignals())
                      .catch(console.error);
                  }
                }}
                style={{
                  background: "#ff4d4d",
                  color: "white",
                  border: "none",
                  padding: "2px 6px",
                  cursor: "pointer",
                }}
              >
                Del
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}