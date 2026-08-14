# Pacote de replicação do M3E

Este repositório reproduz, em **Python** e **R**, o Modelo Macroeconômico de
3 Equações (M3E) apresentado nos slides e implementado nas duas planilhas
fornecidas. O pacote gera:

- as matrizes de coeficientes, vetores exógenos, matrizes inversas e soluções
  dos dois equilíbrios estáticos;
- a simulação dinâmica de `t = -1` a `t = 509`, com as mesmas 511 linhas e a
  mesma ordem de variáveis da planilha;
- a forma reduzida matricial do modelo dinâmico;
- os quatro gráficos da planilha dinâmica e um painel consolidado;
- um gráfico comparativo IS–CP–RM para o modelo estático;
- arquivos CSV de referência e testes de igualdade numérica.

## Fontes utilizadas

- `2026 Macro M3E Estático.pptx` — fundamentação do modelo estático;
- `M3E Estático v2 (1).xlsx` — matrizes e dois equilíbrios numéricos;
- `2026 Macroeconomia M3E dinâmico.pptx` — extensão dinâmica, expectativas e
  histerese;
- `M3E dinâmico v1.xlsx` — recursões, choque de demanda e gráficos.

Os arquivos originais não foram duplicados no pacote. A pasta `reference/`
contém os valores em cache necessários à validação e os hashes SHA-256 dos
arquivos-fonte analisados.

## Instalação e execução em Python

```bash
cd python
python -m pip install .
m3e-replicate --output-dir ../outputs/python
```

Sem instalar, a partir da raiz do pacote:

```bash
PYTHONPATH=python/src python python/examples/replicate_all.py \
  --output-dir outputs/python
```

Testes:

```bash
PYTHONPATH=python/src python -m unittest discover -s python/tests -v
```

## Instalação e execução em R

```r
install.packages("R/m3eReplication", repos = NULL, type = "source")
library(m3eReplication)
m3e_generate_all("outputs/R")
```

Ou, após a instalação:

```bash
Rscript R/m3eReplication/inst/examples/replicate_all.R outputs/R
```

## Exemplo mínimo

Python:

```python
from m3e import excel_dynamic_shocks, simulate_dynamic

sim = simulate_dynamic(
    shocks=excel_dynamic_shocks(509),
    horizon=509,
)
print(sim.loc[sim["t"].isin([-1, 0, 1, 509])])
```

R:

```r
sim <- m3e_simulate_dynamic(
  shocks = m3e_excel_dynamic_shocks(509L),
  horizon = 509L
)
sim[sim$t %in% c(-1, 0, 1, 509), ]
```

## Variantes teóricas

As versões apresentadas nos slides são obtidas sem mudar as equações:

| Variante | `chi` | `eta` |
|---|---:|---:|
| Expectativas ancoradas, sem histerese | `0` | `0` |
| Expectativas desancoradas, sem histerese | maior que `0` | `0` |
| Expectativas desancoradas e histerese (Excel) | `0.10` | `0.05` |

Em Python, use `DynamicParameters(chi=0, eta=0)`. Em R, use
`m3e_dynamic_defaults(chi = 0, eta = 0)`.

## Estrutura

```text
python/                 pacote Python instalável
R/m3eReplication/       pacote R instalável
reference/              valores de referência extraídos do Excel
outputs/python/         reprodução já gerada e verificada
docs/                    teoria, mapeamento das células e validação
tools/                   extrator opcional das planilhas originais
```

Leia `docs/MODEL_SPECIFICATION.md` para a matemática completa e
`docs/VALIDATION_REPORT.md` para os resultados dos testes.

