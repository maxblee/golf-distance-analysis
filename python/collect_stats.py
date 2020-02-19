import os
import csv
import collections
import re
import time
import random
import urllib.parse
from typing import List, Dict, Optional
import requests
import bs4

def get_soup(url: str) -> bs4.BeautifulSoup:
    """Returns a BeautifulSoup object given a url."""
    resp = requests.get(url)
    if not resp.ok:
        resp.raise_for_status()
    return bs4.BeautifulSoup(resp.content, "html.parser")

def clean_column_names(column_names: List[bs4.element.Tag]):
    return [
        re.sub(r"\s+", "_", field.get_text().strip().lower()) 
        for field in column_names
    ]

def collect_tournament_stats(
        stat: str, 
        season: str, 
        time_period: str, 
        tournament: str
    ) -> List[Dict[str, str]]:
    """Collect the results from a specific PGA tournament, for a specific stats table.

    An example site is available here: 
    https://www.pgatour.com/content/pgatour/stats/stat.109.y2020.eon.t005.html

    Parameters
    ----------
    stat: str
        This is the specific stat you're looking at. In the example URL, it's 109.
    season:  str
        The year you're looking at. Forms the y2020 part of this URL.
    time_period: str
        This is whether you're looking at the Tournament Only
        or Year-to-Date through. The eon part of the example
    tournament: str
        The id of the tournament. This is t005 in this example
    """
    tournament_stats = []
    url = "https://www.pgatour.com/content/pgatour/stats/stat.{}.{}.{}.{}.html".format(
        stat, season, time_period, tournament
    )
    html = get_soup(url)
    table_container = html.find("div", class_="details-table-wrap")
    if table_container.get_text().strip() == "Data Not Available.":
        return []
    stat_table = table_container.find(id="statsTable")
    header_row = stat_table.find("thead").find("tr")
    fields = clean_column_names(header_row.find_all("th")) 
    player_rows = stat_table.find("tbody").find_all("tr")
    for row in player_rows:
        row_info = row.find_all("td")
        player_content = [field.get_text().strip() for field in row_info]
        for cell in row_info:
            if cell.has_attr("class") and "player-name" in cell.attrs["class"]:
                fields += ["player_id", "player_url"]
                player_base_url = cell.find("a")["href"]
                player_url = urllib.parse.urljoin(url, player_base_url)
                player_id = re.search(r"/players/player\.([0-9]{5})\..*", player_url).group(1)
                player_content += [player_id, player_url]
                break
        tournament_stats.append(dict(zip(fields, player_content)))
    return tournament_stats

def collect_stat_metadata(stat: str, season: Optional[str] = None) -> Dict[str, List[str]]:
    """Returns a list of valid seasons, time periods and tournaments,
    and their corresponding values for a specific stat.

    Parameters
    ----------
    stat: str
        The ID for the given stat (see `collect_tournament_stats`)
    season: Optional[str]
        If specified, get the tournament data (but not data on the seasons). Otherwise return {"season":[seasons]}
    """
    stats_metadata = {}
    url = "https://www.pgatour.com/stats/stat.{}.html".format(stat)
    html = get_soup(url)
    stats_group = html.find("div", class_="statistics-details-select-group")
    metadata_labels = clean_column_names(
        stats_group.find_all("span", class_="statistics-details-select-label")
    )
    stats_select_bars = stats_group.find_all("select", class_="statistics-details-select")
    for label, selection in zip(metadata_labels, stats_select_bars):
        stats_metadata[label] = [
            (item.get_text(), item["value"]) 
            for item in selection.find_all("option")
        ]
    if season is None:
        return { "season": stats_metadata["season"] }
    # The season data is useless if you're focusing on tournaments, because list of tournaments varies year by year
    del stats_metadata["season"]
    return stats_metadata

