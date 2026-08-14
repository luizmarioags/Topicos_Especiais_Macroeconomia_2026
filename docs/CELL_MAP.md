# Mapeamento entre Excel e código

## Planilha estática: `M3E Estático v2 (1).xlsx`

### Aba `M3E equações`

A aba contém objetos gráficos com as hipóteses, as quatro equações do modelo,
as equações de Fisher e a definição do hiato e do juro natural. Não contém
células numéricas.

### Aba `M3E numérico`

| Intervalo | Conteúdo | Função correspondente |
|---|---|---|
| `A4:C14` | parâmetros dos equilíbrios 1 e 2 | `StaticParameters` / `m3e_static_defaults()` |
| `E2:H5` | matriz $A_1$ | `static_matrices()` / `m3e_static_matrices()` |
| `I2:I5` | vetor $b_1$ | mesmas funções |
| `E8:H11` | `MINVERSE(E2:H5)` | `solution.inverse` / `solution$A_inverse` |
| `I8:I11` | `MMULT(E8:H11,I2:I5)` | `solve_static()` / `m3e_solve_static()` |
| `E14:H17` | matriz $A_2$ | mesmas funções para o cenário 2 |
| `I14:I17` | vetor $b_2$ | mesmas funções para o cenário 2 |
| `E20:H23` | `MINVERSE(E14:H17)` | matriz inversa do cenário 2 |
| `I20:I23` | `MMULT(E20:H23,I14:I17)` | solução do cenário 2 |
| `K8:K11` | desvios do equilíbrio 1 | `compare_static()` / `m3e_compare_static()` |
| `K20:K23` | desvios do equilíbrio 2 | mesmas funções |

Ordenamento das linhas de solução: `y`, `pi_expected`, `pi`, `r_expected`.

## Planilha dinâmica: `M3E dinâmico v1.xlsx`

### Aba `M3E dinâmico`

| Intervalo | Conteúdo |
|---|---|
| `E3:F13` | condição inicial e parâmetros |
| `E15` | choque de 1% em `y_AD` no período zero |
| `B16:L16` | valores de longo prazo, referenciando a linha 528 |
| `B17:S17` | nomes das 18 séries e parâmetros |
| `A18:S18` | condição inicial em `t=-1` |
| `A19:S19` | período `t=0` e aplicação do choque |
| `A20:S528` | recursões até `t=509` |

As fórmulas do período $t$ são:

| Coluna | Fórmula conceitual | Exemplo no Excel |
|---|---|---|
| `A` | tempo | `A20=A19+1` |
| `B` | $h_t = y_t-y_t^{*}$ | `B20=C20-D20` |
| `C` | $y_t = y_{AD,t}-\gamma r_t^{e}$ | `C20=E20-M20*F20` |
| `D` | $y_t^{*}=(1-\eta)y_{t-1}^{*}+\eta y_{t-1}$ | `D20=(1-S20)*D19+S20*C19` |
| `E` | demanda autônoma | `E20=E19` |
| `F` | $r_t^{e}=r_{CB,t}+\phi_{\pi}(\pi_t^{e}-\pi_{GOV})$ | `F20=G20+P20*(J20-L20)` |
| `G` | $r_{CB,t}=r_{CB,t-1}+\phi_y h_{t-1}$ | `G20=G19+Q20*B19` |
| `H` | $r_t^{*}=\dfrac{y_{AD,t}-y_t^{*}}{\gamma}$ | `H20=(E20-D20)/M20` |
| `I` | $\pi_t=\pi_t^{e}+\alpha h_t$ | `I20=J20+O20*B20` |
| `J` | $\pi_t^{e}=\theta\pi_{t-1}+(1-\theta)\pi_t^{*}$ | `J20=N20*I19+(1-N20)*K20` |
| `K` | $\pi_t^{*}=(1-\chi)\pi_{GOV}+\chi\pi_{t-1}$ | `K20=(1-R20)*L20+R20*I19` |
| `L` | meta de inflação | `L20=L19` |
| `M:S` | parâmetros constantes | referência à linha anterior |

### Abas de gráficos

| Aba | Séries | Categorias |
|---|---|---|
| `Gráfico hiato` | `B18:B528` | `A18:A528` |
| `Gráfico produto` | `C18:C528`, `D18:D528` | `A18:A528` |
| `Gráfico juro real` | `F18:F528`, `G18:G528` | `A18:A528` |
| `Gráfico inflação` | `I18:I528`, `J18:J528`, `K18:K528` | `A18:A528` |
