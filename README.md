# Analysis of Golf Shots

This is the GitHub repository we're using to analyze golf shots over time. Below, you'll see general information about the structure of the project and about installation.

## Table of Contents

- [Installation](#installation)
- [Project Structure](#project-structure)

## Installation

First, this assumes that you have `R` installed to your computer. In addition, you should have packrat installed:

```r
install.packages("packrat")
```

From here, you can initialize the project by moving to the root of your repository and typing

```r
packrat::init()
```

This will install your required dependencies.

## Project Structure

I've tried to make the structure of this project logical and straightforward. I've used labels derived from [this article](https://medium.com/@dave_lunny/sane-github-labels-c5d2e6004b63) and GitHub projects to allow the team to figure out what needs to be done.

Guides for setting up and quick explanations of how to do things (e.g. how do I install git?) are in the project Wiki.

In addition, the directory structure should be fairly straightforward:

- The `analysis` directory is for any analysis we do (using Jupyter Notebooks or RMarkdown files)
- The `clean_data` directory is for the final, processed data we'll be performing our analysis on
- The `R` directory is for any data preparation/cleaning scripts (using `.R` files)
- The `raw_data` directory is for any unprocessed data we use. We may wind up writing code to acquire this data (e.g. by scraping), but once we've acquired it, this original data should remain unchanged.
- The `research` directory is for writing our final paper and presentation and storing things like literature reviews. It will likely consist of RMarkdown files, .pdfs, powerpoints, and Markdown files