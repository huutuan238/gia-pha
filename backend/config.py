import os


class Config:
    # SQLALCHEMY_DATABASE_URI = (
    #     f"postgresql://{os.getenv('DB_USER')}:"
    #     f"{os.getenv('DB_PASSWORD')}@"
    #     f"{os.getenv('DB_HOST')}:"
    #     f"{os.getenv('DB_PORT')}/"
    #     f"{os.getenv('DB_NAME')}"
    # )
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
