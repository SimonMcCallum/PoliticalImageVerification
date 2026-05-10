/**
 * MV3 service worker.
 *
 * - Creates the "Flag this political image" context menu.
 * - Downloads the bloom-filter snapshot on install and on a daily alarm
 *   so most image lookups never have to leave the device.
 * - Listens for a "refresh-bloom" message from the popup so the user
 *   can trigger a manual reload at any time (essential for the EC's
 *   transparency review).
 */

import { refreshBloomSnapshot } from "../lib/bloom/snapshot";
import { REFRESH_ALARM, REFRESH_PERIOD_MINUTES } from "../lib/config";
import { debugLog } from "../lib/debug/log";

const FLAG_MENU_ID = "pivs-flag-image";

function safeRefresh(reason: string) {
  refreshBloomSnapshot().catch((err) => {
    // eslint-disable-next-line no-console
    console.warn(`[PIVS] bloom refresh (${reason}) failed:`, err);
  });
}

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: FLAG_MENU_ID,
    title: "Flag this political image",
    contexts: ["image"],
  });

  chrome.alarms.create(REFRESH_ALARM, {
    delayInMinutes: 1,
    periodInMinutes: REFRESH_PERIOD_MINUTES,
  });

  safeRefresh("install");
});

chrome.runtime.onStartup?.addListener(() => {
  safeRefresh("startup");
});

chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === REFRESH_ALARM) {
    safeRefresh("alarm");
  }
});

chrome.contextMenus.onClicked.addListener((info, _tab) => {
  if (info.menuItemId !== FLAG_MENU_ID) return;
  if (!info.srcUrl) return;
  debugLog.push("flag-submitted", `flag requested for ${info.srcUrl}`);
});

chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg?.type === "pivs.refreshBloom") {
    refreshBloomSnapshot()
      .then((meta) => sendResponse({ ok: true, meta }))
      .catch((err) =>
        sendResponse({
          ok: false,
          error: err instanceof Error ? err.message : String(err),
        })
      );
    return true; // tell Chrome we will respond asynchronously
  }
  return false;
});
