# Revue scraper memory

- 2026-03-26: Selenium/Bricks pagination path proved unreliable in headless cron runs.
- The Revue films page server-rendered HTML contains many more query-loop entries than the Selenium DOM initially materializes.
- Preferred direction: parse the richer HTML source directly with a realistic browser user-agent instead of relying on Bricks `Load More` interactions.
- 2026-03-26: The stable direct-source parser currently yields ~20 current Revue listings. Sanity checks must evaluate Revue against this new stable baseline rather than the old ~135 Selenium-era count.
- If the scraper changes, verify the fix cascades through local run, staged wrapper, git/origin, and live calendar output.
