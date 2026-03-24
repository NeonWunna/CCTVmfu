const fs = require('fs');
const path = require('path');

const inputFile = path.join(__dirname, 'oldcctvinfo3.json');
const outputFile = path.join(__dirname, 'oldcctvinfo3.json'); // overwrite in place

/**
 * Parse CAMERA NAME_NEW -> { building, floor, position }
 *
 * Pattern examples (from oldcctvinfo2.json reference):
 *   AD1-FL1-East        -> building=AD1, floor=1,  position=East
 *   AD1-FLG-P2          -> building=AD1, floor=G,  position=P2
 *   AD1-FL2-FireSouth   -> building=AD1, floor=2,  position=FireSouth
 *   AD2-Fire-FL1-inside -> building=AD2, floor=1,  position=Fire-inside
 *   AD2-Carpark         -> building=AD2, floor='', position=Carpark
 *   AS-FL.G             -> building=AS,  floor=G,  position=''
 *   AS-FL.G-MotorBike1  -> building=AS,  floor=G,  position=MotorBike1
 *   Library-Living-FL3-1-> building=Library-Living, floor=3, position=1
 *   D1-Stair-FL2        -> building=D1,  floor=2,  position=Stair
 *   Dorm-F1-FL1-Outside -> building=Dorm-F1, floor=1, position=Outside
 */
function parseCameraName(name) {
  const parts = name.split('-');
  let building = '';
  let floor = '';
  let positionParts = [];
  let floorIndex = -1;

  // Find the first segment that looks like FL<x> or FL.<x>
  // A FL segment matches /^FL\.?([0-9]+|[A-Z])$/i
  for (let i = 0; i < parts.length; i++) {
    const m = parts[i].match(/^FL\.?([0-9]+|[A-Za-z])$/i);
    if (m) {
      floorIndex = i;
      floor = m[1].toUpperCase(); // e.g. "1", "2", "G"
      break;
    }
  }

  if (floorIndex === -1) {
    // No FL segment found
    // First part = building, rest = position
    building = parts[0];
    positionParts = parts.slice(1);
  } else {
    // Building = everything before the FL segment joined by '-'
    building = parts.slice(0, floorIndex).join('-');
    // Position = everything after the FL segment joined by '-'
    positionParts = parts.slice(floorIndex + 1);
  }

  const position = positionParts.join('-');

  return {
    building,
    floor,
    position
  };
}

// Load
const cameras = JSON.parse(fs.readFileSync(inputFile, 'utf8'));

// Fill
const result = cameras.map(cam => {
  const { building, floor, position } = parseCameraName(cam['CAMERA NAME_NEW'] || '');
  return {
    ...cam,
    'BUILDING': building,
    'FLOOR': floor,
    'POSITION': position
  };
});

// Save (pretty 2-space indent, no BOM)
fs.writeFileSync(outputFile, JSON.stringify(result, null, 2), 'utf8');
console.log(`Done! Processed ${result.length} cameras -> ${outputFile}`);

// Print a sample for verification
console.log('\nSample (first 10):');
result.slice(0, 10).forEach(c => {
  console.log(`  ${c['CAMERA NAME_NEW'].padEnd(30)} | building=${c['BUILDING'].padEnd(15)} floor=${String(c['FLOOR']).padEnd(4)} position=${c['POSITION']}`);
});
