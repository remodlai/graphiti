#!/usr/bin/env python3
"""
Test script for Graphiti Core with full logging enabled.
Run from the graphiti/ directory to test episode addition with detailed logs.
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType

# Configure comprehensive logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(),  # Console output
        logging.FileHandler('graphiti_debug.log')  # File output
    ]
)

# Set specific loggers to debug level
logging.getLogger('graphiti_core').setLevel(logging.DEBUG)
logging.getLogger('neo4j').setLevel(logging.DEBUG)
logging.getLogger('httpx').setLevel(logging.INFO)  # Reduce HTTP noise

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

async def test_episode_addition():
    """Test adding episodes with full logging."""
    
    # Get Neo4j connection parameters
    neo4j_uri = os.environ.get('NEO4J_URI')
    neo4j_user = os.environ.get('NEO4J_USER')
    neo4j_password = os.environ.get('NEO4J_PASSWORD')
    
    logger.info(f"Connecting to Neo4j at: {neo4j_uri}")
    logger.info(f"Using user: {neo4j_user}")
    
    if not all([neo4j_uri, neo4j_user, neo4j_password]):
        raise ValueError('NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD must be set in .env')
    
    # Initialize Graphiti
    logger.info("Initializing Graphiti...")
    graphiti = Graphiti(neo4j_uri, neo4j_user, neo4j_password)
    
    try:
        # Initialize indices
        logger.info("Building indices and constraints...")
        await graphiti.build_indices_and_constraints()
        logger.info("Indices and constraints built successfully")
        
        # Test episodes
        test_episodes = [
            {
                'content': 'Brian is working on fixing the JSON episode issue in Graphiti MCP server. The text episodes work fine but JSON episodes have problems.',
                'type': EpisodeType.text,
                'description': 'development issue',
            },
            {
                'content': {
                    'task': 'Debug Graphiti MCP JSON episodes',
                    'status': 'in_progress',
                    'developer': 'Brian',
                    'issue': 'JSON episodes not processing correctly',
                    'solution_approach': 'Run locally with full logging to identify the problem'
                },
                'type': EpisodeType.json,
                'description': 'structured task data',
            }
        ]
        
        # Add episodes with detailed logging
        for i, episode in enumerate(test_episodes):
            logger.info(f"\\n=== ADDING EPISODE {i+1} ===")
            logger.info(f"Type: {episode['type']}")
            logger.info(f"Content: {episode['content']}")
            
            try:
                await graphiti.add_episode(
                    name=f'Test Episode {i+1}',
                    episode_body=episode['content'] if isinstance(episode['content'], str) else json.dumps(episode['content']),
                    source=episode['type'],
                    source_description=episode['description'],
                    reference_time=datetime.now(timezone.utc),
                )
                logger.info(f"✅ Successfully added episode {i+1}")
                
            except Exception as e:
                logger.error(f"❌ Failed to add episode {i+1}: {e}")
                logger.exception("Full exception details:")
        
        # Test search
        logger.info("\\n=== TESTING SEARCH ===")
        try:
            results = await graphiti.search('JSON episodes debugging Brian')
            logger.info(f"Search returned {len(results)} results")
            
            for j, result in enumerate(results):
                logger.info(f"Result {j+1}: {result.fact}")
                
        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            logger.exception("Full search exception details:")
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        logger.exception("Full exception details:")
        
    finally:
        # Always close the connection
        logger.info("Closing Graphiti connection...")
        await graphiti.close()
        logger.info("Connection closed")

if __name__ == '__main__':
    logger.info("🚀 Starting Graphiti Core test with full logging...")
    asyncio.run(test_episode_addition())
    logger.info("✅ Test completed. Check graphiti_debug.log for detailed logs.")