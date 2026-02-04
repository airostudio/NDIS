#!/usr/bin/env python3
"""
Velma - NDIS Virtual AI Executive Suite
Main application entry point
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from velma.core import Velma
from velma.utils import Config, get_logger

logger = get_logger(__name__)


async def main():
    """Main application entry point"""
    logger.info("Starting Velma - NDIS Virtual AI Executive Suite")

    # Load configuration
    config = Config()

    # Initialize Velma
    velma = Velma(config)

    logger.info("Velma is ready!")
    print("\n" + "="*60)
    print("🤖  Velma - NDIS Virtual AI Executive Suite")
    print("="*60)
    print("\nVelma is running and ready to assist!")
    print(f"Company: {config.company_name}")
    print(f"Timezone: {config.timezone}")
    print("\nAvailable interfaces:")
    print("  - API: http://localhost:8000")
    print("  - Web Chat: http://localhost:8000/chat")
    print("  - API Docs: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop")
    print("="*60 + "\n")

    # Example: Process a test request
    try:
        # Interactive mode for testing
        print("Type your message (or 'quit' to exit):")

        while True:
            try:
                user_input = input("\nYou: ")

                if user_input.lower() in ['quit', 'exit', 'q']:
                    break

                # Process request
                response = await velma.process_request(
                    message=user_input,
                    channel="chat",
                    user_id="demo_user"
                )

                print(f"\nVelma: {response.get('message', 'No response')}")

            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Error processing request: {e}", exc_info=True)
                print(f"\nError: {e}")

    except KeyboardInterrupt:
        pass
    finally:
        # Cleanup
        logger.info("Shutting down Velma...")
        await velma.shutdown()
        logger.info("Velma shutdown complete")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
