import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from flask import Flask
from app import create_app

@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'DATABASE': 'test_words.db'
    })
    with app.app_context():
        app.db.setup_tables(app.db.cursor())
    yield app
    with app.app_context():
        app.db.close()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def setup_database(app):
    with app.app_context():
        cursor = app.db.cursor()
        cursor.execute('DELETE FROM words')
        cursor.execute('DELETE FROM word_reviews')
        cursor.execute('DELETE FROM word_groups')
        cursor.execute('DELETE FROM groups')
        cursor.execute('''
            INSERT INTO words (id, kanji, romaji, english, parts) 
            VALUES (1, '漢字', 'kanji', 'Chinese characters', '[]')
        ''')
        cursor.execute('''
            INSERT INTO word_reviews (word_id, correct_count, wrong_count) 
            VALUES (1, 0, 0)
        ''')
        cursor.execute('''
            INSERT INTO groups (id, name) 
            VALUES (1, 'Test Group')
        ''')
        cursor.execute('''
            INSERT INTO word_groups (word_id, group_id) 
            VALUES (1, 1)
        ''')
        app.db.commit()

def test_get_words(client, setup_database):
    response = client.get('/words')
    assert response.status_code == 200
    assert 'words' in response.get_json()

def test_get_word(client, setup_database):
    response = client.get('/words/1')
    assert response.status_code == 200
    assert response.get_json()['word']['id'] == 1

def test_create_word(client, setup_database):
    response = client.post('/words', json={
        'kanji': '新しい漢字',
        'romaji': 'atarashii kanji',
        'english': 'new kanji',
        'parts': [{'kanji': '新', 'romaji': ['atarashii']}, {'kanji': '字', 'romaji': ['kanji']}]
    })
    assert response.status_code == 200 or response.status_code == 201
    assert response.get_json()['message'] == 'Word added successfully'

def test_update_word(client, setup_database):
    response = client.put('/words/1', json={
        'kanji': '更新された漢字',
        'romaji': 'koushin sareta kanji',
        'english': 'updated kanji',
        'parts': [{'kanji': '更新', 'romaji': ['koushin']}, {'kanji': 'された', 'romaji': ['sareta']}, {'kanji': '漢字', 'romaji': ['kanji']}]
    })
    assert response.status_code == 200
    assert response.get_json()['message'] == 'Word updated successfully'

def test_delete_word(client, setup_database):
    response = client.delete('/words/1')
    assert response.status_code == 200
    assert response.get_json()['message'] == 'Word deleted successfully'

def test_get_groups(client, setup_database):
    response = client.get('/groups')
    assert response.status_code == 200
    assert 'groups' in response.get_json()

def test_get_group(client, setup_database):
    response = client.get('/groups/1')
    assert response.status_code == 200
    assert response.get_json()['id'] == 1

def test_create_group(client, setup_database):
    response = client.post('/groups', json={'name': 'New Test Group'})
    assert response.status_code == 201
    assert response.get_json()['message'] == 'Group created successfully'

def test_update_group(client, setup_database):
    response = client.put('/groups/1', json={'name': 'Updated Test Group'})
    assert response.status_code == 200
    assert response.get_json()['message'] == 'Group updated successfully'

def test_delete_group(client, setup_database):
    response = client.delete('/groups/1')
    assert response.status_code == 200
    assert response.get_json()['message'] == 'Group deleted successfully'

def test_get_study_sessions(client, setup_database):
    response = client.get('/api/study-sessions')
    assert response.status_code == 200
    assert 'items' in response.get_json()

def test_create_study_session(client, setup_database):
    response = client.post('/api/study-sessions', json={
        'group_id': 1,
        'activity_id': 1
    })
    assert response.status_code == 400  # Assuming no activity with ID 1 exists initially

def test_get_dashboard_recent_session(client, setup_database):
    response = client.get('/dashboard/recent-session')
    assert response.status_code == 200

def test_get_dashboard_stats(client, setup_database):
    response = client.get('/dashboard/stats')
    assert response.status_code == 200