GET_ATTACHMENT_PATH = "select ValueStr from x_UserSettings where Property = N'Путь к хранилищу прикреплённых файлов'"
GET_FILETYPE_ID = "select FileTypeID from atf_FileType where Code = %s"
CREATE_FILETYPE = "insert into atf_FileType (Code, Name) values (%s, %s)d"
GET_DOCUMENT_GUID = "select GUID from x_DocTypeDef where HeadTable = 'hlt_MKAB'"
GET_FILEINFO = """
select top 1 FileInfoID
from atf_FileInfo
where rf_FileTypeID = %d
  and rf_DescTypeGuid = %s
  and DescGuid = %s
  and cast(DateDoc as date) = cast(getdate() as date)
"""
CREATE_FILEINFO = "insert into atf_FileInfo (rf_FileTypeID, rf_DescTypeGuid, DescGuid) values (%d, %s, %s)"
CREATE_ATTACHMENT = """
insert into atf_FileAttachment (rf_CreateUserID, CreateUserName, rf_FileInfoID, Path, Description)
values (%d, %s, %d, %s, %s)
"""
GET_MKAB = "select * from hlt_MKAB where NUM = %s"
