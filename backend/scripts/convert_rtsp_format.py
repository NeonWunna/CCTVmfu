import json
import re

input_file = r"c:\Users\Classroom\Documents\GitHub\CCTVmfu\backend\scripts\rtsp กล้องเก่า ม.json"
output_file = r"c:\Users\Classroom\Documents\GitHub\CCTVmfu\backend\scripts\rtsp กล้องเก่า ม_new.json"

with open(input_file, "r", encoding="utf-8") as f:
    content = f.read().strip()

# The file might not be a valid JSON array, wrap if needed
if not content.startswith("["):
    content = "[" + content + "]"

# Fix trailing commas before ]
content = re.sub(r",\s*\]", "]", content)

cameras = json.loads(content)

def parse_wkt_point(wkt):
    """Parse WKT POINT (lon lat) -> (lat_str, lon_str)"""
    match = re.match(r"POINT\s*\(([0-9.]+)\s+([0-9.]+)\)", wkt or "")
    if match:
        lon = float(match.group(1))
        lat = float(match.group(2))
        return f"{lat:.4f}N", f"{lon:.4f}E"
    return "", ""

def build_rtsp_url(ip, rtsp_raw):
    """Build clean RTSP URL from raw field."""
    if rtsp_raw:
        # Unescape \/ -> /
        return rtsp_raw.replace("\\/", "/")
    if ip:
        return f"rtsp://mfustream:mediamfu2025@{ip}/Streaming/Channels/101/"
    return ""

result = []
for i, cam in enumerate(cameras, start=1):
    wkt = cam.get("WKT", "")
    name = cam.get("name", "")
    ip = cam.get("ip", "")
    rtsp_raw = cam.get("rtsp", "")

    lat_str, lon_str = parse_wkt_point(wkt)
    rtsp_url = build_rtsp_url(ip, rtsp_raw)

    new_entry = {
        "NO": str(i),
        "IP ADDRESS": ip,
        "CAMERA NAME_NEW": name,
        "BUILDING": "",
        "FLOOR": "",
        "POSITION": "",
        "Latitude": lat_str,
        "Longtitude": lon_str,
        "Location": name,
        "enable rtsp": "",
        "ANPR&PTZ RTSP": rtsp_url,
        "PTZ": "",
        "": ""
    }
    result.append(new_entry)

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"Done! Converted {len(result)} cameras -> {output_file}")
