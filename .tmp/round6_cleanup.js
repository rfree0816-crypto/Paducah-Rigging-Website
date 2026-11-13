const fs = require('fs');
let html = fs.readFileSync('index.html', 'utf8');

// --- CATS_META ---
const catsRe = /const CATS_META\s*=\s*(\[.*?\]);/s;
const catsMatch = html.match(catsRe);
let cats = JSON.parse(catsMatch[1]);
const beforeCats = cats.length;
cats = cats.filter(c => !['Barge & marine', 'Shop supplies'].includes(c.name));
console.log('categories:', beforeCats, '->', cats.length);
html = html.replace(catsRe, `const CATS_META = ${JSON.stringify(cats)};`);

// --- ITEMS ---
const itemsRe = /const ITEMS\s*=\s*(\[.*?\]);/s;
const itemsMatch = html.match(itemsRe);
let items = JSON.parse(itemsMatch[1]);
const beforeItems = items.length;
items = items.filter(i => !['Barge & marine', 'Shop supplies'].includes(i.cat));
// Also remove the whistle item specifically (stays in Safety cat otherwise)
items = items.filter(i => i.upn !== 'PH-00325');
console.log('items:', beforeItems, '->', items.length);
html = html.replace(itemsRe, `const ITEMS = ${JSON.stringify(items)};`);

fs.writeFileSync('index.html', html);
console.log('done');
