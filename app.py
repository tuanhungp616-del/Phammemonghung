import os
import random
import re
from collections import deque
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# ==========================================
# 🔐 HỆ THỐNG AN NINH
# ==========================================
KEYS_DB = {
    "hungadmin1122334455": "admin",
    "bo1": "user",
    "viphung": "user",
    "chutaidou": "user"
}
LOCKED_KEYS = set()
HISTORY = deque(maxlen=50)

# ==========================================
# 🧠 LÕI AI MONTE CARLO & HYBRID PATTERN
# ==========================================
def get_id(item):
    if isinstance(item, dict):
        for k in ['id', 'phien', 'sessionId', 'sid', 'referenceId', 'matchId']:
            if k in item and str(item[k]).replace('-', '').isdigit():
                return int(item[k])
    raw_str = str(item)
    matches = re.findall(r"'?(?:id|phien|referenceId|sessionId|matchId)'?\s*:\s*'?(\d+)'?", raw_str, re.IGNORECASE)
    return int(matches[0]) if matches else 0

def analyze_patterns(seq):
    if len(seq) < 5: return "T" if random.random() > 0.5 else "X", 52.0
    seq_str = "".join(seq)
    patterns = [(r"(T{3,}|X{3,})$", 0.62), (r"(TX{2,}|XT{2,})$", 0.58), (r"(TTXX|XXTT)$", 0.57), (r"(TXXX|XTTT)$", 0.59)]
    for regex, bias in patterns:
        if re.search(regex, seq_str[-10:]): return ("X" if seq[-1] == "T" else "T"), bias * 100
    prob_t = seq.count("T") / len(seq) if seq else 0.5
    return "T" if prob_t > 0.5 else "X", max(50.0, min(68.0, abs(prob_t - 0.5) * 120 + 50))

def monte_carlo_predict(history_list, n_sim=5000):
    if not history_list: return 50.0, "T"
    p_t = history_list.count("T") / len(history_list)
    sim_t = sum(1 for _ in range(n_sim) if random.random() < p_t * 1.05)
    prob = (sim_t / n_sim) * 100
    return round(prob, 1), "T" if prob > 50 else "X"

def advanced_predict(is_chanle, current_history):
    if len(current_history) < 3: return "TÀI", 53.5, "Đang thu thập dữ liệu..."
    seq = ["T" if x == "T" else "X" for x in current_history]
    pred_pattern, conf_pattern = analyze_patterns(seq)
    prob_mc, pred_mc = monte_carlo_predict(seq)
    final_prob = (conf_pattern * 0.4 + prob_mc * 0.6)
    final_pred = pred_mc if abs(prob_mc - 50) > 8 else pred_pattern
    du_doan = ("CHẴN" if final_pred == "T" else "LẺ") if is_chanle else ("TÀI" if final_pred == "T" else "XỈU")
    loi_khuyen = "🔥 MOMENTUM MẠNH" if final_prob > 62 else "✅ CÂN BẰNG TỐT" if final_prob > 55 else "⚠️ RỦI RO CAO"
    return du_doan, round(final_prob, 1), loi_khuyen

# ==========================================
# 📡 CỔNG MẠNG & API
# ==========================================
@app.route("/api/login", methods=["POST"])
def login():
    key = (request.json or {}).get("key", "").strip()
    if not key or key not in KEYS_DB: return jsonify({"status": "error", "msg": "Key không tồn tại!"})
    if key in LOCKED_KEYS: return jsonify({"status": "error", "msg": "Key đã bị Admin khóa!"})
    return jsonify({"status": "success", "role": KEYS_DB[key], "msg": "Đăng nhập thành công!"})

@app.route("/api/admin", methods=["POST"])
def admin_action():
    data = request.json or {}
    if data.get("admin_key", "") != "hungadmin1122334455": return jsonify({"status": "error", "msg": "Không có quyền!"})
    target = data.get("target_key", "")
    if target not in KEYS_DB or target == "hungadmin1122334455": return jsonify({"status": "error", "msg": "Key lỗi!"})
    if data.get("action", "") == "lock": LOCKED_KEYS.add(target)
    else: LOCKED_KEYS.discard(target)
    return jsonify({"status": "success", "msg": f"Đã xử lý Key: {target}"})

@app.route("/api/scan", methods=["GET"])
def scan_game():
    tool, key = request.args.get("tool", ""), request.args.get("key", "")
    if key not in KEYS_DB or key in LOCKED_KEYS: return jsonify({"status": "auth_error", "msg": "Key bị khóa. Văng!"})
    is_chanle = ("chanle" in tool.lower() or "xd" in tool.lower())
    urls = {"lc79_xd": "https://wcl.tele68.com/v1/chanlefull/sessions", "lc79_tx": "https://wtx.tele68.com/v1/tx/sessions", "betvip_tx": "https://wtx.macminim6.online/v1/tx/sessions", "sunwin_tx": "https://apisunhpt.onrender.com/", "hitclub_md5": "https://jakpotgwab.geightdors.net/glms/v1/notify/taixiu"}
    url = urls.get(tool, "")

    try:
        res = requests.get(url, headers={"User-Agent": "QUANTUM-X-V2"}, timeout=4).json()
        lst = res.get("data", res.get("list", res)) if isinstance(res, dict) else res
        if not isinstance(lst, list):
            phien_thuc = res.get("phien", res.get("id", res.get("referenceId", "AUTO")))
            if str(phien_thuc).isdigit() and "sunwin" not in tool: phien_thuc = str(int(phien_thuc) + 1)
            return jsonify({"status": "success", "data": {"du_doan": "TÀI", "ti_le": 55.5, "loi_khuyen": "QUANTUM X V2", "phien": str(phien_thuc)}})

        lst = sorted(lst, key=get_id)
        if not lst: raise Exception("Trống")

        arr = []
        for s in lst:
            v = str(s).upper()
            if is_chanle: arr.append("T" if any(x in v for x in ["CHẴN", "CHAN", "C", "0", "EVEN"]) else "X")
            else: arr.append("T" if any(x in v for x in ["TAI", "TÀI", "BIG"]) else "X")

        HISTORY.clear(); HISTORY.extend(arr[-40:])
        phien_hien_tai = str(get_id(lst[-1]) + 1)

        m = re.search(r"[0-9a-f]{32}", str(lst[-1]).lower())
        if m and ("md5" in tool.lower() or "sunwin" in tool.lower()):
            return jsonify({"status": "success", "data": {"type": "md5", "md5_str": m.group(0), "phien": phien_hien_tai}})

        # Tính nhanh gửi về Web ép Web đếm 20 giây
        du_doan, ti_le, loi_khuyen = advanced_predict(is_chanle, list(HISTORY))
        return jsonify({"status": "success", "data": {"type": "quantum_v2", "du_doan": du_doan, "ti_le": ti_le, "loi_khuyen": loi_khuyen, "phien": phien_hien_tai}})

    except Exception as e:
        return jsonify({"status": "success", "data": {"du_doan": "TÀI", "ti_le": 52.0, "loi_khuyen": "QUANTUM V2 FALLBACK", "phien": "#" + str(random.randint(100000, 999999))}})

@app.route("/")
def home():
    try: return send_file(os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html"))
    except: return "LỖI: Không tìm thấy file index.html"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
    
