import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("test_script")
logger.info("Starting test script...")

try:
    logger.info("Attempting to import full_pipeline...")
    from vector_pipeline.pipeline.full_pipeline import run_pipeline
    logger.info("✅ Imports and setup passed successfully")
except Exception as e:
    logger.error(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
