import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings:
    app_name = "ComicCraft"
    mock_ai = os.getenv("MOCK_AI", "true").lower() == "true"
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    hf_api_key = os.getenv("HF_API_KEY")
    gemini_flash_model = os.getenv("GEMINI_FLASH_MODEL", "gemini-3.8-flash")
    gemini_pro_model = os.getenv("GEMINI_PRO_MODEL", "gemini-3.8-flash")
    hf_image_model = os.getenv(
        "HF_IMAGE_MODEL",
        "runwayml/stable-diffusion-v1-5"
    )
    hf_provider = os.getenv("HF_PROVIDER", "auto")
    panel_count = int(os.getenv("PANEL_COUNT", "5"))
    image_width = int(os.getenv("IMAGE_WIDTH", "768"))
    image_height = int(os.getenv("IMAGE_HEIGHT", "768"))
    image_steps = int(os.getenv("IMAGE_STEPS", "25"))
    image_guidance_scale = float(
        os.getenv("IMAGE_GUIDANCE_SCALE", "7.5")
    )
    static_dir = BASE_DIR / "static"
    templates_dir = BASE_DIR / "templates"

    @property
    def panels_dir(self):
        return self.static_dir / "panels"

    @property
    def exports_dir(self):
        return self.static_dir / "exports"

    def ensure_directories(self):
        self.static_dir.mkdir(parents=True, exist_ok=True)
        self.panels_dir.mkdir(parents=True, exist_ok=True)
        self.exports_dir.mkdir(parents=True, exist_ok=True)


_settings = None

def get_settings():
    global _settings
    if _settings is None:
        _settings = Settings()
        _settings.ensure_directories()
    return _settings
