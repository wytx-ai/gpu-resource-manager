"""
数据管理模块
负责GPU、任务和关联关系的数据存储和读取
"""
import json
import os
from typing import List, Dict, Optional


class DataManager:
    """数据管理器，使用JSON文件存储数据"""
    
    def __init__(self, data_file: str = "gpu_data.json"):
        """
        初始化数据管理器
        
        Args:
            data_file: 数据文件路径
        """
        self.data_file = data_file
        self.data = {
            "schemes": [],  # 分配方案列表（每个方案包含自己的gpus、tasks、allocations）
            "current_scheme_id": None  # 当前选中的方案ID
        }
        self.load_data()
        # 如果没有方案，创建默认方案
        if not self.data.get("schemes") or len(self.data.get("schemes", [])) == 0:
            self.create_default_scheme()
        # 如果没有当前方案，设置第一个方案为当前方案
        if self.data.get("current_scheme_id") is None and self.data.get("schemes"):
            self.data["current_scheme_id"] = self.data["schemes"][0]["id"]
            self.save_data()
    
    def load_data(self):
        """从JSON文件加载数据"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    # 兼容旧数据格式
                    if "schemes" not in loaded_data:
                        # 迁移旧数据到默认方案
                        self.data = {
                            "schemes": [],
                            "current_scheme_id": None
                        }
                        # 创建默认方案并迁移数据
                        scheme_id = self.create_default_scheme()
                        scheme = self.get_scheme(scheme_id)
                        if scheme:
                            # 迁移GPU列表
                            scheme["gpus"] = loaded_data.get("gpus", [])
                            # 迁移任务和分配
                            scheme["tasks"] = loaded_data.get("tasks", [])
                            scheme["allocations"] = loaded_data.get("allocations", [])
                            self.save_data()
                    else:
                        # 新格式数据，但需要检查是否有全局gpus需要迁移
                        self.data = loaded_data
                        # 如果有全局gpus，迁移到所有方案
                        if "gpus" in loaded_data and loaded_data["gpus"]:
                            global_gpus = loaded_data["gpus"]
                            for scheme in self.data.get("schemes", []):
                                if "gpus" not in scheme or not scheme.get("gpus"):
                                    scheme["gpus"] = global_gpus.copy()
                            # 删除全局gpus
                            if "gpus" in self.data:
                                del self.data["gpus"]
                            self.save_data()
                        # 确保每个方案都有gpus字段
                        for scheme in self.data.get("schemes", []):
                            if "gpus" not in scheme:
                                scheme["gpus"] = []
            except Exception as e:
                print(f"加载数据失败: {e}")
                self.data = {"schemes": [], "current_scheme_id": None}
        else:
            self.data = {"schemes": [], "current_scheme_id": None}
    
    def create_default_scheme(self):
        """创建默认方案"""
        scheme_id = max([s.get("id", 0) for s in self.data.get("schemes", [])], default=0) + 1
        scheme = {
            "id": scheme_id,
            "name": "默认方案",
            "gpus": [],  # 该方案的GPU列表
            "tasks": [],
            "allocations": []
        }
        self.data.setdefault("schemes", []).append(scheme)
        if self.data.get("current_scheme_id") is None:
            self.data["current_scheme_id"] = scheme_id
        self.save_data()
        return scheme_id
    
    def get_current_scheme(self):
        """获取当前方案"""
        scheme_id = self.data.get("current_scheme_id")
        if scheme_id:
            return self.get_scheme(scheme_id)
        return None
    
    def get_scheme(self, scheme_id):
        """获取指定方案"""
        for scheme in self.data.get("schemes", []):
            if scheme["id"] == scheme_id:
                return scheme
        return None
    
    def add_scheme(self, name: str) -> int:
        """
        添加方案
        
        Args:
            name: 方案名称
        
        Returns:
            新方案的ID
        """
        scheme_id = max([s.get("id", 0) for s in self.data.get("schemes", [])], default=0) + 1
        scheme = {
            "id": scheme_id,
            "name": name,
            "gpus": [],  # 该方案的GPU列表
            "tasks": [],
            "allocations": []
        }
        self.data.setdefault("schemes", []).append(scheme)
        self.save_data()
        return scheme_id
    
    def update_scheme(self, scheme_id: int, name: str) -> bool:
        """
        更新方案名称
        
        Args:
            scheme_id: 方案ID
            name: 方案名称
        
        Returns:
            是否成功
        """
        scheme = self.get_scheme(scheme_id)
        if scheme:
            scheme["name"] = name
            self.save_data()
            return True
        return False
    
    def delete_scheme(self, scheme_id: int) -> bool:
        """
        删除方案
        
        Args:
            scheme_id: 方案ID
        
        Returns:
            是否成功
        """
        self.data["schemes"] = [s for s in self.data.get("schemes", []) if s["id"] != scheme_id]
        # 如果删除的是当前方案，切换到第一个方案
        if self.data.get("current_scheme_id") == scheme_id:
            if self.data.get("schemes"):
                self.data["current_scheme_id"] = self.data["schemes"][0]["id"]
            else:
                self.data["current_scheme_id"] = None
        self.save_data()
        return True
    
    def set_current_scheme(self, scheme_id: int) -> bool:
        """
        设置当前方案
        
        Args:
            scheme_id: 方案ID
        
        Returns:
            是否成功
        """
        if self.get_scheme(scheme_id):
            self.data["current_scheme_id"] = scheme_id
            self.save_data()
            return True
        return False
    
    def get_all_schemes(self) -> List[Dict]:
        """获取所有方案"""
        return self.data.get("schemes", [])
    
    def save_data(self):
        """保存数据到JSON文件"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存数据失败: {e}")
            return False
    
    # ========== GPU管理 ==========
    
    def add_gpu(self, name: str, total_memory: float) -> int:
        """
        添加GPU（当前方案）
        
        Args:
            name: GPU名称
            total_memory: 总显存（GB）
        
        Returns:
            新GPU的ID
        """
        scheme = self.get_current_scheme()
        if not scheme:
            scheme_id = self.create_default_scheme()
            scheme = self.get_scheme(scheme_id)
        
        gpus = scheme.get("gpus", [])
        gpu_id = max([gpu.get("id", 0) for gpu in gpus], default=0) + 1
        gpu = {
            "id": gpu_id,
            "name": name,
            "total_memory": total_memory
        }
        gpus.append(gpu)
        scheme["gpus"] = gpus
        self.save_data()
        return gpu_id
    
    def update_gpu(self, gpu_id: int, name: str, total_memory: float) -> bool:
        """
        更新GPU信息（当前方案）
        
        Args:
            gpu_id: GPU ID
            name: GPU名称
            total_memory: 总显存（GB）
        
        Returns:
            是否成功
        """
        scheme = self.get_current_scheme()
        if not scheme:
            return False
        
        gpus = scheme.get("gpus", [])
        for gpu in gpus:
            if gpu["id"] == gpu_id:
                gpu["name"] = name
                gpu["total_memory"] = total_memory
                scheme["gpus"] = gpus
                self.save_data()
                return True
        return False
    
    def delete_gpu(self, gpu_id: int) -> bool:
        """
        删除GPU（当前方案，同时删除相关分配）
        
        Args:
            gpu_id: GPU ID
        
        Returns:
            是否成功
        """
        scheme = self.get_current_scheme()
        if not scheme:
            return False
        
        # 删除GPU
        gpus = scheme.get("gpus", [])
        scheme["gpus"] = [gpu for gpu in gpus if gpu["id"] != gpu_id]
        
        # 删除相关分配
        allocations = scheme.get("allocations", [])
        scheme["allocations"] = [
            alloc for alloc in allocations
            if alloc["gpu_id"] != gpu_id
        ]
        self.save_data()
        return True
    
    def get_gpu(self, gpu_id: int) -> Optional[Dict]:
        """获取GPU信息（当前方案）"""
        scheme = self.get_current_scheme()
        if not scheme:
            return None
        
        for gpu in scheme.get("gpus", []):
            if gpu["id"] == gpu_id:
                return gpu
        return None
    
    def get_all_gpus(self) -> List[Dict]:
        """获取所有GPU（当前方案）"""
        scheme = self.get_current_scheme()
        if not scheme:
            return []
        return scheme.get("gpus", [])
    
    # ========== 任务管理 ==========
    
    def add_task(self, name: str, description: str = "") -> int:
        """
        添加任务（添加到当前方案）
        
        Args:
            name: 任务名称
            description: 任务描述
        
        Returns:
            新任务的ID
        """
        scheme = self.get_current_scheme()
        if not scheme:
            scheme_id = self.create_default_scheme()
            scheme = self.get_scheme(scheme_id)
        
        tasks = scheme.get("tasks", [])
        task_id = max([task.get("id", 0) for task in tasks], default=0) + 1
        task = {
            "id": task_id,
            "name": name,
            "description": description
        }
        tasks.append(task)
        scheme["tasks"] = tasks
        self.save_data()
        return task_id
    
    def update_task(self, task_id: int, name: str, description: str = "") -> bool:
        """
        更新任务信息（当前方案）
        
        Args:
            task_id: 任务ID
            name: 任务名称
            description: 任务描述
        
        Returns:
            是否成功
        """
        scheme = self.get_current_scheme()
        if not scheme:
            return False
        
        tasks = scheme.get("tasks", [])
        for task in tasks:
            if task["id"] == task_id:
                task["name"] = name
                task["description"] = description
                scheme["tasks"] = tasks
                self.save_data()
                return True
        return False
    
    def delete_task(self, task_id: int) -> bool:
        """
        删除任务（同时删除相关分配，当前方案）
        
        Args:
            task_id: 任务ID
        
        Returns:
            是否成功
        """
        scheme = self.get_current_scheme()
        if not scheme:
            return False
        
        # 删除任务
        tasks = scheme.get("tasks", [])
        scheme["tasks"] = [task for task in tasks if task["id"] != task_id]
        
        # 删除相关分配
        allocations = scheme.get("allocations", [])
        scheme["allocations"] = [
            alloc for alloc in allocations
            if alloc["task_id"] != task_id
        ]
        self.save_data()
        return True
    
    def get_task(self, task_id: int) -> Optional[Dict]:
        """获取任务信息（当前方案）"""
        scheme = self.get_current_scheme()
        if not scheme:
            return None
        
        for task in scheme.get("tasks", []):
            if task["id"] == task_id:
                return task
        return None
    
    def get_all_tasks(self) -> List[Dict]:
        """获取所有任务（当前方案）"""
        scheme = self.get_current_scheme()
        if not scheme:
            return []
        return scheme.get("tasks", [])
    
    # ========== 分配管理 ==========
    
    def add_allocation(self, task_id: int, gpu_id: int, memory_usage: float) -> bool:
        """
        添加任务-GPU分配（当前方案）
        
        Args:
            task_id: 任务ID
            gpu_id: GPU ID
            memory_usage: 显存占用（GB）
        
        Returns:
            是否成功
        """
        scheme = self.get_current_scheme()
        if not scheme:
            return False
        
        allocations = scheme.get("allocations", [])
        # 检查是否已存在
        for alloc in allocations:
            if alloc["task_id"] == task_id and alloc["gpu_id"] == gpu_id:
                # 更新现有分配
                alloc["memory_usage"] = memory_usage
                scheme["allocations"] = allocations
                self.save_data()
                return True
        
        # 添加新分配
        allocation = {
            "task_id": task_id,
            "gpu_id": gpu_id,
            "memory_usage": memory_usage
        }
        allocations.append(allocation)
        scheme["allocations"] = allocations
        self.save_data()
        return True
    
    def delete_allocation(self, task_id: int, gpu_id: int) -> bool:
        """
        删除任务-GPU分配（当前方案）
        
        Args:
            task_id: 任务ID
            gpu_id: GPU ID
        
        Returns:
            是否成功
        """
        scheme = self.get_current_scheme()
        if not scheme:
            return False
        
        allocations = scheme.get("allocations", [])
        scheme["allocations"] = [
            alloc for alloc in allocations
            if not (alloc["task_id"] == task_id and alloc["gpu_id"] == gpu_id)
        ]
        self.save_data()
        return True
    
    def get_allocations_by_gpu(self, gpu_id: int) -> List[Dict]:
        """获取指定GPU的所有分配（当前方案）"""
        scheme = self.get_current_scheme()
        if not scheme:
            return []
        
        return [
            alloc for alloc in scheme.get("allocations", [])
            if alloc["gpu_id"] == gpu_id
        ]
    
    def get_allocations_by_task(self, task_id: int) -> List[Dict]:
        """获取指定任务的所有分配（当前方案）"""
        scheme = self.get_current_scheme()
        if not scheme:
            return []
        
        return [
            alloc for alloc in scheme.get("allocations", [])
            if alloc["task_id"] == task_id
        ]
    
    def get_all_allocations(self) -> List[Dict]:
        """获取所有分配（当前方案）"""
        scheme = self.get_current_scheme()
        if not scheme:
            return []
        return scheme.get("allocations", [])
    
    def get_gpu_usage(self, gpu_id: int) -> Dict:
        """
        获取GPU使用情况（当前方案）
        
        Args:
            gpu_id: GPU ID
        
        Returns:
            {
                "gpu": GPU信息,
                "total_memory": 总显存,
                "used_memory": 已用显存,
                "free_memory": 剩余显存,
                "allocations": 分配列表（包含任务信息）
            }
        """
        gpu = self.get_gpu(gpu_id)
        if not gpu:
            return None
        
        allocations = self.get_allocations_by_gpu(gpu_id)
        used_memory = sum(alloc["memory_usage"] for alloc in allocations)
        
        # 为每个分配添加任务信息
        allocations_with_task = []
        for alloc in allocations:
            task = self.get_task(alloc["task_id"])
            if task:
                allocations_with_task.append({
                    **alloc,
                    "task_name": task["name"]
                })
        
        return {
            "gpu": gpu,
            "total_memory": gpu["total_memory"],
            "used_memory": used_memory,
            "free_memory": gpu["total_memory"] - used_memory,
            "allocations": allocations_with_task
        }


