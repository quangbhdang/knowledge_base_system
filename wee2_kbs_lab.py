# =====================================================================
# COSC3009 – Knowledge-Based Systems Tutorial
# Technical Support Assistant (Standalone, no external libraries)
# =====================================================================
# Layers:
#   Domain knowledge: KNOWLEDGE["advice"], KNOWLEDGE["policy"]
#   Inference knowledge: RULES (conditions -> conclusion)
#   Task knowledge: main() obtains input, translates, infers, presents
# Run:
#   python kbs_tech_support.py
# =====================================================================

import re
from typing import Dict, List, Any

# -----------------------------
# Domain knowledge
# -----------------------------
KNOWLEDGE: Dict[str, Any] = {
    "advice": {
        # Connectivity
        "wifi": "Check airplane mode is off. Toggle Wi-Fi off then on. Reconnect to your network. Restart the router.",
        "wifi_drops": "If Wi-Fi drops often: move closer to the router. Forget the network then reconnect. Try another channel.",
        "no_internet": "Connected but no internet: flush DNS and reboot router. Test with another device to isolate the issue.",
        "ethernet": "Check the cable and port. Try another cable. Verify adapter lights.",
        "vpn": "Disconnect VPN and test again. Some VPNs block local network access.",
        "dns": "Use automatic DNS or set 8.8.8.8 and 1.1.1.1 for a quick test.",

        # Power and battery
        "battery": "Lower screen brightness. Close background apps. Turn on battery saver. Disable unused radios when idle.",
        "charging": "Use the original charger. Try a different outlet. Inspect the cable and port for debris.",
        "battery_health": "Check battery health in system settings. Replace the battery if capacity is very low.",

        # Performance and storage
        "slow": "Restart the device. Close heavy apps. Update the system. Scan for malware.",
        "storage_low": "Free space is low: remove large downloads, empty recycle bin, uninstall unused apps.",
        "high_cpu": "CPU is high: end runaway tasks. On Windows use Task Manager. On Mac use Activity Monitor.",
        "high_memory": "RAM pressure is high: close memory-heavy apps and consider more RAM.",

        # Heat and fans
        "overheating": "Improve airflow. Do not block vents. Use a cooling pad if available.",
        "fan_noise": "Fan loud: clean dust from vents. Stop background tasks that cause heat.",

        # Audio, mic, webcam
        "audio_none": "No sound: select the correct output device. Unmute. Test with headphones.",
        "mic_none": "Mic not working: check app permissions and input device.",
        "webcam_none": "Camera not detected: grant app permissions and close other apps using the camera.",

        # Display
        "black_screen": "Black screen but power on: force restart. Try external display. Adjust brightness keys.",
        "flicker": "Screen flicker: update graphics driver. Try a different refresh rate.",

        # Bluetooth and USB
        "bluetooth": "Toggle Bluetooth off and on. Remove device and re-pair near the computer.",
        "usb": "USB not recognized: try a different port, reboot, then reinstall USB drivers if needed.",

        # Printer
        "printer_offline": "Power cycle the printer. Ensure same network as the computer. Re-add the printer.",
        "paper_jam": "Remove jammed paper. Reload correctly. Check rollers.",

        # Updates and startup
        "update": "Install pending updates and restart.",
        "startup": "Slow startup: reduce startup apps. Windows: Task Manager Startup tab. Mac: Login Items.",

        # Generic
        "diagnose": "Describe your device issue in one sentence. I will recommend a next step."
    },
    "policy": {
        "dns_windows": "Windows DNS flush: ipconfig /flushdns",
        "dns_mac": "Mac DNS flush: sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder",
        "audio_privacy_windows": "Windows: Settings > Privacy > Microphone > Allow apps to access your microphone.",
        "audio_privacy_mac": "Mac: System Settings > Privacy & Security > Microphone.",
        "camera_privacy_windows": "Windows: Settings > Privacy > Camera.",
        "camera_privacy_mac": "Mac: System Settings > Privacy & Security > Camera."
    }
}

