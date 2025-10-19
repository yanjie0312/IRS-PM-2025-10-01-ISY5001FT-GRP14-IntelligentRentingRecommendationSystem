import os
from dotenv import load_dotenv

def get_database_url():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(current_dir, '.env.googlecloudservice')
    '''从环境变量读取数据库url'''
    load_dotenv(env_path)
    username = os.getenv('DB_USERNAME')
    password = os.getenv('DB_PASSWORD')
    host = os.getenv('DB_HOST')
    port = os.getenv('DB_PORT')
    database = os.getenv('DB_DATABASE')
    db_url = f"postgresql://{username}:{password}@{host}:{port}/{database}"
    print(f"数据库URL: {db_url}")
    return db_url

if __name__ == "__main__":
    print(os.getcwd())
    get_database_url()