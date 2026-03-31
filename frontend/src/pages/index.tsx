import { useState } from "react";
import SignalForm from "../components/SignalForm";
import SignalTable from "../components/SignalTable";

export default function Home() {
  const [, setRefresh] = useState(0); // trigger refresh after a create

  return (
    <div style={{ padding: "20px", fontFamily: "system-ui, sans-serif" }}>
      <h1>Trading Signal Tracker</h1>
      <SignalForm onCreate={() => setRefresh((v) => v + 1)} />
      <SignalTable />
    </div>
  );
}