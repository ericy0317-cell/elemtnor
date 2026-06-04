const { setupBrowserRuntime } = await import("file:///C:/Users/24362/.codex/plugins/cache/openai-bundled/browser/26.601.21317/scripts/browser-client.mjs");
await setupBrowserRuntime({ globals: globalThis });
globalThis.browser = await agent.browsers.get("iab");
await browser.nameSession("🔍 Elementor Learning");
globalThis.tab = await browser.tabs.new();
await tab.goto("https://yange14.sg-host.com/wp-admin");
console.log("Browser ready, navigating to WP admin");
