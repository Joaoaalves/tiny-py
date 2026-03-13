from collections.abc import AsyncIterator
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from tiny_py._async_http import AsyncHTTPAdapter


class AsyncBaseResource:
    def __init__(self, http: "AsyncHTTPAdapter") -> None:
        self._http = http

    async def _paginate(
        self,
        endpoint: str,
        collection_key: str,
        item_key: str,
        params: dict[str, Any],
    ) -> AsyncIterator[dict[str, Any]]:
        """
        Generic async pagination iterator. Yields raw item dicts page by page.
        Stops when the current page equals numero_paginas.
        """
        page = 1
        while True:
            retorno = await self._http.get(endpoint, {**params, "pagina": page})
            numero_paginas = int(retorno.get("numero_paginas", 1))
            collection = retorno.get(collection_key, [])
            for wrapper in collection:
                if isinstance(wrapper, dict) and item_key in wrapper:
                    yield wrapper[item_key]
                else:
                    yield wrapper
            if page >= numero_paginas:
                break
            page += 1
