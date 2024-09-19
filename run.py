from src import create_app
from src.extensions import db

app = create_app()

print("Zarejestrowane trasy:")
for rule in app.url_map.iter_rules():
    print(f"{rule.endpoint}: {rule.rule}")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)