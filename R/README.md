# m3eReplication (R)

Pacote R, sem dependências externas, para reproduzir o M3E estático e
dinâmico.

```r
install.packages("m3eReplication", repos = NULL, type = "source")
library(m3eReplication)

cenarios <- m3e_excel_static_scenarios()
eq1 <- m3e_solve_static(cenarios$equilibrium_1)
eq2 <- m3e_solve_static(cenarios$equilibrium_2)

sim <- m3e_simulate_dynamic(
  shocks = m3e_excel_dynamic_shocks(509L),
  horizon = 509L
)

m3e_generate_all("outputs/R")
```

Os gráficos usam apenas o sistema gráfico básico do R.