# -----------------------------
# Inference knowledge – rules
# -----------------------------
RULES: List[Dict[str, Any]] = [
    # Connectivity
    {"id": "wifi_drops_windows",
     "conditions": [{"attribute": "wifi", "op": "eq", "value": True},
                    {"attribute": "drops", "op": "eq", "value": True},
                    {"attribute": "os", "op": "eq", "value": "windows"}],
     "conclusion": "Wi-Fi drops on Windows. Forget the network then reconnect. Update the driver. " +
                   KNOWLEDGE["policy"]["dns_windows"]},

    {"id": "wifi_drops_mac",
     "conditions": [{"attribute": "wifi", "op": "eq", "value": True},
                    {"attribute": "drops", "op": "eq", "value": True},
                    {"attribute": "os", "op": "eq", "value": "mac"}],
     "conclusion": "Wi-Fi drops on Mac. Forget the network then reconnect. Reset DHCP lease. " +
                   KNOWLEDGE["policy"]["dns_mac"]},

    {"id": "wifi_no_internet",
     "conditions": [{"attribute": "wifi", "op": "eq", "value": True},
                    {"attribute": "no_internet", "op": "eq", "value": True}],
     "conclusion": KNOWLEDGE["advice"]["no_internet"]},

    {"id": "ethernet_down",
     "conditions": [{"attribute": "ethernet", "op": "eq", "value": True},
                    {"attribute": "no_internet", "op": "eq", "value": True}],
     "conclusion": KNOWLEDGE["advice"]["ethernet"]},

    {"id": "vpn_blocks",
     "conditions": [{"attribute": "vpn", "op": "eq", "value": True},
                    {"attribute": "cannot_access_local", "op": "eq", "value": True}],
     "conclusion": "VPN may block local access. Disconnect VPN and retest. Add a split tunnel if needed."},

    # Battery and power
    {"id": "battery_fast_drain",
     "conditions": [{"attribute": "battery", "op": "eq", "value": True},
                    {"attribute": "drains", "op": "eq", "value": True}],
     "conclusion": "Battery drains fast. " + KNOWLEDGE["advice"]["battery"] + " Check battery health in settings."},

    {"id": "charging_issue",
     "conditions": [{"attribute": "charging", "op": "eq", "value": True},
                    {"attribute": "not_charging", "op": "eq", "value": True}],
     "conclusion": KNOWLEDGE["advice"]["charging"]},

    # Performance and storage
    {"id": "slow_low_storage",
     "conditions": [{"attribute": "slow", "op": "eq", "value": True},
                    {"attribute": "storage_low", "op": "eq", "value": True}],
     "conclusion": "System slow and storage low. " + KNOWLEDGE["advice"]["storage_low"]},

    {"id": "slow_high_cpu",
     "conditions": [{"attribute": "slow", "op": "eq", "value": True},
                    {"attribute": "high_cpu", "op": "eq", "value": True}],
     "conclusion": KNOWLEDGE["advice"]["high_cpu"]},

    {"id": "slow_high_memory",
     "conditions": [{"attribute": "slow", "op": "eq", "value": True},
                    {"attribute": "high_memory", "op": "eq", "value": True}],
     "conclusion": KNOWLEDGE["advice"]["high_memory"]},

    # Heat and fans
    {"id": "overheating_with_fan",
     "conditions": [{"attribute": "overheating", "op": "eq", "value": True},
                    {"attribute": "fan_loud", "op": "eq", "value": True}],
     "conclusion": KNOWLEDGE["advice"]["overheating"] + " " + KNOWLEDGE["advice"]["fan_noise"]},

    # Audio, mic, webcam
    {"id": "no_sound_after_update",
     "conditions": [{"attribute": "audio_none", "op": "eq", "value": True},
                    {"attribute": "after_update", "op": "eq", "value": True}],
     "conclusion": KNOWLEDGE["advice"]["audio_none"] + " Reinstall the audio driver if the issue started after an update."},

    {"id": "mic_permissions_windows",
     "conditions": [{"attribute": "mic_none", "op": "eq", "value": True},
                    {"attribute": "os", "op": "eq", "value": "windows"}],
     "conclusion": KNOWLEDGE["advice"]["mic_none"] + " " + KNOWLEDGE["policy"]["audio_privacy_windows"]},

    {"id": "mic_permissions_mac",
     "conditions": [{"attribute": "mic_none", "op": "eq", "value": True},
                    {"attribute": "os", "op": "eq", "value": "mac"}],
     "conclusion": KNOWLEDGE["advice"]["mic_none"] + " " + KNOWLEDGE["policy"]["audio_privacy_mac"]},

    {"id": "camera_permissions_windows",
     "conditions": [{"attribute": "webcam_none", "op": "eq", "value": True},
                    {"attribute": "os", "op": "eq", "value": "windows"}],
     "conclusion": KNOWLEDGE["advice"]["webcam_none"] + " " + KNOWLEDGE["policy"]["camera_privacy_windows"]},

    {"id": "camera_permissions_mac",
     "conditions": [{"attribute": "webcam_none", "op": "eq", "value": True},
                    {"attribute": "os", "op": "eq", "value": "mac"}],
     "conclusion": KNOWLEDGE["advice"]["webcam_none"] + " " + KNOWLEDGE["policy"]["camera_privacy_mac"]},

    # Display
    {"id": "black_screen_running",
     "conditions": [{"attribute": "black_screen", "op": "eq", "value": True},
                    {"attribute": "power_on", "op": "eq", "value": True}],
     "conclusion": KNOWLEDGE["advice"]["black_screen"]},

    # Bluetooth and USB
    {"id": "bt_pairing_issue",
     "conditions": [{"attribute": "bluetooth", "op": "eq", "value": True},
                    {"attribute": "pairing_issue", "op": "eq", "value": True}],
     "conclusion": KNOWLEDGE["advice"]["bluetooth"]},

    {"id": "usb_not_recognized",
     "conditions": [{"attribute": "usb", "op": "eq", "value": True},
                    {"attribute": "not_recognized", "op": "eq", "value": True}],
     "conclusion": KNOWLEDGE["advice"]["usb"]},

    # Printer
    {"id": "printer_offline",
     "conditions": [{"attribute": "printer", "op": "eq", "value": True},
                    {"attribute": "offline", "op": "eq", "value": True}],
     "conclusion": KNOWLEDGE["advice"]["printer_offline"]},

    {"id": "printer_jam",
     "conditions": [{"attribute": "printer", "op": "eq", "value": True},
                    {"attribute": "paper_jam", "op": "eq", "value": True}],
     "conclusion": KNOWLEDGE["advice"]["paper_jam"]},

    # Updates and startup
    {"id": "updates_pending",
     "conditions": [{"attribute": "update", "op": "eq", "value": True},
                    {"attribute": "pending", "op": "eq", "value": True}],
     "conclusion": KNOWLEDGE["advice"]["update"]},

    {"id": "slow_startup",
     "conditions": [{"attribute": "startup", "op": "eq", "value": True},
                    {"attribute": "slow", "op": "eq", "value": True}],
     "conclusion": KNOWLEDGE["advice"]["startup"]},

    # Generic error code
    {"id": "error_code_present",
     "conditions": [{"attribute": "error_code", "op": "exists"}],
     "conclusion": "An error code was detected. Search the vendor support page for that exact code and include full error text."},
]

