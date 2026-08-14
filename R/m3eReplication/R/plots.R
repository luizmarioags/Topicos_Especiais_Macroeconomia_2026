M3E_BLUE <- "#156082"
M3E_ORANGE <- "#E97132"
M3E_LIGHT_BLUE <- "#00A6ED"
M3E_PURPLE <- "#7030A0"
M3E_RED <- "#FF0000"
M3E_GREEN <- "#00A65A"

.m3e_plot_window <- function(data, period_max) {
  if (is.null(period_max)) return(data)
  data[data$t >= -1 & data$t <= period_max, , drop = FALSE]
}

.m3e_open_png <- function(file, width = 1600, height = 950, res = 180) {
  if (is.null(file)) return(FALSE)
  dir.create(dirname(file), recursive = TRUE, showWarnings = FALSE)
  grDevices::png(file, width = width, height = height, res = res)
  TRUE
}

.m3e_percent_axis <- function(side, values, digits = 1) {
  ticks <- pretty(range(values, finite = TRUE))
  axis(side, at = ticks, labels = sprintf(paste0("%.", digits, "f%%"), 100 * ticks))
}

m3e_plot_gap <- function(data, period_max = 25L, file = NULL) {
  opened <- .m3e_open_png(file)
  if (opened) on.exit(grDevices::dev.off(), add = TRUE)
  x <- .m3e_plot_window(data, period_max)
  plot(x$t, x$h, type = "l", lwd = 2.5, col = M3E_BLUE, axes = FALSE,
       xlab = "t", ylab = "", main = "Hiato do Produto")
  axis(1)
  .m3e_percent_axis(2, x$h, 1)
  box()
  grid(col = "#D9D9D9")
  lines(x$t, x$h, lwd = 2.5, col = M3E_BLUE)
  invisible(file)
}

m3e_plot_output <- function(data, period_max = 25L, file = NULL) {
  opened <- .m3e_open_png(file)
  if (opened) on.exit(grDevices::dev.off(), add = TRUE)
  x <- .m3e_plot_window(data, period_max)
  matplot(
    x$t, cbind(x$y, x$y_potential), type = "l", lty = 1, lwd = 2.5,
    col = c(M3E_BLUE, M3E_ORANGE), xlab = "t", ylab = "",
    main = "Produto efetivo e potencial"
  )
  grid(col = "#D9D9D9")
  matlines(x$t, cbind(x$y, x$y_potential), lty = 1, lwd = 2.5,
           col = c(M3E_BLUE, M3E_ORANGE))
  legend("topright", legend = c("y", "y*"), col = c(M3E_BLUE, M3E_ORANGE),
         lty = 1, lwd = 2.5, bty = "n", horiz = TRUE)
  invisible(file)
}

m3e_plot_real_rate <- function(data, period_max = 25L, file = NULL) {
  opened <- .m3e_open_png(file)
  if (opened) on.exit(grDevices::dev.off(), add = TRUE)
  x <- .m3e_plot_window(data, period_max)
  values <- cbind(x$r_expected, x$r_cb)
  matplot(x$t, values, type = "l", lty = 1, lwd = 2.5,
          col = c(M3E_BLUE, M3E_ORANGE), axes = FALSE, xlab = "t", ylab = "",
          main = "Taxa de juro real e estimativa do juro natural pelo BCB")
  axis(1)
  .m3e_percent_axis(2, values, 2)
  box()
  grid(col = "#D9D9D9")
  matlines(x$t, values, lty = 1, lwd = 2.5, col = c(M3E_BLUE, M3E_ORANGE))
  legend("bottomright", legend = c("r_exp", "r_CB"),
         col = c(M3E_BLUE, M3E_ORANGE), lty = 1, lwd = 2.5, bty = "n", horiz = TRUE)
  invisible(file)
}

m3e_plot_inflation <- function(data, period_max = 25L, file = NULL) {
  opened <- .m3e_open_png(file)
  if (opened) on.exit(grDevices::dev.off(), add = TRUE)
  x <- .m3e_plot_window(data, period_max)
  values <- cbind(x$pi, x$pi_expected, x$pi_long_run)
  matplot(x$t, values, type = "l", lty = c(1, 1, 2), lwd = 2.5,
          col = c(M3E_LIGHT_BLUE, M3E_PURPLE, M3E_RED), axes = FALSE,
          xlab = "t", ylab = "",
          main = "Inflação e expectativas de inflação, de curto e longo prazo")
  axis(1)
  .m3e_percent_axis(2, values, 2)
  box()
  grid(col = "#D9D9D9")
  matlines(x$t, values, lty = c(1, 1, 2), lwd = 2.5,
           col = c(M3E_LIGHT_BLUE, M3E_PURPLE, M3E_RED))
  legend("topright", legend = c("pi", "pi_exp", "pi*"),
         col = c(M3E_LIGHT_BLUE, M3E_PURPLE, M3E_RED), lty = c(1, 1, 2),
         lwd = 2.5, bty = "n", horiz = TRUE)
  invisible(file)
}

