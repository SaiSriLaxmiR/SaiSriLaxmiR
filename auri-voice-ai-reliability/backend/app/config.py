from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "Auri API"
    demo_mode: bool = True
    default_judge_model: str = "demo-judge-v1"


settings = Settings()
