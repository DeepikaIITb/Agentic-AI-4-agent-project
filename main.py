import sys
from database.db import init_db, SessionLocal
from database.seed import run_seed

def seed():
    init_db()
    db = SessionLocal()
    run_seed(db)
    db.close()

def run_agent(learner_id):
    from orchestrator import run_cycle
    db = SessionLocal()
    run_cycle(db, learner_id)
    db.close()

if __name__ == "__main__":
    args = sys.argv[1:]

    if not args or args[0] == "seed":
        seed()

    elif args[0] == "run":
        if len(args) < 2:
            print("Usage: python main.py run <learner_id>")
            sys.exit(1)
        init_db()
        run_agent(int(args[1]))

    else:
        print("Commands:")
        print("  python main.py seed       → create fake data")
        print("  python main.py run 1      → run agents for learner 1")
