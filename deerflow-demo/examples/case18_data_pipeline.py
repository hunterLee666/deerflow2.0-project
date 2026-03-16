"""
案例 18: DeerFlow 2.0 数据管道集成
完整代码示例 - ETL、数据转换、批处理
"""

from deerflow.client import DeerFlowClient
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import json
import csv
import asyncio
from pathlib import Path


@dataclass
class DataRecord:
    """数据记录"""
    id: str
    source: str
    content: str
    metadata: Dict
    timestamp: datetime


class DataExtractor:
    """数据提取器"""
    
    def extract_from_csv(self, filepath: str) -> List[DataRecord]:
        """从 CSV 提取数据"""
        records = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                records.append(DataRecord(
                    id=f"csv-{i}",
                    source=filepath,
                    content=json.dumps(row),
                    metadata={"format": "csv", "row": i},
                    timestamp=datetime.now()
                ))
        return records
    
    def extract_from_json(self, filepath: str) -> List[DataRecord]:
        """从 JSON 提取数据"""
        records = []
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                for i, item in enumerate(data):
                    records.append(DataRecord(
                        id=f"json-{i}",
                        source=filepath,
                        content=json.dumps(item),
                        metadata={"format": "json", "index": i},
                        timestamp=datetime.now()
                    ))
        return records
    
    def extract_from_text(self, filepath: str) -> List[DataRecord]:
        """从文本文件提取数据"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return [DataRecord(
            id="text-0",
            source=filepath,
            content=content,
            metadata={"format": "text"},
            timestamp=datetime.now()
        )]


class DataTransformer:
    """数据转换器"""
    
    def __init__(self, client: DeerFlowClient = None):
        self.client = client or DeerFlowClient()
    
    def transform_with_ai(self, record: DataRecord, instruction: str) -> DataRecord:
        """使用 AI 转换数据"""
        prompt = f"""{instruction}

输入数据:
{record.content}

请直接输出转换后的结果，不要添加解释。"""
        
        response = self.client.chat(prompt)
        
        return DataRecord(
            id=f"{record.id}-transformed",
            source=record.source,
            content=response,
            metadata={**record.metadata, "transformed": True, "instruction": instruction},
            timestamp=datetime.now()
        )
    
    def summarize(self, record: DataRecord) -> DataRecord:
        """摘要转换"""
        return self.transform_with_ai(
            record,
            "请对以下内容进行摘要，提取关键信息："
        )
    
    def translate(self, record: DataRecord, target_lang: str = "英文") -> DataRecord:
        """翻译转换"""
        return self.transform_with_ai(
            record,
            f"请将以下内容翻译成{target_lang}："
        )
    
    def classify(self, record: DataRecord, categories: List[str]) -> DataRecord:
        """分类转换"""
        result = self.transform_with_ai(
            record,
            f"请将以下内容分类到以下类别之一：{', '.join(categories)}。只输出类别名称。"
        )
        
        # 添加分类结果到元数据
        result.metadata["category"] = result.content.strip()
        return result
    
    def extract_entities(self, record: DataRecord) -> DataRecord:
        """实体提取"""
        return self.transform_with_ai(
            record,
            "请从以下内容中提取所有命名实体（人名、地名、组织名等），以 JSON 格式输出。"
        )


class DataLoader:
    """数据加载器"""
    
    def load_to_csv(self, records: List[DataRecord], filepath: str):
        """加载到 CSV"""
        if not records:
            return
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'source', 'content', 'metadata', 'timestamp'])
            
            for record in records:
                writer.writerow([
                    record.id,
                    record.source,
                    record.content,
                    json.dumps(record.metadata),
                    record.timestamp.isoformat()
                ])
    
    def load_to_json(self, records: List[DataRecord], filepath: str):
        """加载到 JSON"""
        data = [
            {
                "id": r.id,
                "source": r.source,
                "content": r.content,
                "metadata": r.metadata,
                "timestamp": r.timestamp.isoformat()
            }
            for r in records
        ]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def load_to_database(self, records: List[DataRecord], connection_string: str):
        """加载到数据库（示例）"""
        # 实际实现需要数据库连接
        print(f"加载 {len(records)} 条记录到数据库")
        for record in records:
            print(f"  - {record.id}: {record.content[:50]}...")


class DataPipeline:
    """数据管道"""
    
    def __init__(self):
        self.extractor = DataExtractor()
        self.transformer = DataTransformer()
        self.loader = DataLoader()
        self.steps: List[Callable] = []
    
    def add_step(self, step: Callable):
        """添加处理步骤"""
        self.steps.append(step)
        return self
    
    def process(self, source: str, source_type: str = "auto") -> List[DataRecord]:
        """处理数据"""
        # 1. 提取
        if source_type == "auto":
            ext = Path(source).suffix.lower()
            if ext == '.csv':
                source_type = "csv"
            elif ext == '.json':
                source_type = "json"
            else:
                source_type = "text"
        
        if source_type == "csv":
            records = self.extractor.extract_from_csv(source)
        elif source_type == "json":
            records = self.extractor.extract_from_json(source)
        else:
            records = self.extractor.extract_from_text(source)
        
        print(f"提取了 {len(records)} 条记录")
        
        # 2. 转换
        for step in self.steps:
            records = [step(r) for r in records]
        
        print(f"转换完成")
        
        return records
    
    def process_batch(
        self,
        sources: List[str],
        output_path: str,
        output_format: str = "json"
    ):
        """批处理"""
        all_records = []
        
        for source in sources:
            print(f"\n处理: {source}")
            records = self.process(source)
            all_records.extend(records)
        
        # 3. 加载
        if output_format == "csv":
            self.loader.load_to_csv(all_records, output_path)
        else:
            self.loader.load_to_json(all_records, output_path)
        
        print(f"\n完成！输出到: {output_path}")


# 使用示例
def demonstrate_pipeline():
    """演示数据管道"""
    
    print("=" * 60)
    print("DeerFlow 2.0 数据管道演示")
    print("=" * 60)
    
    # 创建示例数据文件
    sample_csv = "/tmp/sample_data.csv"
    with open(sample_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['title', 'content'])
        writer.writerow(['AI发展', '人工智能正在快速发展，机器学习是核心技术'])
        writer.writerow(['量子计算', '量子计算将改变密码学和药物发现'])
        writer.writerow(['区块链', '区块链技术在金融领域有广泛应用'])
    
    print(f"\n创建示例数据: {sample_csv}")
    
    # 创建管道
    pipeline = DataPipeline()
    
    # 添加转换步骤
    pipeline.add_step(lambda r: pipeline.transformer.summarize(r))
    
    # 处理数据
    print("\n处理数据...")
    records = pipeline.process(sample_csv, "csv")
    
    # 显示结果
    print("\n处理结果:")
    for record in records:
        print(f"\nID: {record.id}")
        print(f"摘要: {record.content}")


if __name__ == "__main__":
    demonstrate_pipeline()
