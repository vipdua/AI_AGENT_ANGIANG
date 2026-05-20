from rank_bm25 import BM25Okapi

from utils.logger import logger

# ===================================================
# 🧠 BM25 INDEX
# ===================================================
class BM25Search:

    def __init__(self, documents):

        self.documents = documents

        self.texts = [
            doc.page_content
            for doc in documents
        ]

        self.tokenized_texts = [

            text.lower().split()

            for text in self.texts
        ]

        self.bm25 = BM25Okapi(
            self.tokenized_texts
        )

        logger.info(
            "✅ BM25 index created"
        )

    # ===================================================
    # 🔍 SEARCH
    # ===================================================
    def search(

        self,

        query,

        top_k=5,

        department=None
    ):

        tokenized_query = (
            query.lower().split()
        )

        scores = self.bm25.get_scores(
            tokenized_query
        )

        ranked_results = sorted(

            zip(self.documents, scores),

            key=lambda x: x[1],

            reverse=True
        )

        results = []

        # ===================================================
        # 🔒 FILTER RESULTS
        # ===================================================
        for doc, score in ranked_results:

            # ===================================================
            # 🏢 DEPARTMENT FILTER
            # ===================================================
            if department:

                if (
                    doc.metadata.get(
                        "department"
                    ) != department
                ):

                    continue

            results.append(doc)

            if len(results) >= top_k:

                break

        return results