import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "5884860755:AAFGzQu-UPsRAScbnG35n26j1uK74NRSLMA")
API_ID = int(os.environ.get("API_ID", "9248715"))
API_HASH = os.environ.get("API_HASH", "a9c1288681c2d3265175ff96c619d064")
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1001893761721"))
AUTH_USERS = set(int(x) for x in os.environ.get("AUTH_USERS", "5784013817").split())
DB_URL = os.environ.get("DB_URL", "mongodb+srv://sharkgame:shark0game@cluster0.oprvkgn.mongodb.net/?retryWrites=true&w=majority")
DB_NAME = os.environ.get("DB_NAME", "BroadcastBot")
BROADCAST_AS_COPY = bool(os.environ.get("BROADCAST_AS_COPY", False))
