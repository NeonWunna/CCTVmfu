import json
import re

# Load source data (oldcctvinfo.json - has BUILDING, FLOOR, POSITION, Location)
with open('oldcctvinfo.json', 'r', encoding='utf-8') as f:
    source_data = json.load(f)

# Load target data (oldcctvinfo2.json - has WKT, name, ip, rtsp)
with open('oldcctvinfo2.json', 'r', encoding='utf-8') as f:
    content = f.read()
    # The file may not be a proper JSON array, fix it
    # It starts without '[' and ends without ']'
    content = content.strip()
    if not content.startswith('['):
        content = '[' + content + ']'
    target_data = json.loads(content)

# Build lookup from source by name and by ip
source_by_name = {}
source_by_ip = {}
for item in source_data:
    name = item.get('CAMERA NAME_NEW', '').strip()
    ip = item.get('IP ADDRESS', '').strip()
    if name:
        source_by_name[name] = item
    if ip:
        source_by_ip[ip] = item

output = []
for item in target_data:
    name = item.get('name', '').strip()
    ip = item.get('ip', '').strip()
    wkt = item.get('WKT', '').strip()
    rtsp = item.get('rtsp', '')

    # Try to find matching source record
    src = source_by_name.get(name) or source_by_ip.get(ip)

    if src:
        building = src.get('BUILDING', '')
        floor = src.get('FLOOR', '')
        position = src.get('POSITION', '')
        location = src.get('Location', '')
        src_ip = src.get('IP ADDRESS', ip)
    else:
        # fallback: no match found - use empty strings
        building = ''
        floor = ''
        position = ''
        location = ''
        src_ip = ip

    # Build new record in the target format
    new_item = {
        "WKT": wkt,
        "name": name,
        "ip": ip if ip else src_ip,
        "BUILDING": building,
        "FLOOR": floor,
        "POSITION": position,
        "Location": location,
    }
    if rtsp:
        new_item["rtsp"] = rtsp

    output.append(new_item)

# Write output back to oldcctvinfo2.json as a proper JSON array
with open('oldcctvinfo2.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"Transformed {len(output)} records.")

# Count matched vs unmatched
matched = sum(1 for item in target_data if 
              source_by_name.get(item.get('name','').strip()) or 
              source_by_ip.get(item.get('ip','').strip()))
print(f"Matched: {matched}, Unmatched: {len(output) - matched}")
