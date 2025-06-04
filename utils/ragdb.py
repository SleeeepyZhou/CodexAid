import json
import os, sys
currunt_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(currunt_dir, ".."))
DATA_PATH = os.path.join(currunt_dir, "..", "data")
from utils import EmbeddingModel, semantic_split

from typing import Optional
# from concurrent.futures import ThreadPoolExecutor
from pymilvus import MilvusClient, DataType

def create_milvus(
        url: str = "http://localhost:19530",
        name: str = "CodexAidBooks"
    ) -> bool:
    """
    创建或检查 Milvus 数据库是否存在。

    :param url: 数据库的 URL 地址
    :param name: 数据库名称
    :return: 如果数据库已存在或创建成功，返回 True；否则返回 False
    """
    try:
        client = MilvusClient(
            url,
            token="root:Milvus"
        )
        existing_databases = client.list_databases()
        if name in existing_databases:
            print(f"[OK] 已存在数据库 {name}")
            client.close()
            return True
        client.create_database(
            db_name=name,
            auto_id=True,
            enable_dynamic_field=True
        )
        client.close()
        print(f"[OK] 已创建数据库 {name}")
        return True
    except Exception as e:
        print(f"[ERROR] 创建 {name} 数据库失败:", e)
        return False

def list_databases(
    url: str = "http://localhost:19530"
    ) -> list:
    try:
        client = MilvusClient(
            url,
            token="root:Milvus"
        )
        existing_databases = client.list_databases()
        print("[OK] 当前数据库列表：")
        for db in existing_databases:
            print(f"  - {db}")
        return existing_databases
    except Exception as e:
        print("[ERROR] 查询数据库列表失败:", e)
        return []

def delete_database(
        url: str = "http://localhost:19530",
        name: str = "CodexAidBooks"
    ) -> bool:
    try:
        client = MilvusClient(
            url,
            token="root:Milvus"  
        )
        existing_databases = client.list_databases()
        if name in existing_databases:
            tables = client.list_collections()
            for table in tables:
                client.drop_collection(
                    collection_name=table
                )
            client.drop_database(
                db_name=name
            )
            print(f"[OK] 已删除数据库 {name}")
            client.close()
            return True
        else:
            print(f"[OK] 数据库 {name} 不存在")
            return True
    except Exception as e:
        print(f"[ERROR] 删除数据库 {name} 失败:", e)
        return False

