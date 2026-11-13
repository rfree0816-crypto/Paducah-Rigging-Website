const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1500, height: 2100 }, deviceScaleFactor: 2 });
  await p.goto('https://rfree0816-crypto.github.io/Paducah-Rigging-Website/?cb=' + Date.now(), { waitUntil: 'networkidle' });
  await p.evaluate(() => { const el=[...document.querySelectorAll('*')].find(e=>/browse catalog/i.test(e.textContent||'')&&e.offsetParent!==null&&e.children.length===0); if(el) el.click(); });
  await p.waitForTimeout(2500);
  await p.evaluate(async () => { const v=Date.now(); await Promise.all([...document.querySelectorAll('img')].map(i=>new Promise(r=>{i.onload=i.onerror=r;i.src=i.src.split('?')[0]+'?f='+v;setTimeout(r,4000);}))); });
  await p.waitForTimeout(1800);
  await p.screenshot({ path: '/home/user/workspace/catalog-final.png' });
  await b.close();
})();
