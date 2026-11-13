const { chromium } = require('playwright');

(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1440, height: 1900 }, deviceScaleFactor: 2 });
  await p.goto('https://rfree0816-crypto.github.io/Paducah-Rigging-Website/?cb=' + Date.now(), { waitUntil: 'networkidle' });

  const clicked = await p.evaluate(() => {
    const el = Array.from(document.querySelectorAll('button,a,span,div'))
      .find(e => /browse catalog|sign in|enter/i.test(e.textContent || '') &&
                 e.textContent.trim().length < 40 && e.offsetParent !== null);
    if (el) { el.click(); return el.textContent.trim(); }
    return null;
  });

  await p.waitForTimeout(2500);

  await p.evaluate(async () => {
    const v = Date.now();
    await Promise.all(Array.from(document.querySelectorAll('img')).map(img =>
      new Promise(res => {
        img.onload = res; img.onerror = res;
        img.src = img.src.split('?')[0] + '?v=' + v;
        setTimeout(res, 4000);
      })));
  });
  await p.waitForTimeout(1200);

  await p.screenshot({ path: '/home/user/workspace/preview-anchor.png' });
  await p.screenshot({ path: '/home/user/workspace/preview-full.png', fullPage: true });
  console.log(JSON.stringify({ clicked, title: await p.title() }));
  await b.close();
})();
