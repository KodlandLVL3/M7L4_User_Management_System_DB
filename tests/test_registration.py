import pytest
import sqlite3
import os

from registration.registration import (
    create_db,
    add_user,
    authenticate_user,
    display_users,
    DB_NAME,
)



#  Исходные тесты


@pytest.fixture(scope="module")
def setup_database():
    """Фикстура для настройки базы данных перед тестами и её очистки после."""
    create_db()
    yield
    try:
        os.remove(DB_NAME)
    except (PermissionError, FileNotFoundError):
        pass


@pytest.fixture
def connection():
    """Фикстура для получения соединения с базой данных и его закрытия после теста."""
    conn = sqlite3.connect(DB_NAME)
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


#  Мои тесты


#Тест добавления пользователя с существующим логином

def test_add_duplicate_user(setup_database, connection):
    """Повторное добавление пользователя с тем же логином должно вернуть False,
    а в базе должен остаться только один пользователь с этим логином."""
    add_user('duplicate', 'first@example.com', 'password1')
    result = add_user('duplicate', 'second@example.com', 'password2')

    assert result is False, "add_user должен вернуть False при дубликате логина"

    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE username='duplicate';")
    count = cursor.fetchone()[0]
    assert count == 1, "В базе должен остаться только один пользователь с таким логином"

    # Данные первого пользователя не должны быть перезаписаны
    cursor.execute("SELECT email, password FROM users WHERE username='duplicate';")
    email, password = cursor.fetchone()
    assert email == 'first@example.com'
    assert password == 'password1'


#Тест успешной аутентификации пользователя

def test_authenticate_success(setup_database):
    """Правильные логин и пароль — authenticate_user возвращает True."""
    add_user('authuser', 'auth@example.com', 'secret')
    assert authenticate_user('authuser', 'secret') is True


#Тест аутентификации несуществующего пользователя

def test_authenticate_nonexistent_user(setup_database):
    """Несуществующий пользователь — authenticate_user возвращает False."""
    assert authenticate_user('ghost', 'anything') is False


#Тест аутентификации пользователя с неправильным паролем

def test_authenticate_wrong_password(setup_database):
    """Существующий логин + неверный пароль — authenticate_user возвращает False."""
    add_user('realuser', 'real@example.com', 'correct')
    assert authenticate_user('realuser', 'wrong') is False


#Тест отображения списка пользователей

def test_display_users(setup_database, capsys):
    """display_users выводит логины и email всех пользователей,
    но не выводит пароли."""
    add_user('alice', 'alice@example.com', 'alicepwd')
    add_user('bob', 'bob@example.com', 'bobpwd')

    display_users()
    captured = capsys.readouterr().out

    assert 'alice' in captured
    assert 'alice@example.com' in captured
    assert 'bob' in captured
    assert 'bob@example.com' in captured
    # Пароли не должны отображаться
    assert 'alicepwd' not in captured
    assert 'bobpwd' not in captured
