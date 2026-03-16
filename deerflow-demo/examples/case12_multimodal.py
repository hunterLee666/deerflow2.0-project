"""
案例 12: DeerFlow 2.0 多模态内容生成
完整代码示例 - 图像、音频、视频处理
"""

from deerflow.client import DeerFlowClient
from typing import List, Dict, Any, Optional
import base64
from pathlib import Path


class MultimodalProcessor:
    """多模态处理器"""
    
    def __init__(self, client: DeerFlowClient = None):
        self.client = client or DeerFlowClient()
    
    def process_image(self, image_path: str, prompt: str = None) -> str:
        """
        处理图像输入
        
        Args:
            image_path: 图像文件路径
            prompt: 关于图像的问题或指令
        """
        # 读取图像并编码
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        # 构建多模态提示词
        full_prompt = f"""请分析以下图像:

[图像数据: base64编码，格式为data:image/png;base64,{image_data[:100]}...]

{prompt or '请描述这张图片的内容'}
"""
        
        # 调用 DeerFlow（假设支持多模态）
        response = self.client.chat(full_prompt)
        return response
    
    def generate_image_prompt(self, description: str) -> str:
        """
        生成图像生成提示词
        """
        prompt = f"""请将以下描述转换为详细的图像生成提示词:

描述: {description}

请生成适合 DALL-E 或 Midjourney 的详细提示词，包括:
- 主体描述
- 风格
- 光照
- 构图
- 氛围

格式: 英文提示词，用逗号分隔"""
        
        return self.client.chat(prompt)
    
    def analyze_document(self, file_path: str, analysis_type: str = "summary") -> str:
        """
        分析文档内容
        
        Args:
            file_path: 文档路径
            analysis_type: 分析类型 (summary, extract, qa)
        """
        # 读取文档内容
        content = self._read_document(file_path)
        
        prompts = {
            "summary": "请总结以下文档的主要内容:",
            "extract": "请从以下文档中提取关键信息:",
            "qa": "基于以下文档回答问题:"
        }
        
        prompt = f"""{prompts.get(analysis_type, prompts['summary'])}

文档内容:
{content[:8000]}  # 限制长度

请提供详细的分析结果。"""
        
        return self.client.chat(prompt)
    
    def _read_document(self, file_path: str) -> str:
        """读取文档内容"""
        path = Path(file_path)
        
        if path.suffix in ['.txt', '.md', '.py', '.js']:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        
        elif path.suffix == '.pdf':
            try:
                import pdfplumber
                with pdfplumber.open(path) as pdf:
                    return "\n".join(page.extract_text() or "" for page in pdf.pages)
            except ImportError:
                return "[需要安装 pdfplumber 来解析 PDF]"
        
        else:
            return f"[不支持的文件类型: {path.suffix}]"
    
    def batch_process_images(self, image_paths: List[str], prompt: str = None) -> List[Dict]:
        """
        批量处理图像
        """
        results = []
        
        for image_path in image_paths:
            try:
                result = self.process_image(image_path, prompt)
                results.append({
                    "path": image_path,
                    "status": "success",
                    "result": result
                })
            except Exception as e:
                results.append({
                    "path": image_path,
                    "status": "error",
                    "error": str(e)
                })
        
        return results
    
    def create_multimodal_response(
        self,
        text_query: str,
        image_paths: List[str] = None,
        document_paths: List[str] = None
    ) -> str:
        """
        创建多模态响应
        
        结合文本、图像和文档生成综合响应
        """
        context_parts = []
        
        # 处理图像
        if image_paths:
            for img_path in image_paths:
                img_analysis = self.process_image(img_path, "描述这张图片")
                context_parts.append(f"[图像分析] {img_analysis}")
        
        # 处理文档
        if document_paths:
            for doc_path in document_paths:
                doc_summary = self.analyze_document(doc_path, "summary")
                context_parts.append(f"[文档摘要] {doc_summary}")
        
        # 构建完整提示词
        full_prompt = f"""基于以下信息回答问题:

{chr(10).join(context_parts)}

用户问题: {text_query}

请综合以上信息提供全面的回答。"""
        
        return self.client.chat(full_prompt)


# 使用示例
def demonstrate_multimodal():
    """演示多模态处理"""
    
    print("=" * 60)
    print("DeerFlow 2.0 多模态处理演示")
    print("=" * 60)
    
    processor = MultimodalProcessor()
    
    # 1. 图像提示词生成
    print("\n1. 生成图像提示词")
    description = "一只在樱花树下睡觉的猫，日式风格，柔和光线"
    image_prompt = processor.generate_image_prompt(description)
    print(f"描述: {description}")
    print(f"生成的提示词: {image_prompt}")
    
    # 2. 文档分析
    print("\n2. 文档分析")
    # 创建一个示例文档
    sample_doc = "/tmp/sample_doc.txt"
    with open(sample_doc, 'w') as f:
        f.write("""
人工智能（AI）是计算机科学的一个分支，致力于创造能够模拟人类智能的系统。
主要应用领域包括：
- 自然语言处理
- 计算机视觉
- 机器学习
- 机器人技术

未来发展趋势包括更强大的大语言模型和多模态AI系统。
""")
    
    analysis = processor.analyze_document(sample_doc, "summary")
    print(f"文档摘要: {analysis}")
    
    # 3. 多模态综合查询
    print("\n3. 多模态综合查询")
    response = processor.create_multimodal_response(
        text_query="请总结所有信息",
        document_paths=[sample_doc]
    )
    print(f"综合响应: {response}")


if __name__ == "__main__":
    demonstrate_multimodal()
