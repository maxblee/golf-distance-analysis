import time
import requests
import random
import csv
from typing import Iterator, Dict
import collect_stats

def get_course_detail(event_id: str) -> Iterator[Dict[str, str]]:
    """Returns the course length for each course in a tournament, given the id of the tournament."""
    api_endpoint = "http://sports.core.api.espn.com/v2/sports/golf/leagues/pga/events/{}".format(event_id)
    resp = requests.get(api_endpoint)
    if not resp.ok:
        resp.raise_for_status()
    endpoint_json = resp.json()
    for course in endpoint_json["courses"]:
        yield {
            "course_name": course["name"],
            "yards": course["totalYards"],
            "par": course["shotsToPar"],
            "num_holes": len(course["holes"])
        }

def get_courses_in_season(season: str) -> Iterator[Dict[str, str]]:
    """Returns the URL for every course in a given season, using ESPN's API Endpoint."""
    endpoint = "http://site.api.espn.com/apis/site/v2/sports/golf/pga/tourschedule?season={}".format(season)
    resp = requests.get(endpoint)
    if not resp.ok:
        resp.raise_for_status()
    endpoint_json = resp.json()
    for season in endpoint_json["seasons"]:
        # the ESPN API prints out every season but only displays events for requested season
        if "events" not in season:
            continue
        for event in season["events"]:
            event_info = {
                "season": season["year"],
                "tournament_name": event["label"],
                "start_date": event["startDate"],
                "end_date": event["endDate"],
                "tournament_id": event["id"],
                "is_major": event["isMajor"],
                # some events don't have a purse labeled
                "purse": event["purse"]["value"] if "purse" in event else "null"
            }
            yield event_info

def collect_course_info(seasons: Iterator[str]) -> Iterator[Dict[str, str]]:
    """Gets the course info for every course in ESPN's data.
    
    Parameters
    ----------
    Seasons: a range or list of integer seasons (e.g. range(2010, 2020))
    """
    for season in seasons:
        print("Processing {}".format(season))
        for event in get_courses_in_season(season):
            time.sleep(random.random())
            for course in get_course_detail(event["tournament_id"]):
                course_info = course.copy()
                course_info.update(event)    
                yield course_info            

def dump_csv(filepath: str, seasons: Iterator[str]) -> None:
    fieldnames = [
        "tournament_id", 
        "tournament_name", 
        "season",
        "start_date", 
        "end_date", 
        "is_major", 
        "purse",
        "course_name",
        "yards",
        "par",
        "num_holes"
    ]
    with open(filepath, "w") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames)
        writer.writeheader()
        for row in collect_course_info(seasons):
            writer.writerow(row)

def main():
    import argparse
    import os
    parser = argparse.ArgumentParser(description="Collects course information, season by season from ESPN")
    parser.add_argument("FILEPATH", help="The output path for your file.")
    parser.add_argument("--seasons", nargs="*", help="If you want to parse specific seasons, write them e.g. 2018,2019 or 2018-2019")
    parser_results = parser.parse_args()
    filepath = parser_results.FILEPATH
    seasons = collect_stats.parse_seasons(parser_results.seasons)
    if os.path.exists(filepath):
        check_overwrite = input(
            "You currently have a file {}. Do you want to overwrite that file? Y/N\n".format(filepath)
        )
        if check_overwrite.lower().strip() not in {"y", "yes"}:
            raise OSError("You declined to overwrite an existing file. Crashing.")
    dump_csv(filepath, seasons)

if __name__ == "__main__":
    main()