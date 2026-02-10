from app import create_app, db


def client():
    app = create_app({"DATABASE_URL": "sqlite:///:memory:", "JWT_SECRET": "test"})
    app.config["TESTING"] = True
    with app.app_context():
        db.create_all()
    return app.test_client()


def register_and_login(c):
    c.post(
        "/api/auth/register",
        json={
            "name": "Ana",
            "age": 19,
            "email": "ana@mail.com",
            "password": "123456",
            "monthly_income": 2000,
        },
    )
    res = c.post("/api/auth/login", json={"email": "ana@mail.com", "password": "123456"})
    return res.get_json()["token"]


def test_auth_and_dashboard():
    c = client()
    token = register_and_login(c)

    c.post(
        "/api/transactions",
        headers={"Authorization": f"Bearer {token}"},
        json={"amount": 2000, "category": "salario", "kind": "income", "date": "2026-01-02"},
    )
    c.post(
        "/api/transactions",
        headers={"Authorization": f"Bearer {token}"},
        json={"amount": 600, "category": "lazer", "kind": "expense", "date": "2026-01-03"},
    )

    dash = c.get("/api/dashboard", headers={"Authorization": f"Bearer {token}"})
    data = dash.get_json()
    assert dash.status_code == 200
    assert data["summary"]["balance"] == 1400
    assert "lazer" in data["spendingByCategory"]


def test_module_lock_rule():
    c = client()
    token = register_and_login(c)

    locked = c.post("/api/modules/controle-gastos/complete", headers={"Authorization": f"Bearer {token}"})
    assert locked.status_code == 403

    first = c.post("/api/modules/conceito-orcamento/complete", headers={"Authorization": f"Bearer {token}"})
    assert first.status_code == 200
