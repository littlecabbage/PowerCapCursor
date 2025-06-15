"""
核心任务示例模块
"""
import asyncio
from typing import Any, Dict, List

from celery_app.tasks.base_task import BaseTask, CompositeTask, WorkflowTask


class DataProcessTask(BaseTask):
    """数据处理任务"""
    name = "data_process_task"
    
    async def run(self, data: List[Dict[str, Any]], **kwargs: Any) -> List[Dict[str, Any]]:
        """处理数据列表"""
        # 模拟数据处理
        await asyncio.sleep(2)
        processed_data = []
        for item in data:
            processed_item = {
                **item,
                "processed": True,
                "timestamp": asyncio.get_running_loop().time()
            }
            processed_data.append(processed_item)
        return processed_data


class DataValidationTask(BaseTask):
    """数据验证任务"""
    name = "data_validation_task"
    
    async def run(self, data: List[Dict[str, Any]], **kwargs: Any) -> Dict[str, Any]:
        """验证数据"""
        # 模拟数据验证
        await asyncio.sleep(1)
        valid_count = 0
        invalid_count = 0
        errors = []
        
        for item in data:
            if all(key in item for key in ["id", "value"]):
                valid_count += 1
            else:
                invalid_count += 1
                errors.append(f"Missing required fields in item: {item}")
        
        return {
            "valid_count": valid_count,
            "invalid_count": invalid_count,
            "errors": errors
        }


class DataPipelineTask(CompositeTask):
    """数据处理管道任务"""
    name = "data_pipeline_task"
    
    def __init__(self):
        super().__init__()
        # 添加子任务
        self.add_subtask(DataProcessTask())
        self.add_subtask(DataValidationTask())


class ETLWorkflowTask(WorkflowTask):
    """ETL工作流任务"""
    name = "etl_workflow_task"
    
    def __init__(self):
        super().__init__()
        # 定义工作流步骤
        self.add_step("extract", ExtractTask())
        self.add_step("transform", TransformTask(), depends_on=["extract"])
        self.add_step("load", LoadTask(), depends_on=["transform"])
        self.add_step("validate", DataValidationTask(), depends_on=["load"])


class ExtractTask(BaseTask):
    """数据提取任务"""
    name = "extract_task"
    
    async def run(self, source: str, **kwargs: Any) -> List[Dict[str, Any]]:
        """从数据源提取数据"""
        # 模拟数据提取
        await asyncio.sleep(2)
        return [
            {"id": 1, "value": "data1"},
            {"id": 2, "value": "data2"},
            {"id": 3, "value": "data3"}
        ]


class TransformTask(BaseTask):
    """数据转换任务"""
    name = "transform_task"
    
    async def run(self, data: List[Dict[str, Any]], **kwargs: Any) -> List[Dict[str, Any]]:
        """转换数据格式"""
        # 模拟数据转换
        await asyncio.sleep(1.5)
        return [
            {
                **item,
                "transformed": True,
                "value_upper": item["value"].upper()
            }
            for item in data
        ]


class LoadTask(BaseTask):
    """数据加载任务"""
    name = "load_task"
    
    async def run(self, data: List[Dict[str, Any]], **kwargs: Any) -> Dict[str, Any]:
        """加载数据到目标存储"""
        # 模拟数据加载
        await asyncio.sleep(1)
        return {
            "loaded_count": len(data),
            "success": True,
            "target": kwargs.get("target", "default_storage")
        } 