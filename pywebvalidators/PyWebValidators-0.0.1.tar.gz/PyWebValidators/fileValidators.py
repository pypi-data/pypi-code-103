"""
The script contains the following file based validations:
1. JPEG/JPG
2. PNG
3. TXT
4. Word/PPT/Excel/CSV
5. PDF
6. ZIP
7. RAR
8. Video Formats - MP4, MPEG, AVI
9. Audio Formats - MP3, WAV, AAC,
"""

# Imports
import magic


# JPEG/JPG Validator
def validate_jpeg(filepath: str) -> bool:
    ext = filepath.split(".")[-1]
    mime = magic.Magic(mime=True).from_file(filename=filepath)

    if (ext == "jpg" or ext == "jpeg") and mime == "image/jpeg":
        return True

    return False


# PNG Validator
def validate_png(filepath: str) -> bool:
    ext = filepath.split(".")[-1]
    mime = magic.Magic(mime=True).from_file(filename=filepath)

    if ext == "png" and mime == "image/png":
        return True

    return False


# TXT Validator
def validate_txt(filepath: str) -> bool:
    ext = filepath.split(".")[-1]
    mime = magic.Magic(mime=True).from_file(filename=filepath)

    if ext == "txt" and mime == "text/plain":
        return True

    return False


# Word File Validator
def validate_doc(filepath: str) -> bool:
    ext = filepath.split(".")[-1]
    mime = magic.Magic(mime=True).from_file(filename=filepath)

    if ext == "doc" and mime == "application/msword":
        return True

    if ext == "docx" and mime == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return True

    return False


# PPT File Validator
def validate_ppt(filepath: str) -> bool:
    ext = filepath.split(".")[-1]
    mime = magic.Magic(mime=True).from_file(filename=filepath)

    if ext == "ppt" and mime == "application/vnd.ms-powerpoint":
        return True

    if ext == "pptx" and mime == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
        return True

    return False


# Excel File Validator
def validate_xls(filepath: str) -> bool:
    ext = filepath.split(".")[-1]
    mime = magic.Magic(mime=True).from_file(filename=filepath)

    if ext == "xls" and mime == "application/vnd.ms-excel":
        return True

    if ext == "xlsx" and mime == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        return True

    return False


# CSV File Validator
def validate_csv(filepath: str) -> bool:
    ext = filepath.split(".")[-1]
    mime = magic.Magic(mime=True).from_file(filename=filepath)

    if ext == "csv" and mime == "text/csv":
        return True

    return False


# PDF File Validator
def validate_pdf(filepath: str) -> bool:
    ext = filepath.split(".")[-1]
    mime = magic.Magic(mime=True).from_file(filename=filepath)

    if ext == "pdf" and mime == "application/pdf":
        return True

    return False


# ZIP File Validator
def validate_zip(filepath: str) -> bool:
    ext = filepath.split(".")[-1]
    mime = magic.Magic(mime=True).from_file(filename=filepath)

    if ext == "zip" and mime == "application/zip":
        return True

    return False


# RAR File Validator
def validate_rar(filepath: str) -> bool:
    ext = filepath.split(".")[-1]
    mime = magic.Magic(mime=True).from_file(filename=filepath)

    if ext == "rar" and mime == "application/vnd.rar":
        return True

    return False


# MP4 File Validator
def validate_mp4(filepath: str) -> bool:
    ext = filepath.split(".")[-1]
    mime = magic.Magic(mime=True).from_file(filename=filepath)

    if ext == "mp4" and mime == "video/mp4":
        return True

    return False


# MPEG File Validator
def validate_mpeg(filepath: str) -> bool:
    ext = filepath.split(".")[-1]
    mime = magic.Magic(mime=True).from_file(filename=filepath)

    if ext == "mpeg" and mime == "video/mpeg":
        return True

    return False


# AVI File Validator
def validate_avi(filepath: str) -> bool:
    ext = filepath.split(".")[-1]
    mime = magic.Magic(mime=True).from_file(filename=filepath)

    if ext == "avi" and mime == "video/x-msvideo":
        return True

    return False


# MP3 File Validator
def validate_mp3(filepath: str) -> bool:
    ext = filepath.split(".")[-1]
    mime = magic.Magic(mime=True).from_file(filename=filepath)

    if ext == "mp3" and mime == "audio/mpeg":
        return True

    return False


# WAV File Validator
def validate_wav(filepath: str) -> bool:
    ext = filepath.split(".")[-1]
    mime = magic.Magic(mime=True).from_file(filename=filepath)

    if ext == "wav" and mime == "audio/wav":
        return True

    return False


# AAC File Validator
def validate_aac(filepath: str) -> bool:
    ext = filepath.split(".")[-1]
    mime = magic.Magic(mime=True).from_file(filename=filepath)

    if ext == "aac" and mime == "audio/aac":
        return True

    return False