def _yield_stat_data(
        stat: str, 
        seasons: Optional[str] = None, 
        time_periods: Optional[str] = None
    ) -> Dict[str, str]:
    """Yields dictionary records to go into the final CSV, filtering out dat
    as specified in dump_stat_csv.
    """
    stat_metadata = collect_stat_metadata(stat)["season"]
    if seasons is not None:
        stat_metadata = [season for season in stat_metadata if season[0] in seasons]
    for season, season_id in stat_metadata:
        # be nice to the servers
        time.sleep(random.random() * 1.5)
        season_metadata = collect_stat_metadata(stat, season)
        for time_period, tp_id in season_metadata["time_period"]:
            if time_periods is not None and time_period not in time_periods:
                continue
            for tournament, tourn_id in season_metadata["tournament"]:
                record_metadata = {
                    "season": season,
                    "time_period": time_period,
                    "tournament": tournament
                }
                for record in collect_tournament_stats(stat, season_id, tp_id, tourn_id):
                    # Add season, time period and tournament data to each record
                    record.update(record_metadata)
                    yield record

def dump_stat_csv(
        path_to_csv: str,
        stat: str, 
        seasons: Optional[str] = None, 
        time_periods: Optional[str] = None,
        ) -> None:
    """Takes a stat and dumps the complete CSV file for that stat.

    Parameters
    ----------
    stat: str
        See the stat parameter for collect_tournament_stats
    seasons: Optional[int]
        If specified, a list of years to yield data from. Otherwise, returns all seasons
    time_periods: Optional[str]
        If specified, only returns some of the time periods. Otherwise returns all.
    """
    stat_records = list(_yield_stat_data(stat, seasons, time_periods))
    if len(stat_records) == 0:
        # write to an empty file if there aren't any records
        header = []
    elif len(stat_records) == 1:
        header = list(stat_records[0].keys())
    else:
        header = list(set(stat_records[0].keys()).union(*stat_records[1:]))
    with open(path_to_csv, "w") as csvfile:
        writer = csv.DictWriter(csvfile, header)
        writer.writeheader()
        for record in stat_records:
            writer.writerow(record)

def write_mult_stat_files(
        file_suffix: str,
        stats: List[str],
        file_dir: Optional[str] = None,
        seasons: Optional[str] = None,
        time_periods: Optional[str] = None
    ):
    """Takes a file suffix (e.g. golf_stats.csv) and prepends the name of each given stat,
    writing the file.
    """
    for stat in stats:
        path_to_file = "{}_{}".format(stat, file_suffix)
        path_to_file = os.path.join(file_dir, path_to_file) if file_dir is not None else path_to_file
        dump_stat_csv(path_to_file, stat, seasons, time_periods)

def main():
    """The main function. Runs on the command line."""
    import argparse
    parser = argparse.ArgumentParser(description="A command-line interface for scraping PGA data.")
    parser.add_argument("suffix", help="The suffix you plan on using to name your files. (e.g. have all files end with pga_stats20102020.csv)")
    parser.add_argument("-d", nargs="?", help="The directory you plan on sending your files to", dest="file_dir")
    parser.add_argument("--stats", nargs="+", help="The ID numbers for each of the stat tables you want to scrape")
    parser.add_argument("--seasons", nargs="*", help="If you want to parse specific seasons, write them e.g. 2018,2019 or 2018-2019")
    parser.add_argument("--time-periods", nargs="*", help="Tournament Only or Year-To-Date through")
    init_parse = parser.parse_args()
    suffix = init_parse.suffix
    stats = init_parse.stats
    file_dir = init_parse.file_dir
    seasons = []
    for season in init_parse.seasons:
        if re.match("[0-9]{4}\-[0-9]{4}", season):
            int_range = list(map(int, season.split("-")))
            # increase end so our range is inclusive
            int_range[1] += 1
            seasons += list(map(str, range(*int_range)))
        elif re.match("[0-9]{4}", season):
            seasons.append(season)
        else:
            raise ValueError("The season must be a valid 4-digit year")
    time_periods = init_parse.time_periods
    write_mult_stat_files(suffix, stats, file_dir, seasons, time_periods)

if __name__ == "__main__":
    main()