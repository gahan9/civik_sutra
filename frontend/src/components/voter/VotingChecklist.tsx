import { useCallback, useEffect, useState } from "react";

import { ACCEPTED_PHOTO_IDS, CHECKLIST_ITEMS } from "../../data/voter-readiness";


const STORAGE_KEY = "civiksutra-checklist";

function loadChecked(): Record<string, boolean> {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored ? JSON.parse(stored) : {};
  } catch {
    return {};
  }
}

function saveChecked(checked: Record<string, boolean>): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(checked));
  } catch { /* localStorage unavailable */ }
}

export function VotingChecklist() {
  const [checked, setChecked] = useState<Record<string, boolean>>(loadChecked);

  useEffect(() => {
    saveChecked(checked);
  }, [checked]);

  const toggle = useCallback((id: string) => {
    setChecked((prev) => ({ ...prev, [id]: !prev[id] }));
  }, []);

  const handleShare = useCallback(() => {
    const lines = CHECKLIST_ITEMS.map(
      (item) => `${checked[item.id] ? "✅" : "⬜"} ${item.label}`,
    );
    const text = `📋 My Voting Day Checklist (CivikSutra)\n\n${lines.join("\n")}`;

    if (navigator.share) {
      navigator.share({ title: "Voting Day Checklist", text }).catch(() => {});
    } else {
      navigator.clipboard.writeText(text).catch(() => {});
    }
  }, [checked]);

  const beforeItems = CHECKLIST_ITEMS.filter((i) => i.category === "before");
  const boothItems = CHECKLIST_ITEMS.filter((i) => i.category === "at_booth");
  const dontItems = CHECKLIST_ITEMS.filter((i) => i.category === "dont");
  const total = CHECKLIST_ITEMS.filter((i) => i.category !== "dont").length;
  const done = CHECKLIST_ITEMS.filter(
    (i) => i.category !== "dont" && checked[i.id],
  ).length;

  return (
    <div className="voter-section">
      <h2>Voting Day Checklist</h2>
      <p className="muted">
        {done} of {total} items completed
      </p>

      <div className="checklist-progress">
        <div
          className="checklist-progress-bar"
          style={{ width: `${total > 0 ? (done / total) * 100 : 0}%` }}
        />
      </div>

      <div className="checklist-group">
        <h3>Before You Leave</h3>
        {beforeItems.map((item) => (
          <label key={item.id} className="checklist-item">
            <input
              type="checkbox"
              checked={!!checked[item.id]}
              onChange={() => toggle(item.id)}
            />
            <span>{item.label}</span>
          </label>
        ))}
      </div>

      <div className="checklist-group">
        <h3>Accepted Photo IDs (any one)</h3>
        <div className="photo-id-list">
          {ACCEPTED_PHOTO_IDS.map((id) => (
            <span key={id.name} className="photo-id-chip">
              {id.preferred && "★ "}
              {id.name}
            </span>
          ))}
        </div>
        <p className="muted" style={{ marginTop: "0.5rem", fontSize: "0.82rem" }}>
          ★ = Preferred. e-EPIC (digital) also accepted.
        </p>
      </div>

      <div className="checklist-group">
        <h3>At The Booth</h3>
        {boothItems.map((item) => (
          <label key={item.id} className="checklist-item">
            <input
              type="checkbox"
              checked={!!checked[item.id]}
              onChange={() => toggle(item.id)}
            />
            <span>{item.label}</span>
          </label>
        ))}
      </div>

      <div className="checklist-group checklist-group--warning">
        <h3>Do NOT:</h3>
        {dontItems.map((item) => (
          <div key={item.id} className="checklist-dont">
            {item.label}
          </div>
        ))}
      </div>

      <div className="checklist-group">
        <h3>Accessibility</h3>
        <ul className="accessibility-list">
          <li>Wheelchair ramps at most booths</li>
          <li>Braille-enabled EVMs available</li>
          <li>Companion allowed for PWD voters</li>
          <li>Priority queue for elderly/PWD</li>
        </ul>
      </div>

      <div className="card-actions">
        <button type="button" className="secondary" onClick={handleShare}>
          Share Checklist
        </button>
      </div>
    </div>
  );
}
