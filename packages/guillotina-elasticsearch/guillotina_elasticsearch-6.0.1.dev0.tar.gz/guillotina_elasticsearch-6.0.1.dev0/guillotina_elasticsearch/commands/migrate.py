from guillotina import task_vars
from guillotina.commands import Command
from guillotina.commands.utils import change_transaction_strategy
from guillotina.component import get_utility
from guillotina.interfaces import ICatalogUtility
from guillotina.tests.utils import get_mocked_request
from guillotina.tests.utils import login
from guillotina.utils import get_containers
from guillotina_elasticsearch.migration import Migrator

import asyncio
import logging
import time


logger = logging.getLogger("guillotina_elasticsearch")


class printer:
    def write(self, txt):
        if isinstance(txt, bytes):
            txt = txt.decode("utf-8")
        logger.warning(txt.strip())


class MigrateCommand(Command):
    description = "Migrate indexes"
    migrator = None

    def get_parser(self):
        parser = super(MigrateCommand, self).get_parser()
        parser.add_argument("--full", help="Do a full reindex", action="store_true")
        parser.add_argument(
            "--force",
            help="Override failing migration if existing " "migration index exists",
            action="store_true",
        )
        parser.add_argument("--log-details", action="store_true")
        parser.add_argument("--memory-tracking", action="store_true")
        parser.add_argument("--reindex-security", action="store_true")
        parser.add_argument("--mapping-only", action="store_true")
        return parser

    async def migrate_all(self, arguments):
        search = get_utility(ICatalogUtility)
        change_transaction_strategy("none")
        await asyncio.sleep(1)  # since something initialize custom types...
        async for _, tm, container in get_containers():
            try:
                self.migrator = Migrator(
                    search,
                    container,
                    response=printer(),
                    full=arguments.full,
                    force=arguments.force,
                    log_details=arguments.log_details,
                    memory_tracking=arguments.memory_tracking,
                    reindex_security=arguments.reindex_security,
                    mapping_only=arguments.mapping_only,
                    cache=False,
                )
                await self.migrator.run_migration()
                seconds = int(time.time() - self.migrator.start_time)
                logger.warning(
                    f"""Finished migration:
Total Seconds: {seconds}
Processed: {self.migrator.processed}
Indexed: {self.migrator.indexed}
Objects missing: {len(self.migrator.missing)}
Objects orphaned: {len(self.migrator.orphaned)}
Mapping Diff: {self.migrator.mapping_diff}
"""
                )
            finally:
                await tm.commit()

    def run(self, arguments, settings, app):
        request = get_mocked_request()
        login()
        task_vars.request.set(request)
        loop = self.get_loop()
        try:
            loop.run_until_complete(self.migrate_all(arguments))
        except KeyboardInterrupt:  # pragma: no cover
            pass
        finally:
            if self.migrator.status != "done":
                loop = self.get_loop()
                loop.run_until_complete(self.migrator.cancel_migration())
