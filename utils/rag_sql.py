from pymilvus import MilvusClient

import pymysql as MySQLdb
from pyobvector import *
from sqlalchemy import Column, BigInteger, Text, String, DateTime, func
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from typing import Optional

import json
import uuid
import os, sys
currunt_dir = os.path.dirname(__file__)
sys.path.append(currunt_dir)
from embedding import EmbeddingModel
from chunk_split import semantic_split

with open(os.path.join(currunt_dir, "sql_config.json"), "r") as f:
    OCEANBASE_CONFIG = json.load(f)

def config_database() -> None:
    try:
        conn = MySQLdb.connect(charset="utf8mb4", **OCEANBASE_CONFIG)
        conn.autocommit(True)
        cursor = conn.cursor()
        cursor.execute("ALTER SYSTEM SET memstore_limit_percentage = 30")
        cursor.execute("ALTER SYSTEM SET ob_vector_memory_limit_percentage = 50")
        print("[INFO] 数据库配置修改成功")
    except MySQLdb.Error as e:
        print("[ERROR] 修改数据库失败:", e)

def list_databases() -> None:
    conn = MySQLdb.connect(**OCEANBASE_CONFIG)
    conn.autocommit(True)
    cursor = conn.cursor()
    try:
        cursor.execute("SHOW DATABASES;")
        databases = [row[0] for row in cursor.fetchall()]
        print("[OK] 当前数据库列表：")
        for db in databases:
            print(f"  - {db}")
    except MySQLdb.Error as e:
        print("[ERROR] 查询数据库列表失败:", e)
    finally:
        cursor.close()
        conn.close()

def delete_database(database_name: str = "search_rag") -> None:
    conn = MySQLdb.connect(**OCEANBASE_CONFIG)
    conn.autocommit(True)
    cursor = conn.cursor()
    client = MilvusClient(
        uri="http://localhost:19530",
        token="root:Milvus"
    )
    try:
        cursor.execute(f"DROP DATABASE IF EXISTS {database_name};")
        client.drop_collection(
            collection_name=database_name
        )
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
    def __init__(self, database: str = "search_rag", dim: int = 1024):
        """
        :param database: 要操作的数据库
        :param dim: 嵌入向量维度
        """
        self.database = database
        self.dim = dim
        self.embedder = EmbeddingModel()

        if not self._database_create():
            raise Exception(f"[ERROR] 数据库 {self.database} 出错")
        
        self.client = ObVecClient(
            uri=OCEANBASE_CONFIG["host"] + ":" + str(OCEANBASE_CONFIG["port"]), 
            user=OCEANBASE_CONFIG["user"], 
            password=OCEANBASE_CONFIG["password"] if "password" in OCEANBASE_CONFIG else "",
            db_name=self.database
        )
        self.milvus = MilvusClient(
            uri="http://localhost:19530", 
            token="root:Milvus"
        )

        self._table_create()

        
    def __del__(self):
        self.client.engine.clear_compiled_cache()
        self.client.engine
    
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
            Column('source', String(512)),
            Column('description', Text),
            Column('title', String(256)),
            Column('content', MEDIUMTEXT),
        ]
        self.client.create_table('original', columns=docs_cols)

        # 分块表
        if not self.milvus.has_collection(self.database):
            schema = MilvusClient.create_schema(
                auto_id=True,
                enable_dynamic_field=True,
            )
            schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True)
            schema.add_field(field_name="document_id", datatype=DataType.VARCHAR, max_length=36)
            schema.add_field(field_name="chunk_text", datatype=DataType.VARCHAR, max_length=2048)
            schema.add_field(field_name="embedding", datatype=DataType.FLOAT_VECTOR, dim=self.dim)

            index_params = self.milvus.prepare_index_params()
            index_params.add_index(
                field_name="id",
                index_type="AUTOINDEX"
            )

            index_params.add_index(
                field_name="embedding", 
                index_type="AUTOINDEX",
                metric_type="COSINE"
            )

            self.milvus.create_collection(
                collection_name=self.database,
                schema=schema,
                index_params=index_params
            )

        res = self.milvus.get_load_state(
            collection_name=self.database
        )
        print(f"[OK] Vector index {res}.")
        
        print(f"[OK] Tables created or exists.")

    def insert_data(self, content: str, title: str = None, source: Optional[str] = None, description: Optional[str] = None):
        doc_id = str(uuid.uuid4())
        self.client.insert(
            "original", 
            data=[{
                "document_id": doc_id,
                "title": title,
                "content": content,
                "source": source,
                "description": description
        }])

        # chunks = semantic_split(content)
        # milvus_data = [{
        #     "document_id": doc_id,
        #     "chunk_text": chunk,
        #     "embedding": self.embedder.embed(chunk)
        # } for chunk in chunks if chunk.strip()]
        milvus_data = [
            {
                "document_id": doc_id,
                "chunk_text": description,
                "embedding": self.embedder.embed(description)
            }
        ]

        self.milvus.insert(collection_name=self.database, data=milvus_data)

        # for section_text in semantic_split(content, mode="section"):
        #     section_id = str(uuid.uuid4())
        #     self.client.insert("section", data=[{
        #         "section_id": section_id,
        #         "document_id": doc_id,
        #         "text": section_text
        #     }])
        #     chunks = semantic_split(section_text, mode="chunk")
        #     chunk_records = []
        #     for chunk_text in chunks:
        #         embedding = self.embedder.embed(chunk_text)
        #         # self.client.insert("chunks", data=[{
        #         #     "section_id": section_id,
        #         #     "chunk_text": chunk_text,
        #         #     "embedding": embedding
        #         # }])
        #         chunk_records.append({
        #             "section_id": section_id,
        #             "chunk_text": chunk_text,
        #             "embedding": embedding
        #         })
        #     batch_size = 8
        #     for i in range(0, len(chunk_records), batch_size):
        #         batch = chunk_records[i:i + batch_size]
        #         self.client.insert("chunks", data=batch)
        # print(f"[OK] 文档 '{title}' 分块插入完成。")

    def query(self, text: str, top_k: int = 5):
        qvec = self.embedder.embed(text)

        res = self.milvus.search(
            collection_name=self.database,
            data=[qvec],
            anns_field="embedding",
            search_params={"metric_type": "COSINE"},
            limit=top_k,
            output_fields=["chunk_text", "document_id"]
        )[0]
        results = []
        for hit in res:
            doc_id = hit["entity"]["document_id"]
            if doc_id:
                doc = self.client.get(
                    "original", 
                    ids=doc_id, 
                    output_column_name=["content", "source", "description", "title"]
                ).all()[0]
                results.append({
                    # "chunk": hit["entity"]["chunk_text"],
                    "document": doc[0],
                    "title": doc[3],
                    "source": doc[1],
                    "description": doc[2],
                    "similarity": hit["distance"]
                })
        return results
    
    def search(self, text: str, top_k: int = 5):
        qvec = self.embedder.embed(text)

        res = self.milvus.search(
            collection_name=self.database,
            data=[qvec],
            anns_field="embedding",
            search_params={"metric_type": "COSINE"},
            limit=top_k * 15,  # 加倍搜索量，提高命中概率
            output_fields=["chunk_text", "document_id"]
        )[0]

        seen_sources = set()
        results = []

        for hit in res:
            doc_id = hit["entity"]["document_id"]
            if not doc_id:
                continue
            doc = self.client.get(
                "original", 
                ids=doc_id, 
                output_column_name=["content", "source", "description", "title"]
            ).all()[0]

            source_url = doc[1]
            if source_url in seen_sources :
                continue  # 跳过重复
            seen_sources.add(source_url)

            results.append({
                # "chunk": hit["entity"]["chunk_text"],
                "document": doc[0],
                "title": doc[3],
                "source": source_url,
                "description": doc[2],
                "similarity": hit["distance"]
            })

            # if len(results) >= top_k:
            #     break

        return results

