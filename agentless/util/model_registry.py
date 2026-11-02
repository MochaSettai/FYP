"""Single source of truth for supported models."""

# price = USD per 1M tokens (input, output)
# supports_temperature = whether sending `temperature` actually has an effect / is allowed
MODELS = {
    # --- legacy (kept so Phase 0 changes no behaviour; remove in Phases 1-3) ---
    "gpt-4o-2024-05-13":          {"backend": "openai",    "supports_temperature": True,  "price": (5.00, 15.00)},
    "gpt-4o-mini-2024-07-18":     {"backend": "openai",    "supports_temperature": True,  "price": (0.15, 0.60)},
    "claude-3-5-sonnet-20241022": {"backend": "anthropic", "supports_temperature": True,  "price": (3.00, 15.00)},
    "deepseek-coder":             {"backend": "deepseek",  "supports_temperature": True,  "price": (0.14, 0.28)},

    # --- current (verified 2026-11-02) ---
    "deepseek-flash":     {"backend": "deepseek",  "supports_temperature": False, "price": (0.30, 1.20)},   # peak price
    "deepseek-v4-pro":    {"backend": "deepseek",  "supports_temperature": False, "price": (1.32, 3.96)},   # peak price
    "gpt-6-astra":        {"backend": "openai",    "supports_temperature": False, "price": (10.00, 50.00)},
    "gpt-6.1-sol":        {"backend": "openai",    "supports_temperature": False, "price": (2.00, 10.00)},
    "gpt-6.1-terra":      {"backend": "openai",    "supports_temperature": False, "price": (1.00, 5.00)},
    "gpt-6-luna":         {"backend": "openai",    "supports_temperature": False, "price": (0.10, 0.50)},
    "claude-opus-5-5":    {"backend": "anthropic", "supports_temperature": False, "price": (4.00, 20.00)},
    "claude-sonnet-5-5":  {"backend": "anthropic", "supports_temperature": False, "price": (2.00, 10.00)},
    "claude-haiku-5-5":   {"backend": "anthropic", "supports_temperature": False, "price": (0.10, 0.50)},
}

DEFAULT_MODEL = "gpt-4o-2024-05-13"   # unchanged for now; pick a new default after the phase decisions
BACKENDS = sorted({m["backend"] for m in MODELS.values()})


def supports_temperature(model: str) -> bool:
    # Unknown models keep the old behaviour (send temperature)
    return MODELS.get(model, {}).get("supports_temperature", True)


def get_price(model: str):
    return MODELS[model]["price"]


def check_backend(model: str, backend: str):
    expected = MODELS[model]["backend"]
    assert backend == expected, f"Model {model} requires `--backend {expected}` (got {backend})"