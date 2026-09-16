// Stand-in for the chrome.* APIs so the REAL popup.html / content.js can be
// rendered outside an extension for Web Store screenshots. Sample data only;
// nothing here ships in the extension package (package.sh uses a whitelist).
(function () {
  // A global rather than a query string: for file:// URLs Chrome treats
  // "page.html?x=y" as a literal filename, the load fails, and a headless
  // --screenshot never fires. render.sh writes one demo file per state.
  function demoState() {
    if (typeof window.FN_DEMO_STATE === "string") return window.FN_DEMO_STATE;
    return new URLSearchParams(location.search).get("helper");
  }

  const NOTES = [
    { id: "n1", title: "HTTP caching", storage_target: "drive", doc_id: "demo" },
    { id: "n2", title: "Two pointers", storage_target: "apple_notes", apple_note_id: "demo" },
    { id: "n3", title: "Rust ownership", storage_target: "local", local_path: "/demo.md" },
    { id: "n4", title: "Stoicism reading notes", storage_target: "drive", doc_id: "demo" },
    { id: "n5", title: "System design prep", storage_target: "drive", doc_id: "demo" },
  ];
  const REPLIES = {
    GET_NOTES: { ok: true, notes: NOTES },
    GET_PLATFORM: { ok: true, os: "mac" },
    // ?helper=outdated renders the "update the helper" panel, so that state
    // can be inspected without downgrading a real install.
    LOCAL_SERVER_STATUS: demoState() === "outdated"
      ? {
          ok: true, reachable: true, outdated: true, version: "0.5.0",
          requiredVersion: "0.6.0", downloadConfigured: true,
          downloadUrl: "https://example.com/release",
          extensionId: "hjfdeceggiefdpdgmfciadlmckhkpkbp",
        }
      : demoState() === "missing"
      ? {
          ok: true, reachable: false, requiredVersion: "0.6.0",
          downloadConfigured: true,
          downloadUrl: "https://example.com/release",
          extensionId: "hjfdeceggiefdpdgmfciadlmckhkpkbp",
        }
      : { ok: true, reachable: true, outdated: false, version: "0.6.0" },
    GET_MODEL_KEY_STATUS: { ok: true, set: false },
  };
  window.chrome = {
    runtime: {
      id: "demo",
      lastError: undefined,
      sendMessage(msg, cb) {
        const reply = REPLIES[msg.type] || { ok: true };
        if (cb) { setTimeout(() => cb(reply), 0); return; }
        return Promise.resolve(reply);
      },
    },
    storage: {
      sync: { get(defaults, cb) { setTimeout(() => cb(Object.assign({}, defaults)), 0); }, set() {} },
      onChanged: { addListener() {} },
    },
    tabs: { create() {} },
  };

  // Popup only: freeze one row in its hover state (the Organise/Summarise
  // actions only appear on hover, which a headless capture cannot do), and
  // report the popup's height so the parent stage can size its iframe.
  const list = document.getElementById("note-list");
  if (!list) return;
  const style = document.createElement("style");
  style.textContent =
    ".note-item.demo-hover{background-size:100% 78%}" +
    ".note-item.demo-hover .note-actions{display:flex}" +
    ".note-item.demo-hover .note-target{display:none}";
  document.head.appendChild(style);
  new MutationObserver(() => {
    const rows = list.querySelectorAll(".note-item");
    if (rows[0] && !rows[0].classList.contains("demo-hover")) rows[0].classList.add("demo-hover");
  }).observe(list, { childList: true });
  // Measure the body, not documentElement.scrollHeight: the latter is never
  // smaller than the iframe's own viewport, so the frame could only grow and
  // would leave an empty block under the popup.
  const report = () => {
    const cs = getComputedStyle(document.body);
    const h = document.body.getBoundingClientRect().height +
      parseFloat(cs.marginTop) + parseFloat(cs.marginBottom);
    parent.postMessage({ h: Math.ceil(h) }, "*");
  };
  new ResizeObserver(report).observe(document.body);
})();