if __name__ == "__main__":
    rag = RAGDatabase(database="test_rag", dim=1024)
    # rag.insert_data(
    #     content="This is a test document for RAG database.",
    #     title="Test Document",
    #     source="https://example.com/test_document",
    #     description="This is a description of the test document."
    # )
    # print(rag.query("test document", top_k=5))
    # res = rag.query(SEARCH_QUERY)
    # result = [{
    #     "title": r["title"],
    #     "source": r["source"],
    #     "similarity": r["similarity"]
    # } for r in res if r["similarity"] > 0.5]
    # print(result)

    check_oceanbase_version()
    delete_database("test_rag")
    list_databases()

    # config_database()
    # client = ObVecClient(
    #     uri=OCEANBASE_CONFIG["host"] + ":" + str(OCEANBASE_CONFIG["port"]), 
    #     user=OCEANBASE_CONFIG["user"], 
    #     db_name="search_rag"
    # )
    # res = client.get(
    #     "test_rag",
    #     1,
    #     output_column_name=["chunk_text","source","sub_id"]).all()
    # print(res)
    # print(OCEANBASE_CONFIG)


    # import time
    # t1 = time.time()
    # rag = RAGDatabase("legal_data_2", 1024)
    # t2 = time.time()
    # print(f"RAGDatabase 初始化耗时: {t2 - t1:.2f}秒")

    # create rag
    # from data.chunk_split import extract_title_and_description
    # md_folder = "E:/AI/Chat/Qwen3/data/markdown"
    # for filename in os.listdir(md_folder):

    #     with open(os.path.join(md_folder, filename), "r", encoding="utf-8") as f:
    #         full_text = f.read()
    #     title, des, body = extract_title_and_description(full_text)
    #     rag.insert_data(body, os.path.splitext(filename)[0], os.path.splitext(filename)[0], des)
    #     t_temp = time.time()
    #     print(f"RAGDatabase 此轮耗时: {t_temp - t2:.2f}秒")
    # t3 = time.time()
    # print(f"RAGDatabase 总耗时: {t3 - t2:.2f}秒")
    
    # rag.insert("新测试！", source="https://example.com", sub_id="p1")
