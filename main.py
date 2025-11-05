"""Main application entry point."""

import argparse
import logging
import os
from dotenv import load_dotenv

from src.logger import setup_logging
from src.scheduler import ResetScheduler
from src.database import PasswordResetDB


def main():
    """Main application function."""
    parser = argparse.ArgumentParser(
        description='Automated password reset for unlocktool.net'
    )
    parser.add_argument(
        '--mode',
        choices=['run-once', 'schedule', 'daemon'],
        default='daemon',
        help='Execution mode'
    )
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level'
    )
    parser.add_argument(
        '--hour',
        type=int,
        default=None,
        help='Scheduled hour (0-23)'
    )
    parser.add_argument(
        '--minute',
        type=int,
        default=None,
        help='Scheduled minute (0-59)'
    )
    parser.add_argument(
        '--day',
        type=str,
        default='0',
        help='Day of week (0-6, 0=Monday)'
    )

    args = parser.parse_args()

    # Setup logging
    logger = setup_logging(args.log_level)
    logger.info("=" * 60)
    logger.info("Unlock Tool Password Reset Automation")
    logger.info("=" * 60)

    # Load environment variables
    load_dotenv()

    # Initialize scheduler
    scheduler = ResetScheduler()

    try:
        if args.mode == 'run-once':
            logger.info("Running password resets once...")
            results = scheduler.run_now()
            logger.info(f"Results: {results}")

        elif args.mode == 'schedule':
            # Get schedule from arguments or environment
            hour = args.hour or int(os.getenv('RESET_SCHEDULE_HOUR', '2'))
            minute = args.minute or int(os.getenv('RESET_SCHEDULE_MINUTE', '0'))
            day = args.day or os.getenv('RESET_SCHEDULE_DAY_OF_WEEK', '0')

            logger.info(f"Setting up scheduled job for {day} {hour:02d}:{minute:02d}")
            scheduler.schedule_job(hour=hour, minute=minute, day_of_week=day)
            scheduler.start()
            
            logger.info("Scheduler started. Press Ctrl+C to stop.")
            try:
                while True:
                    pass
            except KeyboardInterrupt:
                logger.info("Received interrupt signal")

        elif args.mode == 'daemon':
            # Load schedule from environment or use defaults
            hour = int(os.getenv('RESET_SCHEDULE_HOUR', '2'))
            minute = int(os.getenv('RESET_SCHEDULE_MINUTE', '0'))
            day = os.getenv('RESET_SCHEDULE_DAY_OF_WEEK', '0')

            logger.info(f"Starting daemon mode - scheduling for {day} {hour:02d}:{minute:02d}")
            scheduler.schedule_job(hour=hour, minute=minute, day_of_week=day)
            scheduler.start()
            
            logger.info("Daemon running. Press Ctrl+C to stop.")
            try:
                while True:
                    pass
            except KeyboardInterrupt:
                logger.info("Received interrupt signal")

    except Exception as e:
        logger.error(f"Application error: {str(e)}", exc_info=True)
        return 1

    finally:
        scheduler.stop()
        logger.info("Application stopped")

    return 0


if __name__ == '__main__':
    exit(main())
