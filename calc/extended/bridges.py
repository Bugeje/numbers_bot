from calc import extract_base


def calculate_bridge(a: str, b: str) -> int:
    return abs(extract_base(a) - extract_base(b))


def calculate_bridges(core_profile: dict) -> dict:
    return {
        "expression_soul": calculate_bridge(core_profile["expression"], core_profile["soul"]),
        "soul_personality": calculate_bridge(core_profile["soul"], core_profile["personality"]),
        "life_soul": calculate_bridge(core_profile["life_path"], core_profile["soul"]),
        "life_personality": calculate_bridge(
            core_profile["life_path"], core_profile["personality"]
        ),
    }
