from backend.rag.pipeline import KnowledgePipeline

# Shared pipeline instance
pipeline_instance = KnowledgePipeline()

def get_pipeline() -> KnowledgePipeline:
    return pipeline_instance