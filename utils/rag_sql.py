import MySQLdb
from pyobvector import *

import json
import os, sys
currunt_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(currunt_dir, ".."))
from utils.embedding import EmbeddingModel

with open(os.path.join(currunt_dir, "..", "config", "sql_config.json"), "r") as f:
    OCEANBASE_CONFIG = json.load(f)

class RAGDatabase:
    def __init__(self, table: str, dim: int = 384):
        """
        :param table: 要操作的表名
        :param dim: 嵌入向量维度
        """
        self.db = MySQLdb.connect(**OCEANBASE_CONFIG)
        self.db.autocommit(False)
        self.vec_client = ObVecClient(
            uri=OCEANBASE_CONFIG["host"] + ":" + str(OCEANBASE_CONFIG["port"]), 
            user=OCEANBASE_CONFIG["user"], 
            db_name=OCEANBASE_CONFIG["database"],
            password=OCEANBASE_CONFIG["password"]
        )

        self.table = table
        self.dim = dim
        
        self.create()
        self.embedder = EmbeddingModel()

    def __del__(self):
        try:
            self.db.close()
        except Exception:
            pass

    def create(self) -> None:
        """
        创建RAG数据表
        字段名	        类型	        说明
        id          INT             UNSIGNED AUTO_INCREMENT	主键
        chunk_text	TEXT	        存储文本片段
        embedding	VECTOR(384)	    原生向量列（384维，可改）
        source      VARCHAR(128)	来源标识：URL / 书籍ID
        sub_id	    VARCHAR(128)	来源内部标识：如章节+段落编号
        created_at	DATETIME	    插入时间
        """
        sql = f"""
        CREATE TABLE IF NOT EXISTS {self.table} (
             id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
             chunk_text TEXT NOT NULL,
             embedding VECTOR({self.dim}) NOT NULL,
             source VARCHAR(128),
             sub_id VARCHAR(128),
             created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
             PRIMARY KEY(id)
        ) ENGINE=OCEANBASE;
        """
        with self.db.cursor() as cur:
            cur.execute(sql)
        self.db.commit()
        print(f"[OK] Table `{self.table}` ready.")
        self.create_index(
            idx_name=f"{self.table}_hnsw_idx",
            distance="l2",
            idx_type="hnsw",
            lib="vsag"
        )

    def create_index(self,
                     idx_name: str,
                     distance: str = "l2",
                     idx_type: str = "hnsw",
                     lib: str = "vsag") -> None:
        """
        单独创建向量索引：
          - 先检测 embedding 列上是否已有向量索引，若有则跳过
          - 支持参数：distance=l2|inner_product, type=hnsw|hnsw_sq|ivf_flat,
                       lib=vsag|ob, m, ef_construction, ef_search
        """
        # 1) 检查已有索引
        with self.db.cursor() as cur:
            cur.execute(f"SHOW INDEX FROM {self.table}")
            for row in cur.fetchall():
                # row[4] 是 Column_name, row[10] 是 Index_type
                if row[4] == "embedding" and row[10] == "VECTOR":
                    print(f"[WARN] Table `{self.table}` column `embedding` already has a vector index, skip creation.")
                    return

        # 2) 组装 WITH 子句
        clauses = [f"distance={distance}", f"type={idx_type}", f"lib={lib}"]
        params = ", ".join(clauses)

        sql = f"""
        CREATE VECTOR INDEX {idx_name}
          ON {self.table} (embedding)
          WITH ({params});
        """
        # 3) 尝试创建
        with self.db.cursor() as cur:
            cur.execute(sql)
        self.db.commit()
        print(f"[OK] Index `{idx_name}` on `{self.table}` created.")
    
    def insert(self, text, source=None, sub_id=None):
        vec = self.embedder.embed(text)
        data = {
            "chunk_text": text, 
            "source": source, 
            "sub_id": sub_id,
            "embedding": vec
        }
        self.vec_client.insert(self.table, data=[data])

    def query(self, text, top_k=5, filters=None):
        qvec = self.embedder.embed(text)
        res = self.vec_client.ann_search(
            self.table, 
            vec_data=qvec, 
            vec_column_name='embedding',
            distance_func=l2_distance,
            topk=top_k,
            with_dist=True,
            output_column_names=["chunk_text", "source", "sub_id"],
            filter_conditions=filters or {}
        )
        results_list = res.all()
        rank = sorted(results_list, key=lambda x: x[-1], reverse=True)
        return rank

# 使用示例
if __name__ == "__main__":
    print(OCEANBASE_CONFIG)
    # import time
    # t1 = time.time()
    # rag = RAGDatabase(table="test_rag")
    # t2 = time.time()
    # print(f"RAGDatabase 初始化耗时: {t2 - t1:.2f}秒")
    # rag.insert("新测试！", source="https://example.com", sub_id="p1")
    
    # results = rag.query("你好", top_k=3)
    # t3 = time.time()
    # print(f"RAGDatabase 查询耗时: {t3 - t2:.2f}秒")
    # print("查询结果：")

    # print(results)
    # for result in results:
    #     print(result)
