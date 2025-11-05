# Unlock Tool Auto - Password Reset Automation

## Project Overview
Automated password reset system for unlocktool.net accounts with:
- Cloudflare and reCAPTCHA bypass using free tools
- SQLite database for account and reset history tracking
- Scheduled task automation (Windows Task Scheduler)
- Email notifications
- Comprehensive logging

## Stack
- **Language**: Python 3.8+
- **Browser Automation**: Selenium WebDriver + Chrome
- **reCAPTCHA Handling**: 2captcha (free account) or manual solving
- **Database**: SQLite3
- **Scheduling**: APScheduler (free)
- **Free Tools**: Task Scheduler, Chrome, Python

## Key Components
1. `config/` - Configuration files and account lists
2. `src/` - Core application modules
3. `logs/` - Application and error logs
4. `database/` - SQLite database files

## Status Checklist
- [x] Project scaffolded
- [x] Directory structure created
- [ ] Dependencies installed
- [ ] Configuration files created
- [ ] Database schema initialized
- [ ] Core automation scripts created
- [ ] Scheduler configured
- [ ] Testing completed
- [ ] Windows Task Scheduler setup documented
