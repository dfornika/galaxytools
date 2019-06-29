#!/usr/bin/env Rscript

library(grid)

suppressMessages(
  library(ggtree)
)

args = commandArgs(trailingOnly=TRUE)

tree <- read.tree(args[1])

tree_plot <- ggplot(tree, aes(x, y)) + 
  geom_tree() + 
  theme_tree2() +
  geom_tiplab(size=3, align=TRUE, hjust=-0.1) + ggplot2::xlim(0, 0.08) +
  geom_tippoint() +
  theme(plot.margin=unit(c(1,1,1,1),"cm"))

suppressMessages(
  ggsave(args[2], plot=tree_plot, device="png")
)
