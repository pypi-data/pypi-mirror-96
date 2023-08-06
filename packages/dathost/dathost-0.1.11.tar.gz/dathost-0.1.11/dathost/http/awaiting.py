import typing

from .base import BaseHttp


class AwaitingHttp(BaseHttp):
    async def _get(self, url, read_bytes: bool = False,
                   read_json: bool = True, *args, **kwargs) -> dict:
        """Wrapped HTTPX Delete.
        """

        return self.handle_resp(
            await self._client.get(url, *args, **kwargs),
            read=read_bytes,
            json=read_json
        )

    async def _delete(self, url, *args, **kwargs) -> bool:
        """Wrapped HTTPX Delete.
        """

        return self.handle_resp(
            await self._client.delete(url, *args, **kwargs),
            False
        )

    async def _post(self, url, read_json: bool = False,
                    *args, **kwargs) -> bool:
        """Wrapped HTTPX Post.
        """

        return self.handle_resp(
            await self._client.post(url, *args, **kwargs),
            read_json
        )

    async def _put(self, url, *args, **kwargs) -> bool:
        """Wrapped HTTPX Put.
        """

        return self.handle_resp(
            await self._client.put(url, *args, **kwargs),
            False
        )

    async def _stream(self, url, *args, **kwargs
                      ) -> typing.AsyncGenerator[bytes, None]:
        """Wrapped HTTPX stream GET.

        Yields
        -------
        bytes
        """

        async with self._client.stream("GET", url, *args, **kwargs) as resp:
            if resp.status_code == 200:
                async for chunk in resp.aiter_bytes():
                    yield chunk
