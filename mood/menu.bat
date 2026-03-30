@echo off
REM =================================================================
REM Crypto Sentiment Data Sourcing - Main Menu
REM =================================================================

:menu
cls
echo.
echo =================================================================
echo.  Crypto Sentiment Data Sourcing System
echo.
echo   Choose an option:
echo.
echo   1. Setup (install dependencies and Playwright)
echo   2. Run scraper (collect posts from Twitter and Reddit)
echo   3. Run Twitter scraper only
echo   4. Run Reddit scraper only
echo   5. Edit configuration
echo   6. View output files
echo   7. View logs
echo   8. Run example: Basic usage
echo   9. Run example: Custom config
echo   10. Run example: Data access
echo   11. Exit
echo.
echo =================================================================
echo.

set /p choice="Select option (1-11): "

if "%choice%"=="1" goto setup
if "%choice%"=="2" goto run_main
if "%choice%"=="3" goto run_twitter
if "%choice%"=="4" goto run_reddit
if "%choice%"=="5" goto edit_config
if "%choice%"=="6" goto view_output
if "%choice%"=="7" goto view_logs
if "%choice%"=="8" goto example_basic
if "%choice%"=="9" goto example_custom
if "%choice%"=="10" goto example_data
if "%choice%"=="11" goto exit_menu

echo Invalid choice. Try again.
timeout /t 2
goto menu

:setup
echo.
echo Running setup...
call setup.bat
goto menu

:run_main
echo.
echo Running full pipeline...
python -m data_sourcing.main
pause
goto menu

:run_twitter
echo.
echo Running Twitter scraper only...
python -c "
import asyncio
from data_sourcing.scrapers import TwitterScraper
from data_sourcing.storage import JSONWriter

async def main():
    scraper = TwitterScraper()
    posts = await scraper.run(keywords=['#Bitcoin', '#Crypto'], max_tweets=50)
    writer = JSONWriter()
    writer.save(posts, 'twitter')
    print(f'Collected {len(posts)} tweets')

asyncio.run(main())
"
pause
goto menu

:run_reddit
echo.
echo Running Reddit scraper only...
python -c "
import asyncio
from data_sourcing.scrapers import RedditScraper
from data_sourcing.storage import JSONWriter

async def main():
    scraper = RedditScraper()
    posts = await scraper.run(subreddits=['Bitcoin', 'CryptoCurrency'], max_posts_per_subreddit=25)
    writer = JSONWriter()
    writer.save(posts, 'reddit')
    print(f'Collected {len(posts)} posts')

asyncio.run(main())
"
pause
goto menu

:edit_config
echo.
echo Opening configuration file...
if exist "data_sourcing\config.py" (
    start notepad data_sourcing\config.py
) else (
    echo Configuration file not found!
)
goto menu

:view_output
echo.
echo Opening output directory...
if exist "data_sourcing\output" (
    start explorer data_sourcing\output
) else (
    echo Output directory doesn't exist yet. Run the scraper first!
)
pause
goto menu

:view_logs
echo.
echo Latest log file:
for /f "delims=" %%f in ('dir /b /o-d data_sourcing\output\scraper_*.log 2^>nul ^| findstr /r "." ^| findstr /v "^$"') do (
    echo Found: %%f
    type "data_sourcing\output\%%f"
    goto menu
)
echo No logs found yet. Run the scraper first!
pause
goto menu

:example_basic
echo.
echo Running example: Basic usage
python example_basic_run.py
pause
goto menu

:example_custom
echo.
echo Running example: Custom configuration
python example_custom_config.py
pause
goto menu

:example_data
echo.
echo Running example: Data access
python example_data_access.py
pause
goto menu

:exit_menu
echo Goodbye!
exit /b 0
