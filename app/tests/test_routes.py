from fastapi.testclient import TestClient
from main import app
import pytest
from httpx import AsyncClient

client = TestClient(app)


# use testclient to simulate http request and response
# def test_read_main():
#     response = client.get("/")
#     assert response.status_code == 200
#     assert response.json() == {"Server is running"}

# # use pytest-asyncio to test routes
# @pytest.mark.asyncio
# async with AsyncClient(app=app, base_url="http://test")as ac:
