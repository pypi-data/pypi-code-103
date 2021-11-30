import aiofiles
import asyncio
import yaml


async def generate_key(hub, plugin: str):
    ret = hub.crypto[plugin].generate_key()
    if asyncio.iscoroutine(ret):
        return await ret
    return ret


async def encrypt(hub, plugin: str, data, key):
    """
    Call the named crypto_plugin.
    Pass it's "encrypt" function the raw data and the encryption key
    return the encrypted data
    """
    ret = hub.crypto[plugin].encrypt(data, key)
    if asyncio.iscoroutine(ret):
        return await ret
    return ret


async def decrypt(hub, plugin: str, data, key):
    """
    Call the named crypto_plugin.
    Pass it's "decrypt" function the encrypted data and the decryption key
    return the raw decrypted data
    """
    ret = hub.crypto[plugin].decrypt(data, key)
    if asyncio.iscoroutine(ret):
        return await ret
    return ret


async def encrypt_file(
    hub,
    crypto_plugin: str,
    acct_file: str,
    acct_key: str = None,
    output_file: str = None,
):
    async with aiofiles.open(acct_file, "rb") as fh_:
        data = yaml.safe_load(await fh_.read())

    if acct_key is None:
        acct_key = await hub.crypto.init.generate_key(crypto_plugin)

    encrypted = await hub.crypto.init.encrypt(crypto_plugin, data, acct_key)

    if not output_file:
        output_file = f"{acct_file}.{crypto_plugin}"

    async with aiofiles.open(output_file, "wb+") as fh_:
        await fh_.write(encrypted)

    hub.log.info(f"New encrypted file created in {output_file}")

    return acct_key


async def decrypt_file(hub, crypto_plugin: str, acct_file: str, acct_key: str):
    async with aiofiles.open(acct_file, "rb") as fh_:
        raw = await fh_.read()

    decrypted = await hub.crypto.init.decrypt(crypto_plugin, raw, acct_key)
    return decrypted
