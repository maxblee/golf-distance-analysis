library(tidyverse)
library(janitor)

get_tournament_lengths <- function(tournament_df) {
  return(
    tournament_df %>%
      mutate(numeric_purse = as.numeric(str_replace(purse, "^null$", ""))) %>%
      group_by(tournament_clean, season,start_date,end_date,is_major,numeric_purse) %>%
      summarize(
        tournament_length = sum(yards),
        tournament_par = sum(par),
        total_num_holes = sum(num_holes)
      ) %>%
      filter(
        tournament_length != 0.,
        total_num_holes != 0.,
        # some tournaments (like Ryder Cup) don't have a purse
        !is.na(numeric_purse)
      ) %>%
      mutate(yards_per_hole = tournament_length / total_num_holes)
  )
}

get_money <- function(money_df) {
  return(
    money_df %>%
      mutate(
        money_numeric = as.numeric(str_replace_all(money, "[^0-9.]", "")),
        money_numeric = ifelse(is.na(money_numeric), 0, money_numeric),
      ) %>%
      # places where money == 0 seem to not give out money/have actual ranks
      filter(money_numeric != 0)
  )
}

join_all_data <- function(course_length_csv, money_csv, sg_ott_csv, sg_putt_csv) {
  clean_course_length <- get_tournament_lengths(read_csv(course_length_csv))
  clean_money <- get_money(read_csv(money_csv))
  clean_sg_ott <- read_csv(sg_ott_csv) %>%
    clean_names() %>%
    select(total_sg_ott, player_id, season, tournament_id) %>%
    # almost no records hit exactly 0 so when they do, assume it's null
    filter(total_sg_ott != 0)
  clean_sg_putting <- read_csv(sg_putt_csv) %>% 
    clean_names() %>% 
    select(total_sg_putting, player_id, season, tournament_id) %>%
    # almost no records hit exactly 0 so when they do, assume it's null
    filter(total_sg_putting != 0)
  money_and_tourn <- inner_join(clean_money, clean_course_length, by=c("tournament_clean", "season")) %>%
    mutate(pct_purse = money_numeric / numeric_purse)
  return(inner_join(
    inner_join(money_and_tourn, clean_sg_ott, by = c("player_id", "season", "tournament_id")),
    clean_sg_putting,
    by = c("player_id", "season", "tournament_id")
  ))
}

merge_prev <- function(joined_data) {
  final_data <- joined_data %>%
    arrange(player_id, tournament_id, season) %>%
    mutate(
      current_pid_tid = paste(player_id, tournament_id),
      prev_pid_tid = lag(current_pid_tid),
      prev_yards_p_hole = ifelse(prev_pid_tid == current_pid_tid, lag(yards_per_hole), NA),
      prev_sg_ott = ifelse(prev_pid_tid == current_pid_tid, lag(total_sg_ott), NA),
      prev_sg_putt = ifelse(prev_pid_tid == current_pid_tid, lag(total_sg_putting), NA),
    ) %>%
    select(
      player_id,
      player_name,
      tournament_id,
      tournament,
      tournament_clean,
      season,
      is_major,
      numeric_purse,
      yards_per_hole,
      money_numeric,
      total_sg_ott,
      total_sg_putting,
      pct_purse,
      prev_yards_p_hole,
      prev_sg_ott,
      prev_sg_putt
    )
  return(final_data)
}

course_length_csv <- "raw_data/course_length_clean.csv"
money_csv <- "raw_data/109_pga_clean.csv"
sg_ott_csv <- "raw_data/02567_20200309_pga_stats.csv"
sg_putt_csv <- "raw_data/02564_20200309_pga_stats.csv"

joined_data <- join_all_data(course_length_csv, money_csv, sg_ott_csv, sg_putt_csv)
data_w_prev_info <- merge_prev(joined_data)

all_data_path <- "clean_data/complete_merged_data.csv"
has_prev_path <- "clean_data/has_previous_year.csv"

# Write whole dataset
write_csv(data_w_prev_info, all_data_path)

# filter out cases where there isn't a previous baseline
has_prev_data <- data_w_prev_info %>%
  select(
    player_id,
    tournament_id,
    season,
    is_major,
    yards_per_hole,
    total_sg_ott,
    total_sg_putting,
    pct_purse,
    prev_yards_p_hole,
    prev_sg_ott,
    prev_sg_putt
  ) %>%
  drop_na()

write_csv(has_prev_data, has_prev_path)


