---
name: python-unit-testing
description: Write and review pytest unit tests for Python backends (FastAPI, SQLAlchemy, plain functions). Use whenever the user asks to "write tests", "add unit tests", "test this endpoint/function", "increase coverage", or hands over code and asks for test coverage. Also use when the user has a failing or flaky test and wants help debugging it. Covers test structure, fixtures, mocking, FastAPI TestClient patterns, and SQLAlchemy test-DB setup. Always pushes for a short explanation of *why* each test exists, not just working test code — do not skip this step even if the user only asked for the tests themselves.
---

# Python Unit Testing (pytest)

## Core principle: tests encode intent, not just syntax

A test is only as good as the understanding behind it. Before writing any
test, be able to state in one sentence: "this test proves that X happens
when Y" or "this test proves that X does NOT happen when Y". If that
sentence can't be written, the test isn't ready to be written either —
go clarify the expected behavior first (ask the user, or infer it from
the code's docstring/naming and state the assumption explicitly).

After generating tests, always give the user a short plain-language
summary of what each test actually proves — 1 line per test is enough.
This is not optional filler: it's the artifact that lets the user (or a
reviewer, or an interviewer) verify the test is testing the right thing,
not just that it passes. If the user explicitly says they don't want
this summary, skip it — but default to including it.

## Test structure

Use the **Arrange-Act-Assert** pattern, and make each section visually
distinct (blank line or comment) even in short tests:

```python
def test_verify_password_rejects_wrong_password():
    # Arrange
    hashed = hash_password("correct-horse-battery-staple")

    # Act
    result = verify_password("wrong-password", hashed)

    # Assert
    assert result is False
```

One logical behavior per test. If a test needs "and" to describe what it
checks ("checks hashing and verification and expiry"), split it.

## Naming

`test_<unit>_<condition>_<expected_result>`, e.g.:
- `test_create_access_token_sets_expiry_in_future`
- `test_login_returns_401_for_wrong_password`
- `test_login_returns_401_for_unknown_email`

Names should make it possible to understand what broke from the test
name alone in a CI failure list, without opening the file.

## What to cover for a given unit

For any function/endpoint, walk through these categories and include the
ones that are actually meaningful (don't force all four if one doesn't apply):

1. **Happy path** — normal, expected input → expected output
2. **Known error/edge cases** — empty input, boundary values, wrong types,
   duplicate entries (e.g. registering with an email that already exists)
3. **Security-relevant behavior**, if applicable — e.g. does a failed
   login leak whether the email exists vs. the password was wrong; is a
   password ever present in a response body; does an expired token get
   rejected
4. **Failure of dependencies** — what happens if the DB call raises, if
   an external call times out (use mocking for this, see below)

Do not write a test just to inflate coverage numbers. A test with no
clear failure mode it's guarding against is noise, not safety.

## FastAPI-specific patterns

Use `TestClient` for endpoint tests — it exercises the full request/response
cycle (routing, validation, serialization), not just the underlying function:

```python
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_register_returns_created_user_without_password_hash():
    response = client.post("/register", json={
        "username": "kevin",
        "email": "kevin@example.com",
        "password": "a-real-password",
    })
    assert response.status_code == 200
    body = response.json()
    assert "hashed_password" not in body
```

Never call the route function directly (`health_check()` instead of
`client.get("/health")`) unless you are specifically unit-testing pure
logic that has been factored out of the route — direct calls skip
routing, validation, and serialization, so they don't prove the endpoint
actually works over HTTP.

## Database tests: don't hit the real/production DB

Use a separate test database (e.g. a local SQLite file or a throwaway
Postgres schema/container), created fresh per test session or per test,
via a pytest fixture:

```python
# conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from app import app, get_db

TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine)

@pytest.fixture()
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    from fastapi.testclient import TestClient
    yield TestClient(app)
    app.dependency_overrides.clear()
```

Explain to the user, when introducing this: tests must never depend on
secrets or state from the real Supabase/production DB (flaky, slow,
and risks polluting real data) — this is why CI needs its own isolated
test DB setup, separate from the `DATABASE_URL` used in production.

## Mocking: use sparingly, and say why

Mock external calls (network, time, randomness) — not your own business
logic. Mocking your own logic just to make a test pass usually means the
test isn't testing anything real anymore.

```python
from unittest.mock import patch

def test_token_expires_after_configured_delta():
    with patch("security.datetime") as mock_dt:
        ...
```

When you mock something, say one sentence on why it needed mocking
(e.g. "mocked `datetime.now` so the expiry check isn't time-dependent
and flaky") — this is the kind of thing that's easy to do without
understanding, and easy to get subtly wrong.

## Fixtures over duplication

If 3+ tests need the same setup (e.g. a registered user, a valid token),
factor it into a fixture instead of copy-pasting setup code. But don't
over-abstract a single-use setup into a fixture — that's premature.

## Before marking tests "done"

Run through this checklist with the user (briefly, not a formal gate):

- [ ] Each test's one-line "what this proves" statement is written down somewhere
      (commit message, PR description, or just stated in chat) — not just in your head
- [ ] Tests fail when they should — if unsure, temporarily break the
      implementation and confirm the test actually catches it (this is the
      single best way to catch a test that's accidentally not testing anything)
- [ ] No test depends on execution order or leftover state from another test
- [ ] No secrets, real passwords, or production DB connections in test code

The "temporarily break it and confirm the test fails" step is the most
commonly skipped and most valuable one — a test that has never been seen
to fail is unverified. Recommend it explicitly every time, especially for
security-relevant tests (auth, hashing, permissions).