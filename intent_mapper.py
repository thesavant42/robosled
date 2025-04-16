# intent_mapper.py
# Author: savant42

MID = 1500
DEADZONE = 50

MODE_THRESHOLDS = {
    "attract": 50652,
    "dev": 50140,
    "stealth": 0
}

_last_intent = None

def normalize_channel(value):
    if value < 1000 or value > 2000:
        return 0
    return int((value - 1500) / 5)

def map_ibus_to_intent(ch_data, verbose=False):
    global _last_intent

    intent = {}

    intent["throttle"] = abs(normalize_channel(ch_data.get(3, 1500)))

    x = normalize_channel(ch_data.get(4, 1500))
    intent["pivot"] = "left" if x < -DEADZONE else "right" if x > DEADZONE else None

    steer = normalize_channel(ch_data.get(1, 1500))
    intent["veer"] = "left" if steer < -DEADZONE else "right" if steer > DEADZONE else None

    direction = normalize_channel(ch_data.get(2, 1500))
    intent["direction"] = "reverse" if direction < -DEADZONE else "forward" if direction > DEADZONE else None

    intent["brake"] = ch_data.get(5, 0) > 1500
    intent["swb"] = ch_data.get(6, 0)

    ch7 = ch_data.get(7, 0)
    if abs(ch7 - MODE_THRESHOLDS["attract"]) < 20:
        intent["mode"] = "attract"
    elif abs(ch7 - MODE_THRESHOLDS["dev"]) < 20:
        intent["mode"] = "dev"
    else:
        intent["mode"] = "stealth"

    if verbose or intent["mode"] == "dev":
        for ch in range(8, 17):
            intent[f"ch{ch}"] = ch_data.get(ch, 0)

    if verbose or intent["mode"] == "dev" or intent != _last_intent:
        print("\n🎮 Interpreted Robot Intent:")
        for key in ["direction", "throttle", "veer", "pivot", "brake", "mode", "swb"]:
            print(f"{key:>10}: {intent.get(key)}")
        if verbose or intent["mode"] == "dev":
            for ch in range(8, 17):
                key = f"ch{ch}"
                if key in intent:
                    print(f"{key:>10}: {intent[key]}")
        _last_intent = intent.copy()

    return intent
