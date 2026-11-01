import pytest
import sqlite3
import os
from registration.registration import create_db, add_user, authenticate_user, display_users

@pytest.fixture(scope="module")
def setup_database():
    """Фикстура для настройки базы данных перед тестами и её очистки после."""
    create_db()
    yield
    try:
        os.remove('users.db')
    except PermissionError:
        pass

@pytest.fixture
def connection():
    """Фикстура для получения соединения с базой данных и его закрытия после теста."""
    conn = sqlite3.connect('users.db')
    yield conn
    conn.close()


def test_create_db(setup_database, connection):
    """Тест создания базы данных и таблицы пользователей."""
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    table_exists = cursor.fetchone()
    assert table_exists, "Таблица 'users' должна существовать в базе данных."

def test_add_new_user(setup_database, connection):
    """Тест добавления нового пользователя."""
    add_user('testuser', 'testuser@example.com', 'password123')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username='testuser';")
    user = cursor.fetchone()
    assert user, "Пользователь должен быть добавлен в базу данных."

def test_add_duplicate_user(setup_database, connection):
    """Тест добавления пользователя с существующим логином."""
    add_user('testuser', 'testuser@example.com', 'password123')
    result = add_user('testuser', 'another@example.com', 'different123')
    assert result is False, "Добавление дубликата пользователя должно вернуть False."

def test_authenticate_user_success(setup_database, connection):
    """Тест успешной аутентификации пользователя."""
    add_user('testuser', 'testuser@example.com', 'password123')
    result = authenticate_user('testuser', 'password123')
    assert result is True, "Аутентификация с правильными данными должна быть успешной."

def test_authenticate_nonexistent_user(setup_database, connection):
    """Тест аутентификации несуществующего пользователя."""
    result = authenticate_user('nonexistent', 'password123')
    assert result is False, "Аутентификация несуществующего пользователя должна вернуть False."

def test_authenticate_wrong_password(setup_database, connection):
    """Тест аутентификации пользователя с неправильным паролем."""
    add_user('testuser', 'testuser@example.com', 'password123')
    result = authenticate_user('testuser', 'wrongpassword')
    assert result is False, "Аутентификация с неправильным паролем должна вернуть False."

def test_display_users(setup_database, connection, capsys):
    """Тест отображения списка пользователей."""
    add_user('user1', 'user1@example.com', 'pass1')
    add_user('user2', 'user2@example.com', 'pass2')
    display_users()
    captured = capsys.readouterr()
    assert 'user1' in captured.out, "Пользователь user1 должен быть отображен."
    assert 'user2' in captured.out, "Пользователь user2 должен быть отображен."