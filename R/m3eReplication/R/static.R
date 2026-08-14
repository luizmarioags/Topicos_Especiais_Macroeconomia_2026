M3E_STATIC_VARIABLES <- c("y", "pi_expected", "pi", "r_expected")

.m3e_validate_static <- function(parameters) {
  if (parameters$gamma <= 0) stop("gamma deve ser estritamente positivo")
  if (parameters$theta < 0 || parameters$theta >= 1) {
    stop("theta deve pertencer ao intervalo [0, 1)")
  }
  if (parameters$alpha <= 0) stop("alpha deve ser estritamente positivo")
  if (parameters$phi_pi < 0) stop("phi_pi não pode ser negativo")
  parameters
}

m3e_static_defaults <- function(...) {
  parameters <- list(
    y_potential = 1.0,
    y_autonomous = 1.1,
    r_cb = 0.05,
    pi_long_run = 0.035,
    pi_target = 0.035,
    gamma = 2.0,
    theta = 0.3,
    alpha = 0.25,
    phi_pi = 1.5
  )
  changes <- list(...)
  if (length(changes)) parameters <- modifyList(parameters, changes)
  parameters$r_natural <-
    (parameters$y_autonomous - parameters$y_potential) / parameters$gamma
  .m3e_validate_static(parameters)
}

.m3e_static_parameters <- function(parameters = NULL) {
  defaults <- m3e_static_defaults()
  if (is.null(parameters)) return(defaults)
  parameters$r_natural <- NULL
  result <- modifyList(defaults, parameters)
  result$r_natural <- (result$y_autonomous - result$y_potential) / result$gamma
  .m3e_validate_static(result)
}

m3e_static_matrices <- function(parameters = NULL) {
  p <- .m3e_static_parameters(parameters)
  A <- matrix(
    c(
      1, 0, 0, p$gamma,
      0, 1, -p$theta, 0,
      -p$alpha, -1, 1, 0,
      0, -p$phi_pi, 0, 1
    ),
    nrow = 4,
    byrow = TRUE,
    dimnames = list(
      c("IS", "expectations", "Phillips", "monetary_rule"),
      M3E_STATIC_VARIABLES
    )
  )
  b <- c(
    y_autonomous = p$y_autonomous,
    expectations = (1 - p$theta) * p$pi_long_run,
    Phillips = -p$alpha * p$y_potential,
    monetary_rule = p$r_cb - p$phi_pi * p$pi_target
  )
  list(A = A, b = b, variable_order = M3E_STATIC_VARIABLES)
}

m3e_solve_static <- function(parameters = NULL) {
  p <- .m3e_static_parameters(parameters)
  matrices <- m3e_static_matrices(p)
  A_inverse <- solve(matrices$A)
  values <- drop(A_inverse %*% matrices$b)
  names(values) <- M3E_STATIC_VARIABLES
  result <- list(
    parameters = p,
    A = matrices$A,
    b = matrices$b,
    A_inverse = A_inverse,
    values = values,
    output_gap = values[["y"]] - p$y_potential,
    nominal_rate_ex_ante = values[["r_expected"]] + values[["pi_expected"]],
    nominal_rate_ex_post = values[["r_expected"]] + values[["pi"]],
    residual = drop(matrices$A %*% values - matrices$b)
  )
  class(result) <- "m3e_static_solution"
  result
}

.m3e_as_static_solution <- function(value) {
  if (inherits(value, "m3e_static_solution")) return(value)
  m3e_solve_static(value)
}

m3e_compare_static <- function(base = NULL, scenario = NULL) {
  if (is.null(base) || is.null(scenario)) {
    defaults <- m3e_excel_static_scenarios()
    if (is.null(base)) base <- defaults$equilibrium_1
    if (is.null(scenario)) scenario <- defaults$equilibrium_2
  }
  base_solution <- .m3e_as_static_solution(base)
  scenario_solution <- .m3e_as_static_solution(scenario)
  relative <- ifelse(
    base_solution$values != 0,
    scenario_solution$values / base_solution$values - 1,
    NA_real_
  )
  data.frame(
    variable = M3E_STATIC_VARIABLES,
    equilibrium_1 = unname(base_solution$values),
    equilibrium_2 = unname(scenario_solution$values),
    absolute_deviation = unname(scenario_solution$values - base_solution$values),
    relative_deviation = unname(relative),
    check.names = FALSE
  )
}

m3e_excel_static_scenarios <- function() {
  list(
    equilibrium_1 = m3e_static_defaults(),
    equilibrium_2 = m3e_static_defaults(y_autonomous = 1.2)
  )
}
