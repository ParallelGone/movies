"""
Main orchestration script for Toronto Rep Cinema Calendar.
Runs all scrapers (optionally in parallel) and generates the calendar.
"""

import argparse
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict

from config import THEATERS, SCRAPE_SETTINGS
from scrapers import SCRAPER_REGISTRY
from generator import main as generate_calendar


def run_single_scraper(theater_id: str) -> Dict:
    """Run a single scraper and return results."""
    if theater_id not in SCRAPER_REGISTRY:
        print(f"❌ Unknown theater: {theater_id}")
        return {"theater": theater_id, "success": False, "count": 0, "error": "Unknown theater"}
        
    config = THEATERS.get(theater_id, {})
    if not config.get("enabled", True):
        print(f"⏭️ Skipping disabled theater: {theater_id}")
        return {"theater": theater_id, "success": False, "count": 0, "error": "Disabled"}
        
    scraper_class = SCRAPER_REGISTRY[theater_id]
    
    for attempt in range(SCRAPE_SETTINGS["retry_attempts"]):
        try:
            scraper = scraper_class()
            films = scraper.run()
            return {
                "theater": theater_id,
                "success": True,
                "count": len(films),
                "error": None
            }
        except Exception as e:
            print(f"⚠️ [{theater_id}] Attempt {attempt + 1} failed: {e}")
            if attempt < SCRAPE_SETTINGS["retry_attempts"] - 1:
                time.sleep(SCRAPE_SETTINGS["retry_delay"])
                
    return {"theater": theater_id, "success": False, "count": 0, "error": str(e)}


def run_scrapers_parallel(theater_ids: List[str], max_workers: int = 3) -> List[Dict]:
    """Run multiple scrapers in parallel."""
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_theater = {
            executor.submit(run_single_scraper, tid): tid 
            for tid in theater_ids
        }
        
        for future in as_completed(future_to_theater):
            theater_id = future_to_theater[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                results.append({
                    "theater": theater_id,
                    "success": False,
                    "count": 0,
                    "error": str(e)
                })
                
    return results


def run_scrapers_sequential(theater_ids: List[str]) -> List[Dict]:
    """Run scrapers one at a time."""
    results = []
    
    for theater_id in theater_ids:
        result = run_single_scraper(theater_id)
        results.append(result)
        
    return results


def print_results_summary(results: List[Dict]) -> None:
    """Print a summary of scraping results."""
    print("\n" + "=" * 50)
    print("📊 SCRAPING SUMMARY")
    print("=" * 50)
    
    total_films = 0
    successes = 0
    
    for result in results:
        status = "✅" if result["success"] else "❌"
        count = result["count"]
        theater = result["theater"].upper()
        
        if result["success"]:
            print(f"{status} {theater}: {count} films")
            total_films += count
            successes += 1
        else:
            print(f"{status} {theater}: Failed - {result['error']}")
            
    print("-" * 50)
    print(f"Total: {total_films} films from {successes}/{len(results)} theaters")
    print("=" * 50 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Toronto Rep Cinema Calendar - Scrape and Generate"
    )
    parser.add_argument(
        "--theaters", "-t",
        nargs="+",
        choices=list(SCRAPER_REGISTRY.keys()) + ["all"],
        default=["all"],
        help="Which theaters to scrape (default: all)"
    )
    parser.add_argument(
        "--parallel", "-p",
        action="store_true",
        help="Run scrapers in parallel (faster but uses more resources)"
    )
    parser.add_argument(
        "--workers", "-w",
        type=int,
        default=3,
        help="Number of parallel workers (default: 3)"
    )
    parser.add_argument(
        "--scrape-only", "-s",
        action="store_true",
        help="Only scrape, don't generate calendar"
    )
    parser.add_argument(
        "--generate-only", "-g",
        action="store_true",
        help="Only generate calendar from existing data"
    )
    parser.add_argument(
        "--no-git",
        action="store_true",
        help="Skip git commit and push"
    )
    
    args = parser.parse_args()
    
    # Determine which theaters to scrape
    if "all" in args.theaters:
        theater_ids = [
            tid for tid, config in THEATERS.items() 
            if config.get("enabled", True)
        ]
    else:
        theater_ids = args.theaters
        
    print("🎬 Toronto Rep Cinema Calendar")
    print(f"   Theaters: {', '.join(theater_ids)}")
    print(f"   Mode: {'Parallel' if args.parallel else 'Sequential'}")
    print()
    
    # Scrape phase
    if not args.generate_only:
        print("🔍 Starting scrapers...")
        start_time = time.time()
        
        if args.parallel:
            results = run_scrapers_parallel(theater_ids, args.workers)
        else:
            results = run_scrapers_sequential(theater_ids)
            
        elapsed = time.time() - start_time
        print_results_summary(results)
        print(f"⏱️ Scraping completed in {elapsed:.1f} seconds\n")
        
    # Generate phase
    if not args.scrape_only:
        print("🧩 Generating calendar...")
        generate_calendar()
        
    # Git phase (optional)
    if not args.no_git and not args.scrape_only:
        try:
            import subprocess
            print("\n📤 Publishing to GitHub...")
            subprocess.run(["git", "add", "index.html"], check=True)
            subprocess.run(
                ["git", "commit", "-m", "📅 Auto-update calendar"], 
                check=True
            )
            subprocess.run(["git", "push"], check=True)
            print("✅ Published to GitHub.")
        except subprocess.CalledProcessError:
            print("⚠️ Git push failed (may need manual commit)")
        except FileNotFoundError:
            print("⚠️ Git not found, skipping publish")
            
    print("\n🎉 Done!")


if __name__ == "__main__":
    main()
