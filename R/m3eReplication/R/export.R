.m3e_write_matrix <- function(matrix, path) {
  utils::write.csv(matrix, path, row.names = TRUE)
}

m3e_generate_all <- function(output_dir = "outputs/R") {
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
  scenarios <- m3e_excel_static_scenarios()
  equilibrium_1 <- m3e_solve_static(scenarios$equilibrium_1)
  equilibrium_2 <- m3e_solve_static(scenarios$equilibrium_2)
  .m3e_write_matrix(equilibrium_1$A, file.path(output_dir, "static_A.csv"))
  .m3e_write_matrix(
    equilibrium_1$A_inverse,
    file.path(output_dir, "static_A_inverse.csv")
  )
  utils::write.csv(
    m3e_compare_static(equilibrium_1, equilibrium_2),
    file.path(output_dir, "static_comparison.csv"),
    row.names = FALSE
  )
  m3e_plot_static_model(
    equilibrium_1,
    equilibrium_2,
    file.path(output_dir, "static_model.png")
  )

  trajectory <- m3e_simulate_dynamic(
    shocks = m3e_excel_dynamic_shocks(509L),
    horizon = 509L
  )
  utils::write.csv(
    trajectory,
    file.path(output_dir, "dynamic_simulation.csv"),
    row.names = FALSE
  )
  m3e_plot_dynamic_all(trajectory, output_dir, 25L)
  matrices <- m3e_dynamic_matrices()
  .m3e_write_matrix(matrices$A, file.path(output_dir, "dynamic_A.csv"))
  .m3e_write_matrix(matrices$B, file.path(output_dir, "dynamic_B.csv"))
  .m3e_write_matrix(matrices$F, file.path(output_dir, "dynamic_F.csv"))
  .m3e_write_matrix(matrices$G, file.path(output_dir, "dynamic_G.csv"))
  writeLines(
    c(
      sprintf("static_residual_max_abs=%.17g", max(abs(c(equilibrium_1$residual, equilibrium_2$residual)))),
      sprintf("dynamic_rows=%d", nrow(trajectory)),
      sprintf("dynamic_first_period=%d", min(trajectory$t)),
      sprintf("dynamic_last_period=%d", max(trajectory$t))
    ),
    file.path(output_dir, "run_metadata.txt")
  )
  invisible(output_dir)
}

