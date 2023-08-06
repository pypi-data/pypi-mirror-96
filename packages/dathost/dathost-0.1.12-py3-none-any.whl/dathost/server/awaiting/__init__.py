import typing

from ..base import ServerBase

from ...models.server import ServerModel
from ...models.file import FileModel
from ...models.backup import BackupModel
from ...models.metrics import MetricsModel
from ...models.match import MatchModel

from ...match.awaiting import AwaitingMatch

from .backup import AwaitingBackup
from .file import AwaitingFile

from ...settings import ServerSettings, MatchSettings

from ...exceptions import InvalidConsoleLine

from ...routes import SERVER, MATCHES


class ServerAwaiting(ServerBase):
    async def create_match(self, match_settings: MatchSettings,
                           ) -> typing.Tuple[MatchModel, AwaitingMatch]:
        """Creates a match.

        Parameters
        ----------
        match_settings : MatchSettings
            Holds details on the match.

        Returns
        -------
        MatchModel
            Holds match details.
        AwaitingMatch
            Used to interact with a match.
        """

        data = await self.context._post(
            MATCHES.create,
            data={"game_server_id": self.server_id, **match_settings.payload},
            read_json=True
        )

        return MatchModel(data), AwaitingMatch(self.context, data["id"])

    async def delete(self) -> None:
        """Used to delete a sever.
        """

        await self.context._delete(
            SERVER.delete.format(self.server_id),
        )

    async def get(self) -> ServerModel:
        """Used to get details on server.

        Returns
        -------
        ServerModel
            Holds data on server.
        """

        return ServerModel(
            await self.context._get(SERVER.get.format(self.server_id))
        )

    async def update(self, settings: ServerSettings) -> None:
        """Update servers paramters.

        Parameters
        ----------
        settings : ServerSettings
            Used to configure server.
        """

        await self.context._put(
            SERVER.update.format(self.server_id),
            data={
                **settings.payload,
                "server_id": self.server_id
            }
        )

    async def console_send(self, line: str) -> None:
        """Used to send a rcon command to console.

        Parameters
        ----------
        line : str
            Console command.
        """

        await self.context._post(
            url=SERVER.console.format(self.server_id),
            data={
                "line": line,
            }
        )

    async def console_retrive(self, lines: int = 1000) -> list:
        """Used to retrive lines from the console.

        Parameters
        ----------
        lines : int, optional
            Amount of lines to retrive, by default 1000

        Returns
        -------
        list
            List of strings.

        Raises
        ------
        InvalidConsoleLine
            Raised when console lines below 1 or above 100000.
        """

        if lines < 1 or lines > 100000:
            raise InvalidConsoleLine()

        data = await self.context._get(
            url=SERVER.console.format(self.server_id),
            params={
                "max_lines": lines,
            },
        )

        return data["lines"]

    async def sync(self) -> None:
        """Used to sync files from server to cache.
        """

        await self.context._post(
            url=SERVER.sync.format(self.server_id)
        )

    async def duplicate(self, sync: bool = False,
                        ) -> typing.Tuple[ServerModel, ServerBase]:
        """Used to duplicate a server.

        Parameters
        ----------
        sync : bool
            Used to force update server cache, by default False

        Returns
        -------
        ServerModel
            Holds server data.
        ServerAwaiting
            Used to interact with server.
        """

        if sync:
            await self.sync()

        data = await self.context._post(
            url=SERVER.duplicate.format(self.server_id),
            read_json=True,
        )

        return ServerModel(data), ServerAwaiting(self.context, data["id"])

    async def ftp_reset(self) -> None:
        """Resets the FRP password.
        """

        await self.context._post(
            url=SERVER.ftp.format(self.server_id)
        )

    async def stop(self) -> None:
        """Used to stop the server.
        """

        await self.context._post(
            url=SERVER.stop.format(self.server_id),
        )

    async def start(self, allow_host_reassignment: bool = True) -> None:
        """Used to start the server.

        Parameters
        ----------
        allow_host_reassignment : bool, optional
            By default True
        """

        await self.context._post(
            url=SERVER.start.format(self.server_id),
            data={"allow_host_reassignment": allow_host_reassignment}
        )

    async def reset(self) -> None:
        """Used to restart the server.
        """

        await self.context._post(
            url=SERVER.reset.format(self.server_id),
        )

    async def files(self, hide_default: bool = False, path: str = None,
                    file_sizes: bool = False
                    ) -> typing.AsyncGenerator[FileModel, None]:
        """Used to list files.

        Parameters
        ----------
        hide_default : bool, optional
            by default False
        path : str, optional
            Path to use as root, by default None
        file_sizes : bool, optional
            by default False

        Yields
        ------
        FileModel
            Holds details on a file.
        """

        data = await self.context._get(
            SERVER.files.format(self.server_id),
            params={
                "hide_default_files": hide_default,
                "path": path,
                "with_filesizes": file_sizes,
            },
        )

        for file_ in data:
            yield FileModel(file_), self.file(file_["path"])

    def file(self, pathway: str) -> AwaitingFile:
        """Used to interact with a file on the server.

        Parameters
        ----------
        pathway : str
            Pathway of file on server.

        Returns
        -------
        AwaitingFile
        """

        return AwaitingFile(
            self.context,
            self.server_id,
            pathway
        )

    async def backups(self
                      ) -> typing.AsyncGenerator[BackupModel, AwaitingBackup]:
        """Used to list backups a server has.

        Yields
        -------
        BackupModel
            Holds details on backup.
        AwaitingBackup
            Used for interacting with a backup.
        """

        data = await self.context._get(
            SERVER.backups.format(self.server_id),
        )

        for backup in data:
            yield BackupModel(backup), self.backup(backup["name"])

    def backup(self, backup_name: str) -> AwaitingBackup:
        """Used to interact with a backup.

        Parameters
        ----------
        backup_name : str
            Name of backup.

        Returns
        -------
        AwaitingBackup
        """

        return AwaitingBackup(
            self.context,
            self.server_id,
            backup_name
        )

    async def metrics(self) -> MetricsModel:
        """Used to get server metrics.

        Returns
        -------
        MetricsModel
            Holds details on server metrics.
        """

        data = await self.context._get(
            SERVER.metrics.format(self.server_id)
        )

        return MetricsModel(data)
