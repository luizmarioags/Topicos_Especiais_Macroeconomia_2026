\name{m3e-model}
\alias{m3e_static_defaults}
\alias{m3e_static_matrices}
\alias{m3e_solve_static}
\alias{m3e_compare_static}
\alias{m3e_excel_static_scenarios}
\alias{m3e_dynamic_defaults}
\alias{m3e_dynamic_initial}
\alias{m3e_normalise_shocks}
\alias{m3e_excel_dynamic_shocks}
\alias{m3e_simulate_dynamic}
\alias{m3e_simulate_dynamic_matrix}
\alias{m3e_dynamic_matrices}
\alias{m3e_plot_gap}
\alias{m3e_plot_output}
\alias{m3e_plot_real_rate}
\alias{m3e_plot_inflation}
\alias{m3e_plot_dynamic_all}
\alias{m3e_plot_static_model}
\alias{m3e_generate_all}
\title{M3E Replication Functions}
\description{Functions for the static and dynamic M3E replication workflow.}
\usage{
m3e_static_defaults(...)
m3e_static_matrices(parameters = NULL)
m3e_solve_static(parameters = NULL)
m3e_compare_static(base = NULL, scenario = NULL)
m3e_excel_static_scenarios()
m3e_dynamic_defaults(...)
m3e_dynamic_initial(...)
m3e_normalise_shocks(shocks = NULL, horizon = 509L)
m3e_excel_dynamic_shocks(horizon = 509L)
m3e_simulate_dynamic(parameters = NULL, initial = NULL, shocks = NULL,
  horizon = 509L, include_parameters = TRUE)
m3e_simulate_dynamic_matrix(parameters = NULL, initial = NULL, shocks = NULL,
  horizon = 509L, include_parameters = TRUE)
m3e_dynamic_matrices(parameters = NULL)
m3e_plot_gap(data, period_max = 25L, file = NULL)
m3e_plot_output(data, period_max = 25L, file = NULL)
m3e_plot_real_rate(data, period_max = 25L, file = NULL)
m3e_plot_inflation(data, period_max = 25L, file = NULL)
m3e_plot_dynamic_all(data, output_dir, period_max = 25L)
m3e_plot_static_model(equilibrium_1, equilibrium_2, file = NULL)
m3e_generate_all(output_dir = "outputs/R")
}
\arguments{
  \item{...}{Named parameter overrides.}
  \item{parameters}{A named list of model parameters.}
  \item{base, scenario, equilibrium_1, equilibrium_2}{Static parameter lists or solutions.}
  \item{shocks}{A named list or data frame of shock paths.}
  \item{horizon}{Last simulated period, including period zero.}
  \item{initial}{A named list with the values observed at t = -1.}
  \item{include_parameters}{Whether to append parameter columns to the result.}
  \item{data}{A simulated dynamic data frame.}
  \item{period_max}{Last period shown in the chart; use NULL for all periods.}
  \item{file}{Optional PNG output path.}
  \item{output_dir}{Directory for generated replication outputs.}
}
\value{The object described by each function name: parameters, matrices, solutions, simulations or output paths.}

