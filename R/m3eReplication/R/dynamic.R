M3E_DYNAMIC_STATE <- c("y", "y_potential", "y_autonomous", "r_cb", "pi")
M3E_DYNAMIC_OUTPUTS <- c(
  "h", "y", "y_potential", "y_autonomous", "r_expected", "r_cb",
  "r_natural", "pi", "pi_expected", "pi_long_run", "pi_target"
)
M3E_DYNAMIC_SHOCKS <- c(
  "demand", "is", "inflation", "potential", "policy",
  "expectations_short", "expectations_long"
)
M3E_STATE_ROWS <- match(M3E_DYNAMIC_STATE, M3E_DYNAMIC_OUTPUTS)

.m3e_validate_dynamic <- function(parameters) {
  if (parameters$gamma <= 0) stop("gamma deve ser estritamente positivo")
  if (parameters$alpha <= 0) stop("alpha deve ser estritamente positivo")
  for (name in c("theta", "chi", "eta")) {
    if (parameters[[name]] < 0 || parameters[[name]] > 1) {
      stop(sprintf("%s deve pertencer ao intervalo [0, 1]", name))
    }
  }
  if (parameters$phi_pi < 0 || parameters$phi_y < 0) {
    stop("phi_pi e phi_y não podem ser negativos")
  }
  parameters
}

m3e_dynamic_defaults <- function(...) {
  parameters <- list(
    gamma = 2.0,
    theta = 0.3,
    alpha = 0.25,
    phi_pi = 1.5,
    phi_y = 0.25,
    chi = 0.1,
    eta = 0.05,
    pi_target = 0.035
  )
  changes <- list(...)
  if (length(changes)) parameters <- modifyList(parameters, changes)
  .m3e_validate_dynamic(parameters)
}

.m3e_dynamic_parameters <- function(parameters = NULL) {
  defaults <- m3e_dynamic_defaults()
  if (is.null(parameters)) return(defaults)
  .m3e_validate_dynamic(modifyList(defaults, parameters))
}

m3e_dynamic_initial <- function(...) {
  initial <- list(
    y = 1.0,
    y_potential = 1.0,
    y_autonomous = 1.1,
    r_expected = 0.05,
    r_cb = 0.05,
    pi = 0.035,
    pi_expected = 0.035,
    pi_long_run = 0.035
  )
  changes <- list(...)
  if (length(changes)) initial <- modifyList(initial, changes)
  initial
}

.m3e_dynamic_initial <- function(initial = NULL) {
  defaults <- m3e_dynamic_initial()
  if (is.null(initial)) return(defaults)
  modifyList(defaults, initial)
}

.m3e_transition <- function(previous_state, shock_vector, parameters) {
  p <- parameters
  previous_state <- setNames(as.numeric(previous_state), M3E_DYNAMIC_STATE)
  shock_vector <- setNames(as.numeric(shock_vector), M3E_DYNAMIC_SHOCKS)

  y_autonomous <- previous_state[["y_autonomous"]] + shock_vector[["demand"]]
  y_potential <-
    (1 - p$eta) * previous_state[["y_potential"]] +
    p$eta * previous_state[["y"]] +
    shock_vector[["potential"]]
  r_cb <-
    previous_state[["r_cb"]] +
    p$phi_y * (previous_state[["y"]] - previous_state[["y_potential"]]) +
    shock_vector[["policy"]]
  pi_long_run <-
    (1 - p$chi) * p$pi_target +
    p$chi * previous_state[["pi"]] +
    shock_vector[["expectations_long"]]
  pi_expected <-
    p$theta * previous_state[["pi"]] +
    (1 - p$theta) * pi_long_run +
    shock_vector[["expectations_short"]]
  r_expected <- r_cb + p$phi_pi * (pi_expected - p$pi_target)
  y <- y_autonomous - p$gamma * r_expected + shock_vector[["is"]]
  h <- y - y_potential
  pi <- pi_expected + p$alpha * h + shock_vector[["inflation"]]
  r_natural <- (y_autonomous - y_potential) / p$gamma

  c(
    h = h,
    y = y,
    y_potential = y_potential,
    y_autonomous = y_autonomous,
    r_expected = r_expected,
    r_cb = r_cb,
    r_natural = r_natural,
    pi = pi,
    pi_expected = pi_expected,
    pi_long_run = pi_long_run,
    pi_target = p$pi_target
  )
}