# -----------------------------
# Inference engine
# -----------------------------
class InferenceEngine:
    def __init__(self, rules: List[Dict[str, Any]]):
        self.rules = rules

    def infer(self, entities: Dict[str, Any]) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for rule in self.rules:
            if self._rule_applies(rule, entities):
                results.append({"rule_id": rule["id"], "conclusion": rule["conclusion"]})
        return results

    def _rule_applies(self, rule: Dict[str, Any], entities: Dict[str, Any]) -> bool:
        for cond in rule.get("conditions", []):
            if not self._check(cond, entities):
                return False
        return True

    def _check(self, cond: Dict[str, Any], entities: Dict[str, Any]) -> bool:
        key = cond.get("attribute")
        op = cond.get("op", "eq")
        expect = cond.get("value", None)

        if op == "exists":
            return key in entities

        if key not in entities:
            return False

        value = entities[key]

        if op == "eq":
            return value == expect
        if op == "neq":
            return value != expect
        if op == "in":
            return value in expect
        if op == "gt":
            try:
                return float(value) > float(expect)
            except Exception:
                return False
        if op == "lt":
            try:
                return float(value) < float(expect)
            except Exception:
                return False
        if op == "contains":
            if isinstance(value, str) and isinstance(expect, str):
                return expect in value
            if isinstance(value, list):
                return expect in value
            return False

        return False

