from typing import Tuple


class PreValidator:
    """Pre-validation using Qdrant similarity search"""
    
    def __init__(self, vn_client, threshold: float = 0.5):
        self.vn = vn_client
        self.threshold = threshold
    
    def validate_question(self, question: str) -> Tuple[bool, str]:
        """Pre-validate question using Qdrant similarity search"""
        if not question or not question.strip():
            return False, "Question cannot be empty."
        
        # Check question length (too short questions are usually irrelevant)
        if len(question.strip()) < 3:
            return False, "Question is too short. Please provide a more detailed question."
        
        try:
            # Search for similar questions
            similar_qs_raw = self.vn._client.search(
                self.vn.sql_collection_name,
                query_vector=self.vn.generate_embedding(question),
                limit=self.vn.n_results,
                with_payload=True,
            )
            similar_qs = [result for result in similar_qs_raw if hasattr(result, 'score') and getattr(result, 'score', 0.0) >= self.threshold]
            
            # Search for related DDL
            related_ddl_raw = self.vn._client.search(
                self.vn.ddl_collection_name,
                query_vector=self.vn.generate_embedding(question),
                limit=self.vn.n_results,
                with_payload=True,
            )
            related_ddl = [result for result in related_ddl_raw if hasattr(result, 'score') and getattr(result, 'score', 0.0) >= self.threshold]
            
            # Search for related documentation
            related_doc_raw = self.vn._client.search(
                self.vn.documentation_collection_name,
                query_vector=self.vn.generate_embedding(question),
                limit=self.vn.n_results,
                with_payload=True,
            )
            related_doc = [result for result in related_doc_raw if hasattr(result, 'score') and getattr(result, 'score', 0.0) >= self.threshold]
            
            # Check if we found any relevant context
            if not similar_qs and not related_ddl and not related_doc:
                return False, "Sorry, your question does not match any known database context. Please clarify or rephrase your question."
            
            return True, "Valid question"
            
        except Exception as e:
            print(f"Pre-validation error: {e}")
            # If validation fails, allow the question to proceed (fail-safe)
            return True, "Validation skipped due to error"