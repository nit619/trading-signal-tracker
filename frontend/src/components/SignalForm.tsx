import React, { useState } from "react";
import axios from "axios";

type FormValues = {
  symbol: string;
  direction: "BUY" | "SELL";
  entry_price: string;
  stop_loss: string;
  target_price: string;
  entry_time: string; // ISO string from datetime-local
  expiry_time: string;
};

export default function SignalForm({ onCreate }: { onCreate: () => void }) {
  const [form, setForm] = useState<FormValues>({
    symbol: "",
    direction: "BUY",
    entry_price: "",
    stop_loss: "",
    target_price: "",
    entry_time: "",
    expiry_time: "",
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setForm({ ...form, [name]: value });
    setErrors((prev) => ({ ...prev, [name]: "" }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrors({});
    try {
      await axios.post("http://localhost:8000/api/signals", {
        ...form,
        entry_time: new Date(form.entry_time).toISOString(),
        expiry_time: new Date(form.expiry_time).toISOString(),
      });
      alert("Signal created!");
      onCreate(); // tell parent to refresh the list
      // reset form
      setForm({
        symbol: "",
        direction: "BUY",
        entry_price: "",
        stop_loss: "",
        target_price: "",
        entry_time: "",
        expiry_time: "",
      });
    } catch (err: any) {
      if (err.response?.status === 400) {
        // backend returns validation errors as [{loc: [...], msg: "..."}, ...]
        const fieldErrors: Record<string, string> = {};
        err.response.data.detail.forEach((e: any) => {
          const field = e.loc[e.loc.length - 1]; // last element = field name
          fieldErrors[field] = e.msg;
        });
        setErrors(fieldErrors);
      } else {
        alert("Unexpected error: " + err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ maxWidth: 400, margin: "0 auto" }}>
      <h2>Create Trading Signal</h2>

      {/* Symbol */}
      <div style={{ marginBottom: 12 }}>
        <label>Symbol (e.g., BTCUSDT)</label>
        <input
          name="symbol"
          value={form.symbol}
          onChange={handleChange}
          placeholder="BTCUSDT"
          style={{ width: "100%", padding: 6 }}
        />
        {errors.symbol && (
          <span style={{ color: "red", display: "block", marginTop: 4 }}>
            {errors.symbol}
          </span>
        )}
      </div>

      {/* Direction */}
      <div style={{ marginBottom: 12 }}>
        <label>Direction</label>
        <select
          name="direction"
          value={form.direction}
          onChange={handleChange}
          style={{ width: "100%", padding: 6 }}
        >
          <option value="BUY">BUY</option>
          <option value="SELL">SELL</option>
        </select>
      </div>

      {/* Entry Price */}
      <div style={{ marginBottom: 12 }}>
        <label>Entry Price</label>
        <input
          name="entry_price"
          type="number"
          step="0.01"
          value={form.entry_price}
          onChange={handleChange}
          style={{ width: "100%", padding: 6 }}
        />
        {errors.entry_price && (
          <span style={{ color: "red", display: "block", marginTop: 4 }}>
            {errors.entry_price}
          </span>
        )}
      </div>

      {/* Stop Loss */}
      <div style={{ marginBottom: 12 }}>
        <label>Stop Loss</label>
        <input
          name="stop_loss"
          type="number"
          step="0.01"
          value={form.stop_loss}
          onChange={handleChange}
          style={{ width: "100%", padding: 6 }}
        />
        {errors.stop_loss && (
          <span style={{ color: "red", display: "block", marginTop: 4 }}>
            {errors.stop_loss}
          </span>
        )}
      </div>

      {/* Target Price */}
      <div style={{ marginBottom: 12 }}>
        <label>Target Price</label>
        <input
          name="target_price"
          type="number"
          step="0.01"
          value={form.target_price}
          onChange={handleChange}
          style={{ width: "100%", padding: 6 }}
        />
        {errors.target_price && (
          <span style={{ color: "red", display: "block", marginTop: 4 }}>
            {errors.target_price}
          </span>
        )}
      </div>

      {/* Entry Time */}
      <div style={{ marginBottom: 12 }}>
        <label>Entry Time (local)</label>
        <input
          name="entry_time"
          type="datetime-local"
          value={form.entry_time}
          onChange={handleChange}
          style={{ width: "100%", padding: 6 }}
        />
        {errors.entry_time && (
          <span style={{ color: "red", display: "block", marginTop: 4 }}>
            {errors.entry_time}
          </span>
        )}
      </div>

      {/* Expiry Time */}
      <div style={{ marginBottom: 12 }}>
        <label>Expiry Time (local)</label>
        <input
          name="expiry_time"
          type="datetime-local"
          value={form.expiry_time}
          onChange={handleChange}
          style={{ width: "100%", padding: 6 }}
        />
        {errors.expiry_time && (
          <span style={{ color: "red", display: "block", marginTop: 4 }}>
            {errors.expiry_time}
          </span>
        )}
      </div>

      <button
        type="submit"
        disabled={loading}
        style={{
          background: "#0070f3",
          color: "white",
          border: "none",
          padding: "8px 16px",
          cursor: loading ? "not-allowed" : "pointer",
        }}
      >
        {loading ? "Creating…" : "Create Signal"}
      </button>
    </form>
  );
}