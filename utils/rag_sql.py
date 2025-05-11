import MySQLdb
from pyobvector import *
from sqlalchemy import Column, BigInteger, Text, String, DateTime, func
from typing import Optional, List

import json
import uuid
import os, sys
currunt_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(currunt_dir, ".."))
from utils.embedding import EmbeddingModel
from utils.chunk_split import semantic_split

with open(os.path.join(currunt_dir, "..", "config", "sql_config.json"), "r") as f:
    OCEANBASE_CONFIG = json.load(f)

def delete_database(database_name: str = "search_rag") -> None:
    conn = MySQLdb.connect(**OCEANBASE_CONFIG)
    conn.autocommit(True)
    cursor = conn.cursor()
    try:
        cursor.execute(f"DROP DATABASE IF EXISTS {database_name};")
        print(f"[OK] 数据库 {database_name} 删除或不存在")
    except MySQLdb.Error as e:
        print("[ERROR] 删除数据库失败:", e)
    finally:
        cursor.close()
        conn.close()

def check_oceanbase_version():
    conn = MySQLdb.connect(**OCEANBASE_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT @@version")
    version = cursor.fetchone()[0]
    print(f"OceanBase 版本: {version}")
    cursor.close()
    conn.close()   

class RAGDatabase:
    def __init__(self, database: str = "search_rag", dim: int = 384):
        """
        :param database: 要操作的数据库
        :param dim: 嵌入向量维度
        """
        self.database = database
        if not self._database_create():
            raise Exception(f"[ERROR] 数据库 {self.database} 出错")

        self.client = ObVecClient(
            uri=OCEANBASE_CONFIG["host"] + ":" + str(OCEANBASE_CONFIG["port"]), 
            user=OCEANBASE_CONFIG["user"], 
            db_name=self.database
        )
        self.dim = dim
        
        self._table_create()
        self.embedder = EmbeddingModel()

    def __del__(self):
        pass
    
    def _database_create(self) -> None:
        conn = MySQLdb.connect(**OCEANBASE_CONFIG)
        conn.autocommit(True)
        cursor = conn.cursor()
        success = True
        try:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database};")
            print(f"[OK] 数据库 {self.database} 创建或已存在")
        except MySQLdb.Error as e:
            print("[ERROR] 创建数据库失败:", e)
            success = False
        finally:
            cursor.close()
            conn.close()
            return success

    def _table_create(self) -> None:
        """
        创建RAG数据表
        """
        # 原文表
        docs_cols = [
            Column('document_id', String(36), primary_key=True),
            Column('created_at', DateTime, server_default=func.now()),
            Column('source', String(128)),
            Column('author', String(128)),
            Column('title', String(256)),
            Column('content', Text),
        ]
        self.client.create_table('original', columns=docs_cols)

        # 章节表
        section_cols = [
            Column('section_id', String(36), primary_key=True),
            Column('document_id', String(36)),
            Column('text', Text)
        ]
        self.client.create_table('section', columns=section_cols)

        # 分块表
        chunks_cols = [
            Column('id', BigInteger, primary_key=True, autoincrement=True),
            Column('section_id', String(36)),
            Column('chunk_text', Text, nullable=False),
            Column('embedding', VECTOR(self.dim), nullable=False),
        ]
        self.client.create_table("chunks", columns=chunks_cols)
        print(f"[OK] Tables created or exists.")

        # 向量索引
        idx_name = f"embedding_hnsw_idx"
        self.client.create_index(
            "chunks",
            is_vec_index=True,
            index_name=idx_name,
            column_names=['embedding'],
            vidx_params="distance=l2, type=hnsw, lib=vsag",
        )
        print(f"[OK] Vector index '{idx_name}' ready.")

    def insert_data(self, content: str, title: str = None, source: Optional[str] = None, author: Optional[str] = None):
        doc_id = str(uuid.uuid4())
        self.client.insert("original", data=[{
            "document_id": doc_id,
            "title": title,
            "content": content,
            "source": source,
            "author": author
        }])

        for section_text in semantic_split(content, mode="section"):
            section_id = str(uuid.uuid4())
            self.client.insert("section", data=[{
                "section_id": section_id,
                "document_id": doc_id,
                "text": section_text
            }])
            chunks = semantic_split(section_text, mode="chunk")
            chunk_records = []
            for chunk_text in chunks:
                embedding = self.embedder.embed(chunk_text)
                chunk_records.append({
                    "section_id": section_id,
                    "chunk_text": chunk_text,
                    "embedding": embedding
                })
            self.client.insert("chunks", data=chunk_records)
        print(f"[OK] 文档 '{title}' 分块插入完成。")

    def query(self, text: str, top_k: int = 5):
        qvec = self.embedder.embed(text)
        res = self.client.ann_search(
            "chunks",
            vec_data=qvec,
            vec_column_name="embedding",
            distance_func=l2_distance,
            topk=top_k,
            with_dist=True,
            output_column_names=["chunk_text", "section_id"]
        )
        results = []
        for chunk_text, section_id, dist in res.all():
            section = self.client.get(
                "section", 
                ids=section_id, 
                output_column_name=["document_id", "text"]
                ).all()
            doc_id = section[0]
            doc = self.client.get(
                "original", 
                ids=doc_id, 
                output_column_name=["content", "source", "author", "title"]
                ).all()
            results.append({
                "chunk": chunk_text,
                "section": section[1],
                "document": doc[0],
                "title": doc[3],
                "source": doc[1],
                "author": doc[2],
                "similarity": dist
            })
        return results

# 使用示例
if __name__ == "__main__":
    # check_oceanbase_version()
    client = ObVecClient(
        uri=OCEANBASE_CONFIG["host"] + ":" + str(OCEANBASE_CONFIG["port"]), 
        user=OCEANBASE_CONFIG["user"], 
        db_name="search_rag"
    )
    res = client.get(
        "test_rag",
        1,
        output_column_name=["chunk_text","source","sub_id"]).all()
    print(res)
    # print(OCEANBASE_CONFIG)
    # import time
    # t1 = time.time()
    # rag = RAGDatabase()
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
