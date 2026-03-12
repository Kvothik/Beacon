from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.app.core.db import create_session, shutdown_database
from backend.app.services.parole_board_service import seed_parole_board_reference_data


def main() -> None:
    session = create_session()
    try:
        offices_written, mappings_written = seed_parole_board_reference_data(session)
        session.commit()
        print(
            f"Seeded parole board reference data: offices={offices_written} mappings={mappings_written}"
        )
    finally:
        session.close()
        shutdown_database()


if __name__ == "__main__":
    main()
