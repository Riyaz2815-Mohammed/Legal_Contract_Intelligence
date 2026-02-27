import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("test_script")

logger.info("Starting individual import testing...")

def test_import(module_name):
    logger.info(f"Importing {module_name}...")
    import importlib
    importlib.import_module(module_name)
    logger.info(f"✅ Imported {module_name}")

if __name__ == "__main__":
    try:
        test_import('vector_pipeline.config.settings')
        test_import('vector_pipeline.risk.risk_config')
        test_import('vector_pipeline.risk.risk_tagger')
        test_import('vector_pipeline.similarity.sbert_scorer')
        test_import('vector_pipeline.retrieval.query')
        test_import('vector_pipeline.llm.prompt')
        test_import('vector_pipeline.llm.reasoning')
        test_import('vector_pipeline.embeddings.embed_store')
        test_import('vector_pipeline.pipeline.full_pipeline')
        logger.info("🎉 All imports successful")
    except Exception as e:
        logger.error(f"❌ Failed on import: {e}")
        sys.exit(1)
