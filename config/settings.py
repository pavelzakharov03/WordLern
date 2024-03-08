from pydantic_settings import BaseSettings


class AppSetting(BaseSettings):
    log_level: str = 'DEBUG'
    db: str = ''
    secret_key: str = ''
    api_key: str = ''

    class Config:
        env_prefix = 'APP_'


app_settings = AppSetting()
