# 🤝 Contributing to Mumbai Taffin Service

First off, thank you for taking the time to contribute! 💛
This project exists to show **how to write professional API endpoints in FastAPI with SQLModel and Pydantic**, so the most valuable contributions are the ones that keep the code **clear, simple and easy to learn from**.

---

## 📋 Table of Contents

- [Ways to Contribute](#-ways-to-contribute)
- [Getting Started](#-getting-started)
- [Coding Guidelines](#-coding-guidelines)
- [Commit and Pull Request Process](#-commit-and-pull-request-process)
- [Ideas for New Features](#-ideas-for-new-features-and-enhancements)

---

## 🌱 Ways to Contribute

- 🐛 **Report a bug**: open an issue with the steps to reproduce it, what you expected and what happened.
- 💡 **Suggest a feature**: open an issue and describe the problem it solves.
- 📝 **Improve the docs**: fix a typo, clarify a comment, add an example.
- 🔧 **Write code**: pick an idea from the [list below](#-ideas-for-new-features-and-enhancements) or any open issue.

> 💬 For anything bigger than a small fix, please open an issue first so we can agree on the approach before you spend time coding.

---

## 🚀 Getting Started

The project uses [uv](https://docs.astral.sh/uv/). All dependencies are declared in `pyproject.toml`.

```bash
# 1. Fork the repo on GitHub, then clone your fork
git clone https://github.com/<your-username>/mumbai-taffin-service.git
cd mumbai-taffin-service

# 2. Create a branch for your work
git checkout -b feat/my-awesome-feature

# 3. Add a .env file
echo "DATABASE_URL=sqlite:///./taffin.db" > .env

# 4. Run the project (uv installs the dependencies automatically)
uv run main.py
```

Open http://127.0.0.1:8000/docs and try your changes in the Swagger UI.

Need a new dependency? Add it with `uv add <package>` so `pyproject.toml` and `uv.lock` stay in sync.

---

## 🐍 Coding Guidelines

We follow **[The Zen of Python (PEP 20)](https://peps.python.org/pep-0020/)**. The lines that matter most here:

> **Beautiful is better than ugly.**
> **Simple is better than complex.**
> **Readability counts.**
> **Explicit is better than implicit.**

### The checklist

- ✅ **Keep it simple.** If a junior developer can't understand it in one read, simplify it.
- ✅ **Add type hints** to every function parameter and return value.
- ✅ **Write a docstring** for every function, class and module (one clear sentence is enough).
- ✅ **Comment the *why***, not the obvious *what*.
- ✅ **Validate input with Pydantic/SQLModel** (`Field(min_length=...)`, `Query(ge=...)`) instead of manual `if` checks.
- ✅ **Raise custom exceptions** from `exceptions.py` instead of returning error dictionaries.
- ✅ **Don't over-engineer.** No base classes, helpers or layers until the same code is really repeated and hard to maintain.

### Example

```python
# ❌ Hard to read: no types, no docs, magic numbers
@router.get("/{id}")
def get(id, s=Depends(get_session)):
    o = s.get(Order, id)
    if not o:
        return {"err": "no"}
    return o


# ✅ Simple and clear: typed, documented, uses a custom exception
@router.get(
    "/{order_id}",
    response_model=Order
    )
def get_order(
    order_id: int,
    session: Session = Depends(get_session)
    ) -> Order:
    """Get a single order by its ID."""
    order = session.get(Order, order_id)
    if order is None:
        raise InvalidOrderIdError(order_id)  # becomes a clean 404 response
    return order
```

### Style tips

- Names say what things are: `delivery_address`, not `da`.
- Prefer small functions that do one thing.
- Keep lines reasonably short (about 100 characters).
- Follow [PEP 8](https://peps.python.org/pep-0008/). If you like, check your code with `uvx ruff check .` and `uvx ruff format .` (this runs Ruff without adding it as a dependency).

---

## 🔀 Commit and Pull Request Process

**Branch names:** `feat/...`, `fix/...`, `docs/...`, `refactor/...`

**Commit messages** use a short prefix and the present tense:

```text
feat: add pagination metadata to the orders list
fix: return 404 when the order id does not exist
docs: explain the order lifecycle in the README
```

**Before you open a pull request:**

- [ ] The project starts with `uv run main.py` and your endpoints work in `/docs`
- [ ] New code has type hints, docstrings and helpful comments
- [ ] Your change is small and focused (one idea per PR)
- [ ] README or docs are updated if behaviour changed
- [ ] You described *what* changed and *why* in the PR description

A maintainer will review your PR as soon as possible. Please be patient and kind, as everyone here is a volunteer. 🙏

---

## 💡 Ideas for New Features and Enhancements

Not sure where to start? Pick one. 🟢 = good first issue, 🟡 = intermediate, 🔴 = advanced.

| Level | Idea | What you'll learn |
| :---: | --- | --- |
| 🟢 | Add `total`, `page` and `pages` metadata to `GET /orders/` | Response schemas, `func.count()` |
| 🟢 | Add sorting (`?sort=created_at&order=desc`) to the orders list | Query params, `order_by` |
| 🟢 | Search orders by customer name | Filters, `ilike` |
| 🟢 | Add a readiness endpoint `GET /health/ready` that checks the database | Health checks, 503 responses |
| 🟢 | Move CORS and settings into a `pydantic-settings` config class | Configuration management |
| 🟡 | Write tests with `pytest` and FastAPI's `TestClient` | Testing, in-memory SQLite |
| 🟡 | Split `items: str` into an `OrderItem` table (name, quantity, price) | Relationships, foreign keys |
| 🟡 | Add a `Customer` table and link orders to customers | One-to-many relationships |
| 🟡 | Add `GET /stats/range` (weekly and monthly summaries) | Date handling, aggregation |
| 🟡 | Provide a `Dockerfile` and `docker-compose.yml` with PostgreSQL | Containers |
| 🔴 | JWT authentication with customer and admin roles | Security, dependencies |
| 🔴 | Delivery partners: assign orders and track their location | Data modelling |
| 🔴 | Live order tracking with WebSockets | Real-time APIs |


Have your own idea? Open an issue. We'd love to hear it! ✨

---

## 📄 License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).

<div align="center">

**Thank you for making this project better! 🚀**

</div>
