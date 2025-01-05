import logging
from sqlglot import parse_one
from sqlglot.dialects.postgres import Postgres
import argparse

# Configure logging with more detail
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", force=True
)

# Get loggers
logger = logging.getLogger(__name__)
sqlglot_logger = logging.getLogger("sqlglot")
parser_logger = logging.getLogger("sqlglot.parser")
postgres_logger = logging.getLogger("sqlglot.dialects.postgres")

# Set all relevant loggers to DEBUG
for log in [logger, sqlglot_logger, parser_logger, postgres_logger]:
    log.setLevel(logging.DEBUG)

# Test SQL statements
test_sqls = {
    # Test 1: Basic XMLTABLE with XMLNAMESPACES
    1: """
    SELECT element_id, is_active, updated_at, description, reference_id 
    FROM XMLTABLE(
        XMLNAMESPACES(
            'http://example.com/xsd/sample/v1' AS "ex"
        ),
        '/root/item/*[local-name()="exampleElement"]'
        PASSING xml_content
        COLUMNS
            element_id   VARCHAR2(128) PATH '@id',
            is_active    BOOLEAN       PATH '@ex:isActive',
            updated_at   TIMESTAMP     PATH '@ex:updatedAt',
            description  VARCHAR2(4000) PATH 'ex:description/text()',
            reference_id UUID          PATH 'ex:reference/@ref'
    ) AS x
    """,
    # Test 2: XMLTABLE without XMLNAMESPACES
    2: """
    SELECT id, name 
    FROM XMLTABLE(
        '/root/user'
        PASSING xml_data
        COLUMNS
            id   INT    PATH '@id',
            name TEXT   PATH 'name/text()'
    ) AS t
    """,
    # Test 3: Multiple namespaces
    3: """
    SELECT id, value 
    FROM XMLTABLE(
        XMLNAMESPACES(
            'http://example.com/ns1' AS "ns1",
            'http://example.com/ns2' AS "ns2"
        ),
        '/root/data'
        PASSING xml_content
        COLUMNS
            id    INT  PATH '@ns1:id',
            value TEXT PATH 'ns2:value/text()'
    ) AS t
    """,
    # Test 4: Default namespace
    4: """
    SELECT id, value 
    FROM XMLTABLE(
        XMLNAMESPACES(
            DEFAULT 'http://example.com/default',
            'http://example.com/ns1' AS "ns1"
        ),
        '/root/data'
        PASSING xml_content
        COLUMNS
            id    INT  PATH '@id',
            value TEXT PATH 'ns1:value/text()'
    ) AS t
    """,
}


def main(test_number=2):  # Set default to test 2
    # Run tests with detailed logging
    logger.info("Starting XML parsing tests")

    # If a specific test is requested, run only that test
    if test_number:
        test_to_run = test_number
        logger.info(f"\n{'='*50}\nTest {test_to_run}:\n{'='*50}")
        logger.debug(f"Parsing SQL:\n{test_sqls[test_to_run]}")
        try:
            logger.debug("Calling parse_one...")
            ast = parse_one(test_sqls[test_to_run], read="postgres")
            logger.info(f"Successfully created AST: {ast}")
            generated_sql = ast.sql()
            logger.info(f"Generated SQL: {generated_sql}")
            logger.info("Test completed successfully")
        except Exception as e:
            logger.error(f"Error during parsing: {e}", exc_info=True)
    else:
        # Run all tests
        for i, sql in test_sqls.items():
            logger.info(f"\n{'='*50}\nTest {i}:\n{'='*50}")
            logger.debug(f"Parsing SQL:\n{sql}")
            try:
                logger.debug("Calling parse_one...")
                ast = parse_one(sql, read="postgres")
                logger.info(f"Successfully created AST: {ast}")
                generated_sql = ast.sql()
                logger.info(f"Generated SQL: {generated_sql}")
                logger.info("Test completed successfully")
            except Exception as e:
                logger.error(f"Error during parsing: {e}", exc_info=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run XML parsing tests")
    parser.add_argument(
        "--test", type=int, choices=[1, 2, 3, 4], help="Specific test to run", default=2
    )
    args = parser.parse_args()
    main(args.test)
