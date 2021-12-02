import ujson
import aiofiles
from pathlib import Path
from typing import Any, AnyStr, Optional, Union, IO
from .uiexcep import *
from .uitry import retry
from .uilog import logger
from .uiclient import sync_uiclient, async_uiclient


class uio:
    """请不用理会这个

    Returns:
        ?return什么啊: 啊这
    """

    @staticmethod
    def sync_dump(obj: Any, fp: Optional[IO[AnyStr]]) -> None:
        """同步下的json_dump,单独提出来是因为ensure_ascii跟indent太烦了！

        Args:
            obj (Any): json格式文本
            fp (Optional[IO[AnyStr]]): 同步下的fileIO
        """
        return ujson.dump(obj, fp, indent=4, ensure_ascii=False)

    @staticmethod
    async def async_dump(obj: Any, fp: Optional[IO[AnyStr]]):
        """异步下的json_dump,单独提出来是因为ensure_ascii跟indent太烦了！

        Args:
            obj (Any): json格式文本
            fp (Optional[IO[AnyStr]]): asyncfiles下的fileIO
        """
        return ujson.dump(obj, fp, indent=4, ensure_ascii=False)


class sync_uio(uio):
    def __init__(self) -> None:
        """emmmmm"""
        super().__init__()

    def __open_file(
        self,
        fp: Optional[IO[AnyStr]] = None,
        file_path: str = None,
        open_type: str = "w",
        encoding: Optional[str] = "utf-8",
    ) -> IO:
        if fp:
            return fp
        try:
            return Path(file_path).open(encoding=encoding, mode=open_type)
        except FileNotFoundError:
            parts = Path(file_path).parts
            for i in parts:
                if i == parts[-1]:
                    Path(file_path).touch()
                    break
                Path(i).mkdir(exist_ok=True)
            return Path(file_path).open(encoding=encoding, mode=open_type)

    @retry(logger=logger)
    def save_file(
        self,
        type: Optional[str],
        save_path: Optional[str] = None,
        fp: Optional[IO[AnyStr]] = None,
        obj: Any = None,
        open_type: str = "w",
        encoding: Optional[str] = "utf-8",
        url: Optional[str] = None,
        proxy: Optional[dict] = None,
        timeout: Optional[Union[tuple, int]] = None,
        request_headers: Optional[dict] = None,
        other_headers: Optional[str] = None,
        request_json: Optional[Any] = None,
        request_params: Optional[dict] = None,
        request_data: Optional[dict] = None,
    ) -> list[bool, Optional[str]]:
        """保存文件的方法,提供了以下几种情况的保存:
        1.提供url,保存请求的json或是图片到默认路径`./res/随机id.[json|png]`或给予的路径或是fileIO
        2.提供obj,保存到提供的路径或是默认或是fileIO
        3.提供dict,保存json到提供路径或是fileIO
        4.提供obj及后缀名,写入到提供路径或是fileIO
        除此之外(例如需要post什么的)请自己动手丰衣足食！羽衣已经累坏了

        Args:
            type (Optional[str], optional): ["json"|"url_json"|"image"|"url_image"|"other"].
            save_path (str, optional): 保存的路径,请与fp二选一传入.
            fp (Optional[IO[AnyStr]], optional): fileIO,有需要保存到特定文件时提供,或者提供路径. Defaults to None.
            obj (Any, optional): 任意需要保存的东西[json|dict|text|Any]. Defaults to None.
            open_type (str, optional): open文件的方法,一般不用理会. Defaults to "w".
            encoding (Optional[str], optional): open文件时的encoding,一般不用改. Defaults to "utf-8".
            url (Optional[str], optional): 需要请求url获取数据时,传入url. Defaults to None.
            proxy (Optional[dict], optional): url存在时有效,requests接受的代理. Defaults to None.
            timeout (Optional[Union[tuple, int]], optional): url存在时有效,requests接受的timeout. Defaults to None.
            request_headers (Optional[dict], optional): url存在时有效,默认为中文的windows电脑,传入cookie请使用request_cookies. Defaults to None.
            other_headers (Optional[str]): url存在时有效,传入任意headers的键值对,请求时会加进去. Defaults to None.
            request_json (Optional[AnyStr]): url存在时有效,post的json. Defaults to None.
            request_params (Optional[dict], optional): url存在时有效,请求的params. Defaults to None.
            request_data (Optional[dict], optional): url存在时有效,请求的data. Defaults to None.
        Returns:
            list[bool,Optional[str]]: [成功或失败,保存的文件路径(传入fileIO或出错时返回为None)]
        """
        try:
            if not (save_path or fp):
                raise ValueError("没有给与fp或路径参数,请任选一传入！")
            fp_normal = self.__open_file(fp, save_path, open_type, encoding)
            fp_bytes = self.__open_file(fp, save_path, "wb", encoding=None)
            if type.lower() == "json":
                if obj:
                    self.sync_dump(obj, fp)
                else:
                    raise ValueError(f"检查到type为:json(实际传入:{type}),缺少obj参数")
                return [True, save_path]
            elif type.lower() == "image":
                if obj:
                    fp_bytes.write(obj)
                else:
                    raise ValueError(f"检查到type为:image(实际传入:{type}),缺少obj参数")
                return [True, save_path]
            elif type.lower() == "url_image" or type.lower() == "url_json":
                with sync_uiclient(
                    proxy,
                    timeout,
                    request_headers,
                    other_headers,
                    request_json,
                    request_params,
                    request_data,
                ) as client:
                    if url:
                        res = client.uiget(url)
                    else:
                        raise ValueError(f"检查到type为:url_image(实际传入:{type}),缺少url参数")
                    fp_bytes.write(
                        res.content
                    ) if type.lower() == "url_image" else fp_normal.write(res.json)
                    return [True, save_path]
            elif type.lower() == "other":
                fp_normal.write(obj)
            else:
                raise Uio_MethodNotDefinded
        except Exception as e:
            logger.warning(f"文件保存失败: {e}")
        finally:
            fp_normal.close()
            fp_bytes.close()


