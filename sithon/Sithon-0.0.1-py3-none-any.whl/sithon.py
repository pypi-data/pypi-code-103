import log
from testing import Testing
import asyncio

async def main() -> None:
    asyncio.run(Testing().start())

if __name__ == 'main':
    main()
elif __name__ == '__main__':
    log.fatal("", "Sithon should be run directly, `./sithon.py`")
