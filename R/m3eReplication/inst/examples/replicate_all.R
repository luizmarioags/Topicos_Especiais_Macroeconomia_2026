args <- commandArgs(trailingOnly = TRUE)
output_dir <- if (length(args)) args[[1]] else "outputs/R"
library(m3eReplication)
m3e_generate_all(output_dir)

