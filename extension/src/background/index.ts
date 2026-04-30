/**
 * MV3 service worker. Slice 0 only sets up the context menu
 * entry for user flagging. Later slices wire this to the API.
 */

const FLAG_MENU_ID = "pivs-flag-image";

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: FLAG_MENU_ID,
    title: "Flag this political image",
    contexts: ["image"],
  });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId !== FLAG_MENU_ID) return;
  if (!tab?.id || !info.srcUrl) return;
  // Slice 5 will open the flag dialog in the active tab. For now,
  // log so an engineer can verify the menu is wired up.
  // eslint-disable-next-line no-console
  console.info("[PIVS] flag requested for", info.srcUrl);
});
