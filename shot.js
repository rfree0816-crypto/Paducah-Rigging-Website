const { chromium } = require('playwright');

(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 2 });
  await p.goto('https://rfree0816-crypto.github.io/Paducah-Rigging-Website/', { waitUntil: 'networkidle' });

  // find and click the catalog CTA
  const clicked = await p.evaluate(() => {
    const els = [...document.querySelectorAll('button,a,div')];
    const el = els.find(e => /browse catalog/i.test(e.textContent || '') && e.offsetParent !== null);
    if (el) { el.click(); return true; }
    return false;
  });
  await p.waitForTimeout(2500);

  await p.screenshot({ path: '/home/user/workspace/preview-catalog.png' });

  // taller shot to capture the full tile grid
  await p.setViewportSize({ width: 1440, height: 2000 });
  await p.waitForTimeout(800);
  await p.screenshot({ path: '/home/user/workspace/preview-tiles.png' });

  console.log(JSON.stringify({ clicked, title: await p.title() }));
  await b.close();
})();
