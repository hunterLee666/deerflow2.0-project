"""
案例 8: DeerFlow 2.0 文件上传处理
完整代码示例 - 支持多种文件格式
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from deerflow.client import DeerFlowClient
import os
import shutil
from pathlib import Path
from typing import Optional
import aiofiles

app = FastAPI()
client = DeerFlowClient()

# 上传目录
UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# 支持的文件类型
SUPPORTED_TYPES = {
    # 文档
    ".txt": "text/plain",
    ".md": "text/markdown",
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".doc": "application/msword",
    # 代码文件
    ".py": "text/x-python",
    ".js": "application/javascript",
    ".ts": "application/typescript",
    ".java": "text/x-java",
    ".cpp": "text/x-c++",
    ".c": "text/x-c",
    ".h": "text/x-c-header",
    ".go": "text/x-go",
    ".rs": "text/x-rust",
    # 数据文件
    ".json": "application/json",
    ".yaml": "application/yaml",
    ".yml": "application/yaml",
    ".csv": "text/csv",
    ".xml": "application/xml",
    # 图片（用于多模态）
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
}

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


async def save_upload_file(upload_file: UploadFile, destination: Path) -> str:
    """保存上传的文件"""
    async with aiofiles.open(destination, 'wb') as out_file:
        content = await upload_file.read()
        await out_file.write(content)
    return str(destination)


def read_file_content(file_path: Path) -> str:
    """读取文件内容"""
    suffix = file_path.suffix.lower()
    
    if suffix in ['.txt', '.md', '.py', '.js', '.ts', '.java', '.cpp', 
                  '.c', '.h', '.go', '.rs', '.json', '.yaml', '.yml', 
                  '.csv', '.xml']:
        # 文本文件
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    
    elif suffix == '.pdf':
        # PDF 文件 - 需要 PyPDF2 或 pdfplumber
        try:
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                return "\n".join(page.extract_text() or "" for page in pdf.pages)
        except ImportError:
            return "[PDF 解析需要安装 pdfplumber]"
    
    elif suffix in ['.docx', '.doc']:
        # Word 文档
        try:
            import docx
            doc = docx.Document(file_path)
            return "\n".join(paragraph.text for paragraph in doc.paragraphs)
        except ImportError:
            return "[Word 解析需要安装 python-docx]"
    
    else:
        return f"[不支持的文件类型: {suffix}]"


@app.post("/api/upload")
async def upload_file(
    file: UploadFile = File(...),
    thread_id: Optional[str] = Form(None),
    process_immediately: bool = Form(False)
):
    """
    文件上传接口
    
    Args:
        file: 上传的文件
        thread_id: 对话线程ID
        process_immediately: 是否立即处理
    """
    # 检查文件类型
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in SUPPORTED_TYPES:
        raise HTTPException(
            status_code=400, 
            detail=f"不支持的文件类型: {file_ext}"
        )
    
    # 检查文件大小
    file.file.seek(0, 2)  # 移动到文件末尾
    file_size = file.file.tell()
    file.file.seek(0)  # 重置到开头
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"文件过大，最大支持 {MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    # 生成唯一文件名
    import uuid
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = UPLOAD_DIR / unique_filename
    
    # 保存文件
    await save_upload_file(file, file_path)
    
    # 读取文件内容
    content = read_file_content(file_path)
    
    result = {
        "filename": file.filename,
        "saved_as": unique_filename,
        "file_path": str(file_path),
        "file_size": file_size,
        "file_type": SUPPORTED_TYPES.get(file_ext, "unknown"),
        "content_preview": content[:500] + "..." if len(content) > 500 else content
    }
    
    # 如果需要立即处理
    if process_immediately:
        # 构建提示词
        prompt = f"""请分析以下文件内容:

文件名: {file.filename}
文件类型: {file_ext}

内容:
{content[:10000]}  # 限制长度

请提供:
1. 文件内容摘要
2. 关键信息提取
3. 如果有代码，分析代码结构和功能
4. 建议或改进意见
"""
        
        # 调用 DeerFlow
        response = client.chat(prompt, thread_id=thread_id)
        result["analysis"] = response
    
    return JSONResponse(content=result)


@app.post("/api/upload/batch")
async def upload_multiple_files(
    files: list[UploadFile] = File(...),
    thread_id: Optional[str] = Form(None)
):
    """
    批量文件上传
    """
    results = []
    
    for file in files:
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in SUPPORTED_TYPES:
            results.append({
                "filename": file.filename,
                "status": "error",
                "message": f"不支持的文件类型: {file_ext}"
            })
            continue
        
        # 保存文件
        import uuid
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = UPLOAD_DIR / unique_filename
        await save_upload_file(file, file_path)
        
        results.append({
            "filename": file.filename,
            "status": "success",
            "saved_as": unique_filename,
            "file_path": str(file_path)
        })
    
    return JSONResponse(content={
        "thread_id": thread_id,
        "files": results,
        "total": len(files),
        "successful": sum(1 for r in results if r["status"] == "success")
    })


@app.post("/api/chat/with-file")
async def chat_with_file(
    message: str = Form(...),
    file: Optional[UploadFile] = File(None),
    thread_id: Optional[str] = Form(None)
):
    """
    带文件上下文的对话
    """
    context = ""
    
    if file:
        # 保存并读取文件
        import uuid
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = UPLOAD_DIR / unique_filename
        await save_upload_file(file, file_path)
        
        content = read_file_content(file_path)
        context = f"""
参考文件: {file.filename}
文件内容:
{content[:8000]}

"""
    
    # 构建完整提示词
    full_prompt = f"""{context}用户问题: {message}

请基于以上信息回答问题。"""
    
    # 调用 DeerFlow
    response = client.chat(full_prompt, thread_id=thread_id)
    
    return JSONResponse(content={
        "response": response,
        "thread_id": thread_id,
        "has_file": file is not None
    })


@app.get("/api/files")
async def list_uploaded_files():
    """列出已上传的文件"""
    files = []
    for file_path in UPLOAD_DIR.iterdir():
        if file_path.is_file():
            stat = file_path.stat()
            files.append({
                "filename": file_path.name,
                "size": stat.st_size,
                "created": stat.st_ctime,
                "path": str(file_path)
            })
    
    return JSONResponse(content={"files": files})


@app.delete("/api/files/{filename}")
async def delete_file(filename: str):
    """删除文件"""
    file_path = UPLOAD_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    
    file_path.unlink()
    return JSONResponse(content={"message": "文件已删除"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
