from typing import Optional

from pydantic import BaseSettings, Field


class Config(BaseSettings):
    antigate_api_key: Optional[str] = Field(description='API key for captcha solving')

    class Config:
        case_sensitive = True
        env_file = '.env'
        env_file_encoding = 'utf-8'


config = Config()
