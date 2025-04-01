from prisma import Prisma
import logging
import time

logger = logging.getLogger(__name__)

# Track connection state to avoid redundant operations
_connection_state = {"connected": False, "last_check": 0}
_DB_HEALTH_CACHE_TTL = 60  # Cache DB health checks for 60 seconds
_prisma_initialized = False
prisma = Prisma()

async def connect_db():
    global _prisma_initialized
    start_time = time.time()
    logger.info("Starting database connection...")
    
    try:
        await prisma.connect()
        connect_time = time.time()
        logger.info(f"Prisma connected in {connect_time - start_time:.3f} seconds")
        
        # This is just a test query to warm up Prisma
        test_start = time.time()
        await prisma.execute_raw("SELECT 1;")
        test_end = time.time()
        logger.info(f"First test query took {test_end - test_start:.3f} seconds")
        
        _prisma_initialized = True
        end_time = time.time()
        logger.info(f"Total DB initialization: {end_time - start_time:.3f} seconds")
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        raise

async def disconnect_db():
    if _connection_state["connected"]:
        await prisma.disconnect()
        _connection_state["connected"] = False
        logger.info("Database disconnected")

async def check_db_health(force=False):
    now = time.time()
    # Use cached health result if recent
    if not force and now - _connection_state.get("last_check", 0) < _DB_HEALTH_CACHE_TTL:
        return _connection_state.get("health_status", {"database": "unknown"})
    
    try:
        start = time.time()
        await prisma.execute_raw("SELECT 1;")
        end = time.time()
        status = {"database": "connected", "query_time_ms": int((end - start) * 1000)}
        logger.debug(f"Database health check: {status}")
    except Exception as e:
        status = {"database": "disconnected", "error": str(e)}
        logger.error(f"Database health check failed: {e}")
    
    _connection_state["last_check"] = now
    _connection_state["health_status"] = status
    return status
