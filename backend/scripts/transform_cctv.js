const fs = require('fs');

// Load current oldcctvinfo2.json (already in oldcctvinfo.json format)
const data = JSON.parse(fs.readFileSync('oldcctvinfo2.json', 'utf-8'));

// Extract floor from camera name, various patterns:
// FL1, FL.G, Fl3, FL3, Floor1, Floor 3, F3, F7
function extractFloor(name) {
  let m;

  // "Floor" keyword (e.g. "Floor5 B4", "M3 Floor2", "Floor 3")
  m = name.match(/floor\s*(\S+)/i);
  if (m) return m[1].replace(/[^a-zA-Z0-9.]/g, '');

  // "Floo" typo (e.g. "Floo5 B4")
  m = name.match(/floo\s*(\d+)/i);
  if (m) return m[1];

  // "FL" followed by anything: FL1, FL.G, FL2, Fl3, FL8 (with or without separator)
  m = name.match(/(?:^|[-_\s])FL([^-_\s]+)/i);
  if (m) return m[1];

  // "Fl" at word boundary e.g. "Fl8 Mid", "Fl5 A1", "Lib Fl3 MainIN"
  m = name.match(/\bFl(\d+)\b/i);
  if (m) return m[1];

  // "F" followed by digits with separator (e.g. "F3", "F7", "Dorm F3 Fl2")
  m = name.match(/(?:^|[-_\s])F(\d+)(?:[-_\s]|$)/i);
  if (m) return m[1];

  return '';
}

let filled = 0;
const output = data.map(item => {
  let floor = item['FLOOR'] || '';

  // If FLOOR is empty, try extracting from CAMERA NAME_NEW
  if (!floor) {
    const name = item['CAMERA NAME_NEW'] || '';
    floor = extractFloor(name);
    if (floor) filled++;
  }

  return { ...item, FLOOR: floor };
});

fs.writeFileSync('oldcctvinfo2.json', JSON.stringify(output, null, 4), 'utf-8');
console.log(`Done: ${output.length} records. Floor filled from name: ${filled}`);

// Show still-empty floor records
const stillEmpty = output.filter(r => !r['FLOOR']);
console.log(`\nStill empty FLOOR (${stillEmpty.length}):`);
stillEmpty.forEach(r => console.log(`  - "${r['CAMERA NAME_NEW']}" | ip: ${r['IP ADDRESS']}`));