m3e_normalise_shocks <- function(shocks = NULL, horizon = 509L) {
  horizon <- as.integer(horizon)
  if (horizon < 0) stop("horizon deve ser maior ou igual a zero")
  result <- data.frame(t = 0:horizon, check.names = FALSE)
  for (name in M3E_DYNAMIC_SHOCKS) result[[name]] <- 0
  if (is.null(shocks)) return(result)

  if (is.data.frame(shocks)) {
    if (!"t" %in% names(shocks)) stop("o quadro de choques deve conter a coluna t")
    unknown <- setdiff(names(shocks), c("t", M3E_DYNAMIC_SHOCKS))
    if (length(unknown)) stop("choques desconhecidos: ", paste(unknown, collapse = ", "))
    for (name in intersect(names(shocks), M3E_DYNAMIC_SHOCKS)) {
      positions <- match(as.integer(shocks$t), result$t)
      valid <- !is.na(positions) & !is.na(shocks[[name]])
      result[[name]][positions[valid]] <- as.numeric(shocks[[name]][valid])
    }
    return(result)
  }

  if (!is.list(shocks)) stop("shocks deve ser uma lista ou data.frame")
  unknown <- setdiff(names(shocks), M3E_DYNAMIC_SHOCKS)
  if (length(unknown)) stop("choques desconhecidos: ", paste(unknown, collapse = ", "))
  for (name in names(shocks)) {
    value <- shocks[[name]]
    if (length(value) == 1L) {
      result[[name]][1] <- as.numeric(value)
    } else if (!is.null(names(value))) {
      periods <- as.integer(names(value))
      positions <- match(periods, result$t)
      valid <- !is.na(positions)
      result[[name]][positions[valid]] <- as.numeric(value[valid])
    } else if (length(value) == horizon + 1L) {
      result[[name]] <- as.numeric(value)
    } else {
      stop(sprintf(
        "choque '%s' deve ter %d elementos; recebeu %d",
        name, horizon + 1L, length(value)
      ))
    }
  }
  result
}

m3e_excel_dynamic_shocks <- function(horizon = 509L) {
  m3e_normalise_shocks(list(demand = c("0" = 0.01)), horizon)
}

.m3e_initial_row <- function(initial, parameters) {
  c(
    t = -1,
    h = initial$y - initial$y_potential,
    y = initial$y,
    y_potential = initial$y_potential,
    y_autonomous = initial$y_autonomous,
    r_expected = initial$r_expected,
    r_cb = initial$r_cb,
    r_natural = (initial$y_autonomous - initial$y_potential) / parameters$gamma,
    pi = initial$pi,
    pi_expected = initial$pi_expected,
    pi_long_run = initial$pi_long_run,
    pi_target = parameters$pi_target
  )
}

.m3e_append_parameters <- function(data, parameters) {
  for (name in c("gamma", "theta", "alpha", "phi_pi", "phi_y", "chi", "eta")) {
    data[[name]] <- parameters[[name]]
  }
  data
}

m3e_simulate_dynamic <- function(
  parameters = NULL,
  initial = NULL,
  shocks = NULL,
  horizon = 509L,
  include_parameters = TRUE
) {
  p <- .m3e_dynamic_parameters(parameters)
  init <- .m3e_dynamic_initial(initial)
  shock_data <- m3e_normalise_shocks(shocks, horizon)
  result <- matrix(
    NA_real_,
    nrow = horizon + 2L,
    ncol = length(M3E_DYNAMIC_OUTPUTS) + 1L,
    dimnames = list(NULL, c("t", M3E_DYNAMIC_OUTPUTS))
  )
  result[1, ] <- .m3e_initial_row(init, p)
  previous_state <- c(
    y = init$y,
    y_potential = init$y_potential,
    y_autonomous = init$y_autonomous,
    r_cb = init$r_cb,
    pi = init$pi
  )
  for (period in 0:horizon) {
    shock_vector <- unlist(
      shock_data[shock_data$t == period, M3E_DYNAMIC_SHOCKS, drop = FALSE],
      use.names = FALSE
    )
    output <- .m3e_transition(previous_state, shock_vector, p)
    result[period + 2L, ] <- c(t = period, output)
    previous_state <- output[M3E_STATE_ROWS]
  }
  data <- as.data.frame(result, check.names = FALSE)
  if (include_parameters) data <- .m3e_append_parameters(data, p)
  data
}

