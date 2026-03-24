const fs = require('fs');
const path = require('path');

const dir = path.join(__dirname);
const inputFile = path.join(dir, 'rtsp กล้องเก่า ม.json');
const outputFile = path.join(dir, 'rtsp กล้องเก่า ม_new.json');

let content = fs.readFileSync(inputFile, 'utf8').trim();

// Wrap in array if not already
if (!content.startsWith('[')) {
  content = '[' + content + ']';
}
// Remove trailing commas before ]
content = content.replace(/,(\s*\])/g, '$1');

const cameras = JSON.parse(content);

function parseWKT(wkt) {
  if (!wkt) return { lat: '', lon: '' };
  const m = wkt.match(/POINT\s*\(([0-9.]+)\s+([0-9.]+)\)/);
  if (m) {
    return {
      lat: parseFloat(m[2]).toFixed(4) + 'N',
      lon: parseFloat(m[1]).toFixed(4) + 'E'
    };
  }
  return { lat: '', lon: '' };
}

function buildRTSP(ip, rtsp) {
  if (rtsp) {
    // Unescape \/ -> /
    return rtsp.replace(/\\\//g, '/');
  }
  if (ip) {
    return `rtsp://mfustream:mediamfu2025@${ip}/Streaming/Channels/101/`;
  }
  return '';
}

const result = cameras.map((cam, i) => {
  const { lat, lon } = parseWKT(cam.WKT || '');
  return {
    'NO': String(i + 1),
    'IP ADDRESS': cam.ip || '',
    'CAMERA NAME_NEW': cam.name || '',
    'BUILDING': '',
    'FLOOR': '',
    'POSITION': '',
    'Latitude': lat,
    'Longtitude': lon,
    'Location': cam.name || '',
    'enable rtsp': '',
    'ANPR&PTZ RTSP': buildRTSP(cam.ip, cam.rtsp),
    'PTZ': '',
    '': ''
  };
});

fs.writeFileSync(outputFile, JSON.stringify(result, null, 2), 'utf8');
console.log(`Done! Converted ${result.length} cameras -> ${outputFile}`);
