# analysis_results.R

# 1. Chargement des librairies
library(tidyverse)
library(reshape2)
library(scales)

# 2. Lecture des données
df <- read_csv("match_results.csv",
               col_types = cols(
                 ia_white = col_character(),
                 ia_black = col_character(),
                 winner   = col_integer()
               ))

# 3. Préparation : résultat relatif à l’IA “de référence” (celle en blanc)
df <- df %>%
  mutate(
    result = case_when(
      winner == 1 ~ "win",   # Blanc a gagné
      winner == 2 ~ "loss",  # Noir a gagné
      TRUE        ~ "draw"
    )
  )

# 4. Barplot par IA (tous rôles confondus)
summary_overall <- df %>%
  pivot_longer(cols = c(ia_white, ia_black),
               names_to = "role", values_to = "level") %>%
  # On considère “win” si IA de référence a gagné quand elle joue soit blanc (winner==1)
  # soit noir (winner==2 pour ia_black devient victoire pour level)
  mutate(
    result_ref = case_when(
      (role=="ia_white" & winner==1) | (role=="ia_black" & winner==2) ~ "win",
      (role=="ia_white" & winner==2) | (role=="ia_black" & winner==1) ~ "loss",
      TRUE                                                           ~ "draw"
    )
  ) %>%
  count(level, result_ref) %>%
  group_by(level) %>%
  mutate(pct = n / sum(n))

# Barplot
ggplot(summary_overall, aes(x=level, y=pct, fill=result_ref)) +
  geom_col(position="stack") +
  scale_y_continuous(labels = percent_format()) +
  scale_fill_manual(values = c("win"="seagreen", "draw"="goldenrod", "loss"="tomato")) +
  labs(
    title = "Performance globale par IA",
    x = "Niveau IA",
    y = "Proportion",
    fill = "Résultat"
  ) +
  theme_minimal()

# 5. Heatmap tête-à-tête (blanc vs noir)
h2h <- df %>%
  group_by(ia_white, ia_black) %>%
  summarise(
    n = n(),
    wins_white = sum(winner==1),
    pct_white = wins_white / n
  ) %>%
  ungroup() %>%
  # Pour la heatmap, garder ia_white vs ia_black
  dcast(ia_white ~ ia_black, value.var = "pct_white")

# Convertir en matrice et labels
rownames(h2h) <- h2h$ia_white
h2h <- h2h[,-1] %>% as.matrix()
colnames(h2h) <- paste0("B", colnames(h2h))
rownames(h2h) <- paste0("W", rownames(h2h))

# Affichage heatmap
library(ggplot2)
library(reshape2)
h2hmelt <- melt(h2h, varnames = c("White","Black"), value.name = "pct")

ggplot(h2hmelt, aes(x=Black, y=White, fill=pct)) +
  geom_tile(color="white") +
  scale_fill_gradient2(low="tomato", mid="white", high="seagreen",
                       midpoint=0.5, labels = percent_format()) +
  labs(
    title = "Tête-à-tête : taux de victoires des Blancs",
    x = "IA jouant Noir",
    y = "IA jouant Blanc",
    fill = "Win %"
  ) +
  theme_minimal() +
  theme(axis.text.x = element_text(angle=45, hjust=1))

# 6. Comparaison Blanc vs Noir pour chaque IA
summary_roles <- df %>%
  pivot_longer(cols = c(ia_white, ia_black),
               names_to = "role", values_to = "level") %>%
  mutate(
    win_ref = case_when(
      (role=="ia_white" & winner==1) | (role=="ia_black" & winner==2) ~ 1,
      TRUE                                                           ~ 0
    )
  ) %>%
  group_by(level, role) %>%
  summarise(win_rate = mean(win_ref)) %>%
  ungroup()

ggplot(summary_roles, aes(x=level, y=win_rate, fill=role)) +
  geom_col(position="dodge") +
  scale_y_continuous(labels=percent_format()) +
  scale_fill_manual(values=c("ia_white"="steelblue", "ia_black"="darkorange"),
                    labels=c("Joue Blanc","Joue Noir")) +
  labs(
    title="Taux de victoire selon le rôle (Blanc vs Noir)",
    x="Niveau IA",
    y="Taux de victoire",
    fill=""
  ) +
  theme_minimal()