class async_uio(uio):
    def __init__(self) -> None:
        super().__init__()

    async def __open_file(
        self,
        fp: Optional[IO[AnyStr]] = None,
        file_path: str = None,
        open_type: str = "w",
        encoding: Optional[str] = "utf-8",
    ) -> IO:
        if fp:
            return fp
        try:
            return Path(file_path).open(encoding=encoding, mode=open_type)
        except FileNotFoundError:
            parts = Path(file_path).parts
            for i in parts:
                if i == parts[-1]:
                    Path(file_path).touch()
                    break
                Path(i).mkdir(exist_ok=True)
            return Path(file_path).open(encoding=encoding, mode=open_type)

    @retry(logger=logger)
    async def save_file(
        self,
        type: Optional[str],
        save_path: Optional[str] = None,
        fp: Optional[IO[AnyStr]] = None,
        obj: Any = None,
        open_type: str = "w",
        encoding: Optional[str] = "utf-8",
        url: Optional[str] = None,
        proxy: Optional[dict] = None,
        timeout: Optional[Union[tuple, int]] = None,
        request_headers: Optional[dict] = None,
        other_headers: Optional[str] = None,
        request_json: Optional[AnyStr] = None,
        request_params: Optional[dict] = None,
        request_data: Optional[dict] = None,
    ) -> list[bool, Optional[str]]:
        """保存文件的异步方法,提供了以下几种情况的保存:
        1.提供url,保存请求的json或是图片到默认路径`./res/随机id.[json|png]`或给予的路径或是fileIO
        2.提供obj,保存到提供的路径或是默认或是fileIO
        3.提供dict,保存json到提供路径或是fileIO
        4.提供obj及后缀名,写入到提供路径或是fileIO
        除此之外(例如需要post什么的)请自己动手丰衣足食！羽衣已经累坏了
        Args:
            type (Optional[str], optional): ["json"|"url_json"|"image"|"url_image"|"other"].
            save_path (str, optional): 保存的路径,请与fp二选一传入.
            fp (Optional[IO[AnyStr]], optional): fileIO,有需要保存到特定文件时提供,或者提供路径. Defaults to None.
            obj (Any, optional): 任意需要保存的东西[json|dict|text|Any]. Defaults to None.
            open_type (str, optional): open文件的方法,一般不用理会. Defaults to "w".
            encoding (Optional[str], optional): open文件时的encoding,一般不用改. Defaults to "utf-8".
            url (Optional[str], optional): 需要请求url获取数据时,传入url. Defaults to None.
            proxy (Optional[dict], optional): url存在时有效,requests接受的代理. Defaults to None.
            timeout (Optional[Union[tuple, int]], optional): url存在时有效,requests接受的timeout. Defaults to None.
            request_headers (Optional[dict], optional): url存在时有效,默认为中文的windows电脑,传入cookie请使用request_cookies. Defaults to None.
            other_headers (Optional[str]): url存在时有效,传入任意headers的键值对,请求时会加进去. Defaults to None.
            request_json (Optional[AnyStr]): url存在时有效,post的json. Defaults to None.
            request_params (Optional[dict], optional): url存在时有效,请求的params. Defaults to None.
            request_data (Optional[dict], optional): url存在时有效,请求的data. Defaults to None.
        Returns:
            list[bool,Optional[str]]: [成功或失败,保存的文件路径(传入fileIO或出错时返回为None)]
        """
        try:
            if not (save_path or fp):
                raise ValueError("没有给与fp或路径参数,请任选一传入！")
            fp_normal = await self.__open_file(fp, save_path, open_type, encoding)
            fp_bytes = await self.__open_file(fp, save_path, "wb", encoding=None)
            if type.lower() == "json":
                if obj:
                    await self.async_dump(obj, fp)
                else:
                    raise ValueError(f"检查到type为:json(实际传入:{type}),缺少obj参数")
                return [True, save_path]
            elif type.lower() == "image":
                if obj:
                    fp_bytes.write(obj)
                else:
                    raise ValueError(f"检查到type为:image(实际传入:{type}),缺少obj参数")
                return [True, save_path]
            elif type.lower() == "url_image" or type.lower() == "url_json":
                async with async_uiclient(
                    proxy,
                    timeout,
                    request_headers,
                    other_headers,
                    request_json,
                    request_params,
                    request_data,
                ) as client:
                    if url:
                        res = await client.uiget(url)
                    else:
                        raise ValueError(f"检查到type为:url_image(实际传入:{type}),缺少url参数")
                    fp_bytes.write(
                        res.content
                    ) if type.lower() == "url_image" else await fp_normal.write(
                        res.json
                    )
                    return [True, save_path]
            elif type.lower() == "other":
                fp_normal.write(obj)
            else:
                raise Uio_MethodNotDefinded
        except Exception as e:
            logger.warning(f"文件保存失败: {e}")
        finally:
            fp_normal.close()
            fp_bytes.close()
