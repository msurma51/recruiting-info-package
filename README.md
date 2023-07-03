# Recruiting Info Scraper and Matcher: Project Overview
* Takes pre-scraped roster data and matches it with historical recruiting data from ESPN, 247 and Rivals.
* Uses Selenium to scrape desired recruiting data from the services mentioned above.
* Matching algorithms use fuzzy matching, equivalence and other proximity scores to calculate a comparison score
 between a roster entry and all unmatched recruiting info entries from a given service.
* Relevant information for the roster entry and top-scoring recruiting info entries are printed for visual
  comparison and manual selection of matches.
* Thresholds for automatic matching and determination of non-matches are added as data accumulates over time.

## Process
1. Run `get_players` to determine league of interest and populate/store roster info for players in that league.
2. Run `id_match_espn` to match roster info with previously scraped (if any) ESPN recruiting info
3. Run `espn_add_unmatched_looper` to scrape ESPN recruiting data for unmatched roster entries from Step 2
4. Run `id_match_espn_found` to match roster info with scraped ESPN data
5. Run `espn_merge` to merge roster info with ESPN recruiting info for all matches found
6. Run `id_match_247` to match merged roster/ESPN data with pre-scraped 247 recruiting info
7. Run `add_unmatched_247_looper` to scrape 247 data for unmatched roster entries from Step 6
8. Run `id_match_247_found` to match merged data with scraped 247 data
9. Run `id_match_247_no_espn` to match roster entries with no associated ESPN data to pre-scraped 247 data

