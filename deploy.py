"""
Automated Update and GitHub Deployment Script

This script:
1. Runs all scrapers to get latest film data
2. Generates the HTML calendar
3. Commits changes to git
4. Pushes to GitHub (where it's hosted via GitHub Pages)

Usage:
    python deploy.py                    # Full update and deploy
    python deploy.py --scrape-only      # Just scrape, no deploy
    python deploy.py --skip-scrape      # Just deploy existing data
    python deploy.py --no-push          # Commit but don't push
"""

import argparse
import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path


class GitHubDeployer:
    """Handles scraping, generation, and GitHub deployment."""
    
    def __init__(self, args):
        self.args = args
        self.project_root = Path(__file__).parent
        self.data_dir = self.project_root / "data"
        self.errors = []
        
    def run_command(self, cmd, description, check=True, timeout=None):
        """Run a shell command and handle errors.

        Uses a process-group so timeouts reliably kill child processes (e.g., chromedriver).

        timeout: seconds (None = no timeout)
        """
        print(f"\n{'='*60}")
        print(f"📋 {description}")
        print(f"{'='*60}")

        # Start in a new process group so we can kill the whole tree on timeout.
        popen_kwargs = {
            "shell": True,
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
            "text": True,
            "cwd": self.project_root,
        }
        if os.name == "posix":
            popen_kwargs["start_new_session"] = True
        else:
            # Windows: create a new process group
            popen_kwargs["creationflags"] = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)

        try:
            proc = subprocess.Popen(cmd, **popen_kwargs)
            try:
                stdout, stderr = proc.communicate(timeout=timeout)
            except subprocess.TimeoutExpired:
                # Kill process group/session
                try:
                    if os.name == "posix":
                        import signal
                        os.killpg(proc.pid, signal.SIGKILL)
                    else:
                        proc.kill()
                except Exception:
                    proc.kill()
                stdout, stderr = proc.communicate()
                error_msg = f"⏱️ {description} - Timed out after {timeout}s (killed)"
                print(error_msg)
                self.errors.append(error_msg)
                if stdout:
                    print(stdout)
                if stderr:
                    print(f"Error: {stderr}")
                return False

            if stdout:
                print(stdout)

            if proc.returncode == 0:
                print(f"✅ {description} - Success!")
                return True

            error_msg = f"❌ {description} - Failed!"
            print(error_msg)
            if stderr:
                print(f"Error: {stderr}")
            self.errors.append(error_msg)
            return False

        except Exception as e:
            error_msg = f"❌ {description} - Unexpected error: {e}"
            print(error_msg)
            self.errors.append(error_msg)
            return False
    
    def check_git_setup(self):
        """Verify git is configured and we're in a git repo."""
        print("\n🔍 Checking git setup...")
        
        # Check if git is installed
        result = subprocess.run(
            "git --version",
            shell=True,
            capture_output=True
        )
        if result.returncode != 0:
            print("❌ Git is not installed!")
            return False
        
        # Check if we're in a git repo
        result = subprocess.run(
            "git rev-parse --git-dir",
            shell=True,
            capture_output=True,
            cwd=self.project_root
        )
        if result.returncode != 0:
            print("❌ Not in a git repository!")
            print("Run: git init")
            return False
        
        # Check if remote is configured
        result = subprocess.run(
            "git remote -v",
            shell=True,
            capture_output=True,
            text=True,
            cwd=self.project_root
        )
        if not result.stdout.strip():
            print("⚠️  No git remote configured!")
            print("Run: git remote add origin <your-github-repo-url>")
            return False
        
        print("✅ Git is properly configured")
        print(f"Remote(s):\n{result.stdout}")
        return True
    
    def run_scrapers(self):
        """Run all scrapers to fetch latest data."""
        if self.args.skip_scrape:
            print("\n⏭️  Skipping scraping (--skip-scrape flag)")
            return True
        
        print("\n" + "="*60)
        print("🎬 SCRAPING PHASE - Fetching Latest Film Data")
        print("="*60)
        
        scrapers = ['fox', 'paradise', 'revue', 'tiff', 'kingsway']
        all_success = True
        
        for scraper in scrapers:
            # FOX is intermittently flaky; retry once with a fresh browser if it times out/stalls.
            timeout_s = 240 if scraper == "fox" else 180

            success = self.run_command(
                f"{sys.executable} -m scrapers.{scraper}",
                f"Scraping {scraper.upper()}",
                check=False,  # Don't stop if one fails
                timeout=timeout_s,
            )

            if not success and scraper == "fox":
                print("🔁 FOX scrape failed; retrying once for freshest data...")
                # small breather to avoid reusing a bad state
                try:
                    import time
                    time.sleep(5)
                except Exception:
                    pass
                success = self.run_command(
                    f"{sys.executable} -m scrapers.{scraper}",
                    f"Scraping {scraper.upper()} (retry)",
                    check=False,
                    timeout=timeout_s,
                )

            if not success:
                all_success = False
                print(f"⚠️  Warning: {scraper} scraper failed, continuing...")
        
        if not all_success:
            print("\n⚠️  Some scrapers failed, but continuing with available data...")
        
        return True  # Continue even if some scrapers fail
    
    def generate_calendar(self):
        """Generate the HTML calendar from scraped data."""
        print("\n" + "="*60)
        print("📅 GENERATION PHASE - Creating HTML Calendar")
        print("="*60)
        
        return self.run_command(
            f"{sys.executable} generator.py",
            "Generating HTML calendar"
        )
    
    def check_changes(self):
        """Check if there are any changes to commit."""
        result = subprocess.run(
            "git status --porcelain",
            shell=True,
            capture_output=True,
            text=True,
            cwd=self.project_root
        )
        
        if not result.stdout.strip():
            print("\n📭 No changes detected - nothing to deploy!")
            return False
        
        print("\n📝 Changes detected:")
        print(result.stdout)
        return True
    
    def git_commit_and_push(self):
        """Commit changes and push to GitHub."""
        if self.args.no_push:
            print("\n⏭️  Skipping git push (--no-push flag)")
            return True
        
        print("\n" + "="*60)
        print("🚀 DEPLOYMENT PHASE - Pushing to GitHub")
        print("="*60)
        
        # Check if there are changes
        if not self.check_changes():
            return True
        
        # Add all changes
        if not self.run_command(
            "git add data/*.json index.html data/last_success.json",
            "Staging changes"
        ):
            return False
        
        # Commit with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_message = f"Update calendar - {timestamp}"
        
        if not self.run_command(
            f'git commit -m "{commit_message}"',
            "Committing changes"
        ):
            return False
        
        # Push to GitHub
        if not self.run_command(
            "git push origin main",
            "Pushing to GitHub",
            check=False  # Don't fail if branch name is different
        ):
            # Try 'master' if 'main' fails
            print("ℹ️  Trying 'master' branch...")
            if not self.run_command(
                "git push origin master",
                "Pushing to GitHub (master branch)"
            ):
                return False
        
        return True
    
    def run(self):
        """Main execution flow."""
        print("\n" + "="*60)
        print("🎬 TORONTO REP CINEMA CALENDAR - AUTO DEPLOY")
        print("="*60)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check git setup
        if not self.check_git_setup():
            print("\n❌ Git setup incomplete. Please configure git first.")
            return False
        
        # Phase 1: Scraping
        if not self.args.skip_scrape:
            if not self.run_scrapers():
                if not self.args.continue_on_error:
                    print("\n❌ Scraping failed. Stopping.")
                    return False
        
        # Phase 2: Generation
        if not self.args.scrape_only:
            if not self.generate_calendar():
                print("\n❌ Calendar generation failed. Stopping.")
                return False

            # Phase 2.5: Sanity check current scrape against previous baseline
            sanity = self.run_command(
                f"{sys.executable} check_sanity.py",
                "Sanity checking scraped counts",
                check=False,
                timeout=30,
            )
            if not sanity:
                print("\n❌ Sanity check failed. Stopping before deploy.")
                return False
        
        # Phase 3: Deployment
        if not self.args.scrape_only:
            if not self.git_commit_and_push():
                print("\n❌ Deployment to GitHub failed.")
                return False

            # Phase 3.5: Write/update success baseline after successful push
            self.run_command(
                f"{sys.executable} write_last_success.py",
                "Writing last success metadata",
                check=False,
                timeout=30,
            )
        
        # Summary
        print("\n" + "="*60)
        print("✅ DEPLOYMENT COMPLETE!")
        print("="*60)
        print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if self.errors:
            print(f"\n⚠️  Completed with {len(self.errors)} warnings:")
            for error in self.errors:
                print(f"  - {error}")
        
        print("\n🌐 Your calendar is now live on GitHub Pages!")
        print("   Visit: https://YOUR-USERNAME.github.io/YOUR-REPO-NAME/")
        
        return True


def main():
    parser = argparse.ArgumentParser(
        description='Scrape, generate, and deploy Toronto Rep Cinema calendar to GitHub'
    )
    
    parser.add_argument(
        '--scrape-only',
        action='store_true',
        help='Only run scrapers, skip generation and deployment'
    )
    
    parser.add_argument(
        '--skip-scrape',
        action='store_true',
        help='Skip scraping, just generate and deploy existing data'
    )
    
    parser.add_argument(
        '--no-push',
        action='store_true',
        help='Generate and commit, but do not push to GitHub'
    )
    
    parser.add_argument(
        '--continue-on-error',
        action='store_true',
        help='Continue even if some scrapers fail'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.scrape_only and args.skip_scrape:
        print("❌ Error: --scrape-only and --skip-scrape cannot be used together")
        sys.exit(1)
    
    deployer = GitHubDeployer(args)
    success = deployer.run()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
