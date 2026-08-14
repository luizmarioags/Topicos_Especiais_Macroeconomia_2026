# Paridade entre as APIs Python e R

| Objetivo | Python | R |
|---|---|---|
| Parâmetros estáticos | `StaticParameters()` | `m3e_static_defaults()` |
| Cenários estáticos do Excel | `excel_static_scenarios()` | `m3e_excel_static_scenarios()` |
| Matrizes estáticas | `static_matrices()` | `m3e_static_matrices()` |
| Solução estática | `solve_static()` | `m3e_solve_static()` |
| Comparar equilíbrios | `compare_static()` | `m3e_compare_static()` |
| Parâmetros dinâmicos | `DynamicParameters()` | `m3e_dynamic_defaults()` |
| Condição inicial | `DynamicInitial()` | `m3e_dynamic_initial()` |
| Choque do Excel | `excel_dynamic_shocks()` | `m3e_excel_dynamic_shocks()` |
| Simulação recursiva | `simulate_dynamic()` | `m3e_simulate_dynamic()` |
| Forma reduzida | `dynamic_reduced_form()` | `m3e_dynamic_matrices()` |
| Simulação matricial | `simulate_dynamic_matrix()` | `m3e_simulate_dynamic_matrix()` |
| Quatro gráficos | `plot_dynamic_all()` | `m3e_plot_dynamic_all()` |
| Gráfico estático | `plot_static_model()` | `m3e_plot_static_model()` |
| Gerar tudo | `m3e-replicate` / `generate_all()` | `m3e_generate_all()` |

Os nomes das colunas de saída são idênticos nos dois ambientes e coincidem
com o arquivo `reference/dynamic_excel_reference.csv`.

