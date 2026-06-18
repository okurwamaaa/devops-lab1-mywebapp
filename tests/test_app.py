# flake8: noqa
import os
import sys
from unittest.mock import patch, MagicMock
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_health_alive(client):
    rv = client.get('/health/alive')
    assert rv.status_code == 200
    assert b'OK' in rv.data


@patch('app.get_db_connection')
def test_health_ready_success(mock_get_db, client):
    mock_conn = MagicMock()
    mock_get_db.return_value = mock_conn
    rv = client.get('/health/ready')
    assert rv.status_code == 200


def test_index_html(client):
    rv = client.get('/', headers={'Accept': 'text/html'})
    assert rv.status_code == 200
    assert b'mywebapp API Endpoints' in rv.data


@patch('app.get_db_connection')
def test_get_items(mock_get_db, client):
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_get_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cur
    mock_cur.fetchall.return_value = [(1, 'Laptop')]

    rv = client.get('/items')
    assert rv.status_code == 200