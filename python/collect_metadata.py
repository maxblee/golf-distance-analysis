import time
import random
import re
import csv
import urllib
from typing import Iterator, Dict
import collect_stats

def get_all_stat_ids() -> Iterator[Dict[str, str]]:
    """Gets all of the categories, subcategories, and STAT IDs from the PGA Tour's site.
    """
    url = "https://www.pgatour.com/stats/categories.html"
    main_content = collect_stats.get_soup(url)
    stats_nav = main_content.find("section", class_="module-statistics-navigation")
    # the first item is just the overview page we're on
    main_categories = stats_nav.find("ul", class_="nav").find_all("li")[1:]
    for category in main_categories:
        link = urllib.parse.urljoin(url, category.find("a")["href"])
        category_name = category.get_text().strip().title()
        yield from get_stat_id(link, category_name)

def get_stat_id(url: str, category_name: str) -> Iterator[Dict[str, str]]:
    """Gets all Stat ids for a given category given the URL for the category."""
    category_page = collect_stats.get_soup(url)
    subcategories = category_page.find_all(
        "div", 
        class_="module-statistics-off-the-tee-table"
    )
    for subcategory in subcategories:
        subcategory_name = subcategory.find(
            "div", class_="header"
            ).get_text().title().strip()
        stat_links = subcategory.find("div", class_="table-content").find_all("a")
        for stat in stat_links:
            stat_name = stat.get_text().title().strip()
            stat_id = re.search(
                r"\/stats\/stat\.((?:ATR)?[0-9]+)\.html", stat["href"]
            ).group(1)
            yield {
                "category": category_name,
                "subcategory": subcategory_name,
                "stat_type": stat_name,
                "stat_id": stat_id
            }

def collect_all_metadata() -> Iterator[Dict[str,str]]:
    """Collects season-by-season metadata for every statistical category and subcategory
    on PGA's site.

    Example Return: [{
        "category": "Putting", "subcategory": "Avg. Putting Dist.",
        "stat_type": "Approach Putt Performance", "stat_id": "349",
        "season": "2020"
    }]
    """
    for stat_metadata in get_all_stat_ids():
        time.sleep(random.random() * 1.5)
        stat_id = stat_metadata["stat_id"]
        # if the stat is an all-time record, it won't have seasons affiliated with it
        if stat_id.startswith("ATR"):
            stat_metadata["season"] = "N/A"
            yield stat_metadata
        else:
            for season, _ in collect_stats.collect_stat_metadata(stat_id)["season"]:
                stat_metadata["season"] = season
                yield stat_metadata

def dump_metadata_csv(filepath: str) -> None:
    """Collects all metadata using `collect_all_metadata` and writes to csv.

    Parameters
    ----------
    filepath: str
        The relative or absolute path to your file
    """
    headers = ["stat_id", "season", "stat_type", "category", "subcategory"]
    with open(filepath, "w") as csvfile:
        writer = csv.DictWriter(csvfile, headers)
        writer.writeheader()
        for row in collect_all_metadata():
            writer.writerow(row)

def main():
    import argparse
    import os
    parser = argparse.ArgumentParser(
        description="A CLI tool to dump information about PGA statistics to a CSV"
    )
    parser.add_argument("FILEPATH", help="The output path for your file.")
    parser_results = parser.parse_args()
    filepath = parser_results.FILEPATH
    if os.path.exists(filepath):
        check_overwrite = input(
            "You currently have a file {}. Do you want to overwrite that file? Y/N\n"
        ).format(filepath)
        if check_overwrite.lower().strip() not in {"y", "yes"}:
            raise OSError("You declined to overwrite an existing file. Crashing.")
    dump_metadata_csv(filepath)

if __name__ == "__main__":
    main()
        