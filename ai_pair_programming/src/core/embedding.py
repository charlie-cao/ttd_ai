"""
嵌入向量管理模块
--------------
处理文本到向量的转换，支持多种嵌入模型。
"""

import torch
from transformers import AutoTokenizer, AutoModel
import numpy as np
from typing import Optional, Dict, Any
from pathlib import Path
import json

class EmbeddingManager:
    """嵌入向量管理器"""
    
    def __init__(
        self,
        model_name: str = "shibing624/text2vec-base-chinese",
        device: Optional[str] = None,
        cache_dir: Optional[str] = None
    ):
        """
        初始化嵌入向量管理器
        
        Args:
            model_name: 模型名称或路径
            device: 运行设备 ('cuda', 'cpu' 或具体的 'cuda:0' 等)
            cache_dir: 模型缓存目录
        """
        self.model_name = model_name
        self.cache_dir = cache_dir
        
        # 设置设备
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
        
        # 加载模型和分词器
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir)
        self.model = AutoModel.from_pretrained(model_name, cache_dir=cache_dir)
        self.model.to(self.device)
        
        # 模型配置
        self.max_length = 512
        self.pooling_strategy = "mean"  # mean, cls, max
    
    def get_embedding(self, text: str) -> np.ndarray:
        """
        获取文本的嵌入向量
        
        Args:
            text: 输入文本
            
        Returns:
            numpy.ndarray: 嵌入向量
        """
        # 准备输入
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=self.max_length
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # 获取嵌入
        with torch.no_grad():
            outputs = self.model(**inputs)
            embeddings = outputs.last_hidden_state
            
            # 池化策略
            if self.pooling_strategy == "mean":
                embeddings = embeddings.mean(dim=1)
            elif self.pooling_strategy == "cls":
                embeddings = embeddings[:, 0]
            elif self.pooling_strategy == "max":
                embeddings = embeddings.max(dim=1)[0]
        
        return embeddings.cpu().numpy()[0]
    
    def batch_get_embeddings(self, texts: list[str], batch_size: int = 32) -> np.ndarray:
        """
        批量获取文本的嵌入向量
        
        Args:
            texts: 文本列表
            batch_size: 批处理大小
            
        Returns:
            numpy.ndarray: 嵌入向量数组
        """
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            inputs = self.tokenizer(
                batch_texts,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=self.max_length
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                batch_embeddings = outputs.last_hidden_state
                
                if self.pooling_strategy == "mean":
                    batch_embeddings = batch_embeddings.mean(dim=1)
                elif self.pooling_strategy == "cls":
                    batch_embeddings = batch_embeddings[:, 0]
                elif self.pooling_strategy == "max":
                    batch_embeddings = batch_embeddings.max(dim=1)[0]
                
                embeddings.append(batch_embeddings.cpu().numpy())
        
        return np.concatenate(embeddings, axis=0)
    
    def save_config(self, path: str):
        """
        保存配置到文件
        
        Args:
            path: 配置文件路径
        """
        config = {
            "model_name": self.model_name,
            "device": str(self.device),
            "cache_dir": self.cache_dir,
            "max_length": self.max_length,
            "pooling_strategy": self.pooling_strategy
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    @classmethod
    def from_config(cls, path: str) -> "EmbeddingManager":
        """
        从配置文件加载
        
        Args:
            path: 配置文件路径
            
        Returns:
            EmbeddingManager: 管理器实例
        """
        with open(path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        instance = cls(
            model_name=config["model_name"],
            device=config["device"],
            cache_dir=config["cache_dir"]
        )
        instance.max_length = config["max_length"]
        instance.pooling_strategy = config["pooling_strategy"]
        
        return instance
    
    def __repr__(self) -> str:
        return f"EmbeddingManager(model={self.model_name}, device={self.device})" 