# -----------------------------
# NLP translator
# -----------------------------
class NLPProcessor:
    OS_WORDS = {
        "windows": ["windows", "win11", "win10", "win 11", "win 10"],
        "mac": ["mac", "macos", "mac os", "osx", "os x"],
        "linux": ["linux", "ubuntu", "debian", "fedora"]
    }

    def process_query(self, text: str):
        t = text.strip().lower()
        entities: Dict[str, Any] = {}
        intent = "diagnose"

        # OS
        for os_name, words in self.OS_WORDS.items():
            if any(w in t for w in words):
                entities["os"] = os_name

        # Connectivity
        if any(w in t for w in ["wifi", "wi-fi", "wireless"]):
            entities["wifi"] = True
        if any(w in t for w in ["keeps dropping", "drops", "unstable"]):
            entities["drops"] = True
        if "no internet" in t or "connected no internet" in t:
            entities["no_internet"] = True
        if "ethernet" in t or "lan" in t:
            entities["ethernet"] = True
        if "vpn" in t:
            entities["vpn"] = True
        if "cannot access local" in t or "cannot reach local" in t:
            entities["cannot_access_local"] = True
        if "dns" in t:
            entities["dns"] = True

        # Battery and charging
        if "battery" in t:
            entities["battery"] = True
        if "drain" in t or "drains" in t or "dies fast" in t:
            entities["drains"] = True
        if "charge" in t or "charging" in t:
            entities["charging"] = True
        if "not charging" in t or "won't charge" in t or "does not charge" in t:
            entities["not_charging"] = True

        # Performance and storage
        if "slow" in t or "lag" in t or "sluggish" in t:
            entities["slow"] = True
        if any(p in t for p in ["full disk", "disk full", "storage full", "low storage", "no space"]):
            entities["storage_low"] = True
        if "high cpu" in t or "100% cpu" in t or "cpu usage" in t:
            entities["high_cpu"] = True
        if "high memory" in t or "memory usage" in t or "out of memory" in t:
            entities["high_memory"] = True
        if "startup" in t or "boot" in t or "start up" in t:
            entities["startup"] = True

        # Heat and fans
        if "overheat" in t or "hot" in t or "too warm" in t:
            entities["overheating"] = True
        if "fan loud" in t or "loud fan" in t or "fan noise" in t:
            entities["fan_loud"] = True

        # Audio, mic, webcam
        if "no sound" in t or "sound not working" in t or "audio not working" in t:
            entities["audio_none"] = True
        if "after update" in t or "since update" in t:
            entities["after_update"] = True
        if "mic" in t or "microphone" in t:
            if "not working" in t or "no mic" in t or "not detected" in t:
                entities["mic_none"] = True
        if "camera" in t or "webcam" in t:
            if "not detected" in t or "not working" in t or "cannot find" in t:
                entities["webcam_none"] = True

        # Display
        if "black screen" in t or "screen is black" in t:
            entities["black_screen"] = True
            if "power" in t or "running" in t or "fans on" in t:
                entities["power_on"] = True
        if "flicker" in t or "flickering" in t:
            entities["flicker"] = True

        # Bluetooth and USB
        if "bluetooth" in t:
            entities["bluetooth"] = True
        if "pair" in t or "pairing" in t or "connect headphones" in t:
            entities["pairing_issue"] = True
        if "usb" in t:
            entities["usb"] = True
            if "not recognized" in t or "not recognised" in t:
                entities["not_recognized"] = True

        # Printer
        if "printer" in t:
            entities["printer"] = True
            if "offline" in t:
                entities["offline"] = True
            if "paper jam" in t or "jam" in t:
                entities["paper_jam"] = True

        # Updates
        if "update" in t or "updates" in t:
            entities["update"] = True
            if "pending" in t or "available" in t:
                entities["pending"] = True

        # Error code
        m = re.search(r"(error\s+code\s*[:#]?\s*|code\s*[:#]?\s*)([a-z0-9\-x]+)", t)
        if m:
            entities["error_code"] = m.group(2)

        return {"intent": "diagnose", "entities": entities}

