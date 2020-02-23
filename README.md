# Analysis of Golf Shots

This is the GitHub repository we're using to analyze golf shots over time. Below, you'll see general information about the structure of the project and about installation.

## Table of Contents

- [Installation](#installation)
- [Data preparation](#data-preparation)
- [Project Structure](#project-structure)

## Installation

### Python dependencies

This project uses `requests` and `BeautifulSoup` to scrape data from the PGA tour so that we can analyze that data.
In order to install those, type

```sh
pipenv install
```

### R dependencies

First, this assumes that you have `R` installed to your computer. In addition, you should have packrat installed:

```r
install.packages("packrat")
```

From here, you can initialize the project by moving to the root of your repository and typing

```r
packrat::init()
```

This will install your required dependencies.

## Data Preparation

There are three scripts, all in the `python` directory, that are designed to help us collect data for
various statistics on PGA's site (i.e. they scrape data from the PGA site). 

The first, `collect_metadata.py`, collects basic information about every statistic on PGA's site. Specifically,
it creates a CSV describing the id of each statistic, the main statistic, the category of the statistic, the subcategory
on PGA's site, and the season for that statistic. For instance, one row looks like this:

```csv
stat_id,season,stat_type,category,subcategory
438,2020,Average Distance Of Putts Made,Putting,Avg. Putting Dist.
```

This should allow us to easily see the ID of each statistic and the years that statistic covers, which will be useful for
a) determining the date range our analysis can cover, and b) running the second script to actually get the data.

The second script, `collect_stats.py` provides a CLI to collect tournament-level data for most statistics on PGA's site.
(It won't currently work for the all-time stats or some of the Points/Rankings stats.) Its help menu is below:

```sh
usage: collect_stats.py [-h] [-d [FILE_DIR]] [--stats STATS [STATS ...]]
                        [--seasons [SEASONS [SEASONS ...]]]
                        [--time-periods [TIME_PERIODS [TIME_PERIODS ...]]]
                        suffix

A command-line interface for scraping PGA data.

positional arguments:
  suffix                The suffix you plan on using to name your files. (e.g.
                        have all files end with pga_stats20102020.csv)

optional arguments:
  -h, --help            show this help message and exit
  -d [FILE_DIR]         The directory you plan on sending your files to
  --stats STATS [STATS ...]
                        The ID numbers for each of the stat tables you want to
                        scrape
  --seasons [SEASONS [SEASONS ...]]
                        If you want to parse specific seasons, write them e.g.
                        2018,2019 or 2018-2019
  --time-periods [TIME_PERIODS [TIME_PERIODS ...]]
                        Tournament Only or Year-To-Date through
```

For our initial data acquisition (i.e. to get shots gained: putting, shots_gained: Off-The-Tee, and Money/Finishes),
I ran the following command.

```sh
python python/collect_stats.py raw_data/pga_stats.csv --stats 109 02564 02567 --seasons 2004-2019 --time-periods "Tournament Only" -d raw_data/
```

Finally, to get the lengths of courses for each year in our data, I used the script `collect_course__length.py`:

```sh
python python/collect_course_length.py raw_data/course_length_pga_stats.csv --seasons 2004-2019
```

## Project Structure

I've tried to make the structure of this project logical and straightforward. I've used labels derived from [this article](https://medium.com/@dave_lunny/sane-github-labels-c5d2e6004b63) and GitHub projects to allow the team to figure out what needs to be done.

Guides for setting up and quick explanations of how to do things (e.g. how do I install git?) are in the project Wiki.

In addition, the directory structure should be fairly straightforward:

- The `analysis` directory is for any analysis we do (using Jupyter Notebooks or RMarkdown files)
- The `clean_data` directory is for the final, processed data we'll be performing our analysis on
- The `R` directory is for any data preparation/cleaning scripts (using `.R` files)
- The `raw_data` directory is for any unprocessed data we use. We may wind up writing code to acquire this data (e.g. by scraping), but once we've acquired it, this original data should remain unchanged.
- The `research` directory is for writing our final paper and presentation and storing things like literature reviews. It will likely consist of RMarkdown files, .pdfs, powerpoints, and Markdown files