class RAGDatabase:
    def __init__(
            self, 
            url: str = "http://localhost:19530",
            name: str = "CodexAidBooks"
        ):
        """
        初始化 RAGDatabase 类的实例。

        :param url: 数据库的 URL 地址
        :param name: 数据库名称
        """
        self.name = name
        self.embedder = EmbeddingModel()
        self.dim = len(self.embedder.embed("test"))

        if not create_milvus(
            url=url,
            name=name
        ):
            raise Exception(f"[ERROR] 启动 Milvus 数据库 {name} 失败")
        
        self.client = MilvusClient(
            uri=url,
            token="root:Milvus"
        )
        self.client.use_database(
            db_name=name
        )

    def __del__(self):
        self.client.close()

    def list_collection(self) -> list:
        """
        列出当前数据库中的所有数据表。

        :return: 数据表名称列表
        """
        try:
            databases = self.client.list_collections()
            print("[OK] 当前数据表列表：")
            for db in databases:
                print(f"  - {db}")
            return databases
        except Exception as e:
            print("[ERROR] 查询数据表列表失败:", e)
            return []
    
    def delete_collection(self, table: str) -> None:
        """
        删除指定的数据表。

        :param table: 要删除的数据表名称
        """
        try:
            if not self.client.has_collection(table):
                print(f"[OK] 数据表 {table} 不存在")
                return
            self.client.drop_collection(
                collection_name=table
            )
            with open(os.path.join(DATA_PATH, "original.json"), "r", encoding="utf-8") as f:
                original_data = json.load(f)
            if table in original_data:
                del original_data[table]
            with open(os.path.join(DATA_PATH, "original.json"), "w", encoding="utf-8") as f:
                json.dump(original_data, f, ensure_ascii=False, indent=4)
            print(f"[OK] 数据表 {table} 已删除")
        except Exception as e:
            print("[ERROR] 删除数据库失败:", e)

    def _table_create(self, table: str) -> None:
        """
        创建RAG数据表
        """
        # 分块表
        if not self.client.has_collection(table):
            print(f"[OK] 创建数据表 {table}")
            schema = MilvusClient.create_schema(
                auto_id=True,
                enable_dynamic_field=True,
            )
            schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True)
            schema.add_field(field_name="chunk_text", datatype=DataType.VARCHAR, max_length=2048)
            schema.add_field(field_name="embedding", datatype=DataType.FLOAT_VECTOR, dim=self.dim)

            index_params = self.client.prepare_index_params()
            index_params.add_index(
                field_name="id",
                index_type="AUTOINDEX"
            )

            index_params.add_index(
                field_name="embedding", 
                index_type="AUTOINDEX",
                metric_type="COSINE"
            )

            self.client.create_collection(
                collection_name=table,
                schema=schema,
                index_params=index_params
            )
        else:
            print(f"[OK] 数据表 {table} 已存在")

        res = self.client.get_load_state(
            collection_name=table
        )
        print(f"[OK] Vector index {res}.")

    def insert_data(
            self, 
            title: str, 
            content: str, 
            source: Optional[str] = None, 
            description: Optional[str] = None,
            table: str = None
        ):
        if not table:
            table = title.replace(" ", "_").replace("/", "_")
        self._table_create(table)
        table_inf = {
            "title": title,
            "source": source,
            "description": description
        }
        chunks = semantic_split(content)


        # def embed_chunk(chunk_text):
        #     return {
        #         "chunk_text": chunk_text,
        #         "embedding": self.embedder.embed(chunk_text)
        #     }
        # with ThreadPoolExecutor() as executor:
        #     milvus_data = list(executor.map(embed_chunk, chunks))


        milvus_data = [
            {
                "chunk_text": chunk_text,
                "embedding": self.embedder.embed(chunk_text)
            }
            for chunk_text in chunks
        ]

        self.client.insert(collection_name=table, data=milvus_data)
        print(f"[OK] 已插入 {len(milvus_data)} 条数据到 {table} 数据表")

        original_data = {}
        if os.path.exists(os.path.join(DATA_PATH, "original.json")):
            with open(os.path.join(DATA_PATH, "original.json"), "r", encoding="utf-8") as f:
                original_data = json.load(f)
        original_data[table] = table_inf
        with open(os.path.join(DATA_PATH, "original.json"), "w", encoding="utf-8") as f:
            json.dump(original_data, f, ensure_ascii=False, indent=4)
        print(f"[OK] 已更新表信息")

    def query(self, table: str, text: str, top_k: int = 5):
        qvec = self.embedder.embed(text)

        res = self.client.search(
            collection_name=table,
            data=[qvec],
            anns_field="embedding",
            search_params={"metric_type": "COSINE"},
            limit=top_k,
            output_fields=["chunk_text"]
        )[0]
        with open(os.path.join(DATA_PATH, "original.json"), "r", encoding="utf-8") as f:
            original_data = json.load(f)
            table_info = original_data.get(table, {})
        results = []
        for hit in res:
            results.append({
                "chunk": hit["entity"]["chunk_text"],
                "title": table_info.get("title"),
                "source": table_info.get("source", "Unknown Source"),
                "description": table_info.get("description", "Unknown Description"),
                "similarity": hit["distance"]
            })
        return results
    
    
if __name__ == "__main__":
    create_milvus()
    # rag = RAGDatabase(database="test_rag", dim=1024)
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

    # check_oceanbase_version()
    # delete_database("test_rag")
    # list_databases()

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
