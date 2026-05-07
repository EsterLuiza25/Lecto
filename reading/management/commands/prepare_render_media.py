from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connection
from django.db.utils import OperationalError, ProgrammingError


class Command(BaseCommand):
    help = "Regenerate deploy-time media assets when the database is already migrated."

    def handle(self, *args, **options):
        try:
            table_names = set(connection.introspection.table_names())
        except (OperationalError, ProgrammingError) as error:
            self.stdout.write(self.style.WARNING(f"Database unavailable; skipping media preparation: {error}"))
            return

        required_tables = {"reading_text", "accounts_avataroption"}
        missing_tables = sorted(required_tables - table_names)
        if missing_tables:
            self.stdout.write(
                self.style.WARNING(
                    "Database is not migrated yet; skipping media preparation. "
                    f"Missing tables: {', '.join(missing_tables)}"
                )
            )
            return

        call_command("refresh_text_illustrations")
        call_command("generate_mass_content", "--only-avatars")
        self.stdout.write(self.style.SUCCESS("Render media assets ready."))
