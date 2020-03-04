library('tidyverse')

# Need to fill in missingness in rank
sg_putting <- read_csv('02564_pga_stats.csv')

# Need to fill in missingness in rank
sg_ott <- read_csv('02567_pga_stats.csv')

# Need to fill in missingness in rank
moneylist <- read_csv('109_pga_stats.csv')

tournaments <- read_csv('course_length_pga_stats.csv')
metadata <- read_csv('metadata.csv')

# Accounting for tie and NA values in sg_putting, sg_ott, and moneylist
# Replacing NA with 999 to reflect non-rank in a previous week

# sg_putt last week ties
sg_putt_lw_replace <- grep("T", sg_putting$rank_last_week, fixed=TRUE)
for (elem in sg_putt_lw_replace) {
  sg_putting$rank_last_week[elem] <- substr(sg_putting$rank_last_week[elem], 2, 2)
}

# sg_putt this week ties
sg_putt_tw_replace <- grep("T", sg_putting$rank_this_week, fixed=TRUE)
for (elem in sg_putt_tw_replace) {
  sg_putting$rank_this_week[elem] <- substr(sg_putting$rank_this_week[elem], 2, 2)
}

# sg_putt missing rank
for (i in 1:nrow(sg_putting)) {
  if (is.na(sg_putting$rank_last_week[i])) {
    sg_putting$rank_last_week[i] = 999
  }
}

# sg_ott last week ties
sg_ott_lw_replace <- grep("T", sg_ott$rank_last_week, fixed=TRUE)
for (elem in sg_ott_lw_replace) {
  sg_ott$rank_last_week[elem] <- substr(sg_ott$rank_last_week[elem], 2, 2)
}

# sg_ott this week ties
sg_ott_tw_replace <- grep("T", sg_ott$rank_this_week, fixed=TRUE)
for (elem in sg_ott_tw_replace) {
  sg_ott$rank_this_week[elem] <- substr(sg_ott$rank_this_week[elem], 2, 2)
}

# sg_ott missing rank
for (i in 1:nrow(sg_ott)) {
  if (is.na(sg_ott$rank_last_week[i])) {
    sg_ott$rank_last_week[i] = 999
  }
}

# moneylist last week ties
ml_lw_replace <- grep("T", moneylist$rank_last_week, fixed=TRUE)
for (elem in ml_lw_replace) {
  moneylist$rank_last_week[elem] <- substr(moneylist$rank_last_week[elem], 2, 2)
}

# moneylist this week ties
ml_tw_replace <- grep("T", moneylist$rank_this_week, fixed=TRUE)
for (elem in ml_tw_replace) {
  moneylist$rank_this_week[elem] <- substr(moneylist$rank_this_week[elem], 2, 2)
}

# moneylist missing rank
for (i in 1:nrow(moneylist)) {
  if (is.na(moneylist$rank_last_week[i])) {
    moneylist$rank_last_week[i] = 999
  }
}

# drop ytd victories because all NA values
drops_moneylist <- c("ytd_victories")
moneylist <- moneylist[ , !(names(moneylist) %in% drops_moneylist)]

# Outer join putting and ott on player id, tournament id, and year
ott_putting <- merge(x = sg_putting, y = sg_ott, by = c("tournament", "player_id", "season", "player_name", "player_url"), all = TRUE)
colnames(ott_putting) <- c("tournament", "player_id", "season", "player_name", "player_url",  "average_putting", "total_sg_putting", 
                           "rank_last_week_putting", "measured_rounds_putting", "time_period_putting", "rounds_putting",
                           "rank_this_week_putting", "tournament_id", "total_sg_ott", "measured_rounds_ott", "average_ott",
                           "rounds_ott", "rank_this_week_ott", "rank_last_week_ott", "time_period_ott")

#Outer join putting and ott with moneylist on player id, tournament id, and year
ott_putting_money <- merge(x = ott_putting, y = moneylist, by = c("tournament_id", "player_id", "season", "tournament", "player_name", "player_url"), all = TRUE)

#Left join putting, ott, and moneylist with tournaments information. 
#Note there are not entries in the tournaments information dataset for all tournaments.
all_data <- merge(x = ott_putting_money, y = tournaments, by.x = c("tournament", "season"), by.y = c("tournament_name", "season"), all.x = TRUE)

#Convert data to numeric
all_data$money = gsub(",", "", all_data$money)
all_data$money = gsub("[^a-zA-Z0-9.]", "", all_data$money)
all_data$money = as.numeric(all_data$money)
all_data$total_sg_ott = as.numeric(all_data$total_sg_ott)
all_data$total_sg_putting = as.numeric(all_data$total_sg_putting)

# drop columns in all_data that are all NA values
drops_alldata <- c("tournament_id.y", "start_date", "end_date", "is_major", "purse", "course_name",
           "yards", "par", "num_holes")
all_data <- all_data[ , !(names(all_data) %in% drops_alldata)]

# removing any missingness from edge cases
all_data <- all_data[complete.cases(all_data),]
ott_putting <- ott_putting[complete.cases(ott_putting),]
ott_putting_money <- ott_putting_money[complete.cases(ott_putting_money),]

write.csv(all_data, "clean_data.csv")

