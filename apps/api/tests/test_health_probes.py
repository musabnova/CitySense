import asyncio
from apps.api.core.database import check_db_health, engine
from apps.api.core.redis import check_redis_health, redis_client
from sqlalchemy import text

def test_database_connection():
    print("Testing DB connection...")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1;")).scalar()
        assert result == 1, f"Expected 1, got {result}"
    health = check_db_health()
    assert health["status"] == "healthy"
    print("TASK-004 Database connectivity verified: SELECT 1 returned 1.")

async def test_redis_connection():
    print("Testing Redis connectivity...")
    ping_result = await redis_client.ping()
    assert ping_result is True, "Redis ping failed"
    health = await check_redis_health()
    assert health["status"] == "healthy"
    print(f"TASK-005 Redis connectivity verified: mode={health['mode']}.")

def run_all_tests():
    test_database_connection()
    asyncio.run(test_redis_connection())
    print("ALL PHASE 1 HEALTH PROBE TESTS PASSED.")

if __name__ == "__main__":
    run_all_tests()