# -----------------------------
# Knowledge lookup fallback
# -----------------------------
class KnowledgeBaseQuery:
    def __init__(self, advice: Dict[str, str]):
        self.advice = advice

    def lookup(self, entities: Dict[str, Any]) -> List[str]:
        hits: List[str] = []
        priority = [
            "wifi_drops", "no_internet", "ethernet", "battery", "charging",
            "overheating", "fan_noise", "audio_none", "mic_none", "webcam_none",
            "black_screen", "flicker", "bluetooth", "usb", "printer_offline",
            "paper_jam", "slow", "storage_low", "high_cpu", "high_memory", "startup", "update"
        ]
        for key in priority:
            if key in entities and key in self.advice:
                hits.append(self.advice[key])
        if not hits and "diagnose" in self.advice:
            hits.append(self.advice["diagnose"])
        return hits

# -----------------------------
# Presenter and controller
# -----------------------------
def present_answer(structured, conclusions, advice):
    print("\nStructured:", structured)
    if conclusions:
        print("Why:")
        for c in conclusions:
            print(f" - rule: {c['rule_id']}")
    print("Answer:")
    if conclusions:
        for c in conclusions:
            print(f" - {c['conclusion']}")
    for a in advice:
        print(f" - {a}")

def main():
    print("Technical Support Knowledge-Based System")
    print("Type one sentence. Type 'help' for examples. Type 'quit' to exit.")
    nlp = NLPProcessor()
    engine = InferenceEngine(RULES)
    kbq = KnowledgeBaseQuery(KNOWLEDGE["advice"])

    EXAMPLES = [
        "wifi keeps dropping on windows",
        "connected but no internet on mac",
        "battery drains fast on my laptop",
        "charging but not charging actually",
        "computer very slow disk almost full",
        "cpu usage high and fan noise",
        "laptop is hot and fan loud",
        "no sound after update",
        "mic not working on windows",
        "webcam not detected on mac",
        "screen is black but laptop running",
        "bluetooth cannot pair headphones",
        "usb device not recognized",
        "printer is offline",
        "printer paper jam",
        "updates pending please advise",
        "startup is slow",
        "error code 0x80070005"
    ]

    while True:
        text = input("\n> ").strip()
        if not text:
            continue
        lo = text.lower()
        if lo in {"quit", "exit"}:
            print("Goodbye.")
            break
        if lo in {"help", "examples"}:
            print("\nTry these:")
            for e in EXAMPLES:
                print(" -", e)
            continue

        structured = nlp.process_query(text)
        entities = structured["entities"]
        conclusions = engine.infer(entities)

        extra_advice = kbq.lookup(entities) if not conclusions else []
        present_answer(structured, conclusions, extra_advice)

if __name__ == "__main__":
    main()