m3e_dynamic_matrices <- function(parameters = NULL) {
  p <- .m3e_dynamic_parameters(parameters)
  zero_state <- setNames(rep(0, length(M3E_DYNAMIC_STATE)), M3E_DYNAMIC_STATE)
  zero_shocks <- setNames(rep(0, length(M3E_DYNAMIC_SHOCKS)), M3E_DYNAMIC_SHOCKS)
  constant <- .m3e_transition(zero_state, zero_shocks, p)

  A <- vapply(seq_along(M3E_DYNAMIC_STATE), function(index) {
    basis <- zero_state
    basis[index] <- 1
    .m3e_transition(basis, zero_shocks, p) - constant
  }, numeric(length(M3E_DYNAMIC_OUTPUTS)))
  B <- vapply(seq_along(M3E_DYNAMIC_SHOCKS), function(index) {
    basis <- zero_shocks
    basis[index] <- 1
    .m3e_transition(zero_state, basis, p) - constant
  }, numeric(length(M3E_DYNAMIC_OUTPUTS)))
  rownames(A) <- M3E_DYNAMIC_OUTPUTS
  colnames(A) <- M3E_DYNAMIC_STATE
  rownames(B) <- M3E_DYNAMIC_OUTPUTS
  colnames(B) <- M3E_DYNAMIC_SHOCKS

  list(
    output_names = M3E_DYNAMIC_OUTPUTS,
    state_names = M3E_DYNAMIC_STATE,
    shock_names = M3E_DYNAMIC_SHOCKS,
    constant = constant,
    A = A,
    B = B,
    state_rows = M3E_STATE_ROWS,
    state_constant = constant[M3E_STATE_ROWS],
    F = A[M3E_STATE_ROWS, , drop = FALSE],
    G = B[M3E_STATE_ROWS, , drop = FALSE]
  )
}

m3e_simulate_dynamic_matrix <- function(
  parameters = NULL,
  initial = NULL,
  shocks = NULL,
  horizon = 509L,
  include_parameters = TRUE
) {
  p <- .m3e_dynamic_parameters(parameters)
  init <- .m3e_dynamic_initial(initial)
  shock_data <- m3e_normalise_shocks(shocks, horizon)
  matrices <- m3e_dynamic_matrices(p)
  result <- matrix(
    NA_real_,
    nrow = horizon + 2L,
    ncol = length(M3E_DYNAMIC_OUTPUTS) + 1L,
    dimnames = list(NULL, c("t", M3E_DYNAMIC_OUTPUTS))
  )
  result[1, ] <- .m3e_initial_row(init, p)
  previous_state <- c(
    y = init$y,
    y_potential = init$y_potential,
    y_autonomous = init$y_autonomous,
    r_cb = init$r_cb,
    pi = init$pi
  )
  for (period in 0:horizon) {
    shock_vector <- unlist(
      shock_data[shock_data$t == period, M3E_DYNAMIC_SHOCKS, drop = FALSE],
      use.names = FALSE
    )
    output <- drop(
      matrices$constant + matrices$A %*% previous_state + matrices$B %*% shock_vector
    )
    names(output) <- M3E_DYNAMIC_OUTPUTS
    result[period + 2L, ] <- c(t = period, output)
    previous_state <- output[M3E_STATE_ROWS]
  }
  data <- as.data.frame(result, check.names = FALSE)
  if (include_parameters) data <- .m3e_append_parameters(data, p)
  data
}

