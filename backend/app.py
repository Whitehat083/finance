from datetime import timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash


db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    monthly_income = db.Column(db.Float, default=0)
    profile = db.Column(db.String(120), default="student")
    points = db.Column(db.Integer, default=0)
    plan = db.Column(db.String(50), default="free")


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(80), nullable=False)
    kind = db.Column(db.String(10), nullable=False)  # income | expense
    description = db.Column(db.String(255), default="")
    date = db.Column(db.String(20), nullable=False)


class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0)
    target_months = db.Column(db.Integer, nullable=False)


class LessonProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    module_slug = db.Column(db.String(120), nullable=False)
    completed = db.Column(db.Boolean, default=False)


MODULES = [
    "conceito-orcamento",
    "controle-gastos",
    "poupanca-vs-gastos",
    "planejamento-metas",
    "investimentos-simples",
    "erros-comuns",
]


def create_app(test_config=None):
    app = Flask(__name__)
    CORS(app)

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        test_config.get("DATABASE_URL") if test_config else "sqlite:///finance.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = (
        test_config.get("JWT_SECRET") if test_config else "dev-change-me"
    )
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=12)

    db.init_app(app)
    JWTManager(app)

    with app.app_context():
        db.create_all()

    @app.post("/api/auth/register")
    def register():
        data = request.get_json() or {}
        required = ["name", "age", "email", "password"]
        if not all(k in data for k in required):
            return jsonify({"error": "missing_fields"}), 400
        if User.query.filter_by(email=data["email"]).first():
            return jsonify({"error": "email_in_use"}), 409

        user = User(
            name=data["name"],
            age=int(data["age"]),
            email=data["email"],
            password_hash=generate_password_hash(data["password"]),
            monthly_income=float(data.get("monthly_income", 0)),
            profile=data.get("profile", "student"),
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "registered"}), 201

    @app.post("/api/auth/login")
    def login():
        data = request.get_json() or {}
        user = User.query.filter_by(email=data.get("email")).first()
        if not user or not check_password_hash(user.password_hash, data.get("password", "")):
            return jsonify({"error": "invalid_credentials"}), 401
        token = create_access_token(identity=str(user.id))
        return jsonify({"token": token, "user": _serialize_user(user)})

    @app.get("/api/dashboard")
    @jwt_required()
    def dashboard():
        user = _current_user()
        txs = Transaction.query.filter_by(user_id=user.id).all()
        goals = Goal.query.filter_by(user_id=user.id).all()

        income = sum(t.amount for t in txs if t.kind == "income")
        expense = sum(t.amount for t in txs if t.kind == "expense")
        balance = income - expense

        by_category = {}
        for t in txs:
            if t.kind == "expense":
                by_category[t.category] = by_category.get(t.category, 0) + t.amount

        feedback = []
        if expense > income and income > 0:
            feedback.append("Seus gastos superaram sua renda este mês.")
        if by_category.get("lazer", 0) > income * 0.2 and income > 0:
            feedback.append("Você está gastando mais de 20% da renda em lazer.")

        return jsonify(
            {
                "summary": {
                    "income": income,
                    "expense": expense,
                    "balance": balance,
                    "points": user.points,
                    "plan": user.plan,
                },
                "spendingByCategory": by_category,
                "goals": [_serialize_goal(g) for g in goals],
                "transactions": [_serialize_transaction(t) for t in txs][-20:],
                "feedback": feedback,
                "tips": [
                    "Use a regra 50-30-20 para organizar seu orçamento.",
                    "Automatize uma transferência mensal para sua meta principal.",
                ],
            }
        )

    @app.post("/api/transactions")
    @jwt_required()
    def add_transaction():
        user = _current_user()
        data = request.get_json() or {}
        tx = Transaction(
            user_id=user.id,
            amount=float(data["amount"]),
            category=data["category"],
            kind=data["kind"],
            description=data.get("description", ""),
            date=data.get("date", "2026-01-01"),
        )
        db.session.add(tx)
        db.session.commit()
        return jsonify(_serialize_transaction(tx)), 201

    @app.post("/api/goals")
    @jwt_required()
    def add_goal():
        user = _current_user()
        data = request.get_json() or {}
        goal = Goal(
            user_id=user.id,
            title=data["title"],
            target_amount=float(data["target_amount"]),
            current_amount=float(data.get("current_amount", 0)),
            target_months=int(data["target_months"]),
        )
        db.session.add(goal)
        db.session.commit()
        return jsonify(_serialize_goal(goal)), 201

    @app.get("/api/modules")
    @jwt_required()
    def get_modules():
        user = _current_user()
        progress = {
            p.module_slug: p.completed
            for p in LessonProgress.query.filter_by(user_id=user.id).all()
        }

        modules = []
        unlocked = True
        for slug in MODULES:
            completed = progress.get(slug, False)
            modules.append(
                {
                    "slug": slug,
                    "completed": completed,
                    "unlocked": unlocked,
                    "quiz": [
                        "Qual o primeiro passo para montar orçamento?",
                        "Qual indicador mostra se você está no limite de gastos?",
                    ],
                }
            )
            unlocked = unlocked and completed

        return jsonify(modules)

    @app.post("/api/modules/<slug>/complete")
    @jwt_required()
    def complete_module(slug):
        user = _current_user()
        if slug not in MODULES:
            return jsonify({"error": "not_found"}), 404

        previous = MODULES[: MODULES.index(slug)]
        completed = {
            p.module_slug
            for p in LessonProgress.query.filter_by(user_id=user.id, completed=True).all()
        }
        if any(mod not in completed for mod in previous):
            return jsonify({"error": "module_locked"}), 403

        progress = LessonProgress.query.filter_by(user_id=user.id, module_slug=slug).first()
        if not progress:
            progress = LessonProgress(user_id=user.id, module_slug=slug, completed=True)
            db.session.add(progress)
            user.points += 50
        else:
            progress.completed = True
        db.session.commit()
        return jsonify({"message": "completed", "points": user.points})

    @app.post("/api/simulate")
    @jwt_required()
    def simulate_goal():
        data = request.get_json() or {}
        target = float(data.get("target_amount", 0))
        months = int(data.get("months", 1))
        monthly = target / max(months, 1)
        return jsonify({"required_monthly_saving": round(monthly, 2)})

    @app.get("/api/monetization")
    def monetization():
        return jsonify(
            {
                "free": ["Dashboard básico", "Controle financeiro simples", "Módulos iniciais"],
                "premium": [
                    "Conteúdo exclusivo",
                    "Simuladores avançados",
                    "Metas estendidas + notificações",
                ],
                "b2b": ["Licenças para escolas", "Dashboard institucional", "Relatórios"]
            }
        )

    def _current_user():
        user_id = int(get_jwt_identity())
        return db.session.get(User, user_id)

    return app


def _serialize_user(user):
    return {
        "id": user.id,
        "name": user.name,
        "age": user.age,
        "email": user.email,
        "monthly_income": user.monthly_income,
        "profile": user.profile,
        "points": user.points,
        "plan": user.plan,
    }


def _serialize_transaction(tx):
    return {
        "id": tx.id,
        "amount": tx.amount,
        "category": tx.category,
        "kind": tx.kind,
        "description": tx.description,
        "date": tx.date,
    }


def _serialize_goal(goal):
    required = (goal.target_amount - goal.current_amount) / max(goal.target_months, 1)
    return {
        "id": goal.id,
        "title": goal.title,
        "target_amount": goal.target_amount,
        "current_amount": goal.current_amount,
        "target_months": goal.target_months,
        "required_monthly": round(required, 2),
    }


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
