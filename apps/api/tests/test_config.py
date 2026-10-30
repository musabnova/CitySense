import os
from apps.api.core.config import Settings

def test_settings_validation():
    # Test default values
    settings = Settings()
    assert settings.PROJECT_NAME == "CitySense"
    assert settings.EMBEDDING_DIM == 768
    assert settings.API_PORT == 8000

    # Test override with custom mock env values
    custom = Settings(
        PROJECT_NAME="CitySense-Test",
        API_PORT=9000,
        EMBEDDING_DIM=768,
        ENV="testing"
    )
    assert custom.PROJECT_NAME == "CitySense-Test"
    assert custom.API_PORT == 9000
    assert custom.ENV == "testing"
    print("TASK-002: Settings validation test passed successfully.")

if __name__ == "__main__":
    test_settings_validation()

