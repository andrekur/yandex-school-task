import uvicorn
from api.api_start import app
from dotenv import dotenv_values

CONFIG = dotenv_values('_CI/.env')

# main start method
if __name__ == '__main__':
    uvicorn.run(
        app,
        host=CONFIG['API_SERVER_HOST'],
        port=int(CONFIG['API_SERVER_PORT']),
        debug=True
    )
