from fastapi.exceptions import ValidationException
from fastapi.testclient import TestClient
from app.main import app
from pytest import raises
from app.errors import *

client = TestClient(app)


