import os


BOT_TOKEN = os.environ.get("BOT_TOKEN", None)
DATABASE_RECIPE = os.environ.get("DB_RECIPE", None)
DATABASE_RECIPE = "postgresql://zhalgas@localhost:5432/postgres"