m3e_plot_dynamic_all <- function(data, output_dir, period_max = 25L) {
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
  files <- c(
    gap = file.path(output_dir, "dynamic_gap.png"),
    output = file.path(output_dir, "dynamic_output.png"),
    real_rate = file.path(output_dir, "dynamic_real_rate.png"),
    inflation = file.path(output_dir, "dynamic_inflation.png")
  )
  m3e_plot_gap(data, period_max, files[["gap"]])
  m3e_plot_output(data, period_max, files[["output"]])
  m3e_plot_real_rate(data, period_max, files[["real_rate"]])
  m3e_plot_inflation(data, period_max, files[["inflation"]])
  invisible(files)
}

m3e_plot_static_model <- function(
  equilibrium_1,
  equilibrium_2,
  file = NULL
) {
  s1 <- .m3e_as_static_solution(equilibrium_1)
  s2 <- .m3e_as_static_solution(equilibrium_2)
  if (s1$parameters$theta == 0 || s1$parameters$phi_pi == 0 ||
      s2$parameters$theta == 0 || s2$parameters$phi_pi == 0) {
    stop("o gráfico RM requer theta e phi_pi estritamente positivos")
  }
  opened <- .m3e_open_png(file, width = 2200, height = 950)
  if (opened) on.exit(grDevices::dev.off(), add = TRUE)
  old_par <- par(no.readonly = TRUE)
  on.exit(par(old_par), add = TRUE)
  par(mfrow = c(1, 2), mar = c(4, 4, 4, 1))
  solutions <- list(s1, s2)
  y_min <- min(vapply(solutions, function(s) s$values[["y"]], numeric(1))) - 0.05
  y_max <- max(vapply(solutions, function(s) s$values[["y"]], numeric(1))) + 0.05
  y_grid <- seq(y_min, y_max, length.out = 300)

  r1 <- (s1$parameters$y_autonomous - y_grid) / s1$parameters$gamma
  r2 <- (s2$parameters$y_autonomous - y_grid) / s2$parameters$gamma
  matplot(y_grid, cbind(r1, r2), type = "l", lty = 1, lwd = 2.5,
          col = c(M3E_BLUE, M3E_LIGHT_BLUE), xlab = "y", ylab = "r esperado",
          main = "Curva IS")
  points(c(s1$values[["y"]], s2$values[["y"]]),
         c(s1$values[["r_expected"]], s2$values[["r_expected"]]),
         pch = 19, col = c(M3E_BLUE, M3E_LIGHT_BLUE))
  legend("topright", legend = c("IS 1", "IS 2"),
         col = c(M3E_BLUE, M3E_LIGHT_BLUE), lty = 1, lwd = 2.5, bty = "n")
  grid(col = "#D9D9D9")

  curves <- lapply(solutions, function(solution) {
    p <- solution$parameters
    pi_cp <- p$pi_long_run + p$alpha / (1 - p$theta) * (y_grid - p$y_potential)
    r_is <- (p$y_autonomous - y_grid) / p$gamma
    pi_rm <- (
      p$pi_target + (r_is - p$r_cb) / p$phi_pi -
        (1 - p$theta) * p$pi_long_run
    ) / p$theta
    list(cp = pi_cp, rm = pi_rm)
  })
  values <- cbind(curves[[1]]$cp, curves[[1]]$rm, curves[[2]]$cp, curves[[2]]$rm)
  matplot(y_grid, values, type = "l", lty = 1, lwd = 2.3,
          col = c(M3E_RED, M3E_GREEN, "#FF8080", "#66CC99"),
          xlab = "y", ylab = "inflação",
          main = "Curva de Phillips e regra monetária")
  points(c(s1$values[["y"]], s2$values[["y"]]),
         c(s1$values[["pi"]], s2$values[["pi"]]), pch = 19,
         col = c(M3E_BLUE, M3E_LIGHT_BLUE))
  legend("topright", legend = c("CP 1", "RM 1", "CP 2", "RM 2"),
         col = c(M3E_RED, M3E_GREEN, "#FF8080", "#66CC99"),
         lty = 1, lwd = 2.3, bty = "n", ncol = 2)
  grid(col = "#D9D9D9")
  invisible(file)
}

