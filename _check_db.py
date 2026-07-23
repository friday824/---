import sqlite3, json
conn = sqlite3.connect("data/app.db")
cur = conn.cursor()
cur.execute("SELECT id, status, error_message, script_output FROM video_tasks ORDER BY created_at DESC LIMIT 5")
rows = cur.fetchall()
for r in rows:
    print("ID:", r[0], "Status:", r[1])
    print("Error:", r[2])
    if r[3]:
        so = json.loads(r[3])
        print("Title:", so.get("title", "N/A"))
        scenes = so.get("scenes", [])
        print("Scenes count:", len(scenes))
        for s in scenes[:2]:
            idx = s.get("index", "?")
            nar = s.get("narration_text_cn", "")
            print(f"  Scene {idx}: narration_text_cn={nar[:80]!r}")
            print(f"  All keys: {list(s.keys())}")
    print("---")
conn.close()