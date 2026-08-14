library(m3eReplication)

scenarios <- m3e_excel_static_scenarios()
solution_1 <- m3e_solve_static(scenarios$equilibrium_1)
solution_2 <- m3e_solve_static(scenarios$equilibrium_2)
stopifnot(max(abs(solution_1$values - c(1, 0.035, 0.035, 0.05))) < 1e-13)
stopifnot(max(abs(solution_2$values - c(
  1.0756756756756758,
  0.043108108108108105,
  0.06202702702702702,
  0.06216216216216216
))) < 1e-13)

shocks <- m3e_excel_dynamic_shocks(509L)
recursive <- m3e_simulate_dynamic(shocks = shocks, horizon = 509L)
matrix_run <- m3e_simulate_dynamic_matrix(shocks = shocks, horizon = 509L)
numeric_columns <- setdiff(names(recursive), "t")
stopifnot(max(abs(
  as.matrix(recursive[numeric_columns]) - as.matrix(matrix_run[numeric_columns])
)) < 5e-13)

reference_path <- system.file(
  "extdata", "dynamic_excel_reference.csv", package = "m3eReplication"
)
reference <- utils::read.csv(reference_path, check.names = FALSE)
stopifnot(identical(as.integer(recursive$t), as.integer(reference$t)))
stopifnot(max(abs(
  as.matrix(recursive[numeric_columns]) - as.matrix(reference[numeric_columns])
)) < 2e-13)

