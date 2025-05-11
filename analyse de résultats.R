# analysis_results.R

# 1. Chargement des librairies
library(tidyverse)
library(reshape2)
library(scales)

# 2. Lecture du CSV tel quel
df <- read_csv("match_results.csv",
               col_types = cols(
                 ia_black = col_character(),
                 ia_white = col_character(),
                 winner   = col_integer()
               ))

# 3. Préparation du format “long” pour résumer par IA
df_long <- df %>%
  pivot_longer(
    cols = c(ia_black, ia_white),
    names_to  = "role",    # "ia_black" ou "ia_white"
    values_to = "level"    # niveau de l’IA
  ) %>%
  mutate(
    # on définit “win” si l’IA dans son rôle a gagné
    result_ref = case_when(
      (role == "ia_black" & winner == 2) |
        (role == "ia_white" & winner == 1) ~ "win",
      
      (role == "ia_black" & winner == 1) |
        (role == "ia_white" & winner == 2) ~ "loss",
      
      TRUE ~ "draw"
    )
  )

# 4. Barplot : performance globale par IA (tous rôles confondus)
summary_overall <- df_long %>%
  count(level, result_ref) %>%
  group_by(level) %>%
  mutate(pct = n / sum(n))

ggplot(summary_overall, aes(x = level, y = pct, fill = result_ref)) +
  geom_col(position = "stack") +
  scale_y_continuous(labels = percent_format()) +
  scale_fill_manual(values = c(win = "seagreen", draw = "goldenrod", loss = "tomato")) +
  labs(
    title = "Performance globale par IA",
    x     = "Niveau IA",
    y     = "Proportion",
    fill  = "Résultat"
  ) +
  theme_minimal()

# 5. Heatmap : taux de victoire du premier joueur (Noir) en format long
h2h_long <- df %>%
  group_by(ia_black, ia_white) %>%
  summarise(
    games      = n(),
    wins_black = sum(winner == 2),
    pct_black  = wins_black / games,
    .groups    = "drop"
  )

ggplot(h2h_long, aes(x = ia_white, y = ia_black, fill = pct_black)) +
  geom_tile(color = "white") +
  scale_fill_gradient2(
    low      = "tomato",
    mid      = "white",
    high     = "seagreen",
    midpoint = 0.5,
    labels   = percent_format()
  ) +
  labs(
    title = "Tête-à-tête : % de victoires du premier joueur (Noir)",
    x     = "IA jouant second (Blanc)",
    y     = "IA jouant premier (Noir)",
    fill  = "Win %"
  ) +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))

# 6. Comparaison taux de victoire selon le rôle
summary_roles <- df_long %>%
  group_by(level, role) %>%
  summarise(win_rate = mean(result_ref == "win"), .groups = "drop")

ggplot(summary_roles, aes(x = level, y = win_rate, fill = role)) +
  geom_col(position = "dodge") +
  scale_y_continuous(labels = percent_format()) +
  scale_fill_manual(
    values = c(ia_black = "steelblue", ia_white = "darkorange"),
    labels = c(ia_black = "Joue Noir (1er)", ia_white = "Joue Blanc (2nd)")
  ) +
  labs(
    title = "Taux de victoire selon le rôle (Noir vs Blanc)",
    x     = "Niveau IA",
    y     = "Taux de victoire",
    fill  = ""
  ) +
  theme_minimal()
